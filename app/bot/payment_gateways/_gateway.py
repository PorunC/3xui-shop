import logging
from abc import ABC, abstractmethod

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiohttp.web import Application
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer, SubscriptionData
from app.bot.routers.main_menu.handler import redirect_to_main_menu
from app.bot.utils.constants import (
    DEFAULT_LANGUAGE,
    EVENT_PAYMENT_CANCELED_TAG,
    EVENT_PAYMENT_SUCCEEDED_TAG,
    Currency,
    TransactionStatus,
)
from app.bot.utils.formatting import format_device_count, format_subscription_period
from app.config import Config
from app.db.models import Transaction, User

logger = logging.getLogger(__name__)

from app.bot.models import SubscriptionData
from app.bot.utils.constants import Currency


class PaymentGateway(ABC):
    name: str
    currency: Currency
    callback: str

    def __init__(
        self,
        app: Application,
        config: Config,
        session: async_sessionmaker,
        storage: RedisStorage,
        bot: Bot,
        i18n: I18n,
        services: ServicesContainer,
    ) -> None:
        self.app = app
        self.config = config
        self.session = session
        self.storage = storage
        self.bot = bot
        self.i18n = i18n
        self.services = services

    @abstractmethod
    async def create_payment(self, data: SubscriptionData) -> str:
        pass

    @abstractmethod
    async def handle_payment_succeeded(self, payment_id: str) -> None:
        pass

    @abstractmethod
    async def handle_payment_canceled(self, payment_id: str) -> None:
        pass

    async def _on_payment_succeeded(self, payment_id: str) -> None:
        logger.info(f"Payment succeeded {payment_id}")

        async with self.session() as session:
            transaction = await Transaction.get_by_id(session=session, payment_id=payment_id)
            data = SubscriptionData.unpack(transaction.subscription)
            logger.debug(f"Subscription data unpacked: {data}")
            user = await User.get(session=session, tg_id=data.user_id)

            await Transaction.update(
                session=session,
                payment_id=payment_id,
                status=TransactionStatus.COMPLETED,
            )

        if self.config.shop.REFERRER_REWARD_ENABLED:
            await self.services.referral.add_referrers_rewards_on_payment(
                referred_tg_id=data.user_id,
                payment_amount=data.price,  # TODO: (!) add currency unified processing
                payment_id=payment_id,
            )

        await self.services.notification.notify_developer(
            text=EVENT_PAYMENT_SUCCEEDED_TAG
            + "\n\n"
            + _("payment:event:payment_succeeded").format(
                payment_id=payment_id,
                user_id=user.tg_id,
                devices=format_device_count(data.devices),
                duration=format_subscription_period(data.duration),
            ),
        )

        locale = user.language_code if user else DEFAULT_LANGUAGE
        with self.i18n.use_locale(locale):
            await redirect_to_main_menu(
                bot=self.bot,
                user=user,
                services=self.services,
                config=self.config,
                storage=self.storage,
            )

            if data.is_extend:
                await self.services.product.extend_user_subscription(
                    user=user,
                    devices=data.devices,
                    duration=data.duration,
                    data=data,
                )
                logger.info(f"Subscription extended for user {user.tg_id}")
                await self.services.notification.notify_extend_success(
                    user_id=user.tg_id,
                    data=data,
                )
            elif data.is_change:
                # TODO: Implement change subscription logic for products
                logger.info(f"Subscription change requested for user {user.tg_id} - Not implemented for product system")
                await self.services.notification.notify_change_success(
                    user_id=user.tg_id,
                    data=data,
                )
            else:
                # Create subscription using new product system
                plan = await self.services.plan.get_plan_by_duration_and_devices(
                    duration=data.duration,
                    devices=data.devices
                )
                
                subscription_data = await self.services.subscription.create_subscription(
                    user_id=user.id,
                    plan=plan,
                    transaction_id=transaction.id
                )
                
                logger.info(f"Subscription created for user {user.tg_id}")
                
                # Get product delivery key/info for notification
                product_key = getattr(subscription_data, 'delivery_info', {}).get('key', 'N/A')
                
                await self.services.notification.notify_purchase_success(
                    user_id=user.tg_id,
                    key=product_key,
                )

    async def _on_payment_canceled(self, payment_id: str) -> None:
        logger.info(f"Payment canceled {payment_id}")
        async with self.session() as session:
            transaction = await Transaction.get_by_id(session=session, payment_id=payment_id)
            data = SubscriptionData.unpack(transaction.subscription)

            await Transaction.update(
                session=session,
                payment_id=payment_id,
                status=TransactionStatus.CANCELED,
            )

        await self.services.notification.notify_developer(
            text=EVENT_PAYMENT_CANCELED_TAG
            + "\n\n"
            + _("payment:event:payment_canceled").format(
                payment_id=payment_id,
                user_id=data.user_id,
                devices=format_device_count(data.devices),
                duration=format_subscription_period(data.duration),
            ),
        )
