PRICING = {
    "gemini-2.0-flash-exp": {"input": 0.10, "output": 0.40},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "default": {"input": 0.10, "output": 0.40}
}


def get_model_pricing(model: str) -> dict[str, float]:
    for key in PRICING:
        if key in model:
            return PRICING[key]
    return PRICING["default"]
