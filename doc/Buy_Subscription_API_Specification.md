# 📋 Buy Subscription 服务接口规范

## 🎯 服务调用流程

### 1. 用户点击 "Buy Subscription" 按钮
- **按钮位置**: Profile 页面
- **触发事件**: `NavSubscription.MAIN`
- **文件**: `app/bot/routers/profile/keyboard.py`

### 2. 订阅主处理器调用
- **处理器**: `callback_subscription()`  
- **文件**: `app/bot/routers/subscription/subscription_handler.py:55`
- **依赖服务**: `ProductService`, `ServicesContainer`

### 3. 核心服务接口

## 🔧 ProductService 接口规范

### `get_user_subscription_info(user: User) -> Optional[Dict]`

**功能**: 获取用户当前的产品订阅信息

**输入参数**:
```python
user: User  # 数据库用户模型
```

**返回格式**:
```python
{
    'user_id': int,                    # 用户Telegram ID
    'product_name': str,               # 产品名称
    'category': str,                   # 产品分类
    'status': 'active' | 'expired' | 'none',  # 订阅状态
    'expires_at': str,                 # 过期时间 (ISO格式)
    'days_remaining': int,             # 剩余天数
    'created_at': str,                 # 创建时间
    'is_gift': bool,                   # 是否为礼品
    'is_bonus': bool,                  # 是否为奖励
    'bonus_days_added': int,           # 已添加奖励天数
    'delivery_info': Dict              # 交付信息
}
```

**无订阅时返回**:
```python
{
    'user_id': int,
    'status': 'none',
    'message': 'No active product subscription found'
}
```

### `create_subscription(user_id: int, plan: Plan, transaction_id: int) -> ProductSubscriptionData`

**功能**: 为用户创建产品订阅

**输入参数**:
```python
user_id: int         # 用户ID
plan: Plan          # 订阅计划对象
transaction_id: int # 交易ID
```

**返回类型**:
```python
ProductSubscriptionData:
    start_date: datetime      # 开始时间
    expire_date: datetime     # 过期时间  
    traffic_limit: int        # 流量限制
    is_trial: bool           # 是否试用
    product_id: str          # 产品ID
    product_name: str        # 产品名称
```

### `gift_product(user: User, duration: int, devices: int = 1) -> bool`

**功能**: 赠送用户产品访问权限

**输入参数**:
```python
user: User       # 用户对象
duration: int    # 持续天数
devices: int     # 设备数量 (默认1)
```

**返回**: `True` 成功，`False` 失败

### `process_bonus_days(user: User, duration: int, devices: int = 1) -> bool`

**功能**: 为用户处理奖励天数

**输入参数**:
```python
user: User       # 用户对象  
duration: int    # 奖励天数
devices: int     # 设备数量 (默认1)
```

**返回**: `True` 成功，`False` 失败

## 📊 SubscriptionService 接口规范

### `is_trial_available(user: User) -> bool`

**功能**: 检查用户是否可以使用试用

**返回**: `True` 可用，`False` 不可用

### `gift_trial(user: User) -> bool`

**功能**: 为用户提供试用期

**返回**: `True` 成功，`False` 失败

### `get_user_subscription_status(user: User) -> Optional[Dict]`

**功能**: 获取用户订阅状态（使用ProductService）

**返回格式**: 与 `ProductService.get_user_subscription_info()` 相同

## 🎮 处理器接口规范

### `callback_subscription()` - 主订阅页面

**路由**: `NavSubscription.MAIN`
**功能**: 显示用户订阅状态和可用操作

**关键逻辑**:
1. 获取用户订阅信息
2. 创建兼容的 client_data 结构
3. 显示订阅界面

### `callback_subscription_process()` - 订阅流程

**路由**: `NavSubscription.PROCESS`  
**功能**: 开始新订阅流程

**关键变更**: 
- ❌ 移除服务器可用性检查
- ✅ 直接进入设备选择

### `callback_subscription_extend()` - 延长订阅

**路由**: `NavSubscription.EXTEND`
**功能**: 延长现有订阅

**关键变更**:
- ❌ 移除VPN客户端检查
- ✅ 使用ProductService获取当前状态
- ✅ 默认1设备用于数字产品

## 🏗️ 架构改进

### 兼容性处理

为了保持现有UI的兼容性，创建了模拟的 `ClientData` 结构：

```python
client_data = type('ClientData', (), {
    'has_subscription_expired': subscription_info['status'] != 'active',
    'max_devices': 1,  # 数字产品默认
    'expiry_time': subscription_info.get('expires_at', 'Unknown'),
})()
```

### 错误处理

所有服务调用都包含适当的错误处理：
- 服务不可用时的降级处理
- 用户友好的错误消息
- 完整的日志记录

## 🧪 测试建议

### 功能测试
1. **正常购买流程**: 新用户购买订阅
2. **延长订阅**: 现有用户延长订阅
3. **试用激活**: 新用户获取试用
4. **优惠码使用**: 用户激活优惠码

### 边界测试  
1. **无效优惠码**: 测试错误处理
2. **重复试用**: 防止多次试用
3. **过期订阅**: 正确显示状态

### 性能测试
1. **并发购买**: 多用户同时购买
2. **服务响应**: 各服务接口响应时间
3. **数据库压力**: 订阅信息存储性能

## 🚀 已修复的问题

✅ **VPN服务依赖清理完成**
- 移除 `services.vpn` 调用
- 移除 `services.server_pool` 调用
- 使用 `ProductService` 替代

✅ **数字产品适配完成**  
- 支持多种交付类型
- 产品目录集成
- 自动化交付系统

✅ **错误处理完善**
- 服务降级机制
- 用户友好提示
- 完整日志记录

现在 "Buy Subscription" 按钮应该能正常工作！🎉
