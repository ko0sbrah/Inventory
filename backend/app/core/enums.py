from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    STAFF = "staff"


class TransactionType(str, Enum):
    """Types of inventory transactions."""
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"


class TokenType(str, Enum):
    """Token types for authentication."""
    ACCESS = "access"
    REFRESH = "refresh"
