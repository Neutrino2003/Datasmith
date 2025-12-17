import operator
import json
import logging
import time
from typing import Optional, Literal, TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import get_settings
from schemas import InputType
from extractors import ContentExtractor
from pricing import PRICING

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


class TokenStats:
    """Track token usage and cost."""
    
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_time = 0.0
        self.model = "default"
    
    def add(self, input_tokens: int, output_tokens: int, time_taken: float):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_time += time_taken
    
    def estimate_cost(self) -> float:
        pricing = PRICING.get(self.model, PRICING["default"])
        input_cost = (self.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "estimated_cost_usd": round(self.estimate_cost(), 6),
            "total_time_sec": round(self.total_time, 2),
            "tokens_per_sec": round((self.input_tokens + self.output_tokens) / max(self.total_time, 0.01), 1)
        }


class AgentState(TypedDict):
    session_id: str
    user_message: Optional[str]
    file_content: Optional[bytes]
    filename: Optional[str]
    input_type: Optional[str]
    extracted_text: Optional[str]
    decision: Optional[str]
    response: Optional[str]
    error: Optional[str]
    history: Annotated[list[dict], operator.add]


class DatasmithAgent:
    """Main agent with coordinator pattern, guardrails, and fallbacks."""
    
    MAX_CONTENT_LENGTH = 50000
    MAX_RETRIES = 3
    
    FALLBACK_RESPONSES = {
        "rate_limit": "⚠️ Rate limit exceeded. Please wait a moment and try again.",
        "timeout": "⏱️ Request timed out. Please try with a shorter message.",
        "parse_error": "❌ Failed to process the response. Trying simpler format...",
        "general": "Something went wrong. Please try again."
    }
    
    def __init__(self):
        settings = get_settings()
        self.extractor = ContentExtractor()
        self.model_name = settings.llm_model
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            max_retries=self.MAX_RETRIES
        )
        self.confidence_threshold = settings.ambiguity_confidence_threshold
        self.graph = self._build_graph()
        self.stats = TokenStats()
        self.stats.model = self.model_name
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("preprocess", self._preprocess)
        workflow.add_node("coordinator", self._coordinator)
        workflow.add_node("summarize_agent", self._summarize)
        workflow.add_node("explain_agent", self._explain)
        workflow.set_entry_point("preprocess")
        workflow.add_edge("preprocess", "coordinator")
        workflow.add_conditional_edges("coordinator", self._route, {"summarize": "summarize_agent", "code": "explain_agent", "done": END})
        workflow.add_edge("summarize_agent", END)
        workflow.add_edge("explain_agent", END)
        return workflow.compile()

    async def _safe_llm_call(self, messages: list, fallback: str = None) -> tuple[str, int, int]:
        """LLM call with error handling and guardrails."""
        start_time = time.time()
        
        try:
            response = await self.llm.ainvoke(messages)
            elapsed = time.time() - start_time
            
            input_text = " ".join(m.content for m in messages)
            input_tokens = len(input_text) // 4
            response_text = self._extract_text(response.content)
            output_tokens = len(response_text) // 4
            
            self.stats.add(input_tokens, output_tokens, elapsed)
            logger.info(f"[LLM] {input_tokens}+{output_tokens} tokens, {elapsed:.2f}s")
            
            return response_text, input_tokens, output_tokens
            
        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"[LLM] Error: {e}")
            
            if "rate" in error_str or "quota" in error_str or "429" in error_str:
                raise Exception(self.FALLBACK_RESPONSES["rate_limit"])
            elif "timeout" in error_str:
                raise Exception(self.FALLBACK_RESPONSES["timeout"])
            else:
                raise Exception(fallback or self.FALLBACK_RESPONSES["general"])

    async def _preprocess(self, state: AgentState) -> dict:
        try:
            if state.get("file_content") and state.get("filename"):
                logger.info(f"[PREPROCESS] File: {state['filename']}")
                result = await self.extractor.extract(state["file_content"], state["filename"])
                
                text = result.extracted_text
                if len(text) > self.MAX_CONTENT_LENGTH:
                    text = text[:self.MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"
                    
                return {"input_type": result.input_type.value, "extracted_text": text, "error": result.error}
            
            if state.get("user_message"):
                logger.info(f"[PREPROCESS] Text: {len(state['user_message'])} chars")
                result = await self.extractor.extract(state["user_message"])
                return {"input_type": result.input_type.value, "extracted_text": result.extracted_text, "error": result.error}
            
            return {"error": "No input provided"}
        except Exception as e:
            logger.error(f"[PREPROCESS] Error: {e}")
            return {"error": str(e)}

    async def _coordinator(self, state: AgentState) -> dict:
        if state.get("error"):
            return {"decision": "done", "response": f"Error: {state['error']}"}
        
        content = state.get("extracted_text", "")
        user_msg = state.get("user_message", "") or ""
        
        logger.info(f"[COORDINATOR] Content: {len(content)} chars, Msg: '{user_msg[:30]}'")
        
        if not user_msg.strip() and state.get("file_content"):
            return {"decision": "done", "response": "I received your file. What would you like me to do?\n• **Summarize** the content\n• **Explain** it\n• Just **chat** about it"}
        
        try:
            intent = await self._classify_intent(content, user_msg)
            logger.info(f"[COORDINATOR] Intent: {intent}")
            
            if intent == "summarize":
                return {"decision": "summarize"}
            elif intent in ["code", "explain"]:
                return {"decision": "code"}
            elif intent == "clarify":
                return {"decision": "done", "response": "What would you like me to do?\n• **Summarize**\n• **Explain**\n• **Analyze sentiment**"}
            else:
                response = await self._handle_direct(content, user_msg, intent)
                return {"decision": "done", "response": response}
        except Exception as e:
            return {"decision": "done", "response": str(e)}

    async def _classify_intent(self, content: str, prompt: str) -> str:
        try:
            system = 'Classify intent. Return JSON: {"intent": "summarize"|"explain"|"sentiment"|"chat"|"clarify", "confidence": 0.0-1.0}'
            response_text, _, _ = await self._safe_llm_call([
                SystemMessage(content=system),
                HumanMessage(content=f"User: {prompt}\nContent: {content[:500]}")
            ])
            result = self._extract_json(response_text)
            return result.get("intent", "chat") if float(result.get("confidence", 0)) >= self.confidence_threshold else "clarify"
        except:
            return "chat"

    async def _handle_direct(self, content: str, prompt: str, intent: str) -> str:
        try:
            if intent == "sentiment":
                system = 'Analyze sentiment. Return JSON: {"label": "Positive"|"Negative"|"Neutral", "confidence": 0.0-1.0, "justification": "..."}'
                response_text, _, _ = await self._safe_llm_call([SystemMessage(content=system), HumanMessage(content=f"Analyze:\n{content}")])
                r = self._extract_json(response_text)
                emoji = {"Positive": "😊", "Negative": "😔", "Neutral": "😐"}.get(r["label"], "🤔")
                return f"## Sentiment\n\n**Result:** {emoji} {r['label']}\n**Confidence:** {r['confidence']:.0%}\n**Reason:** {r['justification']}"
            else:
                response_text, _, _ = await self._safe_llm_call([
                    SystemMessage(content="You are Datasmith AI, a helpful assistant."),
                    HumanMessage(content=prompt if not content else f"Context:\n{content[:1000]}\n\nUser: {prompt}")
                ])
                return response_text
        except Exception as e:
            return str(e)

    def _extract_text(self, content) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return ' '.join(item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in content)
        elif isinstance(content, dict):
            return content.get('text', str(content))
        return str(content)

    def _extract_json(self, text: str) -> dict:
        import re
        try:
            return json.loads(text)
        except:
            pass
        
        for pattern in [r'```json\s*(.*?)\s*```', r'```\s*(.*?)\s*```']:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    continue
        
        start, end = text.find('{'), text.rfind('}') + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except:
                pass
        
        raise ValueError("Could not parse JSON")

    def _route(self, state: AgentState) -> Literal["summarize", "code", "done"]:
        return state.get("decision", "done")

    async def _summarize(self, state: AgentState) -> dict:
        logger.info("[SUMMARIZE] Starting...")
        try:
            content = state.get("extracted_text", "")
            system = 'Summarize. Return JSON: {"one_line": "...", "bullets": ["...", "...", "..."], "five_sentence": "..."}'
            response_text, _, _ = await self._safe_llm_call([SystemMessage(content=system), HumanMessage(content=f"Summarize:\n{content}")])
            r = self._extract_json(response_text)
            bullets = "\n".join(f"• {b}" for b in r["bullets"])
            return {"response": f"## Summary\n\n**TL;DR:** {r['one_line']}\n\n**Key Points:**\n{bullets}\n\n**Details:**\n{r['five_sentence']}"}
        except Exception as e:
            try:
                response_text, _, _ = await self._safe_llm_call([
                    SystemMessage(content="Summarize the content concisely."),
                    HumanMessage(content=f"Summarize:\n{state.get('extracted_text', '')[:2000]}")
                ], fallback="Could not summarize")
                return {"response": f"## Summary\n\n{response_text}"}
            except Exception as e2:
                return {"response": str(e2)}

    async def _explain(self, state: AgentState) -> dict:
        logger.info("[EXPLAIN] Starting...")
        try:
            content = state.get("extracted_text", "")
            user_msg = state.get("user_message", "")
            system = 'Explain the content. Return JSON: {"explanation": "...", "key_points": ["...", "..."]}'
            response_text, _, _ = await self._safe_llm_call([SystemMessage(content=system), HumanMessage(content=f"User: {user_msg}\n\nContent:\n{content}")])
            r = self._extract_json(response_text)
            points = "\n".join(f"• {p}" for p in r.get("key_points", [])) if r.get("key_points") else ""
            result = f"## Explanation\n\n{r['explanation']}"
            if points:
                result += f"\n\n**Key Points:**\n{points}"
            return {"response": result}
        except Exception as e:
            try:
                response_text, _, _ = await self._safe_llm_call([
                    SystemMessage(content="Explain the content clearly."),
                    HumanMessage(content=f"Explain:\n{state.get('extracted_text', '')[:2000]}")
                ], fallback="Could not explain")
                return {"response": f"## Explanation\n\n{response_text}"}
            except Exception as e2:
                return {"response": str(e2)}

    def reset_stats(self):
        self.stats = TokenStats()
        self.stats.model = self.model_name

    def get_stats(self) -> dict:
        return self.stats.to_dict()

    async def process(self, session_id: str, message: Optional[str] = None, file_content: Optional[bytes] = None, filename: Optional[str] = None) -> dict:
        try:
            result = await self.graph.ainvoke({
                "session_id": session_id, "user_message": message, "file_content": file_content, "filename": filename,
                "input_type": None, "extracted_text": None, "decision": None, "response": None, "error": None, "history": []
            })
            response = result.get("response", "Something went wrong.")
            decision = result.get("decision", "done")
            return {"response": response, "requires_clarification": decision == "done" and "?" in response, "task_performed": decision if decision in ["summarize", "code"] else None, "stats": self.get_stats()}
        except Exception as e:
            logger.error(f"[PROCESS] Fatal: {e}")
            return {"response": f"Error: {e}", "requires_clarification": False, "task_performed": None, "stats": self.get_stats()}
