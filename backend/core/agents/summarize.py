from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from infrastructure.llm.client import get_llm_client


class SummaryOutput(BaseModel):
    """Structured output for document summarization."""
    one_line: str = Field(description="A single sentence TL;DR summary")
    bullets: list[str] = Field(description="3-5 key bullet points")
    five_sentence: str = Field(description="A detailed 5 sentence summary")


class SummarizeAgent:
    def __init__(self):
        self.llm = get_llm_client()
    
    async def run(self, content: str) -> str:
        try:
            llm_structured = self.llm.with_structured_output(SummaryOutput)
            
            response = await llm_structured.ainvoke([
                SystemMessage(content="You are a summarization expert. Analyze the given content and provide a structured summary."),
                HumanMessage(content=f"Summarize the following content:\n\n{content}")
            ])
            
            bullets = "\n".join(f"• {b}" for b in response.bullets)
            
            return (
                f"## Summary\n\n"
                f"**TL;DR:** {response.one_line}\n\n"
                f"**Key Points:**\n{bullets}\n\n"
                f"**Details:**\n{response.five_sentence}"
            )
        except Exception as e:
            return f"Error analyzing content: {e}"
