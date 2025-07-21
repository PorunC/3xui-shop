from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer
from app.config import Config

from .invite_stats import InviteStatsService
from .notification import NotificationService
from .payment_stats import PaymentStatsService
from .plan import PlanService
from .product import ProductService
from .referral import ReferralService
from .subscription import SubscriptionService


async def initialize(
    config: Config,
    session: async_sessionmaker,
    bot: Bot,
) -> ServicesContainer:
    plan = PlanService()
    product = ProductService(config=config, session_factory=session)
    notification = NotificationService(config=config, bot=bot)
    referral = ReferralService(config=config, session_factory=session, product_service=product)
    subscription = SubscriptionService(config=config, session_factory=session, product_service=product)
    payment_stats = PaymentStatsService(session_factory=session)
    invite_stats = InviteStatsService(session_factory=session, payment_stats_service=payment_stats)

    return ServicesContainer(
        plan=plan,
        product=product,
        notification=notification,
        referral=referral,
        subscription=subscription,
        payment_stats=payment_stats,
        invite_stats=invite_stats,
    )
