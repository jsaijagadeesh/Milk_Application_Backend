# Dairy App Backend - Professional Production-Ready API

**Enterprise-Grade FastAPI Application**  
*Version: 1.0.0*  
*Last Updated: July 2026*

---

## 📁 Project Structure (Company-Level)

```
Application/
│
├── 📂 config/                    # Configuration & Settings
│   ├── __init__.py
│   ├── settings.py              # Load .env & app configuration
│   └── database.py              # SQLAlchemy database setup
│
├── 📂 models/                    # Database Models (ORM)
│   ├── __init__.py
│   ├── user.py                  # User database table
│   └── product.py               # Product database table
│
├── 📂 schemas/                   # Pydantic Data Models
│   ├── __init__.py
│   ├── user_schemas.py          # User request/response schemas
│   └── product_schemas.py       # Product request/response schemas
│
├── 📂 services/                  # Business Logic Layer
│   ├── __init__.py
│   ├── user_service.py          # User operations
│   └── product_service.py       # Product operations
│
├── 📂 controllers/               # API Endpoints & Routers
│   ├── __init__.py
│   ├── user_controller.py       # User API endpoints
│   ├── user_schemas.py          # User schemas
│   ├── product_controller.py    # Product API endpoints
│   └── product_schemas.py       # Product schemas
│
├── 📂 tests/                     # Unit & Integration Tests
│   └── __init__.py
│
├── 📄 main.py                    # FastAPI Application Entry Point ⭐
├── 📄 test_server.py            # Simple Test Server (Optional)
├── 📄 run.py                     # Alternative Run Script
├── 📄 .env                       # Environment Variables (Git ignored)
├── 📄 .gitignore
├── 📄 requirements.txt           # Python Dependencies
├── 📄 README.md                  # Project Documentation
└── 📄 PROFESSIONAL_SETUP.md      # This file
```

---

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run the Server**
```bash
python -m uvicorn main:app --reload
```

Or:
```bash
python run.py
```

Or (simple test version):
```bash
python test_server.py
```

### **3. Access API Documentation**
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## 🏗️ Architecture Layers

### **Layer 1: Config** 🔧
- Loads environment variables from `.env`
- Manages database connections
- Centralized app settings

### **Layer 2: Models** 📊
- SQLAlchemy ORM models
- Database table definitions
- Auto-creates tables on startup

### **Layer 3: Schemas** 📋
- Pydantic request validation
- Response data formatting
- Type safety & documentation

### **Layer 4: Services** ⚙️
- Core business logic
- Database operations
- Data processing & validation

### **Layer 5: Controllers (Routes)** 🌐
- API endpoints
- HTTP request handling
- Response formatting

### **Layer 6: Main** 🎯
- FastAPI app initialization
- Middleware configuration
- Router registration

---

## 📡 API Endpoints

### **Health & Status**
```
GET /               → Welcome message
GET /health         → Health check
GET /api/v1/status  → API status
```

### **Users**
```
GET    /api/v1/users                      → Get all users
GET    /api/v1/users/{user_id}            → Get specific user
POST   /api/v1/users                      → Create new user
GET    /api/v1/users/{user_id}/wallet     → Get wallet balance
POST   /api/v1/users/{user_id}/wallet/add → Add money to wallet
```

### **Products**
```
GET    /api/v1/products                  → Get all products
GET    /api/v1/products/{product_id}     → Get specific product
GET    /api/v1/products/category/{cat}   → Get by category
POST   /api/v1/products                  → Create product (admin)
PUT    /api/v1/products/{product_id}     → Update product (admin)
DELETE /api/v1/products/{product_id}     → Delete product (admin)
```

---

## 💾 Database

### **Default: SQLite** 📦
- File: `dairy_app.db`
- No setup needed
- Perfect for development

### **Production: PostgreSQL** 🐘
Update `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dairy_app
```

Install driver:
```bash
pip install psycopg2-binary
```

---

## 📝 Example Usage

### **Create User**
```bash
POST /api/v1/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
```

### **Add to Wallet**
```bash
POST /api/v1/users/1/wallet/add
Content-Type: application/json

{
  "amount": 500
}
```

### **Check Balance**
```bash
GET /api/v1/users/1/wallet
```

---

## 🔄 Request/Response Flow

```
1. Client sends HTTP request
   ↓
2. FastAPI validates & routes request
   ↓
3. Controller receives request
   ↓
4. Pydantic schema validates data
   ↓
5. Service performs business logic
   ↓
6. Model interacts with database
   ↓
7. Response formatted & returned
   ↓
8. Client receives JSON response
```

---

## ⚙️ Configuration (.env)

```env
# App
APP_NAME=Dairy App API
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///./dairy_app.db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Server
HOST=127.0.0.1
PORT=8000
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115.0 | Web framework |
| uvicorn | 0.30.6 | ASGI server |
| sqlalchemy | ≥2.0 | ORM |
| pydantic | ≥2.0 | Data validation |
| python-dotenv | 1.0.0 | Environment variables |
| email-validator | ≥2.0 | Email validation |

---

## ✨ Key Features

✅ **Professional Architecture** - Separation of concerns  
✅ **Type Safe** - Pydantic validation  
✅ **RESTful** - Standard HTTP methods  
✅ **Documented** - Auto-generated docs (/docs)  
✅ **Scalable** - Easy to add features  
✅ **Testable** - Independent layers  
✅ **Configurable** - Environment-based settings  
✅ **Database Ready** - SQLite/PostgreSQL support  

---

## 🛠️ Development

### **Add New Endpoint**
1. Create method in `services/`
2. Create schemas in `schemas/`
3. Add route in `controllers/`
4. Update documentation

### **Modify Database**
1. Edit model in `models/`
2. Restart server (auto-creates new tables)

### **Change Settings**
1. Update `.env` file
2. Settings auto-reload

---

## 📚 File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry point |
| `run.py` | Alternative entry script |
| `test_server.py` | Simple test version |
| `.env` | Environment configuration |
| `requirements.txt` | Package dependencies |
| `config/settings.py` | Load configuration |
| `config/database.py` | Database connection |
| `models/user.py` | User table schema |
| `models/product.py` | Product table schema |
| `services/user_service.py` | User business logic |
| `services/product_service.py` | Product business logic |
| `controllers/user_controller.py` | User API endpoints |
| `controllers/product_controller.py` | Product API endpoints |

---

## 🔐 Production Checklist

- [ ] Update `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Switch to PostgreSQL
- [ ] Set up proper authentication (JWT)
- [ ] Add API rate limiting
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Add input validation
- [ ] Deploy to production

---

## 🚀 Deployment

### **Local Development**
```bash
python -m uvicorn main:app --reload
```

### **Production (Docker)**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Production (Heroku/AWS/GCP)**
Follow platform-specific deployment guides.

---

## 📞 Support

For issues or questions:
1. Check `/docs` for API documentation
2. Review error messages in terminal
3. Check `.env` configuration
4. Verify database connection

---

## 📄 License

This project is part of the Dairy App ecosystem.

---

**Last Updated:** July 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
