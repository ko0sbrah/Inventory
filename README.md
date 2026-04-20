# Inventory Management System

A scalable, production-grade inventory management system built with FastAPI and React.

## Features

- **Authentication**: JWT-based auth with role-based access (admin/staff)
- **Inventory Management**: Full CRUD for items with categories
- **Transaction System**: Record stock movements (IN/OUT/ADJUSTMENT) with atomic updates
- **Audit Trail**: Immutable history of all changes
- **Dashboard**: Real-time metrics and alerts
- **Search & Filtering**: Advanced filtering and pagination
- **Export**: CSV export functionality
- **Rate Limiting**: API protection against abuse

## Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL with SQLAlchemy (async)
- Alembic for migrations
- Celery for background tasks
- Redis for caching and rate limiting

**Frontend:**
- React 18 with Vite
- TypeScript
- Tailwind CSS
- React Query for state management
- React Router for navigation

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker Desktop installed
- At least 4GB RAM available

### Steps

1. **Clone and navigate to the project:**
```bash
cd /workspace
```

2. **Configure environment variables:**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env if needed (defaults work for local dev)
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Run database migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the application:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/api/docs
- Backend Health: http://localhost:8000/health

## Local Development Setup

### Backend

1. **Install dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up PostgreSQL:**
```bash
# Install PostgreSQL (Mac):
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb inventory_db
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run migrations:**
```bash
alembic upgrade head
```

5. **Start the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (form-data: username, password)
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh token

### Inventory Items
- `GET /api/v1/items` - List items (with filters)
- `POST /api/v1/items` - Create item
- `GET /api/v1/items/{id}` - Get item details
- `PUT /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item
- `POST /api/v1/items/{id}/transactions` - Record transaction

### Transactions
- `GET /api/v1/transactions` - List all transactions

### Dashboard
- `GET /api/v1/dashboard/metrics` - Get dashboard metrics

### Export
- `GET /api/v1/export/items/csv` - Export items to CSV

## Example API Requests

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123", "full_name": "Admin User"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

### Create an Item
```bash
curl -X POST http://localhost:8000/api/v1/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Widget A",
    "sku": "WGT-001",
    "quantity": 100,
    "unit": "pieces",
    "low_stock_threshold": 10,
    "price": 9.99
  }'
```

### Record Stock In
```bash
curl -X POST http://localhost:8000/api/v1/items/ITEM_ID/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "transaction_type": "IN",
    "quantity_change": 50,
    "reference": "Purchase Order #123"
  }'
```

## Architecture

```
backend/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core config, security, celery
│   ├── db/           # Database connection and session
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── alembic/          # Database migrations
└── requirements.txt

frontend/
├── src/
│   ├── api/          # API client and types
│   ├── components/   # Reusable UI components
│   ├── contexts/     # React contexts
│   ├── hooks/        # Custom React hooks
│   ├── pages/        # Page components
│   └── utils/        # Utility functions
└── package.json
```

## Security Features

- Password hashing with bcrypt
- JWT tokens with refresh mechanism
- Role-based access control
- Rate limiting on all endpoints
- CORS configuration
- Input validation with Pydantic

## Data Integrity

- All stock updates are transactional
- No direct quantity edits without logging
- Database locking prevents race conditions
- Audit trail is immutable

## Production Deployment

1. **Build for production:**
```bash
docker-compose -f docker-compose.yml build
```

2. **Set production environment variables:**
- `SECRET_KEY`: Strong random key
- `DATABASE_URL`: Production database
- `REDIS_URL`: Production Redis
- Set `DEBUG=False`

3. **Deploy:**
```bash
docker-compose up -d
```

## Troubleshooting

### Port already in use
Change ports in docker-compose.yml or stop conflicting services.

### Database connection error
Ensure PostgreSQL container is healthy:
```bash
docker-compose ps
docker-compose logs db
```

### Frontend can't connect to backend
Check VITE_API_URL in frontend/.env matches your backend URL.

## License

MIT License
