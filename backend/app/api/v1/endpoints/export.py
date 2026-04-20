from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import csv
import io

from app.db.session import get_db
from app.schemas.schemas import InventoryItemListResponse
from app.services.services import InventoryItemService
from app.api.deps import get_current_user
from app.models.models import User

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/items/csv")
async def export_items_csv(
    search: Optional[str] = Query(None, description="Search by item name"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export inventory items to CSV format."""
    # Get all items (no pagination for export)
    items, total = await InventoryItemService.get_all(
        db=db,
        search=search,
        category_id=category_id,
        low_stock_only=low_stock_only,
        skip=0,
        limit=10000  # Large limit for export
    )
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Name", "SKU", "Category", "Quantity", "Unit",
        "Low Stock Threshold", "Price", "Description", "Created At"
    ])
    
    # Write data
    for item in items:
        writer.writerow([
            str(item.id),
            item.name,
            item.sku or "",
            item.category.name if item.category else "",
            item.quantity,
            item.unit,
            item.low_stock_threshold,
            float(item.price) if item.price else "",
            item.description or "",
            item.created_at.isoformat()
        ])
    
    # Create response
    response = Response(
        content=output.getvalue(),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=inventory_export.csv"
    return response
