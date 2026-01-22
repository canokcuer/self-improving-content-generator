"""Claude API client with cost tracking and retry logic.

Provides a wrapper around the Anthropic API with:
- Automatic retry with exponential backoff
- Cost tracking for API calls
- JSON mode support
"""

import json
import time
from typing import Optional

import anthropic

from content_assistant.config import get_config


class ClaudeError(Exception):
    """Raised when Claude API operations fail."""

    pass


# Pricing per million tokens (as of 2024)
CLAUDE_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
}

# Cached client instance
_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    """Get or create the Anthropic client."""
    global _client
    if _client is None:
        config = get_config()
        _client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    return _client


def clear_client_cache() -> None:
    """Clear the cached client (for testing)."""
    global _client
    _client = None


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate API cost in USD.

    Args:
        model: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    pricing = CLAUDE_PRICING.get(model, {"input": 3.00, "output": 15.00})
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def generate_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> dict:
    """Generate text using Claude.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        model: Model to use (defaults to config)
        max_tokens: Maximum output tokens
        temperature: Sampling temperature (0-1)
        max_retries: Number of retry attempts
        retry_delay: Base delay between retries (exponential backoff)

    Returns:
        dict with keys: content, model, input_tokens, output_tokens, cost_usd

    Raises:
        ClaudeError: If generation fails after retries
    """
    if not prompt or not prompt.strip():
        raise ClaudeError("Prompt cannot be empty")

    config = get_config()
    model = model or config.claude_model

    client = _get_client()
    last_error = None

    for attempt in range(max_retries):
        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)

            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(model, input_tokens, output_tokens)

            return {
                "content": content,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
            }

        except anthropic.RateLimitError as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = retry_delay * (2**attempt)
                time.sleep(delay)
            continue

        except anthropic.APIStatusError as e:
            raise ClaudeError(f"API error: {e}") from e

        except Exception as e:
            raise ClaudeError(f"Unexpected error: {e}") from e

    raise ClaudeError(f"Failed after {max_retries} retries: {last_error}")


def generate_json(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> dict:
    """Generate JSON using Claude.

    Adds instructions for JSON output and parses the response.

    Args:
        prompt: User prompt (should describe expected JSON structure)
        system_prompt: Optional system prompt
        model: Model to use (defaults to config)
        max_tokens: Maximum output tokens
        temperature: Sampling temperature (0-1)
        max_retries: Number of retry attempts
        retry_delay: Base delay between retries

    Returns:
        dict with keys: data (parsed JSON), model, input_tokens, output_tokens, cost_usd

    Raises:
        ClaudeError: If generation or JSON parsing fails
    """
    # Add JSON instruction to system prompt
    json_instruction = "You must respond with valid JSON only. No markdown formatting, no code blocks, just raw JSON."
    if system_prompt:
        full_system = f"{system_prompt}\n\n{json_instruction}"
    else:
        full_system = json_instruction

    result = generate_text(
        prompt=prompt,
        system_prompt=full_system,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )

    # Parse JSON from response
    content = result["content"].strip()

    # Handle markdown code blocks if present (despite instructions)
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last lines (code fence markers)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ClaudeError(f"Failed to parse JSON response: {e}") from e

    return {
        "data": data,
        "model": result["model"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "cost_usd": result["cost_usd"],
    }
