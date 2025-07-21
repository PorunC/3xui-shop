"""
Product delivery handler for sending formatted product information to users.
"""
import logging
from typing import Dict, Any

from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.db.models import User

logger = logging.getLogger(__name__)


class ProductDeliveryHandler:
    """Handles product delivery notifications to users."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def send_product_delivery(
        self, 
        user: User, 
        product: Dict[str, Any], 
        delivery_info: Dict[str, Any]
    ) -> bool:
        """Send formatted product delivery message to user."""
        try:
            delivery_type = product.get('delivery_type', 'digital')
            
            # Get the formatted message from delivery info
            if 'formatted_message' in delivery_info:
                message_text = delivery_info['formatted_message']
            else:
                # Fallback to default message format
                message_text = self._create_default_message(product, delivery_info)
            
            # Add delivery metadata
            delivery_footer = self._create_delivery_footer(delivery_info)
            full_message = f"{message_text}\n\n{delivery_footer}"
            
            # Send the message
            await self.bot.send_message(
                chat_id=user.tg_id,
                text=full_message,
                parse_mode="HTML"
            )
            
            logger.info(f"Product delivery message sent to user {user.tg_id} for product {product['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send delivery message to user {user.tg_id}: {e}")
            return False
    
    def _create_default_message(self, product: Dict[str, Any], delivery_info: Dict[str, Any]) -> str:
        """Create a default delivery message if no template is provided."""
        delivery_type = product.get('delivery_type', 'digital')
        product_name = product['name']
        
        if delivery_type == 'license_key':
            return f"🔑 <b>Your {product_name} License:</b>\n\n<b>License Key:</b> <pre>{delivery_info.get('license_key', 'N/A')}</pre>"
        
        elif delivery_type == 'account_info':
            return f"👤 <b>Your {product_name} Account:</b>\n\n<b>Username:</b> {delivery_info.get('account_username', 'N/A')}\n<b>Password:</b> <pre>{delivery_info.get('account_password', 'N/A')}</pre>\n<b>Login URL:</b> {delivery_info.get('login_url', 'N/A')}"
        
        elif delivery_type == 'download_link':
            return f"📥 <b>Your {product_name} Download:</b>\n\n<b>Download Link:</b> {delivery_info.get('download_url', 'N/A')}\n<b>Expires:</b> {delivery_info.get('download_expires', 'N/A')}"
        
        else:
            return f"✅ <b>Your {product_name} is ready!</b>\n\n<b>Access Token:</b> <pre>{delivery_info.get('access_token', 'N/A')}</pre>"
    
    def _create_delivery_footer(self, delivery_info: Dict[str, Any]) -> str:
        """Create a footer with delivery metadata."""
        footer_parts = []
        
        footer_parts.append(f"📦 <b>Delivery ID:</b> <pre>{delivery_info.get('delivery_id', 'N/A')}</pre>")
        
        if 'delivered_at' in delivery_info:
            footer_parts.append(f"🕐 <b>Delivered:</b> {delivery_info['delivered_at']}")
        
        if 'expires_at' in delivery_info:
            footer_parts.append(f"⏰ <b>Expires:</b> {delivery_info['expires_at']}")
        
        footer_parts.append("💡 <b>Note:</b> Please save this information securely!")
        
        return "\n".join(footer_parts)
    
    async def send_purchase_receipt(
        self, 
        user: User, 
        product: Dict[str, Any], 
        transaction_info: Dict[str, Any]
    ) -> bool:
        """Send purchase receipt to user."""
        try:
            receipt_text = _("catalog:message:purchase_receipt").format(
                product_name=product['name'],
                price=product['price']['amount'],
                currency=product['price']['currency'],
                transaction_id=transaction_info.get('transaction_id', 'N/A'),
                purchase_date=transaction_info.get('created_at', 'N/A')
            )
            
            await self.bot.send_message(
                chat_id=user.tg_id,
                text=receipt_text,
                parse_mode="HTML"
            )
            
            logger.info(f"Purchase receipt sent to user {user.tg_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send purchase receipt to user {user.tg_id}: {e}")
            return False
    
    async def send_delivery_error(
        self, 
        user: User, 
        product: Dict[str, Any], 
        error_message: str
    ) -> bool:
        """Send delivery error notification to user."""
        try:
            error_text = _("catalog:message:delivery_error").format(
                product_name=product['name'],
                error=error_message
            )
            
            await self.bot.send_message(
                chat_id=user.tg_id,
                text=error_text,
                parse_mode="HTML"
            )
            
            logger.info(f"Delivery error notification sent to user {user.tg_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send delivery error notification to user {user.tg_id}: {e}")
            return False