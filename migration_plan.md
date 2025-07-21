# VPN商店到通用电子商品商店改造计划

## 🎯 改造目标
将现有的VPN订阅销售机器人改造成通用的数字商品销售机器人，支持销售各类电子商品如：
- 软件激活码
- 游戏账号
- 数字内容订阅
- 在线服务访问权限
- 其他数字化商品

## 📊 当前VPN相关组件分析

### 核心VPN组件：
1. **py3xui依赖** (`pyproject.toml`)
2. **VPNService服务** (`app/bot/services/vpn.py`)
3. **ServerPoolService服务** (`app/bot/services/server_pool.py`) 
4. **ClientData模型** (`app/bot/models/client_data.py`)
5. **Server数据库模型** (`app/db/models/server.py`)
6. **XUIConfig配置** (`app/config.py`)
7. **VPN相关常量** (`app/bot/utils/constants.py`)
8. **VPN相关翻译** (所有本地化文件中的VPN术语)

## 🔄 分阶段改造计划

### 阶段1：新商品模型设计 (1-2天)

#### 1.1 创建Product数据库模型
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price_data JSON NOT NULL,  -- 支持多货币定价
    stock_quantity INTEGER DEFAULT -1,  -- -1表示无限库存
    is_active BOOLEAN DEFAULT TRUE,
    delivery_type VARCHAR(50) DEFAULT 'digital',  -- digital/physical/service
    delivery_config JSON,  -- 配送配置
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 1.2 创建Order数据库模型
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    total_price DECIMAL(10,2),
    currency VARCHAR(3),
    status VARCHAR(20) DEFAULT 'pending',  -- pending/paid/delivered/failed
    payment_method VARCHAR(50),
    delivery_data JSON,  -- 交付的商品数据
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (tg_id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

#### 1.3 重新设计plans.json结构
从VPN订阅套餐改为通用商品配置：
```json
{
    "categories": ["software", "gaming", "subscription", "service"],
    "products": [
        {
            "id": 1,
            "name": "Premium Software License",
            "description": "1年期高级软件许可证",
            "category": "software",
            "prices": {
                "RUB": {"1": 1000, "12": 10000},
                "USD": {"1": 10, "12": 100}
            },
            "delivery_type": "license_key",
            "stock": -1
        }
    ]
}
```

### 阶段2：服务层重构 (2-3天)

#### 2.1 替换VPNService
创建 `ProductService` 替代 `VPNService`：
- `create_order()` - 创建订单
- `process_payment()` - 处理支付
- `deliver_product()` - 交付商品
- `get_order_status()` - 查询订单状态

#### 2.2 移除服务器相关组件
- 删除 `ServerPoolService`
- 删除 `Server` 数据库模型
- 移除服务器管理相关路由和处理器

#### 2.3 重构数据模型
- 将 `ClientData` 改为 `OrderData`
- 将 `SubscriptionData` 改为 `ProductData`
- 更新用户模型，移除VPN相关字段

### 阶段3：界面和交互重构 (2-3天)

#### 3.1 主菜单改造
- "🔌 连接" → "📦 我的订单"  
- "📱 下载应用" → "📋 商品目录"
- "🎁 免费试用" → "🎁 优惠活动"

#### 3.2 订阅流程改为购买流程
- subscription_handler → product_handler
- 商品选择 → 数量选择 → 支付方式 → 确认购买
- 支付成功后交付商品（激活码/账号信息/下载链接等）

#### 3.3 个人资料页面
- 移除"显示密钥"功能
- 添加"订单历史"功能  
- 添加"商品管理"功能

### 阶段4：管理功能改造 (1-2天)

#### 4.1 管理员工具更新
- 服务器管理 → 商品管理
- 添加商品、编辑库存、价格调整
- 订单管理和状态跟踪

#### 4.2 统计功能调整
- VPN客户端统计 → 商品销售统计
- 服务器负载 → 库存状态
- 收入分析保持不变

### 阶段5：本地化和配置更新 (1天)

#### 5.1 更新所有翻译文件
- 替换VPN相关术语
- 更新为通用电商术语
- 中文/英文/俄文全面更新

#### 5.2 配置文件调整
- 移除XUI相关配置
- 添加商品配置路径
- 更新环境变量文档

### 阶段6：测试和部署 (1-2天)

#### 6.1 功能测试
- 商品浏览和购买流程
- 支付和交付流程  
- 管理员商品管理功能

#### 6.2 数据迁移
- 现有用户数据保留
- 订阅数据转换为订单历史
- 清理VPN相关数据

## 📁 文件修改清单

### 需要删除的文件：
- `app/bot/services/vpn.py`
- `app/bot/services/server_pool.py`  
- `app/db/models/server.py`
- `app/bot/routers/admin_tools/server_handler.py`
- VPN相关的键盘和处理器

### 需要重写的文件：
- `app/bot/services/subscription.py` → `app/bot/services/product.py`
- `app/bot/models/client_data.py` → `app/bot/models/order_data.py`
- `app/bot/routers/subscription/*` → `app/bot/routers/product/*`
- 所有本地化文件
- `plans.json` → `products.json`

### 需要更新的文件：
- `pyproject.toml` (移除py3xui依赖)
- `app/config.py` (移除XUI配置)
- `app/db/models/user.py` (移除VPN字段)
- 所有路由处理器
- Docker配置文件

## 🔧 技术难点和解决方案

### 难点1：商品交付系统设计
**解决方案**：创建灵活的交付系统，支持多种交付方式：
- 文本内容（激活码、账号密码）
- 文件下载（软件、文档）
- API调用（第三方服务激活）

### 难点2：库存管理
**解决方案**：实现分层库存系统：
- 无限库存商品（数字内容）
- 有限库存商品（激活码池）
- 实时库存商品（API对接）

### 难点3：订单状态管理
**解决方案**：建立完整的订单生命周期：
- 创建 → 支付 → 交付 → 完成
- 支持退款和售后处理

## ⚡ 快速开始方案（最小化改动）

如果需要快速改造，可以采用以下最小化方案：

1. **保留现有架构**，只修改用户界面文本
2. **将VPN密钥替换为商品信息**展示
3. **服务器概念映射为商品类别**
4. **订阅时长映射为商品数量或使用期限**

这样可以在1-2天内完成基本改造，后续再逐步优化。

## 📈 预期收益

1. **扩展性**：支持销售各类数字商品
2. **灵活性**：易于添加新商品类型
3. **可维护性**：移除复杂的VPN基础设施依赖
4. **用户体验**：更直观的购买流程

## ⏰ 总预期时间：7-10个工作日

- 设计和规划：1天
- 数据库和模型：2天  
- 服务层重构：3天
- 界面改造：2-3天
- 测试和部署：1-2天
