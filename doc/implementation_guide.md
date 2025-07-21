# 🛒 VPN商店到通用电子商品商店改造实施指南

## 📋 第一阶段：核心组件识别和改造规划

### 1.1 关键VPN相关文件识别

#### 🔴 必须删除的核心VPN文件：
```
app/bot/services/vpn.py                    # VPN客户端管理核心服务
app/bot/services/server_pool.py           # VPN服务器池管理
app/db/models/server.py                    # VPN服务器数据模型
app/bot/routers/admin_tools/server_handler.py  # 服务器管理界面
```

#### 🟡 需要重构的文件：
```
app/bot/services/subscription.py          # 订阅服务 → 产品服务
app/bot/models/client_data.py             # VPN客户端数据 → 订单数据
app/bot/models/subscription_data.py       # 订阅数据 → 产品数据
app/db/models/user.py                     # 用户模型（移除VPN字段）
app/db/models/transaction.py              # 交易记录（更新字段含义）
```

#### 🟢 需要更新内容的文件：
```
app/config.py                            # 移除XUI配置
pyproject.toml                          # 移除py3xui依赖
plans.json                              # 改为products.json
app/locales/*/LC_MESSAGES/bot.po         # 所有翻译文件
```

### 1.2 数据库迁移计划

#### 现有表结构分析：
```sql
-- 需要保留的表
users (移除vpn_id, server_id字段)
transactions (更新字段含义)
promocodes (保留，改为产品优惠码)
referrals (保留)
referrer_rewards (保留)
invites (保留)

-- 需要删除的表
servers (VPN服务器信息)

-- 需要新增的表
products (产品信息)
orders (订单信息)
product_categories (产品分类)
inventory (库存管理，如需要)
```

## 📝 第二阶段：具体实施步骤

### 步骤1：创建新的数据模型 (预计时间：半天)

#### 1.1 创建Products数据库模型
```python
# app/db/models/product.py
class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    price_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON格式
    stock_quantity: Mapped[int] = mapped_column(Integer, default=-1)  # -1表示无限
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    delivery_type: Mapped[str] = mapped_column(String(50), default='digital')
    delivery_config: Mapped[str] = mapped_column(Text, nullable=True)  # JSON格式
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
```

#### 1.2 创建Orders数据库模型
```python
# app/db/models/order.py
class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='pending')
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)
    delivery_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON格式
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="orders")
    product: Mapped["Product"] = relationship("Product")
```

### 步骤2：移除VPN依赖 (预计时间：1天)

#### 2.1 更新pyproject.toml
```toml
# 移除这一行：
# py3xui = "^0.3.2"

# 可选：添加新的依赖
requests = "^2.31.0"  # 如果需要调用第三方API交付商品
```

#### 2.2 删除VPN核心服务文件
```bash
rm app/bot/services/vpn.py
rm app/bot/services/server_pool.py
rm app/db/models/server.py
rm app/bot/routers/admin_tools/server_handler.py
```

#### 2.3 更新用户模型
```python
# 在app/db/models/user.py中删除这些字段：
# vpn_id: Mapped[str]
# server_id: Mapped[int | None]
# server: Mapped["Server | None"]

# 添加新的关系：
orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
```

### 步骤3：创建产品服务 (预计时间：1天)

#### 3.1 创建ProductService
```python
# app/bot/services/product.py
class ProductService:
    def __init__(self, config: Config, session_factory: async_sessionmaker):
        self.config = config
        self.session_factory = session_factory
    
    async def get_products(self, category: str = None) -> list[Product]:
        """获取产品列表"""
        
    async def create_order(self, user: User, product_id: int, quantity: int) -> Order:
        """创建订单"""
        
    async def process_payment(self, order_id: int, payment_method: str) -> bool:
        """处理支付"""
        
    async def deliver_product(self, order_id: int) -> bool:
        """交付产品"""
        
    async def get_user_orders(self, user: User) -> list[Order]:
        """获取用户订单"""
```

#### 3.2 重构SubscriptionService
```python
# 将app/bot/services/subscription.py重构为product.py的一部分
# 移除VPN相关的方法：
# - is_client_exists
# - create_subscription  
# - extend_subscription
# - change_subscription

# 保留但重构的方法：
# - gift_trial → gift_product (赠送产品)
# - activate_promocode (优惠码激活，改为产品优惠)
```

### 步骤4：重构路由和界面 (预计时间：2天)

#### 4.1 更新主菜单
```python
# app/bot/routers/main_menu/keyboard.py
# 修改按钮文本：
"🔌 连接" → "📦 我的订单"
"📱 下载应用" → "🛍️ 商品目录" 
"💳 购买订阅" → "💳 购买商品"
"🎁 免费试用" → "🎁 免费商品"
```

#### 4.2 重构订阅路由
```bash
# 重命名目录
mv app/bot/routers/subscription app/bot/routers/product

# 更新文件内容：
# - subscription_handler.py → product_handler.py
# - 更新所有处理器逻辑
# - 更新键盘定义
```

#### 4.3 更新个人资料页面
```python
# app/bot/routers/profile/handler.py
# 移除VPN相关功能：
# - show_key (显示VPN密钥)
# - connect_to_vpn

# 添加新功能：
# - show_orders (显示订单历史) 
# - show_purchased_products (显示已购买的产品)
```

### 步骤5：更新配置和常量 (预计时间：半天)

#### 5.1 更新config.py
```python
# 删除XUIConfig类和相关配置
# 添加ProductConfig类：

@dataclass
class ProductConfig:
    PRODUCTS_FILE: str
    DEFAULT_CATEGORY: str
    DELIVERY_TIMEOUT: int
```

#### 5.2 更新constants.py
```python
# 移除VPN相关常量：
# APP_IOS_LINK, APP_ANDROID_LINK, APP_WINDOWS_LINK
# APP_*_SCHEME

# 添加产品相关常量：
PRODUCT_CATEGORIES = ["software", "gaming", "subscription", "digital"]
ORDER_STATUSES = ["pending", "paid", "delivered", "failed", "refunded"]
DELIVERY_TYPES = ["digital", "manual", "api"]
```

### 步骤6：管理员功能改造 (预计时间：1天)

#### 6.1 替换服务器管理
```python
# 删除：app/bot/routers/admin_tools/server_handler.py
# 创建：app/bot/routers/admin_tools/product_handler.py

# 新功能：
# - 添加产品
# - 编辑产品信息
# - 管理库存
# - 查看销售统计
```

#### 6.2 更新统计功能
```python
# app/bot/routers/admin_tools/statistics_handler.py
# 修改统计指标：
# "VPN客户端数量" → "总订单数量"
# "服务器状态" → "产品销量排行"
# "活跃连接" → "活跃订单"
```

### 步骤7：更新本地化文件 (预计时间：1天)

#### 7.1 批量替换翻译
```bash
# 在所有.po文件中替换：
"VPN" → "产品" / "Product" / "Продукт"  
"服务器" → "商品" / "Product" / "Товар"
"连接" → "使用" / "Use" / "Использовать"
"订阅" → "购买" / "Purchase" / "Покупка"
"密钥" → "商品信息" / "Product Info" / "Информация о товаре"
```

#### 7.2 更新核心界面文本
```po
# 主菜单欢迎语：
msgid "main_menu:message:main"
msgstr ""
"欢迎来到电子商品商店！🛍️\n"
"\n"
"我们提供各类优质数字商品，包括软件许可证、游戏账号、"
"在线服务等。安全支付，即时交付。\n"
"\n"
"🚀 即时交付\n"
"🔒 安全支付\n"  
"📱 多样商品\n"
"♾️ 优质服务\n"
"✅ 售后保障\n"
"👥 推荐奖励\n"
```

### 步骤8：数据迁移脚本 (预计时间：半天)

#### 8.1 创建迁移脚本
```python
# scripts/migrate_to_ecommerce.py
async def migrate_data():
    """数据迁移脚本"""
    
    # 1. 备份现有数据
    # 2. 创建新表结构
    # 3. 迁移用户数据（移除VPN字段）
    # 4. 将现有transactions转换为orders
    # 5. 清理servers表
    # 6. 创建示例产品数据
```

#### 8.2 创建产品配置文件
```json
// products.json (替换plans.json)
{
    "categories": [
        {"id": "software", "name": "软件许可证", "name_en": "Software Licenses"},
        {"id": "gaming", "name": "游戏相关", "name_en": "Gaming"},
        {"id": "subscription", "name": "订阅服务", "name_en": "Subscriptions"},
        {"id": "digital", "name": "数字内容", "name_en": "Digital Content"}
    ],
    "products": [
        {
            "id": 1,
            "name": "Premium Software License",
            "description": "高级软件1年许可证",
            "category": "software", 
            "prices": {
                "RUB": {"1": 1000, "6": 5000, "12": 9000},
                "USD": {"1": 10, "6": 50, "12": 90}
            },
            "delivery_type": "license_key",
            "stock": -1,
            "delivery_config": {
                "template": "您的许可证密钥：{license_key}",
                "key_length": 25
            }
        }
    ]
}
```

## 🔧 第三阶段：测试和部署

### 步骤9：功能测试 (预计时间：1天)
- [ ] 产品浏览功能
- [ ] 购买流程测试
- [ ] 支付集成测试  
- [ ] 产品交付测试
- [ ] 管理员功能测试
- [ ] 多语言界面测试

### 步骤10：部署和监控 (预计时间：半天)
- [ ] 数据库迁移
- [ ] Docker镜像更新
- [ ] 环境变量配置
- [ ] 监控日志检查

## 📊 改造完成后的新架构

### 新的服务结构：
```
ProductService          # 产品管理服务
OrderService           # 订单处理服务  
DeliveryService        # 产品交付服务
InventoryService       # 库存管理服务（可选）
PaymentService         # 支付处理服务（保留现有）
```

### 新的路由结构：
```
/product/              # 产品相关路由
  - browse.py          # 产品浏览
  - purchase.py        # 购买流程
  - orders.py          # 订单管理
/admin_tools/
  - product_mgmt.py    # 产品管理
  - order_mgmt.py      # 订单管理
  - inventory_mgmt.py  # 库存管理
```

## ⚡ 快速实施方案（3天完成）

如果时间紧迫，可以采用以下快速方案：

### Day 1: 核心改造
1. 移除VPN依赖（删除相关文件）
2. 创建基础Product和Order模型
3. 重构主要界面文本

### Day 2: 功能适配  
1. 将VPN订阅逻辑改为产品购买逻辑
2. 更新支付成功后的处理流程
3. 修改个人资料页面

### Day 3: 完善和测试
1. 更新管理员功能
2. 批量更新翻译文件
3. 功能测试和修复

## 🎯 预期成果

改造完成后，机器人将具备以下能力：

### 用户功能：
- 🛍️ 浏览产品目录
- 💳 选择和购买产品
- 📦 查看订单历史
- 🎁 使用优惠码
- 👥 推荐奖励（保留）

### 管理员功能：
- 📝 产品管理（添加、编辑、删除）
- 📊 销售统计和分析
- 🎟️ 优惠码管理
- 👥 用户管理
- 💰 财务管理

### 技术优势：
- 🚀 移除复杂VPN依赖，提高稳定性
- 🔧 更简单的部署和维护
- 📈 更容易扩展新的产品类型
- 💡 更灵活的商业模式

**总预计时间：5-8个工作日（取决于选择的方案和团队经验）**
