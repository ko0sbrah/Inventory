from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import json

from app.models.models import User, InventoryItem, InventoryTransaction, AuditLog, Category
from app.schemas.schemas import (
    UserCreate, UserUpdate,
    InventoryItemCreate, InventoryItemUpdate,
    InventoryTransactionCreate,
    CategoryCreate
)
from app.core.security import get_password_hash
from app.core.enums import UserRole, TransactionType


# ============== User Service ==============

class UserService:
    """Service for user operations."""
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update(db: AsyncSession, user: User, update_data: UserUpdate) -> User:
        """Update user."""
        update_dict = update_data.model_dump(exclude_unset=True)
        if "password" in update_dict:
            update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        """Get all users with pagination."""
        query = select(User)
        count_query = select(func.count(User.id))
        
        total = await db.scalar(count_query)
        result = await db.execute(query.offset(skip).limit(limit))
        users = result.scalars().all()
        
        return users, total


# ============== Category Service ==============

class CategoryService:
    """Service for category operations."""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        result = await db.execute(
            select(Category)
            .options(selectinload(Category.parent))
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, category_data: CategoryCreate) -> Category:
        """Create a new category."""
        category = Category(**category_data.model_dump())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[List[Category], int]:
        """Get all categories with pagination."""
        query = select(Category).order_by(Category.name)
        count_query = select(func.count(Category.id))
        
        total = await db.scalar(count_query)
        result = await db.execute(query.offset(skip).limit(limit))
        categories = result.scalars().all()
        
        return categories, total
    
    @staticmethod
    async def delete(db: AsyncSession, category: Category) -> None:
        """Delete a category."""
        await db.delete(category)
        await db.commit()


# ============== Inventory Item Service ==============

class InventoryItemService:
    """Service for inventory item operations."""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, item_id: str) -> Optional[InventoryItem]:
        """Get item by ID."""
        result = await db.execute(
            select(InventoryItem)
            .options(selectinload(InventoryItem.category))
            .where(InventoryItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        db: AsyncSession, 
        item_data: InventoryItemCreate,
        created_by: Optional[User] = None
    ) -> InventoryItem:
        """Create a new inventory item with initial stock transaction."""
        item = InventoryItem(**item_data.model_dump())
        db.add(item)
        await db.flush()  # Get the item ID
        
        # Create initial stock-in transaction if quantity > 0
        if item_data.quantity > 0:
            transaction = InventoryTransaction(
                item_id=item.id,
                user_id=created_by.id if created_by else None,
                transaction_type=TransactionType.IN,
                quantity_change=item_data.quantity,
                quantity_before=0,
                quantity_after=item_data.quantity,
                reference="Initial stock",
            )
            db.add(transaction)
        
        await db.commit()
        await db.refresh(item)
        return item
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        item: InventoryItem, 
        update_data: InventoryItemUpdate,
        updated_by: Optional[User] = None
    ) -> InventoryItem:
        """Update an inventory item."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Log audit before update
        old_values = {
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "low_stock_threshold": item.low_stock_threshold,
        }
        
        for field, value in update_dict.items():
            setattr(item, field, value)
        
        # Create audit log
        audit_log = AuditLog(
            user_id=updated_by.id if updated_by else None,
            item_id=item.id,
            action="UPDATE",
            entity_type="INVENTORY_ITEM",
            entity_id=item.id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_dict),
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(item)
        return item
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Tuple[List[InventoryItem], int]:
        """Get all inventory items with filtering and pagination."""
        query = select(InventoryItem).options(selectinload(InventoryItem.category))
        count_query = select(func.count(InventoryItem.id))
        
        # Apply filters
        if search:
            query = query.where(InventoryItem.name.ilike(f"%{search}%"))
            count_query = count_query.where(InventoryItem.name.ilike(f"%{search}%"))
        
        if category_id:
            query = query.where(InventoryItem.category_id == category_id)
            count_query = count_query.where(InventoryItem.category_id == category_id)
        
        if low_stock_only:
            query = query.where(
                (InventoryItem.quantity <= InventoryItem.low_stock_threshold) &
                (InventoryItem.is_active == True)
            )
            count_query = count_query.where(
                (InventoryItem.quantity <= InventoryItem.low_stock_threshold) &
                (InventoryItem.is_active == True)
            )
        
        # Apply sorting
        sort_column = getattr(InventoryItem, sort_by, InventoryItem.name)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        total = await db.scalar(count_query)
        result = await db.execute(query.offset(skip).limit(limit))
        items = result.scalars().all()
        
        return items, total
    
    @staticmethod
    async def delete(db: AsyncSession, item: InventoryItem, deleted_by: Optional[User] = None) -> None:
        """Soft delete an inventory item."""
        item.is_active = False
        
        # Create audit log
        audit_log = AuditLog(
            user_id=deleted_by.id if deleted_by else None,
            item_id=item.id,
            action="DELETE",
            entity_type="INVENTORY_ITEM",
            entity_id=item.id,
            old_values=json.dumps({"is_active": True}),
            new_values=json.dumps({"is_active": False}),
        )
        db.add(audit_log)
        
        await db.commit()


# ============== Transaction Service ==============

class TransactionService:
    """Service for inventory transactions - handles atomic stock updates."""
    
    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        transaction_data: InventoryTransactionCreate,
        user: Optional[User] = None
    ) -> InventoryTransaction:
        """
        Create a transaction and update stock atomically.
        Uses database locking to prevent race conditions.
        """
        # Get the item with FOR UPDATE lock
        result = await db.execute(
            select(InventoryItem)
            .where(InventoryItem.id == transaction_data.item_id)
            .with_for_update()
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Item with ID {transaction_data.item_id} not found")
        
        quantity_before = item.quantity
        quantity_change = transaction_data.quantity_change
        
        # Calculate new quantity based on transaction type
        if transaction_data.transaction_type == TransactionType.IN:
            quantity_after = quantity_before + quantity_change
        elif transaction_data.transaction_type == TransactionType.OUT:
            quantity_after = quantity_before - quantity_change
            if quantity_after < 0:
                raise ValueError(
                    f"Insufficient stock. Current: {quantity_before}, "
                    f"Requested: {quantity_change}"
                )
        elif transaction_data.transaction_type == TransactionType.ADJUSTMENT:
            quantity_after = quantity_change  # For adjustment, quantity_change is the new target
            quantity_change = quantity_after - quantity_before
        else:
            raise ValueError(f"Invalid transaction type: {transaction_data.transaction_type}")
        
        # Update item quantity
        item.quantity = quantity_after
        
        # Create transaction record
        transaction = InventoryTransaction(
            item_id=item.id,
            user_id=user.id if user else None,
            transaction_type=transaction_data.transaction_type,
            quantity_change=quantity_change,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference=transaction_data.reference,
            notes=transaction_data.notes,
        )
        db.add(transaction)
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id if user else None,
            item_id=item.id,
            action=f"TRANSACTION_{transaction_data.transaction_type.value}",
            entity_type="INVENTORY_TRANSACTION",
            entity_id=transaction.id,
            old_values=json.dumps({"quantity": quantity_before}),
            new_values=json.dumps({"quantity": quantity_after}),
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        item_id: Optional[str] = None,
        user_id: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[InventoryTransaction], int]:
        """Get all transactions with filtering and pagination."""
        query = select(InventoryTransaction).order_by(InventoryTransaction.created_at.desc())
        count_query = select(func.count(InventoryTransaction.id))
        
        # Apply filters
        if item_id:
            query = query.where(InventoryTransaction.item_id == item_id)
            count_query = count_query.where(InventoryTransaction.item_id == item_id)
        
        if user_id:
            query = query.where(InventoryTransaction.user_id == user_id)
            count_query = count_query.where(InventoryTransaction.user_id == user_id)
        
        if transaction_type:
            query = query.where(InventoryTransaction.transaction_type == transaction_type)
            count_query = count_query.where(InventoryTransaction.transaction_type == transaction_type)
        
        if start_date:
            query = query.where(InventoryTransaction.created_at >= start_date)
            count_query = count_query.where(InventoryTransaction.created_at >= start_date)
        
        if end_date:
            query = query.where(InventoryTransaction.created_at <= end_date)
            count_query = count_query.where(InventoryTransaction.created_at <= end_date)
        
        total = await db.scalar(count_query)
        result = await db.execute(query.offset(skip).limit(limit))
        transactions = result.scalars().all()
        
        return transactions, total
    
    @staticmethod
    async def get_by_item_id(db: AsyncSession, item_id: str) -> List[InventoryTransaction]:
        """Get all transactions for a specific item."""
        result = await db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.item_id == item_id)
            .order_by(InventoryTransaction.created_at.desc())
        )
        return result.scalars().all()


# ============== Audit Log Service ==============

class AuditLogService:
    """Service for audit log operations."""
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        user_id: Optional[str] = None,
        item_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AuditLog], int]:
        """Get all audit logs with filtering and pagination."""
        query = select(AuditLog).order_by(AuditLog.created_at.desc())
        count_query = select(func.count(AuditLog.id))
        
        # Apply filters
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        
        if item_id:
            query = query.where(AuditLog.item_id == item_id)
            count_query = count_query.where(AuditLog.item_id == item_id)
        
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
            count_query = count_query.where(AuditLog.entity_type == entity_type)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
            count_query = count_query.where(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
            count_query = count_query.where(AuditLog.created_at <= end_date)
        
        total = await db.scalar(count_query)
        result = await db.execute(query.offset(skip).limit(limit))
        logs = result.scalars().all()
        
        return logs, total


# ============== Dashboard Service ==============

class DashboardService:
    """Service for dashboard metrics."""
    
    @staticmethod
    async def get_metrics(db: AsyncSession) -> dict:
        """Get dashboard metrics."""
        # Total items
        total_items_query = select(func.count(InventoryItem.id)).where(InventoryItem.is_active == True)
        total_items = await db.scalar(total_items_query) or 0
        
        # Total categories
        total_categories_query = select(func.count(Category.id))
        total_categories = await db.scalar(total_categories_query) or 0
        
        # Low stock items
        low_stock_query = select(func.count(InventoryItem.id)).where(
            (InventoryItem.quantity <= InventoryItem.low_stock_threshold) &
            (InventoryItem.is_active == True) &
            (InventoryItem.quantity > 0)
        )
        low_stock_items = await db.scalar(low_stock_query) or 0
        
        # Out of stock items
        out_of_stock_query = select(func.count(InventoryItem.id)).where(
            (InventoryItem.quantity == 0) &
            (InventoryItem.is_active == True)
        )
        out_of_stock_items = await db.scalar(out_of_stock_query) or 0
        
        # Transactions today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        transactions_today_query = select(func.count(InventoryTransaction.id)).where(
            InventoryTransaction.created_at >= today_start
        )
        transactions_today = await db.scalar(transactions_today_query) or 0
        
        # Recent transactions
        recent_transactions_query = (
            select(InventoryTransaction)
            .order_by(InventoryTransaction.created_at.desc())
            .limit(5)
        )
        result = await db.execute(recent_transactions_query)
        recent_transactions = result.scalars().all()
        
        return {
            "total_items": total_items,
            "total_categories": total_categories,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_transactions_today": transactions_today,
            "recent_transactions": recent_transactions,
        }
