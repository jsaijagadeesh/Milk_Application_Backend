"""
===============================================
Dairy App Backend - Production Ready API
===============================================
Entry Point: python -m uvicorn main:app --reload
Professional Company-Level Architecture
===============================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application
app = FastAPI(
    title="Dairy App API",
    version="1.0.0",
    description="Professional Dairy Products & User Wallet Management API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow all origins (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from config.database import Base, engine
from controllers import user_controller, product_controller, auth_controller

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed default admin user if none exists
from config.database import SessionLocal
from models.user import User
from services.auth_service import AuthService

db = SessionLocal()
try:
    admin_exists = db.query(User).filter(User.role == "admin").first()
    if not admin_exists:
        admin_email = "admin@example.com"
        admin_password = "adminpassword"
        hashed = AuthService.hash_password(admin_password)
        default_admin = User(
            name="Default Admin",
            email=admin_email,
            password_hash=hashed,
            role="admin",
            wallet_balance=0.0,
            is_active=True
        )
        db.add(default_admin)
        db.commit()
        print(f"[SEED] Created default admin user: {admin_email} / {admin_password}")
except Exception as e:
    print(f"[SEED ERROR] Failed to seed default admin: {e}")
finally:
    db.close()


# Include API routers
app.include_router(auth_controller.router, tags=["Authentication"])
app.include_router(user_controller.router, tags=["users"])
app.include_router(product_controller.router, prefix="/api/v1", tags=["products"])

print("[INFO] Database and full API loaded with JWT Authentication")


# ==================== HEALTH & STATUS ENDPOINTS ====================

@app.get("/", tags=["health"])
def root():
    """Welcome endpoint"""
    return {
        "success": True,
        "api": "Dairy App API",
        "version": "1.0.0",
        "documentation": "/docs",
        "database": "connected"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Dairy App API",
        "version": "1.0.0",
        "database": "connected"
    }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {
        "success": False,
        "error": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
