from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Config
from app.db.models import User, Transaction
from app.bot.models.plan import Plan
from app.bot.models.subscription_data import SubscriptionData

logger = logging.getLogger(__name__)


class ProductService:
    """
    Digital product service for managing digital goods delivery.
    Replaces VPN-specific functionality with general product management.
    """
    
    def __init__(
        self,
        config: Config,
        session_factory: async_sessionmaker,
    ) -> None:
        self.config = config
        self.session_factory = session_factory
        self.product_categories = self.config.product.PRODUCT_CATEGORIES
        self.default_category = self.config.product.DEFAULT_CATEGORY
        logger.info("Product Service initialized")

    async def create_subscription(
        self, user_id: int, plan: Plan, transaction_id: int
    ) -> SubscriptionData:
        """Create a subscription for digital product access."""
        async with self.session_factory() as session:
            user = await User.get(session, user_id)
            
            current_time = datetime.now(timezone.utc)
            
            subscription_data = SubscriptionData(
                start_date=current_time,
                expire_date=current_time + timedelta(days=plan.duration_days),
                traffic_limit=plan.traffic_gb,
                is_trial=False
            )

            # Simulate product delivery
            success = await self._deliver_product(user, plan, subscription_data)

            if success:
                logger.info(
                    "Product subscription created for user %s - Plan: %s - Expires: %s",
                    user.tg_id,
                    plan.title,
                    subscription_data.expire_date,
                )
                return subscription_data
            else:
                logger.error("Product delivery failed for user %s", user.tg_id)
                raise Exception("Product delivery failed")

    async def gift_product(
        self, user: User, duration: int, devices: int = 1
    ) -> bool:
        """Gift a product access for specified duration."""
        try:
            logger.info(
                f"Gifting product access to user {user.tg_id} for {duration} days with {devices} devices"
            )
            
            # TODO: Implement actual product delivery logic
            # For now, simulate successful delivery
            current_time = datetime.now(timezone.utc)
            expiry = current_time + timedelta(days=duration)
            
            # Store product access info (placeholder logic)
            product_info = {
                'user_id': user.tg_id,
                'granted_at': current_time.isoformat(),
                'expires_at': expiry.isoformat(),
                'devices_count': devices,
                'category': self.default_category
            }
            
            logger.info(f"Product gifted successfully: {product_info}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to gift product to user {user.tg_id}: {e}")
            return False

    async def process_bonus_days(
        self, user: User, duration: int, devices: int = 1
    ) -> bool:
        """Process bonus days for existing product subscription."""
        try:
            logger.info(
                f"Processing {duration} bonus days for user {user.tg_id} with {devices} devices"
            )
            
            # TODO: Implement actual bonus processing logic
            # For now, simulate successful processing
            current_time = datetime.now(timezone.utc)
            bonus_expiry = current_time + timedelta(days=duration)
            
            bonus_info = {
                'user_id': user.tg_id,
                'bonus_days': duration,
                'devices_count': devices,
                'processed_at': current_time.isoformat(),
                'expires_at': bonus_expiry.isoformat()
            }
            
            logger.info(f"Bonus days processed successfully: {bonus_info}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process bonus days for user {user.tg_id}: {e}")
            return False

    async def get_user_subscription_info(self, user: User) -> Optional[Dict]:
        """Get user's current product subscription information."""
        try:
            # TODO: Implement actual subscription lookup
            # For now, return placeholder info
            subscription_info = {
                'user_id': user.tg_id,
                'status': 'active',
                'category': self.default_category,
                'expires_at': None,  # Will be set based on actual data
                'devices_count': 1
            }
            
            return subscription_info
            
        except Exception as e:
            logger.error(f"Failed to get subscription info for user {user.tg_id}: {e}")
            return None

    async def get_available_categories(self) -> List[str]:
        """Get list of available product categories."""
        return self.product_categories

    async def _deliver_product(
        self, user: User, plan: Plan, subscription_data: SubscriptionData
    ) -> bool:
        """Internal method to handle product delivery."""
        try:
            # TODO: Implement actual product delivery mechanism
            # This could involve:
            # - Generating product keys/codes
            # - Creating access credentials
            # - Sending delivery notifications
            # - Recording delivery logs
            
            delivery_info = {
                'user_id': user.tg_id,
                'plan_title': plan.title,
                'duration_days': plan.duration_days,
                'traffic_gb': plan.traffic_gb,
                'delivered_at': subscription_data.start_date.isoformat(),
                'expires_at': subscription_data.expire_date.isoformat()
            }
            
            logger.info(f"Product delivered successfully: {delivery_info}")
            return True
            
        except Exception as e:
            logger.error(f"Product delivery failed for user {user.tg_id}: {e}")
            return False
