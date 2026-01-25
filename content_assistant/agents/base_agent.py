"""Base Agent class for TheLifeCo Content Assistant.

Provides common functionality for all agents including:
- Claude API integration with tool use
- Knowledge base access
- Conversation management
- Cost tracking
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

import anthropic

from content_assistant.config import get_config
from content_assistant.rag.knowledge_base import search_knowledge


class AgentError(Exception):
    """Raised when agent operations fail."""
    pass


@dataclass
class AgentTool:
    """Definition of a tool available to an agent."""
    name: str
    description: str
    input_schema: dict
    handler: Callable[..., Any]


@dataclass
class AgentMessage:
    """A message in the agent conversation."""
    role: str  # 'user', 'assistant', 'system', 'tool_result'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    tool_calls: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)


@dataclass
class AgentResponse:
    """Response from an agent."""
    content: str
    is_complete: bool = False  # True if agent has gathered all needed info
    brief_data: dict = field(default_factory=dict)  # Extracted brief data
    next_agent: Optional[str] = None  # Which agent should handle next
    tool_calls_made: list = field(default_factory=list)
    tokens_used: int = 0
    cost_usd: float = 0.0
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents in the system.

    Provides:
    - Claude API integration with tool use
    - Conversation history management
    - Knowledge base search
    - Cost tracking
    """

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        knowledge_sources: Optional[list[str]] = None,
    ):
        """Initialize the agent.

        Args:
            agent_name: Unique identifier for this agent
            system_prompt: System prompt defining agent behavior
            model: Claude model to use (defaults to config)
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
            knowledge_sources: List of knowledge folders/files this agent can access
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.model = model or get_config().claude_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.knowledge_sources = knowledge_sources or []

        self._client: Optional[anthropic.Anthropic] = None
        self._tools: dict[str, AgentTool] = {}
        self._conversation: list[AgentMessage] = []
        self._total_tokens = 0
        self._total_cost = 0.0

        # Register built-in tools
        self._register_builtin_tools()

        # Register agent-specific tools
        self.register_tools()

    def _get_client(self) -> anthropic.Anthropic:
        """Get or create the Anthropic client."""
        if self._client is None:
            config = get_config()
            self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        return self._client

    def _register_builtin_tools(self) -> None:
        """Register tools available to all agents."""
        self.register_tool(AgentTool(
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
            results = search_knowledge(
                query=query,
                top_k=max_results,
                threshold=0.5
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

    def register_tool(self, tool: AgentTool) -> None:
        """Register a tool for this agent."""
        self._tools[tool.name] = tool

    @abstractmethod
    def register_tools(self) -> None:
        """Register agent-specific tools. Override in subclasses."""
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

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to the conversation history."""
        self._conversation.append(AgentMessage(
            role=role,
            content=content,
            **kwargs
        ))

    def get_conversation_history(self) -> list[dict]:
        """Get conversation history in Claude API format."""
        messages = []
        for msg in self._conversation:
            if msg.role in ("user", "assistant"):
                content = msg.metadata.get("claude_content", msg.content)
                messages.append({
                    "role": msg.role,
                    "content": content
                })
            elif msg.role == "tool_result":
                tool_results = msg.metadata.get("tool_results", msg.tool_results)
                if tool_results:
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
        return messages

    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self._conversation = []
        self._total_tokens = 0
        self._total_cost = 0.0

    async def process_message(self, user_message: str) -> AgentResponse:
        """Process a user message and generate a response.

        This method handles:
        1. Adding user message to history
        2. Calling Claude with tools
        3. Processing tool calls if any
        4. Returning the final response

        Args:
            user_message: The user's input message

        Returns:
            AgentResponse with the agent's response and metadata
        """
        # Add user message to history
        self.add_message("user", user_message)

        # Get response from Claude
        response = await self._call_claude()

        return response

    def process_message_sync(self, user_message: str) -> AgentResponse:
        """Synchronous version of process_message."""
        # Add user message to history
        self.add_message("user", user_message)

        # Get response from Claude
        response = self._call_claude_sync()

        return response

    def _call_claude_sync(self) -> AgentResponse:
        """Call Claude API synchronously with tool support."""
        client = self._get_client()
        messages = self.get_conversation_history()
        tools = self._get_tools_schema()

        tool_calls_made = []

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
                current_tool_calls = []

                for block in assistant_content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        # Execute tool
                        result = self._execute_tool(tool_name, tool_input)
                        current_tool_calls.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "id": tool_id,
                            "result": result
                        })
                        tool_calls_made.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "id": tool_id,
                            "result": result
                        })

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

                tool_calls_metadata = [
                    {
                        "tool": call["tool"],
                        "input": call["input"],
                        "tool_use_id": call["id"]
                    }
                    for call in current_tool_calls
                    if "id" in call
                ]

                self.add_message(
                    "assistant",
                    "",
                    tool_calls=tool_calls_metadata,
                    metadata={"claude_content": assistant_content}
                )
                self.add_message(
                    "tool_result",
                    "",
                    tool_results=tool_results,
                    metadata={"tool_results": tool_results}
                )

                # Continue the loop to get final response
                continue

            # No more tool calls, extract text response
            text_content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text_content += block.text

            # Add assistant response to conversation
            self.add_message("assistant", text_content)

            # Let subclass extract any structured data
            brief_data, is_complete, next_agent = self._extract_response_data(text_content)

            return AgentResponse(
                content=text_content,
                is_complete=is_complete,
                brief_data=brief_data,
                next_agent=next_agent,
                tool_calls_made=tool_calls_made,
                tokens_used=self._total_tokens,
                cost_usd=self._total_cost
            )

    async def _call_claude(self) -> AgentResponse:
        """Call Claude API with tool support."""
        # For now, use sync version
        # Can be updated to use async client later
        return self._call_claude_sync()

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

    def _extract_response_data(self, response: str) -> tuple[dict, bool, Optional[str]]:
        """Extract structured data from response.

        Override in subclasses to extract brief data, determine completion, etc.

        Returns:
            tuple of (brief_data dict, is_complete bool, next_agent str or None)
        """
        return {}, False, None

    def get_stats(self) -> dict:
        """Get agent usage statistics."""
        return {
            "agent_name": self.agent_name,
            "total_tokens": self._total_tokens,
            "total_cost_usd": self._total_cost,
            "message_count": len(self._conversation)
        }
