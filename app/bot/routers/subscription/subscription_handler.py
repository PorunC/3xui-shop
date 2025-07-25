import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.models import ClientData, ServicesContainer, SubscriptionData
from app.bot.payment_gateways import GatewayFactory
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import User

from .keyboard import (
    devices_keyboard,
    duration_keyboard,
    payment_method_keyboard,
    subscription_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_subscription(
    callback: CallbackQuery,
    client_data: ClientData | None,
    callback_data: SubscriptionData,
) -> None:
    if client_data:

        if client_data.has_subscription_expired:
            text = _("subscription:message:expired")
        else:
            text = _("subscription:message:active").format(
                devices=client_data.max_devices,
                expiry_time=client_data.expiry_time,
            )
    else:
        text = _("subscription:message:not_active")

    await callback.message.edit_text(
        text=text,
        reply_markup=subscription_keyboard(
            has_subscription=client_data,
            callback_data=callback_data,
        ),
    )


@router.callback_query(F.data == NavSubscription.MAIN)
async def callback_subscription(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} opened subscription page.")
    await state.set_state(None)

    # Get user's current subscription status using ProductService
    subscription_info = await services.product.get_user_subscription_info(user)
    
    # Create client_data equivalent from product service
    client_data = None
    if subscription_info and subscription_info.get('status') == 'active':
        # Mock ClientData structure for compatibility
        client_data = type('ClientData', (), {
            'has_subscription_expired': subscription_info['status'] != 'active',
            'max_devices': 1,  # Default devices for digital products
            'expiry_time': subscription_info.get('expires_at', 'Unknown'),
        })()

    callback_data = SubscriptionData(state=NavSubscription.PROCESS, user_id=user.tg_id)
    await show_subscription(callback=callback, client_data=client_data, callback_data=callback_data)


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.EXTEND))
async def callback_subscription_extend(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started extend subscription.")
    
    # Get current subscription info from ProductService
    subscription_info = await services.product.get_user_subscription_info(user)
    
    # Default to 1 device for digital products
    current_devices = 1
    if subscription_info and subscription_info.get('status') == 'active':
        # For digital products, we typically use 1 device
        current_devices = 1
    
    if not services.plan.get_plan(current_devices):
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:error_fetching_plan"),
        )
        return

    callback_data.devices = current_devices
    callback_data.state = NavSubscription.DURATION
    callback_data.is_extend = True
    await callback.message.edit_text(
        text=_("subscription:message:duration"),
        reply_markup=duration_keyboard(
            plan_service=services.plan,
            callback_data=callback_data,
            currency=config.shop.CURRENCY,
        ),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.CHANGE))
async def callback_subscription_change(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started change subscription.")
    callback_data.state = NavSubscription.DEVICES
    callback_data.is_change = True
    await callback.message.edit_text(
        text=_("subscription:message:devices"),
        reply_markup=devices_keyboard(services.plan.get_all_plans(), callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.PROCESS))
async def callback_subscription_process(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    callback_data: SubscriptionData,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started subscription process.")
    
    # For digital products, we don't need server availability check
    # Digital products are always "available"
    logger.info(f"Processing digital product subscription for user {user.tg_id}")

    callback_data.state = NavSubscription.DEVICES
    await callback.message.edit_text(
        text=_("subscription:message:devices"),
        reply_markup=devices_keyboard(services.plan.get_all_plans(), callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DEVICES))
async def callback_devices_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} selected devices: {callback_data.devices}")
    callback_data.state = NavSubscription.DURATION
    await callback.message.edit_text(
        text=_("subscription:message:duration"),
        reply_markup=duration_keyboard(
            plan_service=services.plan,
            callback_data=callback_data,
            currency=config.shop.CURRENCY,
        ),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DURATION))
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
    gateway_factory: GatewayFactory,
) -> None:
    logger.info(f"User {user.tg_id} selected duration: {callback_data.duration}")
    callback_data.state = NavSubscription.PAY
    await callback.message.edit_text(
        text=_("subscription:message:payment_method"),
        reply_markup=payment_method_keyboard(
            plan=services.plan.get_plan(callback_data.devices),
            callback_data=callback_data,
            gateways=gateway_factory.get_gateways(),
        ),
    )
