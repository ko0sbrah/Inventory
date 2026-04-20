from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
from datetime import datetime

from app.db.session import get_db
from app.schemas.schemas import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryItemListResponse, InventoryTransactionCreate,
    InventoryTransactionResponse, InventoryTransactionListResponse,
    MessageResponse
)
from app.services.services import InventoryItemService, TransactionService
from app.api.deps import get_current_user
from app.models.models import User
from app.core.enums import TransactionType

router = APIRouter(prefix="/items", tags=["Inventory Items"])


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: InventoryItemCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new inventory item."""
    # Check if SKU already exists
    if item_data.sku:
        existing = await InventoryItemService.get_by_id(db, item_data.sku)
    
    item = await InventoryItemService.create(db, item_data, current_user)
    return item


@router.get("/", response_model=InventoryItemListResponse)
async def list_items(
    search: Optional[str] = Query(None, description="Search by item name"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", description="Sort by field"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all inventory items with filtering and pagination."""
    skip = (page - 1) * page_size
    
    items, total = await InventoryItemService.get_all(
        db=db,
        search=search,
        category_id=category_id,
        low_stock_only=low_stock_only,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific inventory item by ID."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    item = await InventoryItemService.get_by_id(db, item_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_item(
    item_id: str,
    update_data: InventoryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an inventory item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    item = await InventoryItemService.get_by_id(db, item_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    updated_item = await InventoryItemService.update(db, item, update_data, current_user)
    return updated_item


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete an inventory item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    item = await InventoryItemService.get_by_id(db, item_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    await InventoryItemService.delete(db, item, current_user)
    
    return {"message": "Item deleted successfully"}


@router.post("/{item_id}/transactions", response_model=InventoryTransactionResponse)
async def create_transaction(
    item_id: str,
    transaction_data: InventoryTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a stock transaction for an item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    # Verify item exists
    item = await InventoryItemService.get_by_id(db, item_uuid)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Set the item_id from path
    transaction_data.item_id = item_uuid
    
    try:
        transaction = await TransactionService.create_transaction(
            db, transaction_data, current_user
        )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{item_id}/transactions", response_model=InventoryTransactionListResponse)
async def get_item_transactions(
    item_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all transactions for a specific item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    skip = (page - 1) * page_size
    
    transactions, total = await TransactionService.get_all(
        db=db,
        item_id=str(item_uuid),
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
