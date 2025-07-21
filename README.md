<div align="center" markdown>

<p align="center">
    <a href="#english"><u><b>ENGLISH</b></u></a> •
    <a href="#中文"><u><b>中文</b></u></a> •
    <a href="https://github.com/snoups/3xui-shop/blob/main/doc/README.ru_RU.md"><u><b>РУССКИЙ</b></u></a>
</p>

![3xui-shop](http## 🐛 Support & Issues

If you find a bug or have a feature request, please open an issue on the GitHub repository.

## 💸 Support the Project

You can support development via:
- **Bitcoin:** `bc1ql53lcaukdv3thxcheh3cmgucwlwkr929gar0cy`
- **Ethereum:** `0xe604a10258d26c085ada79cdea9a84a5b0894b91`
- **USDT (TRC20):** `TUqDQ4mdtVJZC76789kPYBMzaLFQBDdKhE`
- **TON:** `UQDogBlLFgrxkVWvDJn6YniCwrJDro7hbk5AqDMoSzmBQ-KQ`user-attachments/assets/282d10db-a355-4c65-a2cf-eb0e8ec8eed1)

**This project is a Telegram bot for selling digital products and electronic goods.**

<a id="english"></a>

## 📝 English Documentation

For complete installation guide and documentation in English, please visit:
**[📚 English Documentation](doc/README_EN.md)**

<a id="中文"></a>

## 📝 中文文档  

完整的安装指南和中文文档，请访问：
**[📚 中文文档](doc/README.zh_CN.md)**

---

## 🚀 Quick Start

This is a digital products sales bot that supports:
- 🛍️ **Digital Product Sales** - Software licenses, game keys, subscriptions
- 💳 **Multiple Payment Methods** - Cryptomus, Telegram Stars  
- 🎁 **Trial System** - Free trials for new users
- 👥 **Referral Program** - Two-level referral rewards
- 📦 **Automated Delivery** - Instant product delivery

### Installation
```bash
# Clone and install
bash <(curl -Ls https://raw.githubusercontent.com/snoups/3xui-shop/main/scripts/install.sh) -q
cd 3xui-shop

# Configure
cp plans.example.json plans.json
cp .env.example .env
# Edit .env and plans.json with your settings

# Run
docker compose build && docker compose up -d
```

### Project Status: ✅ Production Ready

- ✅ **Phase 1 Complete** - VPN system removed, core architecture migrated
- ✅ **Phase 2 Complete** - Enhanced ProductService, real product catalog, model fixes
- 🚀 **Ready for Production** - Full digital product sales capability

## 📚 Documentation Index

| Document | Description | Language |
|----------|-------------|----------|
| [English Docs](doc/README_EN.md) | Complete installation and configuration guide | 🇺🇸 EN |
| [中文文档](doc/README.zh_CN.md) | 完整的安装配置指南 | 🇨🇳 中文 |
| [Russian Docs](doc/README.ru_RU.md) | Полное руководство по установке | 🇷🇺 RU |
| [Migration Guide](doc/implementation_guide.md) | VPN to e-commerce migration guide | 🇨🇳 中文 |
| [Phase Reports](doc/) | Detailed phase completion reports | 🇺🇸 EN |

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#installation-guide">Installation guide</a> •
    <a href="#bugs-and-feature-requests">Bugs and Feature Requests</a> •
    <a href="#support-the-project">Support the Project</a>
</p>

![GitHub License](https://img.shields.io/github/license/snoups/3xui-shop)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/snoups/3xui-shop/total)
![GitHub Release](https://img.shields.io/github/v/release/snoups/3xui-shop)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/snoups/3xui-shop)


[![Static Badge](https://img.shields.io/badge/public_channel-white?style=social&logo=Telegram&logoColor=blue&logoSize=auto&labelColor=white&link=https%3A%2F%2Ft.me%2Fsn0ups)](https://t.me/sn0ups)
[![Static Badge](https://img.shields.io/badge/contact_me-white?style=social&logo=Telegram&logoColor=blue&logoSize=auto&labelColor=white&link=https%3A%2F%2Ft.me%2Fsnoups)](https://t.me/snoups)
![GitHub Repo stars](https://img.shields.io/github/stars/snoups/3xui-shop)
</div>

<a id="overview"></a>

## 📝 Overview

**3X-UI-SHOP** is a comprehensive solution designed to automate the sale of digital products through Telegram.
The bot supports multiple payment methods, including **Cryptomus** and **Telegram Stars**, and can deliver
various types of digital goods including software licenses, game keys, subscriptions, and digital content.

The bot enables efficient product sales with advanced features:

- **Product Management**
    - Browse digital products by category
    - Advanced product catalog with 8+ products
    - Automated delivery system for digital goods
    - Support for multiple product types (licenses, accounts, downloads, APIs)
    - Dynamic key generation and secure delivery
- **Flexible Delivery System**
    - License key delivery (software, games)
    - Account information delivery (streaming services)
    - Download link delivery (digital files, eBooks)
    - API access delivery (developer tools)
- **Promocode System**
    - Create, edit, and delete promocodes
    - Promocodes for product discounts
    - Time-limited promotional offers
- **Notifications**
    - Send messages to a specific user or all users
    - Edit the last sent notification
    - Format text using HTML
    - Preview notifications before sending
    - System notifications for the developer and administrators
- **Two-Level Referral Program** (by [@Heimlet](https://github.com/Heimlet))
    - View referral statistics
    - Reward users for inviting new members with products or bonuses
    - Support for two-tier referral rewards
- **Trial Period** (by [@Heimlet](https://github.com/Heimlet))
    - Provide free trial products
    - Extended trial benefits for referred users
    - Configure and customize trial offerings
- **Flexible Payment System**
    - Change the default currency
    - Easily extendable architecture for adding new payment gateways
    - Support for multiple product pricing models
    - Real-time order processing and delivery
- **~~User Editor~~**
    - ~~View user information~~
    - ~~View referral statistics~~
    - ~~View payment history and activated promocodes~~
    - ~~View server information~~
    - ~~Edit user subscriptions~~
    - ~~Block or unblock users~~
    - ~~Quick access to a user via forwarded messages~~
    - ~~Personal discounts for users~~

### ⚙️ Admin Panel
The bot includes a user-friendly admin panel with tools for efficient management.
Administrators can manage products, orders, and user accounts.

- **`Product Manager`**: Add, edit, and manage digital products
- **`Order Management`**: Track and process customer orders
- **`Statistics`**: View sales analytics and performance data
- **`User Editor`**: Manage user accounts and purchase history
- **`Promocode Editor`**: Create, edit, and delete promocodes
- **`Notification Sender`**: Send custom notifications to users
- **`Database Backup`**: Create and send database backups
- **`Maintenance Mode`**: Disable user access during updates or fixes


### 🚧 Current Status
- [x] Trial period
- [x] Referral system
- [x] Product catalog management
- [x] Multi-type delivery system
- [x] Payment integration
- [ ] Advanced statistics
- [ ] Enhanced user editor
- [ ] Product review system
- [ ] Inventory management
- [ ] Custom product categories

<a id="installation-guide"></a>

## 🛠️ Installation guide

### Dependencies

Before starting the installation, make sure you have the installed [**Docker**](https://www.docker.com/)

### Docker Installation

1. **Install & Upgrade:**
   ```bash
   bash <(curl -Ls https://raw.githubusercontent.com/snoups/3xui-shop/main/scripts/install.sh) -q
   cd 3xui-shop
   ```

2. **Set up environment variables and product catalog:**
- Copy `plans.example.json` to `plans.json` and `.env.example` to `.env`:
    ```bash
    cp plans.example.json plans.json
    cp .env.example .env
    ```
    > Update `plans.json` file with your product catalog. [(Product Catalog Configuration)](#product-catalog-configuration) 

    > Update `.env` file with your configuration. [(Environment Variables Configuration)](#environment-variables-configuration)

3. **Build the Docker image:**
   ```bash
   docker compose build
   ```

4. **Run the Docker container:**
   ```bash
   docker compose up -d
   ```

### Environment Variables Configuration

| Variable | Required | Default | Description |
|-|-|-|-|
| LETSENCRYPT_EMAIL | 🔴 | - | Email for generating certificates |
| | | |
| BOT_TOKEN | 🔴 | - | Telegram bot token |
| BOT_ADMINS | ⭕ | - | List of admin IDs (e.g., 123456789,987654321) |
| BOT_DEV_ID | 🔴 | - | ID of the bot developer |
| BOT_SUPPORT_ID | 🔴 | - | ID of the support person |
| BOT_DOMAIN | 🔴 | - | Domain of the bot (e.g., 3xui-shop.com) |
| BOT_PORT | ⭕ | 8080 | Port of the bot |
| | | |
| SHOP_EMAIL | ⭕ | support@3xui-shop.com | Email for receipts |
| SHOP_CURRENCY | ⭕ | RUB | Currency for buttons (e.g., RUB, USD, XTR) |
| SHOP_TRIAL_ENABLED | ⭕ | True | Enable trial products for new users |
| SHOP_TRIAL_PERIOD | ⭕ | 3 | Duration of the trial access in days |
| SHOP_REFERRED_TRIAL_ENABLED | ⭕ | False | Enable extended trial period for referred users |
| SHOP_REFERRED_TRIAL_PERIOD | ⭕ | 7 | Duration of the extended trial for referred users (in days) |
| SHOP_REFERRER_REWARD_ENABLED | ⭕ | True | Enable the two-level referral reward system |
| SHOP_REFERRER_LEVEL_ONE_PERIOD | ⭕ | 10 | Reward in days for the first-level referrer (inviter) |
| SHOP_REFERRER_LEVEL_TWO_PERIOD | ⭕ | 3 | Reward in days for the second-level referrer (inviter of the inviter). |
| SHOP_BONUS_DEVICES_COUNT | ⭕ | 1 | Default bonus count for promocode and referral rewards |
| SHOP_PAYMENT_STARS_ENABLED | ⭕ | True | Enable Telegram stars payment |
| SHOP_PAYMENT_CRYPTOMUS_ENABLED | ⭕ | False | Enable Cryptomus payment |
| | | |
| PRODUCT_CATALOG_FILE | ⭕ | products.json | Path to product catalog file |
| PRODUCT_DEFAULT_CATEGORY | ⭕ | digital | Default product category |
| PRODUCT_DELIVERY_TIMEOUT | ⭕ | 3600 | Product delivery timeout in seconds |
| | | |
| CRYPTOMUS_API_KEY | ⭕ | - | API key for Cryptomus payment |
| CRYPTOMUS_MERCHANT_ID | ⭕ | - | Merchant ID for Cryptomus payment |
| | | |
| LOG_LEVEL | ⭕ | DEBUG | Log level (e.g., INFO, DEBUG) |
| LOG_FORMAT | ⭕ | %(asctime)s \| %(name)s \| %(levelname)s \| %(message)s | Log format |
| LOG_ARCHIVE_FORMAT | ⭕ | zip | Log archive format (e.g., zip, gz) |


### Product Catalog Configuration

```json
{
    "categories": [
        "software",     // Software licenses and applications
        "gaming",       // Game keys and gaming accounts  
        "subscription", // Streaming services and subscriptions
        "digital",      // Digital content and downloads
        "education"     // Educational courses and materials
    ],

    "products": [
        {
            "id": "microsoft_office_365",
            "name": "Microsoft Office 365 Personal",
            "description": "Complete Microsoft Office suite with 1TB OneDrive storage",
            "category": "software",
            "price": {
                "amount": 999,
                "currency": "RUB"
            },
            "duration_days": 365,
            "delivery_type": "license_key",
            "delivery_template": "🔑 Your Microsoft Office 365 license: {license_key}",
            "key_format": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "stock": -1,  // -1 for unlimited stock
            "is_active": true
        },
        {
            "id": "steam_random_key",
            "name": "Steam Random Game Key",
            "description": "Random Steam game key - Premium games guaranteed",
            "category": "gaming", 
            "price": {
                "amount": 299,
                "currency": "RUB"
            },
            "duration_days": 0,  // Permanent
            "delivery_type": "license_key",
            "delivery_template": "🎮 Your Steam key: {license_key}",
            "key_format": "XXXXX-XXXXX-XXXXX",
            "stock": 100,
            "is_active": true
        }
    ]
}
```

### 3X-UI Configuration

To ensure the bot functions correctly, you must configure the 3X-UI panel:

- [Set up SSL certificate.](https://github.com/MHSanaei/3x-ui?tab=readme-ov-file#ssl-certificate)
- Set up an Inbound **(the first one will be used)** for adding clients.
- Enable the subscription service with port `2096` and path `/user/`.
    > **Don't forget to specify certificate for the subscription.**
- Disabling configuration encryption is recommended.

<a id="bugs-and-feature-requests"></a>

### Referral and Trial Rewards Configuration
```

### YooKassa Configuration

1. **Webhook Setup:**
    - Visit the [HTTP Notifications](https://yookassa.ru/my/merchant/integration/http-notifications) page.
    - Enter the bot’s domain in the notification URL, ending with `/yookassa` (e.g., `https://3xui-shop.com/yookassa`).
    - Select the following events:
        <a id="bugs-and-feature-requests"></a>

### Referral and Trial Rewards Configuration

Bot now supports **trial subscriptions** and a **two-level referral reward system**. Here's how it works:

### YooMoney Configuration

1. **Webhook Setup:**
    - Visit the [HTTP Notifications](https://yoomoney.ru/transfer/myservices/http-notification) page.
    - Enter the bot’s domain in the notification URL, ending with `/yoomoney` (e.g., `https://3xui-shop.com/yoomoney`).
    - Copy the notification secret key.
    - Check the box for `sending HTTP-notifications`.
    - Save the changes.

2. **Environment Variables Setup:**
    - Set the following environment variables:
        - `YOOMONEY_WALLET_ID`: Your wallet ID
        - `YOOMONEY_NOTIFICATION_SECRET`: Your notification secret key

### 3X-UI Configuration

To ensure the bot functions correctly, you must configure the 3X-UI panel:

- [Set up SSL certificate.](https://github.com/MHSanaei/3x-ui?tab=readme-ov-file#ssl-certificate)
- Set up an Inbound **(the first one will be used)** for adding clients.
- Enable the subscription service with port `2096` and path `/user/`.
    > **Don’t forget to specify certificate for the subscription.**
- Disabling configuration encryption is recommended.

<a id="bugs-and-feature-requests"></a>

### Referral and Trial Rewards Configuration

Bot now supports **trial subscriptions** and a **two-level referral reward system**. Here’s how it works:
All configuration is available via `.env` [(see it above)](#environment-variables-configuration).

| Type of reward | How it works |
| - | - |
| Trial period | A trial subscription is available by 'TRY FOR FREE' button at start menu to any user who opens the bot and does not have an active subscription. |
| Extended Trial period | This option is just like previous 'trial period', but allows to configure **extended trial period** for an invited user. |
| Two-Level Referral Payment Rewards | When a referred user pays for a subscription, the referrer and the second-level referrer (the user who invited the referrer) receive fixed count of days at the moment fore each level. |

## 🐛 Bugs and Feature Requests

If you find a bug or have a feature request, please open an issue on the GitHub repository.
You're also welcome to contribute to the project by opening a pull request.

<a id="support-the-project"></a>

## 💸 Support the Project

A special thanks to the following individuals for their generous support:

- **Boto**
- [**@olshevskii-sergey**](https://github.com/olshevskii-sergey/)
- **Aleksey**
- [**@DmitryKryloff**](https://t.me/DmitryKryloff)

You can support me via the following methods ([or RUB](https://t.me/shop_3xui/2/1580)):

- **Bitcoin:** `bc1ql53lcaukdv3thxcheh3cmgucwlwkr929gar0cy`
- **Ethereum:** `0xe604a10258d26c085ada79cdea9a84a5b0894b91`
- **USDT (TRC20):** `TUqDQ4mdtVJZC76789kPYBMzaLFQBDdKhE`
- **TON:** `UQDogBlLFgrxkVWvDJn6YniCwrJDro7hbk5AqDMoSzmBQ-KQ`

Any support will help me dedicate more time to development and accelerate the project!
