from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProductSubscriptionData:
    """Data container for product subscription information."""
    start_date: datetime
    expire_date: datetime
    traffic_limit: int = 0
    is_trial: bool = False
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    delivery_id: Optional[str] = None
    
    def days_remaining(self) -> int:
        """Calculate remaining days in subscription."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if now > self.expire_date:
            return 0
        return (self.expire_date - now).days
    
    def is_active(self) -> bool:
        """Check if subscription is still active."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        return now < self.expire_date


@dataclass  
class ProductPlan:
    """Enhanced plan model for product sales."""
    id: str
    title: str
    duration_days: int
    traffic_gb: int = 0
    price: float = 0
    currency: str = "RUB"
    description: Optional[str] = None
    category: Optional[str] = None
    
    @classmethod
    def from_catalog_product(cls, product: dict) -> "ProductPlan":
        """Create a plan from catalog product data."""
        return cls(
            id=product.get('id', ''),
            title=product.get('name', ''),
            duration_days=product.get('duration_days', 0),
            traffic_gb=0,  # Not applicable for most digital products
            price=product.get('price', {}).get('amount', 0),
            currency=product.get('price', {}).get('currency', 'RUB'),
            description=product.get('description', ''),
            category=product.get('category', 'digital')
        )
