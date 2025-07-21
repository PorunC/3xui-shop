"""
新的产品数据库模型
替代原有的VPN服务器和客户端模型
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from sqlalchemy import Float, Integer, String, Text, Boolean, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
import json

if TYPE_CHECKING:
    from app.db.models.user import User

from . import Base


class Product(Base):
    """
    产品模型 - 替代原有的VPN订阅概念
    支持各种数字商品：软件许可证、游戏账号、在线服务等
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="产品名称")
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="产品描述")
    category: Mapped[str] = mapped_column(String(100), nullable=False, comment="产品分类")
    
    # JSON格式存储多货币定价: {"USD": {"1": 10, "3": 25}, "RUB": {"1": 800, "3": 2000}}
    price_data: Mapped[str] = mapped_column(Text, nullable=False, comment="价格数据JSON")
    
    stock_quantity: Mapped[int] = mapped_column(
        Integer, default=-1, comment="库存数量，-1表示无限库存"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    
    # 交付类型：digital(数字商品), manual(人工处理), api(API调用)
    delivery_type: Mapped[str] = mapped_column(
        String(50), default='digital', comment="交付类型"
    )
    
    # 交付配置JSON: {"template": "您的密钥: {key}", "key_format": "XXXX-XXXX"}
    delivery_config: Mapped[str] = mapped_column(
        Text, nullable=True, comment="交付配置JSON"
    )
    
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

    # 关系
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', category='{self.category}')>"

    @property
    def prices(self) -> Dict[str, Dict[str, float]]:
        """解析价格数据"""
        try:
            return json.loads(self.price_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    @property
    def delivery_settings(self) -> Dict[str, Any]:
        """解析交付配置"""
        try:
            return json.loads(self.delivery_config) if self.delivery_config else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_price(self, currency: str, duration: str) -> Optional[float]:
        """获取指定货币和时长的价格"""
        prices = self.prices
        return prices.get(currency, {}).get(str(duration))

    def update_stock(self, quantity_change: int) -> bool:
        """更新库存"""
        if self.stock_quantity == -1:  # 无限库存
            return True
        
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            return False
            
        self.stock_quantity = new_quantity
        return True

    @classmethod
    async def get_active_products(
        cls, 
        session: AsyncSession, 
        category: Optional[str] = None
    ) -> List["Product"]:
        """获取活跃产品列表"""
        from sqlalchemy import select
        
        query = select(cls).where(cls.is_active == True)
        if category:
            query = query.where(cls.category == category)
            
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_by_id(cls, session: AsyncSession, product_id: int) -> Optional["Product"]:
        """通过ID获取产品"""
        from sqlalchemy import select
        
        result = await session.execute(select(cls).where(cls.id == product_id))
        return result.scalar_one_or_none()


class Order(Base):
    """
    订单模型 - 替代原有的Transaction概念
    记录用户购买的产品信息
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 用户信息
    user_id: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        comment="用户Telegram ID"
    )
    
    # 产品信息
    product_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="产品ID"
    )
    
    quantity: Mapped[int] = mapped_column(Integer, default=1, comment="购买数量")
    duration: Mapped[str] = mapped_column(String(10), nullable=False, comment="购买时长")
    
    # 价格信息
    total_price: Mapped[float] = mapped_column(Float, nullable=False, comment="总价格")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, comment="货币")
    
    # 订单状态：pending, paid, delivered, failed, refunded, cancelled
    status: Mapped[str] = mapped_column(String(20), default='pending', comment="订单状态")
    
    # 支付信息
    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="支付方式"
    )
    payment_id: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="支付ID"
    )
    
    # 交付数据JSON: {"license_key": "XXXX-XXXX", "download_url": "https://..."}
    delivery_data: Mapped[str] = mapped_column(
        Text, nullable=True, comment="交付数据JSON"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )
    paid_at: Mapped[datetime] = mapped_column(nullable=True, comment="支付时间")
    delivered_at: Mapped[datetime] = mapped_column(nullable=True, comment="交付时间")

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="orders")
    product: Mapped["Product"] = relationship("Product", back_populates="orders")

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, user_id={self.user_id}, "
            f"product_id={self.product_id}, status='{self.status}')>"
        )

    @property
    def delivery_info(self) -> Dict[str, Any]:
        """解析交付数据"""
        try:
            return json.loads(self.delivery_data) if self.delivery_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_delivery_data(self, data: Dict[str, Any]) -> None:
        """设置交付数据"""
        self.delivery_data = json.dumps(data, ensure_ascii=False)

    def mark_as_paid(self, payment_id: str, payment_method: str) -> None:
        """标记为已支付"""
        self.status = 'paid'
        self.payment_id = payment_id
        self.payment_method = payment_method
        self.paid_at = datetime.now()

    def mark_as_delivered(self, delivery_data: Dict[str, Any]) -> None:
        """标记为已交付"""
        self.status = 'delivered'
        self.set_delivery_data(delivery_data)
        self.delivered_at = datetime.now()

    def mark_as_failed(self, reason: str = None) -> None:
        """标记为失败"""
        self.status = 'failed'
        if reason:
            self.set_delivery_data({"failure_reason": reason})

    @classmethod
    async def get_user_orders(
        cls, 
        session: AsyncSession, 
        user_id: int,
        status: Optional[str] = None
    ) -> List["Order"]:
        """获取用户订单列表"""
        from sqlalchemy import select
        
        query = select(cls).where(cls.user_id == user_id)
        if status:
            query = query.where(cls.status == status)
            
        query = query.order_by(cls.created_at.desc())
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_by_id(cls, session: AsyncSession, order_id: int) -> Optional["Order"]:
        """通过ID获取订单"""
        from sqlalchemy import select
        
        result = await session.execute(select(cls).where(cls.id == order_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_pending_orders(cls, session: AsyncSession) -> List["Order"]:
        """获取待处理订单"""
        from sqlalchemy import select
        
        query = select(cls).where(cls.status == 'pending')
        result = await session.execute(query)
        return list(result.scalars().all())


class ProductCategory(Base):
    """
    产品分类模型（可选）
    用于更好地组织产品
    """
    __tablename__ = "product_categories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称")
    name_en: Mapped[str] = mapped_column(String(100), nullable=True, comment="英文名称")
    name_ru: Mapped[str] = mapped_column(String(100), nullable=True, comment="俄文名称")
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="分类描述")
    icon: Mapped[str] = mapped_column(String(10), nullable=True, comment="图标emoji")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")

    def __repr__(self) -> str:
        return f"<ProductCategory(id='{self.id}', name='{self.name}')>"

    @classmethod
    async def get_active_categories(cls, session: AsyncSession) -> List["ProductCategory"]:
        """获取活跃分类列表"""
        from sqlalchemy import select
        
        query = select(cls).where(cls.is_active == True).order_by(cls.sort_order)
        result = await session.execute(query)
        return list(result.scalars().all())
