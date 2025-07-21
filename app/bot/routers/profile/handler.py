import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.models import ClientData
from app.bot.services import ServicesContainer
from app.bot.utils.constants import PREVIOUS_CALLBACK_KEY
from app.bot.utils.navigation import NavProfile
from app.db.models import User

from .keyboard import buy_subscription_keyboard, profile_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def prepare_message(user: User, client_data: ClientData | None) -> str:
    profile = _("profile:message:main").format(name=user.first_name, id=user.tg_id)

    if not client_data:
        subscription = _("profile:message:subscription_none")
        return profile + subscription

    subscription = _("profile:message:subscription").format(devices=client_data.max_devices)

    subscription += (
        _("profile:message:subscription_expiry_time").format(expiry_time=client_data.expiry_time)
        if not client_data.has_subscription_expired
        else _("profile:message:subscription_expired")
    )

    statistics = _("profile:message:statistics").format(
        total=client_data.traffic_used,
        up=client_data.traffic_up,
        down=client_data.traffic_down,
    )

    return profile + subscription + statistics


@router.callback_query(F.data == NavProfile.MAIN)
async def callback_profile(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
    state: FSMContext,
) -> None:
    logger.info(f"👤 User {user.tg_id} clicked profile button -> opening profile page")
    await state.update_data({PREVIOUS_CALLBACK_KEY: NavProfile.MAIN})

    # Get subscription info from ProductService
    subscription_info = await services.product.get_user_subscription_info(user)
    logger.debug(f"📊 Subscription info for user {user.tg_id}: {subscription_info}")
    
    # Create client_data equivalent from product service
    client_data = None
    if subscription_info and subscription_info.get('status') == 'active':
        client_data = type('ClientData', (), {
            'has_subscription_expired': subscription_info['status'] != 'active',
        })()
        logger.debug(f"✅ Active subscription found for user {user.tg_id}")
    else:
        logger.debug(f"❌ No active subscription for user {user.tg_id}")

    reply_markup = (
        profile_keyboard()
        if client_data and not client_data.has_subscription_expired
        else buy_subscription_keyboard()
    )
    
    profile_text = await prepare_message(user=user, client_data=client_data)
    logger.debug(f"📝 Profile text prepared for user {user.tg_id}")
    
    await callback.message.edit_text(
        text=profile_text,
        reply_markup=reply_markup,
    )
    logger.debug(f"✅ Profile page displayed for user {user.tg_id}")


@router.callback_query(F.data == NavProfile.SHOW_KEY)
async def callback_show_key(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} looked key.")
    
    # Get product access key from subscription info
    subscription_info = await services.product.get_user_subscription_info(user)
    
    if subscription_info and subscription_info.get('status') == 'active':
        # Get delivery info which contains the access key/license
        delivery_info = subscription_info.get('delivery_info', {})
        key = (delivery_info.get('license_key') or 
               delivery_info.get('access_token') or 
               delivery_info.get('api_key') or 
               f"DIGITAL-{user.tg_id}")  # Fallback key format
    else:
        key = "No active subscription"
    
    key_text = _("profile:message:key")
    message = await callback.message.answer(key_text.format(key=key, seconds_text=_("10 seconds")))

    for seconds in range(9, 0, -1):
        seconds_text = _("1 second", "{} seconds", seconds).format(seconds)
        await asyncio.sleep(1)
        await message.edit_text(text=key_text.format(key=key, seconds_text=seconds_text))
    await message.delete()


@router.callback_query(F.data == NavProfile.SHOW_ORDERS)
async def callback_show_orders(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
) -> None:
    """Show user's order history."""
    logger.info(f"User {user.tg_id} requested order history.")
    
    # Get user's subscription info (acts as order history for now)
    subscription_info = await services.product.get_user_subscription_info(user)
    
    if subscription_info and subscription_info.get('status') in ['active', 'expired']:
        text = _("profile:message:orders").format(
            product_name=subscription_info['product_name'],
            status=subscription_info['status'],
            expires_at=subscription_info.get('expires_at', 'N/A'),
            days_remaining=subscription_info.get('days_remaining', 0)
        )
    else:
        text = _("profile:message:no_orders")
    
    from .keyboard import profile_keyboard
    await callback.message.edit_text(
        text=text,
        reply_markup=profile_keyboard(),
    )


@router.callback_query(F.data == NavProfile.SHOW_PURCHASED_PRODUCTS)
async def callback_show_purchased_products(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
) -> None:
    """Show user's purchased products."""
    logger.info(f"User {user.tg_id} requested purchased products.")
    
    subscription_info = await services.product.get_user_subscription_info(user)
    
    if subscription_info and subscription_info.get('status') == 'active':
        delivery_info = subscription_info.get('delivery_info', {})
        product_info = f"""
📦 **{subscription_info['product_name']}**
📅 到期时间: {subscription_info.get('expires_at', 'N/A')}
⏰ 剩余天数: {subscription_info.get('days_remaining', 0)} 天

🔑 访问信息:
"""
        if delivery_info.get('license_key'):
            product_info += f"许可证密钥: `{delivery_info['license_key']}`\n"
        if delivery_info.get('access_token'):
            product_info += f"访问令牌: `{delivery_info['access_token']}`\n"
        if delivery_info.get('api_key'):
            product_info += f"API密钥: `{delivery_info['api_key']}`\n"
            
        text = product_info
    else:
        text = _("profile:message:no_purchased_products")
    
    from .keyboard import profile_keyboard
    await callback.message.edit_text(
        text=text,
        reply_markup=profile_keyboard(),
    )
