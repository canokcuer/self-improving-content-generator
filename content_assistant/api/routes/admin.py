"""
Admin API Routes

Handles admin-only operations like cost monitoring and user management.
All routes require admin role verification.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime, date
import logging

from content_assistant.api.middleware.auth import require_admin, AuthenticatedUser
from content_assistant.api.middleware.rate_limit import rate_limit_admin
from content_assistant.api.dependencies import get_admin_client

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================

class CostSummary(BaseModel):
    """Cost summary for a service."""
    service: str
    total_cost: float
    total_tokens_input: int
    total_tokens_output: int
    operation_count: int


class CostReport(BaseModel):
    """Full cost report."""
    start_date: date
    end_date: date
    services: List[CostSummary]
    total_cost: float


class UserInfo(BaseModel):
    """User information for admin view."""
    id: str
    email: Optional[str]
    created_at: datetime
    generation_count: int
    is_admin: bool


class AdminStats(BaseModel):
    """Admin dashboard statistics."""
    total_users: int
    total_generations: int
    total_conversations: int
    total_cost_usd: float


# ============================================
# Routes
# ============================================

@router.get(
    "/costs",
    response_model=CostReport,
    dependencies=[Depends(rate_limit_admin)],
)
async def get_cost_report(
    admin: AuthenticatedUser = Depends(require_admin),
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
):
    """
    Get cost report for the specified date range.

    Requires admin role.
    """
    try:
        client = get_admin_client()

        # Use the get_cost_summary RPC function
        result = client.rpc(
            "get_cost_summary",
            {
                "start_date": datetime.combine(start_date, datetime.min.time()).isoformat(),
                "end_date": datetime.combine(end_date, datetime.max.time()).isoformat(),
            },
        ).execute()

        services = []
        total_cost = 0.0

        for row in (result.data or []):
            cost = float(row.get("total_cost", 0) or 0)
            services.append(CostSummary(
                service=row.get("service", "unknown"),
                total_cost=cost,
                total_tokens_input=row.get("total_tokens_input", 0) or 0,
                total_tokens_output=row.get("total_tokens_output", 0) or 0,
                operation_count=row.get("operation_count", 0) or 0,
            ))
            total_cost += cost

        logger.info(f"Admin {admin.user_id} retrieved cost report: ${total_cost:.2f}")

        return CostReport(
            start_date=start_date,
            end_date=end_date,
            services=services,
            total_cost=total_cost,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cost report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cost report",
        )


@router.get(
    "/stats",
    response_model=AdminStats,
    dependencies=[Depends(rate_limit_admin)],
)
async def get_admin_stats(
    admin: AuthenticatedUser = Depends(require_admin),
):
    """
    Get overall system statistics.

    Requires admin role.
    """
    try:
        client = get_admin_client()

        # Get counts from various tables
        generations = client.table("content_generations")\
            .select("id", count="exact")\
            .execute()

        conversations = client.table("conversations")\
            .select("id", count="exact")\
            .execute()

        # Get total costs
        costs = client.table("api_costs")\
            .select("cost_usd")\
            .execute()

        total_cost = sum(float(c.get("cost_usd", 0) or 0) for c in (costs.data or []))

        # Note: User count would require auth.users access which is restricted
        # Using a placeholder for now

        return AdminStats(
            total_users=0,  # Would need admin API access to auth.users
            total_generations=generations.count or 0,
            total_conversations=conversations.count or 0,
            total_cost_usd=total_cost,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )


@router.get(
    "/check-status",
    dependencies=[Depends(rate_limit_admin)],
)
async def check_admin_status(
    user: AuthenticatedUser = Depends(require_admin),
):
    """
    Check if the current user has admin status.

    Returns 200 if admin, 403 if not.
    """
    return {
        "is_admin": True,
        "user_id": user.user_id,
        "email": user.email,
    }


@router.get(
    "/users",
    response_model=List[UserInfo],
    dependencies=[Depends(rate_limit_admin)],
)
async def list_users(
    admin: AuthenticatedUser = Depends(require_admin),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    List users with their generation counts.

    Requires admin role.
    """
    try:
        client = get_admin_client()

        # Get unique user_ids from content_generations with counts
        # Note: Full user listing would require auth.users access
        result = client.table("content_generations")\
            .select("user_id")\
            .not_.is_("user_id", "null")\
            .execute()

        # Count generations per user
        user_counts: Dict[str, int] = {}
        for row in (result.data or []):
            user_id = row.get("user_id")
            if user_id:
                user_counts[user_id] = user_counts.get(user_id, 0) + 1

        # Get admin status for each user
        admin_users = set()
        admin_result = client.table("user_roles")\
            .select("user_id")\
            .eq("role", "admin")\
            .execute()
        for row in (admin_result.data or []):
            admin_users.add(row.get("user_id"))

        # Build user list
        users = []
        for user_id, count in list(user_counts.items())[offset:offset + limit]:
            users.append(UserInfo(
                id=user_id,
                email=None,  # Would need auth.users access
                created_at=datetime.utcnow(),  # Placeholder
                generation_count=count,
                is_admin=user_id in admin_users,
            ))

        return users

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        )
