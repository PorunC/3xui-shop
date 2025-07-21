"""
产品服务类 - 替代VPNService
处理产品购买、订单管理、商品交付等核心业务逻辑
"""
import json
import logging
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.config import Config
from app.db.models import User
# 这些是新的模型，需要在实际实施时创建
# from app.db.models import Product, Order, ProductCategory

logger = logging.getLogger(__name__)


class ProductService:
    """
    产品服务类 - 替代原VPNService
    负责产品管理、订单处理、商品交付等核心功能
    """
    
    def __init__(self, config: Config, session_factory: async_sessionmaker):
        self.config = config
        self.session_factory = session_factory
        logger.info("Product Service initialized.")

    # ========== 产品管理 ==========
    
    async def get_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取产品列表
        替代原来的获取VPN套餐逻辑
        """
        async with self.session_factory() as session:
            # 这里将从数据库获取产品，或从products.json文件读取
            return await self._load_products_from_config(category)
    
    async def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """获取单个产品信息"""
        async with self.session_factory() as session:
            # 从数据库或配置文件获取产品信息
            products = await self._load_products_from_config()
            for product in products:
                if product.get("id") == product_id:
                    return product
            return None
    
    async def _load_products_from_config(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """从配置文件加载产品信息（临时实现，后续改为数据库）"""
        try:
            # 读取products.json文件（替代plans.json）
            with open(self.config.shop.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            products = data.get("products", [])
            
            if category:
                products = [p for p in products if p.get("category") == category]
                
            return products
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            return []

    # ========== 订单管理 ==========
    
    async def create_order(
        self, 
        user: User, 
        product_id: int, 
        duration: str,
        quantity: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        创建订单 - 替代原来的创建VPN订阅逻辑
        """
        try:
            # 获取产品信息
            product = await self.get_product_by_id(product_id)
            if not product:
                logger.error(f"Product {product_id} not found")
                return None
            
            # 计算价格
            price = self._calculate_price(product, duration, quantity)
            if not price:
                logger.error(f"Price calculation failed for product {product_id}")
                return None
            
            # 检查库存
            if not self._check_stock(product, quantity):
                logger.error(f"Insufficient stock for product {product_id}")
                return None
            
            async with self.session_factory() as session:
                # 创建订单记录（这里使用字典模拟，实际应使用Order模型）
                order_data = {
                    "id": self._generate_order_id(),
                    "user_id": user.tg_id,
                    "product_id": product_id,
                    "product_name": product["name"],
                    "quantity": quantity,
                    "duration": duration,
                    "total_price": price["amount"],
                    "currency": price["currency"],
                    "status": "pending",
                    "created_at": datetime.now(),
                    "payment_method": None,
                    "delivery_data": None
                }
                
                # 实际实现中应该保存到数据库
                logger.info(f"Order created: {order_data}")
                return order_data
                
        except Exception as e:
            logger.error(f"Failed to create order for user {user.tg_id}: {e}")
            return None
    
    async def get_user_orders(
        self, 
        user: User, 
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取用户订单列表"""
        async with self.session_factory() as session:
            # 实际实现中从数据库查询
            # 这里返回模拟数据
            return [
                {
                    "id": "ORD_123456",
                    "product_name": "Premium Software License",
                    "status": "delivered",
                    "total_price": 1000,
                    "currency": "RUB",
                    "created_at": datetime.now()
                }
            ]

    # ========== 支付处理 ==========
    
    async def process_payment(
        self, 
        order_id: str, 
        payment_method: str,
        payment_id: str
    ) -> bool:
        """
        处理支付 - 替代原VPN订阅支付逻辑
        """
        try:
            async with self.session_factory() as session:
                # 1. 获取订单信息
                order = await self._get_order_by_id(order_id)
                if not order or order["status"] != "pending":
                    return False
                
                # 2. 更新订单状态为已支付
                order["status"] = "paid"
                order["payment_method"] = payment_method
                order["payment_id"] = payment_id
                order["paid_at"] = datetime.now()
                
                # 3. 触发商品交付
                delivery_success = await self.deliver_product(order_id)
                
                logger.info(f"Payment processed for order {order_id}: {delivery_success}")
                return delivery_success
                
        except Exception as e:
            logger.error(f"Payment processing failed for order {order_id}: {e}")
            return False
    
    # ========== 商品交付 ==========
    
    async def deliver_product(self, order_id: str) -> bool:
        """
        商品交付 - 替代原VPN密钥生成和客户端创建逻辑
        """
        try:
            # 1. 获取订单和产品信息
            order = await self._get_order_by_id(order_id)
            if not order:
                return False
                
            product = await self.get_product_by_id(order["product_id"])
            if not product:
                return False
            
            # 2. 根据交付类型处理
            delivery_type = product.get("delivery_type", "digital")
            delivery_data = None
            
            if delivery_type == "license_key":
                delivery_data = await self._generate_license_key(product, order)
            elif delivery_type == "account_info":
                delivery_data = await self._generate_account_info(product, order)
            elif delivery_type == "download_link":
                delivery_data = await self._generate_download_link(product, order)
            elif delivery_type == "manual":
                delivery_data = {"message": "商品将在24小时内人工处理并交付"}
            else:
                delivery_data = {"message": "数字商品已交付"}
            
            # 3. 更新订单状态
            order["status"] = "delivered"
            order["delivery_data"] = delivery_data
            order["delivered_at"] = datetime.now()
            
            logger.info(f"Product delivered for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Product delivery failed for order {order_id}: {e}")
            return False
    
    async def _generate_license_key(
        self, 
        product: Dict[str, Any], 
        order: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成许可证密钥"""
        # 生成格式化的许可证密钥
        key = f"{product['id']:04d}-{uuid.uuid4().hex[:8].upper()}-{order['duration']}"
        
        template = product.get("delivery_config", {}).get("template", "您的许可证密钥：{license_key}")
        message = template.format(license_key=key)
        
        return {
            "type": "license_key",
            "license_key": key,
            "message": message,
            "expiry_date": self._calculate_expiry_date(order["duration"])
        }
    
    async def _generate_account_info(
        self, 
        product: Dict[str, Any], 
        order: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成账号信息"""
        # 这里可以集成第三方API或从预设账号池中分配
        username = f"user_{uuid.uuid4().hex[:8]}"
        password = uuid.uuid4().hex[:12]
        
        return {
            "type": "account_info",
            "username": username,
            "password": password,
            "message": f"您的账号信息：\n用户名：{username}\n密码：{password}",
            "expiry_date": self._calculate_expiry_date(order["duration"])
        }
    
    async def _generate_download_link(
        self, 
        product: Dict[str, Any], 
        order: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成下载链接"""
        # 生成临时下载链接
        download_token = uuid.uuid4().hex
        download_url = f"https://download.example.com/{download_token}"
        
        return {
            "type": "download_link",
            "download_url": download_url,
            "message": f"您的下载链接：{download_url}",
            "expires_in": "7天"
        }

    # ========== 优惠码系统 ==========
    
    async def activate_promocode(
        self, 
        user: User, 
        promocode_str: str
    ) -> bool:
        """
        激活优惠码 - 改造原VPN优惠码逻辑
        现在可以赠送产品或提供折扣
        """
        try:
            async with self.session_factory() as session:
                # 1. 验证优惠码
                promocode = await self._get_promocode(promocode_str)
                if not promocode or promocode["is_used"]:
                    return False
                
                # 2. 根据优惠码类型处理
                if promocode["type"] == "free_product":
                    # 直接赠送产品
                    success = await self._gift_product(user, promocode["product_id"])
                elif promocode["type"] == "discount":
                    # 为用户添加折扣券
                    success = await self._add_discount_coupon(user, promocode)
                else:
                    return False
                
                if success:
                    # 标记优惠码为已使用
                    await self._mark_promocode_used(promocode_str, user.tg_id)
                
                return success
                
        except Exception as e:
            logger.error(f"Promocode activation failed for user {user.tg_id}: {e}")
            return False
    
    async def _gift_product(self, user: User, product_id: int) -> bool:
        """赠送产品给用户"""
        # 创建免费订单并直接交付
        order = await self.create_order(user, product_id, "30", 1)  # 默认30天
        if not order:
            return False
        
        # 标记为已支付（免费）
        order["status"] = "paid"
        order["payment_method"] = "promocode"
        order["total_price"] = 0
        
        # 交付产品
        return await self.deliver_product(order["id"])

    # ========== 辅助方法 ==========
    
    def _calculate_price(
        self, 
        product: Dict[str, Any], 
        duration: str, 
        quantity: int
    ) -> Optional[Dict[str, Any]]:
        """计算价格"""
        prices = product.get("prices", {})
        currency = self.config.shop.CURRENCY
        
        if currency not in prices:
            return None
            
        unit_price = prices[currency].get(duration)
        if unit_price is None:
            return None
        
        total = unit_price * quantity
        
        return {
            "amount": total,
            "currency": currency,
            "unit_price": unit_price,
            "quantity": quantity
        }
    
    def _check_stock(self, product: Dict[str, Any], quantity: int) -> bool:
        """检查库存"""
        stock = product.get("stock", -1)
        return stock == -1 or stock >= quantity  # -1表示无限库存
    
    def _generate_order_id(self) -> str:
        """生成订单ID"""
        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6].upper()}"
    
    def _calculate_expiry_date(self, duration: str) -> str:
        """计算过期日期"""
        from datetime import timedelta
        
        days = int(duration)
        expiry = datetime.now() + timedelta(days=days)
        return expiry.strftime("%Y-%m-%d %H:%M:%S")
    
    async def _get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """通过ID获取订单（模拟实现）"""
        # 实际实现中应该从数据库查询
        return None
    
    async def _get_promocode(self, code: str) -> Optional[Dict[str, Any]]:
        """获取优惠码信息（模拟实现）"""
        # 实际实现中应该从数据库查询
        return None
    
    async def _mark_promocode_used(self, code: str, user_id: int) -> None:
        """标记优惠码为已使用"""
        pass
    
    async def _add_discount_coupon(self, user: User, promocode: Dict[str, Any]) -> bool:
        """为用户添加折扣券"""
        # 实际实现中应该在数据库中为用户添加折扣券记录
        return True
