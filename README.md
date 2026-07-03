# Dairy App Backend - Professional Architecture

A production-level FastAPI backend for managing dairy products and user wallets with proper separation of concerns.

## 📁 Project Structure (Professional Level)

```
Application/
├── config/                          # Configuration & Settings
│   ├── __init__.py
│   ├── settings.py                 # Load .env and app settings
│   └── database.py                 # Database connection & session
│
├── models/                          # Database Models (ORM)
│   ├── __init__.py
│   ├── user.py                     # User model with schema
│   └── product.py                  # Product model with schema
│
├── services/                        # Business Logic Layer
│   ├── __init__.py
│   ├── user_service.py             # User operations logic
│   └── product_service.py          # Product operations logic
│
├── controllers/                     # API Handlers & Schemas
│   ├── __init__.py
│   ├── user_controller.py          # User API endpoints
│   ├── user_schemas.py             # User request/response models
│   ├── product_controller.py       # Product API endpoints
│   └── product_schemas.py          # Product request/response models
│
├── tests/                           # Unit & Integration Tests
│
├── .env                             # Environment variables (Git ignored)
├── .gitignore
├── main.py                          # FastAPI App Entry Point
├── requirements.txt                 # Python Dependencies
└── README.md
```

---

## 🏗️ Architecture Explanation

### **Layer 1: Config (Configuration)**
- Loads environment variables from `.env`
- Sets up database connections
- Manages app settings

### **Layer 2: Models (Database)**
- Define database tables using SQLAlchemy ORM
- Represent real-world entities (User, Product)
- Automatically creates tables in database

### **Layer 3: Services (Business Logic)**
- Core application logic
- Database queries
- Data validation and processing
- Independent of HTTP/API details

### **Layer 4: Controllers (API Layer)**
- Handle HTTP requests/responses
- Request validation using Pydantic schemas
- Call services to process data
- Return responses

### **Layer 5: Main (Application Setup)**
- Create FastAPI app
- Register middleware (CORS)
- Include all routers
- Start the server

---

## 🚀 Installation & Setup

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Configure .env File**
The `.env` file is already created with default values. Update if needed:
```
DATABASE_URL=sqlite:///./dairy_app.db
APP_NAME=Dairy App API
DEBUG=True
HOST=127.0.0.1
PORT=8000
```

### **3. Run the Application**
```bash
uvicorn main:app --reload
```

Or run with Python:
```bash
python main.py
```

### **4. Visit the API Documentation**
Open: http://127.0.0.1:8000/docs

---

## 📋 API Endpoints

### **Health & Info**
- `GET /` - Welcome message
- `GET /health` - Health check

### **Users**
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get specific user
- `POST /users` - Create new user
- `GET /users/{user_id}/wallet` - Get wallet balance
- `POST /users/{user_id}/wallet/add` - Add money to wallet

### **Products**
- `GET /products` - Get all products
- `GET /products/{product_id}` - Get specific product
- `GET /products/category/{category}` - Get products by category
- `POST /products` - Create new product (admin)
- `PUT /products/{product_id}` - Update product (admin)
- `DELETE /products/{product_id}` - Delete product (admin)

---

## 📝 Example: Create User & Add Wallet

### **Step 1: Create User**
```json
POST /users
{
  "name": "Raj Kumar",
  "email": "raj@example.com",
  "role": "user"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 2,
    "name": "Raj Kumar",
    "email": "raj@example.com",
    "role": "user",
    "wallet_balance": 0.0
  }
}
```

### **Step 2: Add Money to Wallet**
```json
POST /users/2/wallet/add
{
  "amount": 1000
}
```

**Response:**
```json
{
  "success": true,
  "user": { ... },
  "walletBalance": 1000.0
}
```

### **Step 3: Check Wallet Balance**
```json
GET /users/2/wallet
```

**Response:**
```json
{
  "success": true,
  "walletBalance": 1000.0
}
```

---

## 🔄 Data Flow

```
HTTP Request
    ↓
Controller (user_controller.py)
    ↓
Schema Validation (user_schemas.py)
    ↓
Service (user_service.py)
    ↓
Model (models/user.py)
    ↓
Database (SQLite/PostgreSQL)
    ↓
Response back to Client
```

---

## 💾 Database

### **SQLite (Default - Development)**
- File: `dairy_app.db`
- No setup required
- Good for development

### **PostgreSQL (Production)**
Update `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/dairy_app
```

---

## ✨ Why This Structure?

✅ **Separation of Concerns** - Each layer has one responsibility  
✅ **Testable** - Easy to test each layer independently  
✅ **Scalable** - Add features without breaking existing code  
✅ **Professional** - Used by real companies (Netflix, Spotify, etc.)  
✅ **Maintainable** - Easy to find and fix bugs  
✅ **Collaborative** - Multiple developers can work simultaneously  

---

## 📚 Next Steps

1. ✅ Test all API endpoints
2. Add authentication (JWT tokens)
3. Add database migrations (Alembic)
4. Write unit tests
5. Add logging
6. Deploy to production (AWS, Heroku, etc.)

---

## 🛠️ Development Tips

### **Modify an Endpoint?**
1. Go to `controllers/user_controller.py` (or `product_controller.py`)
2. Make changes
3. Server auto-reloads with `--reload` flag

### **Add Business Logic?**
1. Go to `services/user_service.py`
2. Add the method
3. Call it from controller

### **Add Database Fields?**
1. Go to `models/user.py`
2. Add a new column
3. Database auto-creates it

---

## 📧 Support
For issues or questions, contact the development team.

Happy coding! 🚀
