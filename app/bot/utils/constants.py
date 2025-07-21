# region: Product Categories
PRODUCT_CATEGORIES = ["software", "gaming", "subscription", "digital", "education"]

# endregion

# region: Order Status
ORDER_STATUSES = ["pending", "paid", "delivered", "failed", "refunded", "cancelled"]

# endregion

# region: Delivery Types  
DELIVERY_TYPES = ["digital", "license_key", "account_info", "download_link", "manual", "api"]

# endregion

# region: App Schemes and Links (for download)
APP_ANDROID_SCHEME = "https://play.google.com/store/apps/details?id=com.example.app"
APP_ANDROID_LINK = "https://play.google.com/store/apps/details?id=com.example.app"
APP_IOS_SCHEME = "https://apps.apple.com/app/example-app/id123456789"
APP_IOS_LINK = "https://apps.apple.com/app/example-app/id123456789"
APP_WINDOWS_SCHEME = "https://www.microsoft.com/store/apps/example-app"
APP_WINDOWS_LINK = "https://www.microsoft.com/store/apps/example-app"

# Connection webhook for product setup
CONNECTION_WEBHOOK = "https://example.com/api/product/setup"

# endregion

# region: Keys
MAIN_MESSAGE_ID_KEY = "main_message_id"
PREVIOUS_CALLBACK_KEY = "previous_callback"

INPUT_PROMOCODE_KEY = "input_promocode"

PRODUCT_NAME_KEY = "product_name"
PRODUCT_CATEGORY_KEY = "product_category"
PRODUCT_PRICE_KEY = "product_price"

# Server management keys (legacy - for admin tools)
SERVER_HOST_KEY = "server_host"
SERVER_NAME_KEY = "server_name"
SERVER_PORT_KEY = "server_port"
SERVER_MAX_CLIENTS_KEY = "server_max_clients"

NOTIFICATION_CHAT_IDS_KEY = "notification_chat_ids"
NOTIFICATION_LAST_MESSAGE_IDS_KEY = "notification_last_message_ids"
NOTIFICATION_MESSAGE_TEXT_KEY = "notification_message_text"
NOTIFICATION_PRE_MESSAGE_TEXT_KEY = "notification_pre_message_text"
# endregion

# region: Webhook paths
TELEGRAM_WEBHOOK = "/webhook"  # Webhook path for Telegram bot updates
CONNECTION_WEBHOOK = "/connection"  # Webhook path for receiving connection requests
CRYPTOMUS_WEBHOOK = "/cryptomus"  # Webhook path for receiving Cryptomus payment notifications
# endregion

# region: Notification tags
BOT_STARTED_TAG = "#BotStarted"
BOT_STOPPED_TAG = "#BotStopped"
BACKUP_CREATED_TAG = "#BackupCreated"
EVENT_PAYMENT_SUCCEEDED_TAG = "#EventPaymentSucceeded"
EVENT_PAYMENT_CANCELED_TAG = "#EventPaymentCanceled"
# endregion

# region: I18n settings
DEFAULT_LANGUAGE = "en"
I18N_DOMAIN = "bot"
# endregion

# region: Constants
UNLIMITED = "∞"
DB_FORMAT = "sqlite3"
LOG_ZIP_ARCHIVE_FORMAT = "zip"
LOG_GZ_ARCHIVE_FORMAT = "gz"
MESSAGE_EFFECT_IDS = {
    "🔥": "5104841245755180586",
    "👍": "5107584321108051014",
    "👎": "5104858069142078462",
    "❤️": "5044134455711629726",
    "🎉": "5046509860389126442",
    "💩": "5046589136895476101",
}
# endregion

# region: Enums
from enum import Enum
from typing import Any, Optional


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Currency(Enum):
    RUB = ("RUB", "₽")
    USD = ("USD", "$")
    XTR = ("XTR", "★")

    @property
    def symbol(self) -> str:
        return self.value[1]

    @property
    def code(self) -> str:
        return self.value[0]

    @classmethod
    def from_code(cls, code: str) -> "Currency":
        code = code.upper()
        for currency in cls:
            if currency.code == code:
                return currency
        raise ValueError(f"Invalid currency code: {code}")


class ReferrerRewardType(Enum):
    DAYS = "days"
    MONEY = "money"  # TODO: consider using currencies instead? depends on balance implementation

    @classmethod
    def from_str(cls, value: str) -> Optional["ReferrerRewardType"]:
        try:
            return cls[value.upper()]
        except KeyError:
            try:
                return cls(value.lower())
            except ValueError:
                return None


class ReferrerRewardLevel(Enum):
    FIRST_LEVEL = 1
    SECOND_LEVEL = 2

    @classmethod
    def from_value(cls, value: Any) -> Optional["ReferrerRewardLevel"]:
        try:
            return cls(int(value))
        except (ValueError, KeyError):
            return None


# endregion
