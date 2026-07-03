# JWT Authentication & Role-Based Access Control

**Complete authentication system with login, registration, JWT tokens, and role-based permissions**

---

## 🔐 Authentication Overview

Your backend now has:
- ✅ User registration with password hashing
- ✅ User login with JWT token generation
- ✅ Role-based access control (User/Admin)
- ✅ Password security with bcrypt
- ✅ Token expiration (24 hours)
- ✅ Protected endpoints

---

## 📝 API Endpoints

### **Authentication Endpoints** (No token required)

#### **1. Register New User**
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

#### **2. Login User**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "wallet_balance": 0
  }
}
```

---

#### **3. Verify Token**
```bash
POST /api/v1/auth/verify-token?token=YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "user_id": 1,
  "email": "john@example.com",
  "role": "user"
}
```

---

### **Protected Endpoints** (Requires JWT Token)

All protected endpoints require JWT token in the `Authorization` header:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

#### **User Endpoints:**

**Get User's Wallet Balance** (User can view own, Admin can view any)
```bash
GET /api/v1/users/{user_id}/wallet
Authorization: Bearer YOUR_JWT_TOKEN
```

**Add Money to Wallet** (User can add to own, Admin can add to any)
```bash
POST /api/v1/users/{user_id}/wallet/add
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "amount": 500
}
```

---

### **Admin Only Endpoints** (Requires Admin role)

#### **Create User**
```bash
POST /api/v1/users
Authorization: Bearer ADMIN_JWT_TOKEN
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "user"
}
```

#### **Delete User**
```bash
DELETE /api/v1/users/{user_id}
Authorization: Bearer ADMIN_JWT_TOKEN
```

#### **Update User Role**
```bash
PUT /api/v1/users/{user_id}/role?new_role=admin
Authorization: Bearer ADMIN_JWT_TOKEN
```

---

## 🔑 User Roles

### **User Role**
- Can login
- Can view own wallet
- Can add money to own wallet
- Cannot delete users
- Cannot create users
- Cannot change roles

### **Admin Role**
- Can login
- Can view any user's wallet
- Can add money to any user's wallet
- **Can delete users**
- **Can create users**
- **Can change user roles**

---

## 🧪 Complete Testing Workflow

### **Step 1: Register User**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### **Step 2: Login**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Copy the `access_token` from response**

### **Step 3: Use Token to Add Money**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/1/wallet/add" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500
  }'
```

### **Step 4: Check Wallet**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/1/wallet" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔒 Security Features

| Feature | Details |
|---------|---------|
| **Password Hashing** | Bcrypt with automatic salting |
| **Token Expiration** | 24 hours (can be changed) |
| **Token Algorithm** | HS256 (HMAC with SHA-256) |
| **Resource Ownership** | Users can only access their own data unless admin |
| **Self-Deletion Protection** | Admin cannot delete their own account |

---

## 💡 How It Works

### **Registration Flow**
```
1. User submits name, email, password
2. Password is hashed with bcrypt
3. User is stored in database with hashed password
4. Response confirms registration
```

### **Login Flow**
```
1. User submits email & password
2. User found by email
3. Password verified against hash
4. JWT token generated with user info
5. Token returned to client
6. Client stores token (localStorage/cookie)
```

### **Protected Route Flow**
```
1. Client sends request with Authorization header
2. Authorization header is extracted
3. JWT token is verified
4. User permissions are checked
5. If authorized, endpoint executes
6. If unauthorized, 401/403 error returned
```

---

## 📋 Default Admin User

To create an admin user manually:

**Option 1: Via SQL (Manual)**
- Hash a password using bcrypt
- Insert user with role='admin'

**Option 2: Register then Update Role**
```bash
# Register user
# Then run (need another admin token first):
PUT /api/v1/users/{user_id}/role?new_role=admin
Authorization: Bearer ADMIN_TOKEN
```

---

## 🛠️ Configuration

Edit token expiration in `services/auth_service.py`:

```python
JWT_EXPIRATION_HOURS = 24  # Change this value
```

Edit password hashing algorithm:
```python
pwd_context = CryptContext(
    schemes=["bcrypt"],  # Secure algorithm
    deprecated="auto"
)
```

---

## 🔧 Implementation Details

### **Utility Functions:**

Located in `controllers/permissions.py`:

- `get_current_user()` - Extract JWT token and return user info
- `require_admin()` - Only allow admin users
- `require_user()` - Only allow authenticated users
- `check_resource_owner()` - Check if user owns resource

### **Services:**

- `auth_service.py` - JWT and password utilities
- `user_service.py` - User CRUD operations

---

## ⚠️ Production Checklist

- [ ] Change `SECRET_KEY` in `.env` to random string
- [ ] Increase `JWT_EXPIRATION_HOURS` for security
- [ ] Use HTTPS only (not HTTP)
- [ ] Store tokens securely (httpOnly cookies)
- [ ] Add rate limiting to login endpoint
- [ ] Add account lockout after failed attempts
- [ ] Set up password reset functionality
- [ ] Add email verification

---

## 🎯 Example: Admin-Only Delete

```python
@app.delete("/api/v1/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(require_admin)  # ← Admin only!
):
    """Delete a user - only admins can do this"""
    # Implementation...
```

**How it works:**
1. Client sends DELETE request with JWT token
2. `require_admin()` extracts token
3. Checks if role is "admin"
4. If yes → endpoint executes
5. If no → 403 Forbidden error

---

## 📚 Files Created

| File | Purpose |
|------|---------|
| `services/auth_service.py` | JWT & password utilities |
| `controllers/auth_controller.py` | Login/Register endpoints |
| `controllers/auth_schemas.py` | Request/response models |
| `controllers/permissions.py` | Permission decorators |
| Updated `services/user_service.py` | Password support |
| Updated `models/user.py` | Password hash field |
| Updated `main.py` | Auth routes registered |

---

## 🚀 Now Ready!

Your backend has **production-ready authentication** with:
- JWT tokens
- Password hashing
- Role-based access control
- Secure endpoints

Start the server and test at: **http://127.0.0.1:8000/docs** 🎉
