import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import get_settings


class SummarizeAgent:
    """Generates structured summaries with one-liner, bullet points, and detailed text."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature
        )
    
    async def run(self, content: str) -> str:
        try:
            system = """Return JSON: {"one_line": "...", "bullets": ["...", "...", "..."], "five_sentence": "..."}"""
            response = await self.llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=f"Summarize:\n{content}")
            ])
            r = json.loads(response.content)
            bullets = "\n".join(f"• {b}" for b in r["bullets"])
            return f"## Summary\n\n**TL;DR:** {r['one_line']}\n\n**Key Points:**\n{bullets}\n\n**Details:**\n{r['five_sentence']}"
        except Exception as e:
            return f"Error: {e}"


class CodeAgent:
    """Analyzes code for explanation, bugs, and complexity."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature
        )
    
    async def run(self, code: str) -> str:
        try:
            system = """Return JSON: {"explanation": "...", "bugs": [...], "time_complexity": "O(...)", "space_complexity": "O(...)"}"""
            response = await self.llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=f"Analyze:\n```\n{code}\n```")
            ])
            r = json.loads(response.content)
            bugs = "\n".join(f"⚠️ {b}" for b in r.get("bugs", [])) or "✅ No issues found"
            return f"## Code Analysis\n\n{r['explanation']}\n\n**Complexity:**\n- Time: {r['time_complexity']}\n- Space: {r.get('space_complexity', 'N/A')}\n\n**Issues:**\n{bugs}"
        except Exception as e:
            return f"Error: {e}"
