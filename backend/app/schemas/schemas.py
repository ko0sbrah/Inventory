from pydantic import BaseModel, EmailStr, UUID4, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.core.enums import UserRole, TransactionType


# ============== User Schemas ==============

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.STAFF


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for refreshing token."""
    refresh_token: str


# ============== Category Schemas ==============

class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    parent_id: Optional[UUID4] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: UUID4
    parent_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Inventory Item Schemas ==============

class InventoryItemBase(BaseModel):
    """Base inventory item schema."""
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    category_id: Optional[UUID4] = None
    unit: str = "unit"
    low_stock_threshold: int = Field(default=10, ge=0)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating an inventory item."""
    quantity: int = Field(default=0, ge=0)


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    category_id: Optional[UUID4] = None
    unit: Optional[str] = None
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""
    id: UUID4
    quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InventoryItemListResponse(BaseModel):
    """Schema for paginated inventory item list."""
    items: List[InventoryItemResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== Transaction Schemas ==============

class InventoryTransactionBase(BaseModel):
    """Base transaction schema."""
    transaction_type: TransactionType
    quantity_change: int = Field(..., ge=1)
    reference: Optional[str] = None
    notes: Optional[str] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    """Schema for creating a transaction."""
    item_id: UUID4


class InventoryTransactionResponse(BaseModel):
    """Schema for transaction response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4
    item_id: UUID4
    user_id: Optional[UUID4] = None
    transaction_type: TransactionType
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InventoryTransactionListResponse(BaseModel):
    """Schema for paginated transaction list."""
    transactions: List[InventoryTransactionResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== Audit Log Schemas ==============

class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4
    user_id: Optional[UUID4] = None
    item_id: Optional[UUID4] = None
    action: str
    entity_type: str
    entity_id: UUID4
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list."""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== Dashboard Schemas ==============

class DashboardMetrics(BaseModel):
    """Schema for dashboard metrics."""
    total_items: int
    total_categories: int
    low_stock_items: int
    out_of_stock_items: int
    total_transactions_today: int
    recent_transactions: List[InventoryTransactionResponse]


# ============== Common Schemas ==============

class PaginationParams(BaseModel):
    """Common pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None
