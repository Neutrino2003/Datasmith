from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from infrastructure.llm.client import get_llm_client


class CodeAnalysisOutput(BaseModel):
    """Structured output for code analysis."""
    explanation: str = Field(description="A clear explanation of what the code does")
    bugs: list[str] = Field(default_factory=list, description="List of potential bugs or issues found")
    time_complexity: str = Field(description="Big O time complexity, e.g., O(n), O(n^2)")
    space_complexity: str = Field(default="N/A", description="Big O space complexity")


class CodeAnalysisAgent:
    def __init__(self):
        self.llm = get_llm_client()
    
    async def run(self, code: str) -> str:
        try:
            llm_structured = self.llm.with_structured_output(CodeAnalysisOutput)
            
            response = await llm_structured.ainvoke([
                SystemMessage(content="You are a code analysis expert. Analyze the given code for functionality, bugs, and complexity."),
                HumanMessage(content=f"Analyze the following code:\n\n```\n{code}\n```")
            ])
            
            bugs = "\n".join(f"⚠️ {b}" for b in response.bugs) if response.bugs else "✅ No issues found"
            
            return (
                f"## Code Analysis\n\n"
                f"{response.explanation}\n\n"
                f"**Complexity:**\n"
                f"- Time: {response.time_complexity}\n"
                f"- Space: {response.space_complexity}\n\n"
                f"**Issues:**\n{bugs}"
            )
        except Exception as e:
            return f"Error analyzing code: {e}"
