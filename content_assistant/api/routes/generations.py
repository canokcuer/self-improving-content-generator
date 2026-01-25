"""
Generation API Routes

Handles CRUD operations for content generations and signals.
All operations are scoped to the authenticated user via RLS.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from content_assistant.api.middleware.auth import get_current_user, AuthenticatedUser
from content_assistant.api.middleware.rate_limit import rate_limit_default, rate_limit_generation
from content_assistant.api.dependencies import get_authenticated_client

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================

class GenerationCreate(BaseModel):
    """Schema for creating a new generation."""
    brief: Dict[str, Any] = Field(..., description="Content brief data")
    content: str = Field(..., min_length=1, max_length=100000)
    platform: Optional[str] = Field(None, max_length=50)
    preview: Optional[Dict[str, Any]] = Field(None, description="Preview data")
    conversation_id: Optional[str] = Field(None, description="Associated conversation")


class GenerationUpdate(BaseModel):
    """Schema for updating generation signals."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=5000)
    was_approved: Optional[bool] = None


class GenerationResponse(BaseModel):
    """Response schema for a generation."""
    id: str
    user_id: Optional[str]
    brief: Dict[str, Any]
    content: str
    platform: Optional[str]
    rating: Optional[int]
    feedback: Optional[str]
    was_approved: Optional[bool]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerationStats(BaseModel):
    """Statistics about user's generations."""
    total_count: int
    avg_rating: Optional[float]
    approved_count: int
    platform_breakdown: Dict[str, int]


# ============================================
# Routes
# ============================================

@router.get(
    "/",
    response_model=List[GenerationResponse],
    dependencies=[Depends(rate_limit_default)],
)
async def list_generations(
    user: AuthenticatedUser = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    platform: Optional[str] = Query(None, max_length=50),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
):
    """
    List all generations for the authenticated user.

    Supports filtering by platform and minimum rating.
    """
    try:
        client = get_authenticated_client(user)

        query = client.table("content_generations")\
            .select("*")\
            .eq("user_id", user.user_id)\
            .order("created_at", desc=True)

        if platform:
            query = query.eq("platform", platform)
        if min_rating:
            query = query.gte("rating", min_rating)

        result = query.range(offset, offset + limit - 1).execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Error listing generations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve generations",
        )


@router.post(
    "/",
    response_model=GenerationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_generation)],
)
async def create_generation(
    data: GenerationCreate,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Create a new generation record.

    The user_id is automatically set from the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        generation_data = {
            "user_id": user.user_id,
            "brief": data.brief,
            "content": data.content,
            "platform": data.platform,
            "preview": data.preview,
            "conversation_id": data.conversation_id,
        }

        result = client.table("content_generations")\
            .insert(generation_data)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create generation",
            )

        logger.info(f"Created generation {result.data[0]['id']} for user {user.user_id}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create generation",
        )


@router.get(
    "/stats",
    response_model=GenerationStats,
    dependencies=[Depends(rate_limit_default)],
)
async def get_generation_stats(
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Get statistics about the user's generations.
    """
    try:
        client = get_authenticated_client(user)

        # Get all generations for stats calculation
        result = client.table("content_generations")\
            .select("rating, was_approved, platform")\
            .eq("user_id", user.user_id)\
            .execute()

        generations = result.data or []

        # Calculate stats
        total_count = len(generations)
        ratings = [g["rating"] for g in generations if g.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        approved_count = sum(1 for g in generations if g.get("was_approved"))

        # Platform breakdown
        platform_breakdown = {}
        for g in generations:
            platform = g.get("platform") or "unknown"
            platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1

        return GenerationStats(
            total_count=total_count,
            avg_rating=avg_rating,
            approved_count=approved_count,
            platform_breakdown=platform_breakdown,
        )

    except Exception as e:
        logger.error(f"Error getting generation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )


@router.get(
    "/{generation_id}",
    response_model=GenerationResponse,
    dependencies=[Depends(rate_limit_default)],
)
async def get_generation(
    generation_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Get a specific generation by ID.

    Only returns the generation if it belongs to the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        result = client.table("content_generations")\
            .select("*")\
            .eq("id", generation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation not found",
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation {generation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve generation",
        )


@router.put(
    "/{generation_id}",
    response_model=GenerationResponse,
    dependencies=[Depends(rate_limit_default)],
)
async def update_generation(
    generation_id: str,
    data: GenerationUpdate,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Update a generation's signals (rating, feedback, approval status).

    Only allows updating generations owned by the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        # Build update data
        update_data = {}
        if data.rating is not None:
            update_data["rating"] = data.rating
        if data.feedback is not None:
            update_data["feedback"] = data.feedback
        if data.was_approved is not None:
            update_data["was_approved"] = data.was_approved

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        result = client.table("content_generations")\
            .update(update_data)\
            .eq("id", generation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation not found",
            )

        logger.info(f"Updated generation {generation_id}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating generation {generation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update generation",
        )


@router.delete(
    "/{generation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(rate_limit_default)],
)
async def delete_generation(
    generation_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Delete a generation.

    Only allows deleting generations owned by the authenticated user.
    """
    try:
        client = get_authenticated_client(user)

        result = client.table("content_generations")\
            .delete()\
            .eq("id", generation_id)\
            .eq("user_id", user.user_id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation not found",
            )

        logger.info(f"Deleted generation {generation_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting generation {generation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete generation",
        )
