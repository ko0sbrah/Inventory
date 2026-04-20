from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.schemas.schemas import (
    DashboardMetrics, InventoryTransactionListResponse,
    AuditLogListResponse
)
from app.services.services import DashboardService, TransactionService, AuditLogService
from app.api.deps import get_current_user
from app.models.models import User
from app.core.enums import TransactionType

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard metrics and overview."""
    metrics = await DashboardService.get_metrics(db)
    return metrics


@router.get("/transactions", response_model=InventoryTransactionListResponse)
async def list_transactions(
    item_id: Optional[str] = Query(None, description="Filter by item ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all inventory transactions with filtering."""
    skip = (page - 1) * page_size
    
    transactions, total = await TransactionService.get_all(
        db=db,
        item_id=item_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=page_size
    )
    
    pages = (total + page_size - 1) // page_size
    
    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    item_id: Optional[str] = Query(None, description="Filter by item ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List audit logs with filtering."""
    skip = (page - 1) * page_size
    
    logs, total = await AuditLogService.get_all(
        db=db,
        user_id=user_id,
        item_id=item_id,
        entity_type=entity_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=page_size
    )
    
    pages = (total + page_size - 1) // page_size
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }
