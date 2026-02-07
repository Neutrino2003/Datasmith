from .pricing import get_model_pricing


class TokenStats:
    def __init__(self, model: str = "default"):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_time = 0.0
        self.model = model
    
    def add(self, input_tokens: int, output_tokens: int, time_taken: float):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_time += time_taken
    
    def estimate_cost(self) -> float:
        pricing = get_model_pricing(self.model)
        input_cost = (self.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def to_dict(self) -> dict:
        total_tokens = self.input_tokens + self.output_tokens
        tokens_per_sec = total_tokens / self.total_time if self.total_time > 0 else 0
        
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": total_tokens,
            "tokens_per_sec": round(tokens_per_sec, 2),
            "total_time_sec": round(self.total_time, 2),
            "estimated_cost_usd": round(self.estimate_cost(), 4)
        }
