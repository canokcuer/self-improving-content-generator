"""Conversation persistence for TheLifeCo Content Assistant.

Handles storing and retrieving conversations for the "forever conversation" feature,
allowing users to continue content generation across sessions.

SECURITY NOTE:
- Backend agents use get_admin_client() for service-level operations
- Frontend operations should use the API client (services/api_client.py)
- User ownership is validated via RLS policies when using authenticated client
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4
import logging

from content_assistant.db.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


class ConversationError(Exception):
    """Raised when conversation operations fail."""
    pass


class AuthorizationError(ConversationError):
    """Raised when user doesn't have access to a resource."""
    pass


def _validate_user_owns_conversation(
    conversation_id: str,
    user_id: str,
    client=None
) -> bool:
    """
    Validate that a user owns a specific conversation.

    Args:
        conversation_id: ID of the conversation
        user_id: ID of the user to validate
        client: Optional Supabase client (uses admin client if not provided)

    Returns:
        True if user owns the conversation

    Raises:
        AuthorizationError: If user doesn't own the conversation
    """
    if client is None:
        client = get_admin_client()

    result = client.table("conversations")\
        .select("user_id")\
        .eq("id", conversation_id)\
        .execute()

    if not result.data:
        raise ConversationError(f"Conversation not found: {conversation_id}")

    owner_id = result.data[0].get("user_id")
    if owner_id != user_id:
        logger.warning(
            f"Authorization failed: user {user_id} attempted to access "
            f"conversation {conversation_id} owned by {owner_id}"
        )
        raise AuthorizationError("You don't have access to this conversation")

    return True


@dataclass
class ConversationMessage:
    """A message in a conversation."""
    role: str  # 'user', 'orchestrator', 'wellness', 'storytelling', 'review', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "agent_name": self.agent_name,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMessage":
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=timestamp or datetime.now(),
            agent_name=data.get("agent_name"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Conversation:
    """A conversation session."""
    id: str
    user_id: str
    title: Optional[str] = None
    status: str = "active"  # active, completed, archived
    messages: list = field(default_factory=list)
    current_agent: Optional[str] = None
    agent_state: dict = field(default_factory=dict)
    brief_data: Optional[dict] = None
    funnel_stage: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    generation_ids: list = field(default_factory=list)
    campaign_info: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "status": self.status,
            "messages": [m.to_dict() if isinstance(m, ConversationMessage) else m for m in self.messages],
            "current_agent": self.current_agent,
            "agent_state": self.agent_state,
            "brief_data": self.brief_data,
            "funnel_stage": self.funnel_stage,
            "platform": self.platform,
            "content_type": self.content_type,
            "generation_ids": self.generation_ids,
            "campaign_info": self.campaign_info,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        raw_messages = data.get("messages") or []
        if isinstance(raw_messages, dict):
            raw_messages = [raw_messages]
        elif not isinstance(raw_messages, list):
            raw_messages = []

        messages = []
        for m in raw_messages:
            if isinstance(m, dict):
                messages.append(ConversationMessage.from_dict(m))
            else:
                messages.append(m)

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        return cls(
            id=data.get("id", str(uuid4())),
            user_id=data.get("user_id", ""),
            title=data.get("title"),
            status=data.get("status", "active"),
            messages=messages,
            current_agent=data.get("current_agent"),
            agent_state=data.get("agent_state", {}),
            brief_data=data.get("brief_data"),
            funnel_stage=data.get("funnel_stage"),
            platform=data.get("platform"),
            content_type=data.get("content_type"),
            generation_ids=data.get("generation_ids", []),
            campaign_info=data.get("campaign_info", {}),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
        )

    def add_message(self, role: str, content: str, agent_name: Optional[str] = None, **kwargs) -> None:
        """Add a message to the conversation."""
        self.messages.append(ConversationMessage(
            role=role,
            content=content,
            agent_name=agent_name,
            metadata=kwargs
        ))
        self.updated_at = datetime.now()

    def get_message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)

    def generate_title(self) -> str:
        """Generate a title from the first user message."""
        for msg in self.messages:
            if isinstance(msg, ConversationMessage) and msg.role == "user":
                content = msg.content[:50]
                if len(msg.content) > 50:
                    content += "..."
                return content
            elif isinstance(msg, dict) and msg.get("role") == "user":
                content = msg.get("content", "")[:50]
                if len(msg.get("content", "")) > 50:
                    content += "..."
                return content
        return "New Conversation"


def create_conversation(user_id: str, title: Optional[str] = None) -> Conversation:
    """Create a new conversation.

    Args:
        user_id: User's ID
        title: Optional title (auto-generated if not provided)

    Returns:
        Created Conversation object

    Raises:
        ConversationError: If creation fails
    """
    conversation = Conversation(
        id=str(uuid4()),
        user_id=user_id,
        title=title,
        status="active"
    )

    try:
        client = get_admin_client()
        result = client.table("conversations").insert({
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "status": conversation.status,
            "messages": [],
            "current_agent": None,
            "agent_state": {},
            "brief_data": None,
            "funnel_stage": None,
            "platform": None,
            "content_type": None,
            "generation_ids": [],
            "campaign_info": {},
        }).execute()

        if result.data:
            return Conversation.from_dict(result.data[0])
        return conversation

    except Exception as e:
        raise ConversationError(f"Failed to create conversation: {e}") from e


def get_conversation(
    conversation_id: str,
    require_user_id: Optional[str] = None
) -> Optional[Conversation]:
    """Get a conversation by ID.

    Args:
        conversation_id: Conversation ID
        require_user_id: If provided, validates that this user owns the conversation.
                        Use this for user-initiated requests to prevent unauthorized access.

    Returns:
        Conversation object or None if not found

    Raises:
        AuthorizationError: If require_user_id is set and user doesn't own conversation
    """
    try:
        client = get_admin_client()

        # If user validation required, check ownership first
        if require_user_id:
            _validate_user_owns_conversation(conversation_id, require_user_id, client)

        result = client.table("conversations")\
            .select("*")\
            .eq("id", conversation_id)\
            .execute()

        if result.data:
            return Conversation.from_dict(result.data[0])
        return None

    except AuthorizationError:
        raise
    except Exception as e:
        raise ConversationError(f"Failed to get conversation: {e}") from e


def update_conversation(conversation: Conversation) -> Conversation:
    """Update a conversation.

    Args:
        conversation: Conversation object with updates

    Returns:
        Updated Conversation object
    """
    try:
        client = get_admin_client()
        conversation.updated_at = datetime.now()

        data = conversation.to_dict()
        # Convert messages to JSON-serializable format
        data["messages"] = [
            m.to_dict() if isinstance(m, ConversationMessage) else m
            for m in (conversation.messages or [])
        ]

        result = client.table("conversations")\
            .update(data)\
            .eq("id", conversation.id)\
            .execute()

        if result.data:
            return Conversation.from_dict(result.data[0])
        return conversation

    except Exception as e:
        raise ConversationError(f"Failed to update conversation: {e}") from e


def add_message_to_conversation(
    conversation_id: str,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    **metadata
) -> Conversation:
    """Add a message to a conversation.

    Args:
        conversation_id: Conversation ID
        role: Message role
        content: Message content
        agent_name: Optional agent name
        **metadata: Additional metadata

    Returns:
        Updated Conversation object
    """
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise ConversationError(f"Conversation not found: {conversation_id}")

    conversation.add_message(role, content, agent_name, **metadata)
    return update_conversation(conversation)


def get_user_conversations(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> list[Conversation]:
    """Get conversations for a user.

    Args:
        user_id: User's ID
        status: Filter by status (optional)
        limit: Max conversations to return
        offset: Pagination offset

    Returns:
        List of Conversation objects
    """
    try:
        client = get_admin_client()
        query = client.table("conversations")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("updated_at", desc=True)\
            .range(offset, offset + limit - 1)

        if status:
            query = query.eq("status", status)

        result = query.execute()

        return [Conversation.from_dict(row) for row in result.data]

    except Exception as e:
        raise ConversationError(f"Failed to get user conversations: {e}") from e


def search_conversations(
    user_id: str,
    query: str,
    limit: int = 10
) -> list[Conversation]:
    """Search conversations by content.

    Args:
        user_id: User's ID
        query: Search query
        limit: Max results

    Returns:
        List of matching Conversation objects
    """
    try:
        # Get all user conversations and filter by message content
        # In production, this would use full-text search
        conversations = get_user_conversations(user_id, limit=100)

        matching = []
        query_lower = query.lower()

        for conv in conversations:
            # Search in title
            if conv.title and query_lower in conv.title.lower():
                matching.append(conv)
                continue

            # Search in messages
            for msg in conv.messages:
                content = msg.content if isinstance(msg, ConversationMessage) else msg.get("content", "")
                if query_lower in content.lower():
                    matching.append(conv)
                    break

            if len(matching) >= limit:
                break

        return matching[:limit]

    except Exception as e:
        raise ConversationError(f"Failed to search conversations: {e}") from e


def update_conversation_state(
    conversation_id: str,
    current_agent: Optional[str] = None,
    agent_state: Optional[dict] = None,
    brief_data: Optional[dict] = None,
    funnel_stage: Optional[str] = None,
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    campaign_info: Optional[dict] = None
) -> Conversation:
    """Update conversation state fields.

    Args:
        conversation_id: Conversation ID
        current_agent: Current agent name
        agent_state: Agent state dict
        brief_data: Brief data dict
        funnel_stage: Funnel stage
        platform: Target platform
        content_type: Content type
        campaign_info: Campaign information

    Returns:
        Updated Conversation object
    """
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise ConversationError(f"Conversation not found: {conversation_id}")

    if current_agent is not None:
        conversation.current_agent = current_agent
    if agent_state is not None:
        conversation.agent_state = agent_state
    if brief_data is not None:
        conversation.brief_data = brief_data
    if funnel_stage is not None:
        conversation.funnel_stage = funnel_stage
    if platform is not None:
        conversation.platform = platform
    if content_type is not None:
        conversation.content_type = content_type
    if campaign_info is not None:
        conversation.campaign_info = campaign_info

    return update_conversation(conversation)


def add_generation_to_conversation(conversation_id: str, generation_id: str) -> Conversation:
    """Link a content generation to a conversation.

    Args:
        conversation_id: Conversation ID
        generation_id: Generation ID

    Returns:
        Updated Conversation object
    """
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise ConversationError(f"Conversation not found: {conversation_id}")

    if generation_id not in conversation.generation_ids:
        conversation.generation_ids.append(generation_id)

    return update_conversation(conversation)


def complete_conversation(conversation_id: str) -> Conversation:
    """Mark a conversation as completed.

    Args:
        conversation_id: Conversation ID

    Returns:
        Updated Conversation object
    """
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise ConversationError(f"Conversation not found: {conversation_id}")

    conversation.status = "completed"

    # Auto-generate title if not set
    if not conversation.title:
        conversation.title = conversation.generate_title()

    return update_conversation(conversation)


def archive_conversation(conversation_id: str) -> Conversation:
    """Archive a conversation.

    Args:
        conversation_id: Conversation ID

    Returns:
        Updated Conversation object
    """
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise ConversationError(f"Conversation not found: {conversation_id}")

    conversation.status = "archived"
    return update_conversation(conversation)


def delete_conversation(
    conversation_id: str,
    require_user_id: Optional[str] = None
) -> bool:
    """Delete a conversation.

    Args:
        conversation_id: Conversation ID
        require_user_id: If provided, validates that this user owns the conversation.
                        Use this for user-initiated requests to prevent unauthorized access.

    Returns:
        True if deleted successfully

    Raises:
        AuthorizationError: If require_user_id is set and user doesn't own conversation
    """
    try:
        client = get_admin_client()

        # If user validation required, check ownership first
        if require_user_id:
            _validate_user_owns_conversation(conversation_id, require_user_id, client)

        result = client.table("conversations")\
            .delete()\
            .eq("id", conversation_id)\
            .execute()

        if not result.data:
            logger.warning(f"Delete had no effect for conversation {conversation_id}")

        return True

    except AuthorizationError:
        raise
    except Exception as e:
        raise ConversationError(f"Failed to delete conversation: {e}") from e
