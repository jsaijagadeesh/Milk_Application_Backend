from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from config.database import get_db
from services.product_service import ProductService
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from controllers.permissions import require_admin

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=dict)
def get_products(db: Session = Depends(get_db)):
    """Get all products"""
    try:
        products = ProductService.get_all_products(db)
        serialized_products = [ProductResponse.model_validate(p).model_dump() for p in products]
        return {"success": True, "products": serialized_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}", response_model=dict)
def get_products_by_category(category: str, db: Session = Depends(get_db)):
    """Get products by category"""
    try:
        products = ProductService.get_products_by_category(db, category)
        serialized_products = [ProductResponse.model_validate(p).model_dump() for p in products]
        return {"success": True, "products": serialized_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=dict)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "product": ProductResponse.model_validate(product).model_dump()}


@router.post("", status_code=201, response_model=dict)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Create a new product (admin only)"""
    try:
        new_product = ProductService.create_product(
            db,
            payload.name,
            payload.price,
            payload.category,
            payload.description,
            payload.stock
        )
        return {"success": True, "product": ProductResponse.model_validate(new_product).model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}", response_model=dict)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Update a product (admin only)"""
    try:
        updated_product = ProductService.update_product(db, product_id, **payload.dict(exclude_unset=True))
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True, "product": ProductResponse.model_validate(updated_product).model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Delete a product (admin only)"""
    try:
        success = ProductService.delete_product(db, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True, "message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
