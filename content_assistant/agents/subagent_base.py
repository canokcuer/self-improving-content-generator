"""SubAgent Base Class for TheLifeCo Content Assistant.

Provides common functionality for sub-agents (GONCA, CAN, Review) that are
invoked by EPA as tools rather than interacting directly with users.

Key differences from BaseAgent:
- No user-facing conversation management
- Designed for single request-response pattern
- Invoked as tools by EPA
- Returns structured responses
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Generic, Optional, TypeVar

import anthropic

from content_assistant.config import get_config
from content_assistant.rag.knowledge_base import search_knowledge


class SubAgentError(Exception):
    """Raised when sub-agent operations fail."""
    pass


@dataclass
class SubAgentTool:
    """Definition of a tool available to a sub-agent."""
    name: str
    description: str
    input_schema: dict
    handler: Callable[..., Any]


# Type variables for request/response types
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class SubAgentBase(ABC, Generic[TRequest, TResponse]):
    """Base class for sub-agents that are invoked by EPA as tools.

    Sub-agents:
    - Are invoked as tools by EPA, not directly by users
    - Process a single request and return a structured response
    - Have access to knowledge base and their own tools
    - Don't maintain conversation state between invocations

    Type Parameters:
        TRequest: The request type this sub-agent accepts
        TResponse: The response type this sub-agent returns
    """

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ):
        """Initialize the sub-agent.

        Args:
            agent_name: Unique identifier for this sub-agent
            system_prompt: System prompt defining sub-agent behavior
            model: Claude model to use (defaults to config)
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.model = model or get_config().claude_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self._client: Optional[anthropic.Anthropic] = None
        self._tools: dict[str, SubAgentTool] = {}

        # Stats tracking
        self._total_tokens = 0
        self._total_cost = 0.0
        self._invocation_count = 0

        # Register built-in tools
        self._register_builtin_tools()

        # Register sub-agent specific tools
        self.register_tools()

    def _get_client(self) -> anthropic.Anthropic:
        """Get or create the Anthropic client."""
        if self._client is None:
            config = get_config()
            self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        return self._client

    def _register_builtin_tools(self) -> None:
        """Register tools available to all sub-agents."""
        self.register_tool(SubAgentTool(
            name="search_knowledge",
            description="Search the knowledge base for relevant information about TheLifeCo programs, services, centers, and wellness topics.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant knowledge"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_search_knowledge
        ))

    def _handle_search_knowledge(self, query: str, max_results: int = 5) -> str:
        """Handle knowledge base search."""
        try:
            # Sub-agents have full knowledge access (no source filtering)
            results = search_knowledge(
                query=query,
                top_k=max_results,
                threshold=0.4,
                sources=[],  # No filtering
            )

            if not results:
                return "No relevant information found in the knowledge base."

            formatted = []
            for r in results:
                source = r.get("source", "unknown")
                content = r.get("content", "")
                similarity = r.get("similarity", 0)
                formatted.append(f"[Source: {source}, Relevance: {similarity:.2f}]\n{content}")

            return "\n\n---\n\n".join(formatted)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

    def register_tool(self, tool: SubAgentTool) -> None:
        """Register a tool for this sub-agent."""
        self._tools[tool.name] = tool

    @abstractmethod
    def register_tools(self) -> None:
        """Register sub-agent-specific tools. Override in subclasses."""
        pass

    @abstractmethod
    def process_request(self, request: TRequest) -> TResponse:
        """Process a request and return a structured response.

        Args:
            request: The typed request from EPA

        Returns:
            The typed response for EPA
        """
        pass

    @abstractmethod
    def _build_prompt(self, request: TRequest) -> str:
        """Build the prompt from the request.

        Args:
            request: The typed request

        Returns:
            The prompt string to send to Claude
        """
        pass

    @abstractmethod
    def _parse_response(self, response_text: str, request: TRequest) -> TResponse:
        """Parse Claude's response into the typed response.

        Args:
            response_text: Claude's text response
            request: The original request (for context)

        Returns:
            The typed response
        """
        pass

    def _get_tools_schema(self) -> list[dict]:
        """Get tools schema for Claude API."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in self._tools.values()
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result."""
        if tool_name not in self._tools:
            return f"Error: Unknown tool '{tool_name}'"

        tool = self._tools[tool_name]
        try:
            result = tool.handler(**tool_input)
            return str(result) if result is not None else "Tool executed successfully."
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API with tool support and return final text response.

        Args:
            prompt: The prompt to send

        Returns:
            The final text response from Claude
        """
        client = self._get_client()
        tools = self._get_tools_schema()

        messages = [{"role": "user", "content": prompt}]

        while True:
            # Make API call
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": self.system_prompt,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools

            response = client.messages.create(**kwargs)

            # Track usage
            self._total_tokens += response.usage.input_tokens + response.usage.output_tokens
            self._total_cost += self._calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            # Check if we need to handle tool use
            if response.stop_reason == "tool_use":
                # Process tool calls
                assistant_content = response.content
                tool_results = []

                for block in assistant_content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        # Execute tool
                        result = self._execute_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result
                        })

                # Add assistant message with tool use to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })

                # Add tool results
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue the loop to get final response
                continue

            # No more tool calls, extract text response
            text_content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text_content += block.text

            self._invocation_count += 1
            return text_content

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost in USD."""
        # Pricing per million tokens
        pricing = {
            "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
            "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        }

        model_pricing = pricing.get(self.model, {"input": 3.00, "output": 15.00})
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
        return input_cost + output_cost

    def get_stats(self) -> dict:
        """Get sub-agent usage statistics."""
        return {
            "agent_name": self.agent_name,
            "total_tokens": self._total_tokens,
            "total_cost_usd": self._total_cost,
            "invocation_count": self._invocation_count,
        }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self._total_tokens = 0
        self._total_cost = 0.0
        self._invocation_count = 0
