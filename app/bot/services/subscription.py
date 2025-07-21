from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Config
from app.db.models import Referral, User, Transaction
from app.bot.models.plan import Plan
from app.bot.models.subscription_data import SubscriptionData

if TYPE_CHECKING:
    from app.bot.services.product import ProductService

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(
        self,
        config: Config,
        session_factory: async_sessionmaker,
        product_service: "ProductService" = None,
    ) -> None:
        self.config = config
        self.session_factory = session_factory
        self.product_service = product_service
        logger.info("Subscription Service initialized")

    async def is_trial_available(self, user: User) -> bool:
        is_first_check_ok = (
            self.config.shop.TRIAL_ENABLED and not user.is_trial_used
        )

        if not is_first_check_ok:
            return False

        async with self.session_factory() as session:
            referral = await Referral.get_referral(session, user.tg_id)

        return not referral or (referral and not self.config.shop.REFERRED_TRIAL_ENABLED)

    async def gift_trial(self, user: User) -> bool:
        if not await self.is_trial_available(user=user):
            logger.warning(
                f"Failed to activate trial for user {user.tg_id}. Trial period is not available."
            )
            return False

        async with self.session_factory() as session:
            trial_used = await User.update_trial_status(
                session=session, tg_id=user.tg_id, used=True
            )

        if not trial_used:
            logger.critical(f"Failed to activate trial for user {user.tg_id}.")
            return False

        logger.info(f"Begun giving trial period for user {user.tg_id}.")
        
        # Use product service if available, otherwise use placeholder logic
        if self.product_service:
            trial_success = await self.product_service.gift_product(
                user,
                duration=self.config.shop.TRIAL_PERIOD,
                devices=self.config.shop.BONUS_DEVICES_COUNT,
            )
        else:
            # TODO: Replace with product service logic when available
            trial_success = True  # Temporary: Always return success

        if trial_success:
            logger.info(
                f"Successfully gave {self.config.shop.TRIAL_PERIOD} days to a user {user.tg_id}"
            )
            return True

        async with self.session_factory() as session:
            await User.update_trial_status(session=session, tg_id=user.tg_id, used=False)

        logger.warning(f"Failed to apply trial period for user {user.tg_id} due to failure.")
        return False

    async def create_subscription(
        self, user_id: int, plan: Plan, transaction_id: int
    ) -> SubscriptionData:
        """Create a subscription using the product service."""
        if self.product_service:
            return await self.product_service.create_subscription(user_id, plan, transaction_id)
        
        # Fallback logic if product service not available
        async with self.session_factory() as session:
            user = await User.get(session, user_id)
            
            current_time = datetime.now(timezone.utc)
            
            subscription_data = SubscriptionData(
                start_date=current_time,
                expire_date=current_time + timedelta(days=plan.duration_days),
                traffic_limit=plan.traffic_gb,
                is_trial=False
            )

            # Update user status and transaction
            await self.__update_user_after_successful_subscription(
                session, user, subscription_data, transaction_id
            )
            await session.commit()

            logger.info(
                "Subscription created for user %s - Plan: %s - Expires: %s",
                user.tg_id,
                plan.title,
                subscription_data.expire_date,
            )

            return subscription_data

    async def __update_user_after_successful_subscription(
        self, session, user: User, subscription_data: SubscriptionData, transaction_id: int
    ) -> None:
        """Update user and transaction after successful subscription."""
        # Update transaction status
        await Transaction.update(session, transaction_id, status="completed")
        
        # Update user subscription info
        await User.update(
            session, 
            user.id,
            is_trial_used=True if subscription_data.is_trial else user.is_trial_used
        )
        
        logger.info(f"Updated user {user.tg_id} after successful subscription")

    async def get_user_subscription_status(self, user: User) -> Optional[Dict]:
        """Get user's current subscription status using ProductService."""
        if self.product_service:
            return await self.product_service.get_user_subscription_info(user)
        else:
            # Fallback if no product service
            return {
                'user_id': user.tg_id,
                'status': 'unknown',
                'message': 'Product service not available'
            }
