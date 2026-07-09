from sqlalchemy.orm import Session
from models.product import Product
from typing import Optional, List


class ProductService:
    """Service for handling product business logic"""

    @staticmethod
    def get_all_products(db: Session) -> List[Product]:
        """Get all products from database"""
        return db.query(Product).all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_products_by_category(db: Session, category: str) -> List[Product]:
        """Get products by category"""
        return db.query(Product).filter(Product.category == category).all()

    @staticmethod
    def create_product(db: Session, name: str, price: float, category: str, description: str = "", stock: int = 100) -> Product:
        """Create a new product"""
        new_product = Product(
            name=name,
            price=price,
            category=category,
            description=description,
            stock=stock
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product

    @staticmethod
    def update_product(db: Session, product_id: int, **kwargs) -> Optional[Product]:
        """Update product details"""
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return None

        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Delete a product"""
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return False

        db.delete(product)
        db.commit()
        return True
