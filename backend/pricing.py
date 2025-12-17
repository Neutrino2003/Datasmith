"""
Gemini Model Pricing Configuration
Rates are in USD per 1 million tokens.
Source: https://ai.google.dev/pricing
Last Updated: Jan 2025
"""

PRICING = {
    # Gemini 3.0 Series (Preview/Upcoming)
    "gemini-3.0-flash": {"input": 0.50, "output": 3.00},  # Estimated based on announcements
    "gemini-3.0-pro": {"input": 2.00, "output": 12.00},  # Preview pricing

    # Default fallback
    "default": {"input": 0.10, "output": 0.40}
}
