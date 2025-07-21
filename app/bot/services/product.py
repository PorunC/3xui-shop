from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Config
from app.db.models import User, Transaction
from app.bot.models.plan import Plan
from app.bot.models.product_data import ProductSubscriptionData, ProductPlan

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
        self.products_file = Path(self.config.product.PRODUCTS_FILE)
        self.delivery_timeout = self.config.product.DELIVERY_TIMEOUT
        
        # In-memory storage for user subscriptions (replace with DB in production)
        self._user_subscriptions: Dict[int, Dict] = {}
        
        logger.info("Product Service initialized")

    async def load_products_catalog(self) -> List[Dict[str, Any]]:
        """Load products from the catalog file."""
        try:
            if self.products_file.exists():
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    catalog = json.load(f)
                    products = catalog.get('products', [])
                    logger.info(f"Loaded {len(products)} products from catalog")
                    return products
            else:
                logger.warning(f"Products catalog not found at {self.products_file}")
                return []
        except Exception as e:
            logger.error(f"Failed to load products catalog: {e}")
            return []

    async def get_product_by_plan(self, plan: Plan) -> Optional[Dict[str, Any]]:
        """Find a product that matches the given plan."""
        products = await self.load_products_catalog()
        
        for product in products:
            # Match by price and duration if available
            if (product.get('price', {}).get('amount') == plan.price and 
                product.get('duration_days', plan.duration_days) == plan.duration_days):
                return product
                
        # Fallback: return default digital product
        return {
            'id': str(uuid.uuid4()),
            'name': plan.title,
            'category': self.default_category,
            'price': {'amount': plan.price, 'currency': 'RUB'},
            'duration_days': plan.duration_days,
            'delivery_type': 'digital',
            'description': f'Digital product: {plan.title}',
            'features': [f'{plan.duration_days} days access', f'{plan.traffic_gb}GB allowance']
        }

    async def create_subscription(
        self, user_id: int, plan: Plan, transaction_id: int
    ) -> ProductSubscriptionData:
        """Create a subscription for digital product access."""
        async with self.session_factory() as session:
            user = await User.get(session, user_id)
            
            # Find matching product
            product = await self.get_product_by_plan(plan)
            
            current_time = datetime.now(timezone.utc)
            
            subscription_data = ProductSubscriptionData(
                start_date=current_time,
                expire_date=current_time + timedelta(days=plan.duration_days),
                traffic_limit=plan.traffic_gb,
                is_trial=False,
                product_id=product['id'],
                product_name=product['name']
            )

            # Deliver the product
            delivery_result = await self._deliver_product(user, product, subscription_data, transaction_id)

            if delivery_result['success']:
                # Store subscription info
                self._user_subscriptions[user.tg_id] = {
                    'user_id': user.tg_id,
                    'product': product,
                    'subscription_data': subscription_data,
                    'delivery_info': delivery_result['delivery_info'],
                    'created_at': current_time.isoformat(),
                    'transaction_id': transaction_id
                }
                
                logger.info(
                    "Product subscription created for user %s - Product: %s - Expires: %s",
                    user.tg_id,
                    product['name'],
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
            
            # Create a gift product
            gift_product = {
                'id': f'gift-{uuid.uuid4()}',
                'name': f'{duration} Days Gift Access',
                'category': self.default_category,
                'duration_days': duration,
                'delivery_type': 'digital',
                'description': f'Gift access for {duration} days',
                'features': [f'{duration} days access', f'{devices} device(s)']
            }
            
            current_time = datetime.now(timezone.utc)
            expiry = current_time + timedelta(days=duration)
            
            # Create subscription data for the gift
            subscription_data = ProductSubscriptionData(
                start_date=current_time,
                expire_date=expiry,
                traffic_limit=0,  # No traffic limit for gifts
                is_trial=True,
                product_id=gift_product['id'],
                product_name=gift_product['name']
            )
            
            # Deliver the gift product
            delivery_result = await self._deliver_product(user, gift_product, subscription_data, None)
            
            if delivery_result['success']:
                # Store gift subscription
                self._user_subscriptions[user.tg_id] = {
                    'user_id': user.tg_id,
                    'product': gift_product,
                    'subscription_data': subscription_data,
                    'delivery_info': delivery_result['delivery_info'],
                    'created_at': current_time.isoformat(),
                    'is_gift': True
                }
                
                logger.info(f"Product gifted successfully to user {user.tg_id}")
                return True
            else:
                logger.error(f"Failed to deliver gift to user {user.tg_id}")
                return False
            
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
            
            current_time = datetime.now(timezone.utc)
            
            # Check if user has existing subscription
            existing_subscription = self._user_subscriptions.get(user.tg_id)
            
            if existing_subscription:
                # Extend existing subscription
                old_expiry = datetime.fromisoformat(
                    existing_subscription['subscription_data'].expire_date.isoformat()
                )
                new_expiry = old_expiry + timedelta(days=duration)
                
                # Update the subscription
                existing_subscription['subscription_data'].expire_date = new_expiry
                existing_subscription['bonus_days_added'] = existing_subscription.get('bonus_days_added', 0) + duration
                existing_subscription['last_bonus_at'] = current_time.isoformat()
                
                logger.info(f"Extended subscription for user {user.tg_id} by {duration} days until {new_expiry}")
            else:
                # Create new bonus subscription
                bonus_product = {
                    'id': f'bonus-{uuid.uuid4()}',
                    'name': f'{duration} Days Bonus Access',
                    'category': self.default_category,
                    'duration_days': duration,
                    'delivery_type': 'digital',
                    'description': f'Bonus access for {duration} days',
                    'features': [f'{duration} days bonus access', f'{devices} device(s)']
                }
                
                bonus_expiry = current_time + timedelta(days=duration)
                subscription_data = ProductSubscriptionData(
                    start_date=current_time,
                    expire_date=bonus_expiry,
                    traffic_limit=0,
                    is_trial=True,
                    product_id=bonus_product['id'],
                    product_name=bonus_product['name']
                )
                
                delivery_result = await self._deliver_product(user, bonus_product, subscription_data, None)
                
                if delivery_result['success']:
                    self._user_subscriptions[user.tg_id] = {
                        'user_id': user.tg_id,
                        'product': bonus_product,
                        'subscription_data': subscription_data,
                        'delivery_info': delivery_result['delivery_info'],
                        'created_at': current_time.isoformat(),
                        'is_bonus': True,
                        'bonus_days_added': duration
                    }
            
            logger.info(f"Bonus days processed successfully for user {user.tg_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process bonus days for user {user.tg_id}: {e}")
            return False

    async def get_user_subscription_info(self, user: User) -> Optional[Dict]:
        """Get user's current product subscription information."""
        try:
            subscription = self._user_subscriptions.get(user.tg_id)
            
            if subscription:
                current_time = datetime.now(timezone.utc)
                expiry_time = subscription['subscription_data'].expire_date
                
                # Check if subscription is still active
                is_active = current_time < expiry_time
                days_remaining = (expiry_time - current_time).days if is_active else 0
                
                subscription_info = {
                    'user_id': user.tg_id,
                    'product_name': subscription['product']['name'],
                    'category': subscription['product']['category'],
                    'status': 'active' if is_active else 'expired',
                    'expires_at': expiry_time.isoformat(),
                    'days_remaining': max(0, days_remaining),
                    'created_at': subscription['created_at'],
                    'is_gift': subscription.get('is_gift', False),
                    'is_bonus': subscription.get('is_bonus', False),
                    'bonus_days_added': subscription.get('bonus_days_added', 0),
                    'delivery_info': subscription.get('delivery_info', {})
                }
                
                return subscription_info
            else:
                # No active subscription
                return {
                    'user_id': user.tg_id,
                    'status': 'none',
                    'message': 'No active product subscription found'
                }
            
        except Exception as e:
            logger.error(f"Failed to get subscription info for user {user.tg_id}: {e}")
            return None

    async def get_available_categories(self) -> List[str]:
        """Get list of available product categories."""
        return self.product_categories

    async def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all products in a specific category."""
        products = await self.load_products_catalog()
        return [p for p in products if p.get('category', '').lower() == category.lower()]

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search products by name or description."""
        products = await self.load_products_catalog()
        query_lower = query.lower()
        
        results = []
        for product in products:
            if (query_lower in product.get('name', '').lower() or 
                query_lower in product.get('description', '').lower()):
                results.append(product)
        
        return results

    async def _generate_product_key(self, product: Dict[str, Any]) -> str:
        """Generate a unique product key/license."""
        delivery_type = product.get('delivery_type', 'digital')
        
        if delivery_type == 'license_key':
            # Generate a license key format
            key_format = product.get('delivery_config', {}).get('key_format', 'XXXX-XXXX-XXXX')
            # Replace X with random chars/numbers
            import random
            import string
            
            key = ""
            for char in key_format:
                if char == 'X':
                    key += random.choice(string.ascii_uppercase + string.digits)
                else:
                    key += char
            return key
        else:
            # Generate a unique access token
            return f"ACCESS-{uuid.uuid4().hex[:12].upper()}"

    async def _deliver_product(
        self, user: User, product: Dict[str, Any], subscription_data: ProductSubscriptionData, transaction_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Internal method to handle product delivery."""
        try:
            current_time = datetime.now(timezone.utc)
            delivery_type = product.get('delivery_type', 'digital')
            
            # Generate delivery information based on product type
            delivery_info = {
                'delivery_id': str(uuid.uuid4()),
                'user_id': user.tg_id,
                'product_id': product['id'],
                'product_name': product['name'],
                'delivery_type': delivery_type,
                'delivered_at': current_time.isoformat(),
                'expires_at': subscription_data.expire_date.isoformat(),
                'transaction_id': transaction_id
            }
            
            # Generate specific delivery content based on type
            if delivery_type == 'license_key':
                delivery_info['license_key'] = await self._generate_product_key(product)
                delivery_info['activation_instructions'] = product.get('delivery_config', {}).get('template', '')
                
            elif delivery_type == 'account_info':
                # Generate account credentials (placeholder)
                delivery_info['account_username'] = f"user_{user.tg_id}_{current_time.timestamp():.0f}"
                delivery_info['account_password'] = f"pwd_{uuid.uuid4().hex[:8]}"
                delivery_info['login_url'] = product.get('delivery_config', {}).get('login_url', 'https://example.com/login')
                
            elif delivery_type == 'download_link':
                # Generate download link
                delivery_info['download_url'] = f"https://download.example.com/{product['id']}/{uuid.uuid4().hex}"
                delivery_info['download_expires'] = (current_time + timedelta(seconds=self.delivery_timeout)).isoformat()
                
            elif delivery_type == 'api':
                # Generate API access
                delivery_info['api_key'] = f"api_{uuid.uuid4().hex}"
                delivery_info['api_endpoint'] = product.get('delivery_config', {}).get('endpoint', 'https://api.example.com')
                
            else:
                # Default digital delivery
                delivery_info['access_token'] = await self._generate_product_key(product)
                delivery_info['access_instructions'] = f"Your {product['name']} is now active until {subscription_data.expire_date.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            # Log successful delivery
            logger.info(f"Product delivered successfully: {delivery_info['delivery_id']} to user {user.tg_id}")
            
            return {
                'success': True,
                'delivery_info': delivery_info
            }
            
        except Exception as e:
            logger.error(f"Product delivery failed for user {user.tg_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
