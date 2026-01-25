"""
Conversation API Routes

Handles CRUD operations for user conversations.
All operations are scoped to the authenticated user via RLS.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from content_assistant.api.middleware.auth import get_current_user, AuthenticatedUser
from content_assistant.api.middleware.rate_limit import rate_limit_default, rate_limit_chat
from content_assistant.api.dependencies import get_authenticated_client, PaginationParams

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================

class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=50000)


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    title: Optional[str] = Field(None, max_length=200)


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern=r"^(active|completed|archived)$")
    current_agent: Optional[str] = Field(None, max_length=100)
    agent_state: Optional[dict] = None
    brief_data: Optional[dict] = None
    funnel_stage: Optional[str] = Field(None, max_length=50)
    platform: Optional[str] = Field(None, max_length=50)
    content_type: Optional[str] = Field(None, max_length=50)
    campaign_info: Optional[dict] = None


class ConversationResponse(BaseModel):
    """Response schema for a conversation."""
    id: str
    user_id: str
    title: Optional[str]
    status: str
    current_agent: Optional[str]
    messages: List[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Routes
# ============================================

@router.get(
    "/",
    response_model=List[ConversationResponse],
    dependencies=[Depends(rate_limit_default)],
)
async def list_conversations(
    user: AuthenticatedUser = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    List all conversations for the authenticated user.

    Results are ordered by updated_at descending (most recent first).
    """
    try:
        client = get_authenticated_client(user)

        result = client.table("conversations")\
            .select("*")\
            .eq("user_id", user.user_id)\
            .order("updated_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        )


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_chat)],
)
async def create_conversation(
    data: ConversationCreate,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Create a new conversation for the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        conversation_data = {
            "user_id": user.user_id,
            "title": data.title or "New Conversation",
            "status": "active",
            "messages": [],
        }

        result = client.table("conversations")\
            .insert(conversation_data)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation",
            )

        logger.info(f"Created conversation {result.data[0]['id']} for user {user.user_id}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    dependencies=[Depends(rate_limit_default)],
)
async def get_conversation(
    conversation_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Get a specific conversation by ID.

    Only returns the conversation if it belongs to the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        result = client.table("conversations")\
            .select("*")\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation",
        )


@router.put(
    "/{conversation_id}",
    response_model=ConversationResponse,
    dependencies=[Depends(rate_limit_default)],
)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Update a conversation's metadata (title, status).

    Only allows updating conversations owned by the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        # Build update data (only include non-None fields)
        update_data = {}
        if data.title is not None:
            update_data["title"] = data.title
        if data.status is not None:
            update_data["status"] = data.status

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        result = client.table("conversations")\
            .update(update_data)\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        logger.info(f"Updated conversation {conversation_id}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation",
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(rate_limit_default)],
)
async def delete_conversation(
    conversation_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Delete a conversation.

    Only allows deleting conversations owned by the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        result = client.table("conversations")\
            .delete()\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        logger.info(f"Deleted conversation {conversation_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )


@router.post(
    "/{conversation_id}/messages",
    response_model=ConversationResponse,
    dependencies=[Depends(rate_limit_chat)],
)
async def add_message(
    conversation_id: str,
    message: MessageCreate,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Add a message to a conversation.

    Only allows adding messages to conversations owned by the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        # First, get the current conversation
        current = client.table("conversations")\
            .select("messages")\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not current.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Add the new message
        messages = current.data[0].get("messages", []) or []
        new_message = {
            "role": message.role,
            "content": message.content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        messages.append(new_message)

        # Update the conversation
        result = client.table("conversations")\
            .update({"messages": messages})\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add message",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message to conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message",
        )
