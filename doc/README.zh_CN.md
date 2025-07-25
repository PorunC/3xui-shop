<div align="center" markdown>

<p align="center">
    <a href="#english"><u><b>ENGLISH</b></u></a> •
    <a href="#中文"><u><b>中文</b></u></a> •
    <a href="https://github.com/snoups/3xui-shop/blob/main/doc/README.ru_RU.md"><u><b>РУССКИЙ</b></u></a>
</p>

![3xui-shop](https://github.com/user-attachments/assets/282d10db-a355-4c65-a2cf-eb0e8ec8eed1)

**这是一个用于销售数字产品和电子商品的Telegram机器人**

<a id="english"></a>

## 📝 英文文档

完整的英文安装指南和文档，请访问：
**[📚 English Documentation](README_EN.md)**

<a id="中文"></a>

## 📝 中文文档

---

## 🚀 快速开始

这是一个全面的Telegram电商机器人，用于销售数字产品和服务，支持：

- 🛍️ **数字产品销售** - 软件许可证、游戏密钥、订阅服务、数字内容
- 💳 **多种支付网关** - Telegram Stars（内置）、Cryptomus（加密货币支付）
- 🎁 **试用系统** - 为新用户提供免费试用，可配置试用期
- 👥 **多级推荐计划** - 双层推荐奖励系统
- 📦 **自动交付** - 即时产品交付，可自定义模板
- 🌍 **多语言支持** - 英文、俄文、中文翻译
- 🔧 **管理面板** - 全面的管理工具
- 📊 **分析统计** - 支付追踪、用户分析、推荐统计

### 快速安装
```bash
# 克隆仓库
git clone https://github.com/snoups/3xui-shop.git
cd 3xui-shop

# 设置配置文件
cp .env.example .env
cp plans.example.json plans.json
cp plans.json app/data/plans.json

# 编辑配置文件
# nano .env          # 配置机器人token、域名、支付方式
# nano plans.json    # 配置订阅计划

# 构建并运行
docker compose build
docker compose up -d
```

### 自动安装脚本
```bash
bash <(curl -Ls https://raw.githubusercontent.com/snoups/3xui-shop/main/scripts/install.sh) -q
```

### 项目状态：✅ 生产就绪

- ✅ **第一阶段完成** - 移除VPN系统，核心架构迁移
- ✅ **第二阶段完成** - 增强ProductService，真实产品目录，模型修复
- 🚀 **生产就绪** - 完整的数字产品销售功能

### 🏗️ 架构概览

这个机器人使用基于aiogram的**模块化、面向服务的架构**：

```
📦 3xui-shop/
├── 🤖 app/bot/                    # 核心机器人逻辑
│   ├── 🔌 routers/               # 基于功能的消息处理器
│   ├── 🛠️ services/              # 业务逻辑层
│   ├── 💳 payment_gateways/      # 支付系统（可插拔）
│   ├── 🔒 middlewares/           # 认证、数据库等
│   └── 📊 models/                # 数据模型和容器
├── 💾 app/db/                     # 数据库层
│   ├── 📋 models/                # SQLAlchemy模型
│   └── 🔄 migration/             # Alembic数据库迁移
├── 🌍 app/locales/               # 多语言支持
├── 📜 scripts/                   # 实用工具脚本
└── 🐳 docker-compose.yml         # 容器编排
```

**核心功能：**
- 🔌 **可插拔支付网关** - 轻松添加新的支付方式
- 🛠️ **服务层架构** - 业务逻辑清晰分离
- 🌍 **国际化** - 内置多语言支持
- 📊 **全面分析** - 用户跟踪、支付统计、推荐指标
- 🔐 **高级管理面板** - 完整的管理功能
- 🎁 **灵活的产品系统** - 支持各种数字产品类型

<p align="center">
    <a href="#概述">概述</a> •
    <a href="#安装指南">安装指南</a> •
    <a href="#问题反馈">问题反馈</a> •
    <a href="#支持项目">支持项目</a>
</p>

![GitHub License](https://img.shields.io/github/license/snoups/3xui-shop)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/snoups/3xui-shop/total)
![GitHub Release](https://img.shields.io/github/v/release/snoups/3xui-shop)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/snoups/3xui-shop)


[![Static Badge](https://img.shields.io/badge/public_channel-white?style=social&logo=Telegram&logoColor=blue&logoSize=auto&labelColor=white&link=https%3A%2F%2Ft.me%2Fsn0ups)](https://t.me/sn0ups)
[![Static Badge](https://img.shields.io/badge/contact_me-white?style=social&logo=Telegram&logoColor=blue&logoSize=auto&labelColor=white&link=https%3A%2F%2Ft.me%2Fsnoups)](https://t.me/snoups)
![GitHub Repo stars](https://img.shields.io/github/stars/snoups/3xui-shop)
</div>

<a id="概述"></a>

## 📝 概述

**3X-UI-SHOP** 是一个通过Telegram自动销售数字产品的综合解决方案。
该机器人支持多种支付方式，包括 **Cryptomus** 和 **Telegram Stars**，可以交付
各种类型的数字商品，包括软件许可证、游戏密钥、订阅服务和数字内容。

机器人提供高效的产品销售功能：

- **产品管理**
    - 按类别浏览数字产品
    - 拥有8+产品的高级产品目录
    - 数字商品自动交付系统
    - 支持多种产品类型（许可证、账户、下载、API）
    - 动态密钥生成和安全交付
- **灵活的交付系统**
    - 许可证密钥交付（软件、游戏）
    - 账户信息交付（流媒体服务）
    - 下载链接交付（数字文件、电子书）
    - API访问交付（开发工具）
- **促销码系统**
    - 创建、编辑和删除促销码
    - 产品折扣促销码
    - 限时促销活动
- **通知系统**
    - 向特定用户或所有用户发送消息
    - 编辑最后发送的通知
    - 使用HTML格式化文本
    - 发送前预览通知
    - 为开发者和管理员提供系统通知
- **双层推荐计划** (by [@Heimlet](https://github.com/Heimlet))
    - 查看推荐统计
    - 奖励邀请新成员的用户产品或奖励
    - 支持双层推荐奖励
- **试用期** (by [@Heimlet](https://github.com/Heimlet))
    - 提供免费试用产品
    - 为推荐用户提供延长试用福利
    - 配置和自定义试用产品
- **灵活的支付系统**
    - 更改默认货币
    - 易于扩展的架构，可添加新的支付网关
    - 支持多种产品定价模型
    - 实时订单处理和交付
- **~~用户编辑器~~**
    - ~~查看用户信息~~
    - ~~查看推荐统计~~
    - ~~查看支付历史和激活的促销码~~
    - ~~查看服务器信息~~
    - ~~编辑用户订阅~~
    - ~~封禁或解封用户~~
    - ~~通过转发消息快速访问用户~~
    - ~~用户个人折扣~~

### ⚙️ 管理面板
机器人包括一个用户友好的管理面板，提供高效管理工具。
管理员可以管理产品、订单和用户账户。

- **`产品管理`**: 添加、编辑和管理数字产品
- **`订单管理`**: 跟踪和处理客户订单
- **`统计分析`**: 查看销售分析和性能数据
- **`用户编辑器`**: 管理用户账户和购买历史
- **`促销码编辑器`**: 创建、编辑和删除促销码
- **`通知发送器`**: 向用户发送自定义通知
- **`数据库备份`**: 创建和发送数据库备份
- **`维护模式`**: 在更新或修复期间禁用用户访问


### 🚧 当前状态
- [x] 试用期
- [x] 推荐系统
- [x] 产品目录管理
- [x] 多类型交付系统
- [x] 支付集成
- [ ] 高级统计
- [ ] 增强的用户编辑器
- [ ] 产品评价系统
- [ ] 库存管理
- [ ] 自定义产品类别
    - API访问交付（开发工具）
- **优惠码系统**
    - 创建、编辑和删除优惠码
    - 产品折扣优惠码
    - 限时促销活动
- **通知功能**
    - 发送消息给特定用户或所有用户
    - 编辑最后发送的通知
    - 使用HTML格式化文本
    - 发送前预览通知
    - 开发者和管理员系统通知
- **两级推荐计划** (由 [@Heimlet](https://github.com/Heimlet) 提供)
    - 查看推荐统计
    - 奖励邀请新成员的用户产品或奖励
    - 支持两级推荐奖励
- **试用期** (由 [@Heimlet](https://github.com/Heimlet) 提供)
    - 提供免费试用产品
    - 被推荐用户的延长试用福利
    - 配置和自定义试用产品
- **灵活的支付系统**
    - 更改默认货币
    - 易于扩展的架构，便于添加新的支付网关
    - 支持多种产品定价模型
    - 实时订单处理和交付

### ⚙️ 管理面板
机器人包含用户友好的管理面板，提供高效管理工具。
管理员可以管理产品、订单和用户账户。

- **`产品管理`**: 添加、编辑和管理数字产品
- **`订单管理`**: 跟踪和处理客户订单
- **`统计`**: 查看销售分析和性能数据
- **`用户编辑器`**: 管理用户账户和购买历史
- **`优惠码编辑器`**: 创建、编辑和删除优惠码
- **`通知发送器`**: 向用户发送自定义通知
- **`数据库备份`**: 创建和发送数据库备份
- **`维护模式`**: 在更新或修复期间禁用用户访问


### 🚧 当前状态
- [x] 试用期功能
- [x] 推荐系统
- [x] 产品目录管理
- [x] 多类型交付系统
- [x] 支付集成
- [ ] 高级统计
- [ ] 增强用户编辑器
- [ ] 产品评价系统
- [ ] 库存管理
- [ ] 自定义产品分类

<a id="安装指南"></a>

## 🛠️ 安装指南

### 依赖项

开始安装前，请确保已安装 [**Docker**](https://www.docker.com/)

### Docker 安装

1. **安装和升级：**
   ```bash
   bash <(curl -Ls https://raw.githubusercontent.com/snoups/3xui-shop/main/scripts/install.sh) -q
   cd 3xui-shop
   ```

2. **设置环境变量和产品目录：**
- 复制 `plans.example.json` 到 `plans.json` 和 `.env.example` 到 `.env`：
    ```bash
    cp plans.example.json plans.json
    cp .env.example .env
    ```
    > 根据你的产品目录更新 `plans.json` 文件。[(产品目录配置)](#产品目录配置)

    > 根据你的配置更新 `.env` 文件。[(环境变量配置)](#环境变量配置)

3. **构建Docker镜像：**
   ```bash
   docker compose build
   ```

4. **运行Docker容器：**
   ```bash
   docker compose up -d
   ```

### 环境变量配置

| 变量名 | 必需 | 默认值 | 描述 |
|-|-|-|-|
| LETSENCRYPT_EMAIL | 🔴 | - | 生成证书的邮箱 |
| | | |
| BOT_TOKEN | 🔴 | - | Telegram机器人token |
| BOT_ADMINS | ⭕ | - | 管理员ID列表 (例如：123456789,987654321) |
| BOT_DEV_ID | 🔴 | - | 机器人开发者ID |
| BOT_SUPPORT_ID | 🔴 | - | 支持人员ID |
| BOT_DOMAIN | 🔴 | - | 机器人域名 (例如：3xui-shop.com) |
| BOT_PORT | ⭕ | 8080 | 机器人端口 |
| | | |
| SHOP_EMAIL | ⭕ | support@3xui-shop.com | 收据邮箱 |
| SHOP_CURRENCY | ⭕ | RUB | 按钮货币 (例如：RUB, USD, XTR) |
| SHOP_TRIAL_ENABLED | ⭕ | True | 为新用户启用试用产品 |
| SHOP_TRIAL_PERIOD | ⭕ | 3 | 试用访问持续时间（天） |
| SHOP_REFERRED_TRIAL_ENABLED | ⭕ | False | 为推荐用户启用延长试用期 |
| SHOP_REFERRED_TRIAL_PERIOD | ⭕ | 7 | 推荐用户延长试用期持续时间（天） |
| SHOP_REFERRER_REWARD_ENABLED | ⭕ | True | 启用双层推荐奖励系统 |
| SHOP_REFERRER_LEVEL_ONE_PERIOD | ⭕ | 10 | 一级推荐人奖励天数 |
| SHOP_REFERRER_LEVEL_TWO_PERIOD | ⭕ | 3 | 二级推荐人奖励天数 |
| SHOP_BONUS_DEVICES_COUNT | ⭕ | 1 | 促销码和推荐奖励的默认奖励数量 |
| SHOP_PAYMENT_STARS_ENABLED | ⭕ | True | 启用Telegram stars支付 |
| SHOP_PAYMENT_CRYPTOMUS_ENABLED | ⭕ | False | 启用Cryptomus支付 |
| | | |
| PRODUCT_CATALOG_FILE | ⭕ | products.json | 产品目录文件路径 |
| PRODUCT_DEFAULT_CATEGORY | ⭕ | digital | 默认产品类别 |
| PRODUCT_DELIVERY_TIMEOUT | ⭕ | 3600 | 产品交付超时时间（秒） |
| | | |
| CRYPTOMUS_API_KEY | ⭕ | - | Cryptomus支付API密钥 |
| CRYPTOMUS_MERCHANT_ID | ⭕ | - | Cryptomus支付商户ID |
| | | |
| LOG_LEVEL | ⭕ | DEBUG | 日志级别 (例如：INFO, DEBUG) |
| LOG_FORMAT | ⭕ | %(asctime)s \| %(name)s \| %(levelname)s \| %(message)s | 日志格式 |
| LOG_ARCHIVE_FORMAT | ⭕ | zip | 日志存档格式 (例如：zip, gz) |


### 产品目录配置

```json
{
    "categories": [
        "software",     // 软件许可证和应用程序
        "gaming",       // 游戏密钥和游戏账户
        "subscription", // 流媒体服务和订阅
        "digital",      // 数字内容和下载
        "education"     // 教育课程和材料
    ],

    "products": [
        {
            "id": "microsoft_office_365",
            "name": "Microsoft Office 365 Personal",
            "description": "完整的Microsoft Office套件，含1TB OneDrive存储",
            "category": "software",
            "price": {
                "amount": 999,
                "currency": "RUB"
            },
            "duration_days": 365,
            "delivery_type": "license_key",
            "delivery_template": "🔑 您的Microsoft Office 365许可证: {license_key}",
            "key_format": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "stock": -1,  // -1表示无限库存
            "is_active": true
        },
        {
            "id": "steam_random_key",
            "name": "Steam随机游戏密钥",
            "description": "随机Steam游戏密钥 - 保证高级游戏",
            "category": "gaming", 
            "price": {
                "amount": 299,
                "currency": "RUB"
            },
            "duration_days": 0,  // 永久
            "delivery_type": "license_key",
            "delivery_template": "🎮 您的Steam密钥: {license_key}",
            "key_format": "XXXXX-XXXXX-XXXXX",
            "stock": 100,
            "is_active": true
        }
    ]
}
```

在开始安装之前，请确保已安装 [**Docker**](https://www.docker.com/)

### Docker 安装

1. **安装和升级:**
   ```bash
   bash <(curl -Ls https://raw.githubusercontent.com/snoups/3xui-shop/main/scripts/install.sh) -q
   cd 3xui-shop
   ```

2. **设置环境变量和产品目录:**
- 复制 `plans.example.json` 到 `plans.json`，`.env.example` 到 `.env`:
    ```bash
    cp plans.example.json plans.json
    cp .env.example .env
    ```
    > 使用您的产品目录更新 `plans.json` 文件。[(产品目录配置)](#产品目录配置) 

    > 使用您的配置更新 `.env` 文件。[(环境变量配置)](#环境变量配置)

3. **构建Docker镜像:**
   ```bash
   docker compose build
   ```

4. **运行Docker容器:**
   ```bash
   docker compose up -d
   ```

### 环境变量配置

| 变量 | 必需 | 默认值 | 描述 |
|-|-|-|-|
| LETSENCRYPT_EMAIL | 🔴 | - | 生成证书的邮箱 |
| | | |
| BOT_TOKEN | 🔴 | - | Telegram机器人token |
| BOT_ADMINS | ⭕ | - | 管理员ID列表 (例如: 123456789,987654321) |
| BOT_DEV_ID | 🔴 | - | 机器人开发者ID |
| BOT_SUPPORT_ID | 🔴 | - | 客服人员ID |
| BOT_DOMAIN | 🔴 | - | 机器人域名 (例如: 3xui-shop.com) |
| BOT_PORT | ⭕ | 8080 | 机器人端口 |
| | | |
| SHOP_EMAIL | ⭕ | support@3xui-shop.com | 收据邮箱 |
| SHOP_CURRENCY | ⭕ | RUB | 按钮货币 (例如: RUB, USD, XTR) |
| SHOP_TRIAL_ENABLED | ⭕ | True | 为新用户启用试用产品 |
| SHOP_TRIAL_PERIOD | ⭕ | 3 | 试用访问持续天数 |
| SHOP_REFERRED_TRIAL_ENABLED | ⭕ | False | 为被推荐用户启用延长试用期 |
| SHOP_REFERRED_TRIAL_PERIOD | ⭕ | 7 | 被推荐用户延长试用期天数 |
| SHOP_REFERRER_REWARD_ENABLED | ⭕ | True | 启用两级推荐奖励系统 |
| SHOP_REFERRER_LEVEL_ONE_PERIOD | ⭕ | 10 | 一级推荐人奖励天数 |
| SHOP_REFERRER_LEVEL_TWO_PERIOD | ⭕ | 3 | 二级推荐人奖励天数 |
| SHOP_BONUS_DEVICES_COUNT | ⭕ | 1 | 优惠码和推荐奖励的默认奖励数量 |
| SHOP_PAYMENT_STARS_ENABLED | ⭕ | True | 启用Telegram stars支付 |
| SHOP_PAYMENT_CRYPTOMUS_ENABLED | ⭕ | False | 启用Cryptomus支付 |
| | | |
| PRODUCT_CATALOG_FILE | ⭕ | products.json | 产品目录文件路径 |
| PRODUCT_DEFAULT_CATEGORY | ⭕ | digital | 默认产品分类 |
| PRODUCT_DELIVERY_TIMEOUT | ⭕ | 3600 | 产品交付超时时间（秒） |
| | | |
| CRYPTOMUS_API_KEY | ⭕ | - | Cryptomus支付API密钥 |
| CRYPTOMUS_MERCHANT_ID | ⭕ | - | Cryptomus支付商户ID |
| | | |
| LOG_LEVEL | ⭕ | DEBUG | 日志级别 (例如: INFO, DEBUG) |
| LOG_FORMAT | ⭕ | %(asctime)s \| %(name)s \| %(levelname)s \| %(message)s | 日志格式 |
| LOG_ARCHIVE_FORMAT | ⭕ | zip | 日志归档格式 (例如: zip, gz) |


### 产品目录配置

```json
{
    "categories": [
        "software",     // 软件许可证和应用程序
        "gaming",       // 游戏密钥和游戏账户
        "subscription", // 流媒体服务和订阅
        "digital",      // 数字内容和下载
        "education"     // 教育课程和材料
    ],

    "products": [
        {
            "id": "microsoft_office_365",
            "name": "Microsoft Office 365 个人版",
            "description": "完整的Microsoft Office套件，包含1TB OneDrive存储空间",
            "category": "software",
            "price": {
                "amount": 999,
                "currency": "RUB"
            },
            "duration_days": 365,
            "delivery_type": "license_key",
            "delivery_template": "🔑 您的Microsoft Office 365许可证: {license_key}",
            "key_format": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "stock": -1,  // -1表示无限库存
            "is_active": true
        },
        {
            "id": "steam_random_key",
            "name": "Steam随机游戏密钥",
            "description": "随机Steam游戏密钥 - 保证高质量游戏",
            "category": "gaming", 
            "price": {
                "amount": 299,
                "currency": "RUB"
            },
            "duration_days": 0,  // 永久
            "delivery_type": "license_key",
            "delivery_template": "🎮 您的Steam密钥: {license_key}",
            "key_format": "XXXXX-XXXXX-XXXXX",
            "stock": 100,
            "is_active": true
        }
    ]
}
```

### 推荐和试用奖励配置

机器人现在支持**试用产品**和**两级推荐奖励系统**。工作原理如下：
所有配置都可以通过`.env`文件进行设置 [(参见上文)](#环境变量配置)。

| 奖励类型 | 工作原理 |
| - | - |
| 试用期 | 任何打开机器人且没有活跃产品的用户都可以通过"免费试用"按钮获得试用产品。 |
| 延长试用期 | 此选项允许您为被邀请用户配置**延长试用期**。 |
| 两级推荐支付奖励 | 当被推荐用户购买产品时，推荐人和二级推荐人（推荐人的邀请者）将获得奖励或奖励天数。 |

<a id="问题反馈"></a>

## 🐛 问题反馈

如果您发现错误或有功能请求，请在GitHub仓库中提交issue。
也欢迎您通过提交pull request为项目做出贡献。

<a id="支持项目"></a>

## 💸 支持项目

特别感谢以下个人的慷慨支持：

- **Boto**
- [**@olshevskii-sergey**](https://github.com/olshevskii-sergey/)
- **Aleksey**
- [**@DmitryKryloff**](https://t.me/DmitryKryloff)

您可以通过以下方式支持我 ([或RUB](https://t.me/shop_3xui/2/1580))：

- **Bitcoin:** `bc1ql53lcaukdv3thxcheh3cmgucwlwkr929gar0cy`
- **Ethereum:** `0xe604a10258d26c085ada79cdea9a84a5b0894b91`
- **USDT (TRC20):** `TUqDQ4mdtVJZC76789kPYBMzaLFQBDdKhE`
- **TON:** `UQDogBlLFgrxkVWvDJn6YniCwrJDro7hbk5AqDMoSzmBQ-KQ`

任何支持都将帮助我投入更多时间进行开发并加速项目进展！
