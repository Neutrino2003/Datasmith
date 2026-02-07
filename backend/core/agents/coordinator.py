import time

from langchain_core.messages import HumanMessage, SystemMessage

from infrastructure.llm.client import get_llm_client
from infrastructure.llm.stats import TokenStats
from infrastructure.config import get_settings
from infrastructure.logging import get_logger
from utils.errors import AgentError
from .summarize import SummarizeAgent
from .code_analysis import CodeAnalysisAgent


logger = get_logger("agent.coordinator")


class CoordinatorAgent:
    """Routes messages to appropriate handlers based on slash commands."""
    
    # Slash commands mapping
    COMMANDS = {
        "/code_analysis": "code",
        "/code": "code",
        "/analyze": "code",
        "/summarize": "summarize",
        "/summary": "summarize",
        "/tldr": "summarize",
    }
    
    def __init__(self):
        self.llm = get_llm_client()
        self.settings = get_settings()
        self.summarize_agent = SummarizeAgent()
        self.code_agent = CodeAnalysisAgent()

    async def process(
        self,
        session_id: str,
        stats: TokenStats,
        message: str | None = None,
        extracted_text: str | None = None
    ) -> dict:
        content = extracted_text or ""
        user_message = message or ""
        max_length = self.settings.content_max_length

        if len(content) > max_length:
            content = content[:max_length]

        if not content and not user_message:
            return {
                "response": "Please provide a message or upload a file.",
                "requires_clarification": False,
                "stats": stats.to_dict()
            }

        # Check for slash commands
        command, remaining_message = self._parse_command(user_message)
        
        if command == "code":
            # Use remaining message or extracted content for code analysis
            code_content = remaining_message.strip() or content
            if not code_content:
                response = "Please provide code to analyze after the `/code_analysis` command."
            else:
                response = await self._explain_code(code_content, stats)
        elif command == "summarize":
            # Use remaining message or extracted content for summarization
            text_content = remaining_message.strip() or content
            if not text_content:
                response = "Please provide text to summarize after the `/summarize` command."
            else:
                response = await self._summarize(text_content, stats)
        else:
            # Normal chat - no special agents
            response = await self._general_chat(user_message, content, stats)

        return {
            "response": response,
            "requires_clarification": False,
            "stats": stats.to_dict()
        }

    def _parse_command(self, message: str) -> tuple[str | None, str]:
        """Parse slash command from message. Returns (command_type, remaining_message)."""
        if not message:
            return None, ""
        
        message = message.strip()
        
        for cmd, cmd_type in self.COMMANDS.items():
            if message.lower().startswith(cmd):
                remaining = message[len(cmd):].strip()
                return cmd_type, remaining
        
        return None, message

    async def _summarize(self, content: str, stats: TokenStats) -> str:
        start_time = time.time()
        response = await self.summarize_agent.run(content)
        stats.add(len(content) // 4, len(response) // 4, time.time() - start_time)
        return response

    async def _explain_code(self, code: str, stats: TokenStats) -> str:
        start_time = time.time()
        response = await self.code_agent.run(code)
        stats.add(len(code) // 4, len(response) // 4, time.time() - start_time)
        return response

    async def _general_chat(self, message: str, context: str, stats: TokenStats) -> str:
        """Normal conversational chat without structured output."""
        start_time = time.time()

        try:
            # Build messages based on whether there's context (from file upload)
            messages = [
                SystemMessage(content="You are a helpful AI assistant. Respond naturally and conversationally.")
            ]
            
            if context:
                messages.append(HumanMessage(content=f"Context from uploaded file:\n{context}\n\nUser question: {message}"))
            else:
                messages.append(HumanMessage(content=message))
            
            response = await self.llm.ainvoke(messages)
            
            # Handle response content (can be string, list, or complex object)
            response_text = response.content
            if isinstance(response_text, list):
                # List of parts - extract text from each
                parts = []
                for part in response_text:
                    if isinstance(part, str):
                        parts.append(part)
                    elif isinstance(part, dict) and 'text' in part:
                        parts.append(part['text'])
                    else:
                        parts.append(str(part))
                response_text = "".join(parts)
            elif isinstance(response_text, dict) and 'text' in response_text:
                response_text = response_text['text']

            stats.add(
                len(message + context) // 4,
                len(response_text) // 4,
                time.time() - start_time
            )

            return response_text
        except Exception as e:
            logger.error("llm_invocation_failed", error=str(e), exc_info=True)
            raise AgentError(f"Failed to process request: {e}") from e
