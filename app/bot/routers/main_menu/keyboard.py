import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.utils.navigation import (
    NavAdminTools,
    NavCatalog,
    NavProfile,
    NavReferral,
    NavSubscription,
    NavSupport,
)

logger = logging.getLogger(__name__)


def main_menu_keyboard(
    is_admin: bool = False,
    is_referral_available: bool = False,
    is_trial_available: bool = False,
    is_referred_trial_available: bool = False,
) -> InlineKeyboardMarkup:
    logger.debug(f"🔧 Generating main menu keyboard with params: admin={is_admin}, referral={is_referral_available}, trial={is_trial_available}, referred_trial={is_referred_trial_available}")
    
    builder = InlineKeyboardBuilder()

    if is_referred_trial_available:
        referred_trial_text = _("referral:button:get_referred_trial")
        logger.debug(f"🎁 Adding referred trial button: '{referred_trial_text}' -> {NavReferral.GET_REFERRED_TRIAL}")
        builder.row(
            InlineKeyboardButton(
                text=referred_trial_text,
                callback_data=NavReferral.GET_REFERRED_TRIAL,
            )
        )
    elif is_trial_available:
        trial_text = _("subscription:button:get_trial")
        logger.debug(f"🎁 Adding trial button: '{trial_text}' -> {NavSubscription.GET_TRIAL}")
        builder.row(
            InlineKeyboardButton(
                text=trial_text, callback_data=NavSubscription.GET_TRIAL
            )
        )

    # Core buttons - Profile and Subscription  
    logger.debug("🔤 Translating core button texts...")
    profile_text = _("main_menu:button:profile")
    subscription_text = _("main_menu:button:subscription")
    logger.debug(f"👤 Profile button: '{profile_text}' -> {NavProfile.MAIN}")
    logger.debug(f"� Subscription button: '{subscription_text}' -> {NavSubscription.MAIN}")
    
    builder.row(
        InlineKeyboardButton(
            text=profile_text,
            callback_data=NavProfile.MAIN,
        ),
        InlineKeyboardButton(
            text=subscription_text,
            callback_data=NavSubscription.MAIN,
        ),
    )
    # Third row - Catalog, Referral and Support
    logger.debug("🔤 Translating catalog, support and referral button texts...")
    catalog_text = _("main_menu:button:catalog")
    referral_text = _("main_menu:button:referral") if is_referral_available else None
    support_text = _("main_menu:button:support")
    
    logger.debug(f"🛍️ Catalog button: '{catalog_text}' -> {NavCatalog.MAIN}")
    if is_referral_available:
        logger.debug(f"👥 Adding referral button: '{referral_text}' -> {NavReferral.MAIN}")
    logger.debug(f"🆘 Support button: '{support_text}' -> {NavSupport.MAIN}")
    
    # Build catalog button
    catalog_button = InlineKeyboardButton(
        text=catalog_text,
        callback_data=NavCatalog.MAIN,
    )
    
    # Build support button
    support_button = InlineKeyboardButton(
        text=support_text,
        callback_data=NavSupport.MAIN,
    )
    
    # Add row with catalog and referral/support based on availability
    if is_referral_available:
        referral_button = InlineKeyboardButton(
            text=referral_text,
            callback_data=NavReferral.MAIN,
        )
        builder.row(catalog_button, referral_button)
        builder.row(support_button)
    else:
        builder.row(catalog_button, support_button)

    if is_admin:
        logger.debug("🔤 Translating admin tools button text...")
        admin_tools_text = _("main_menu:button:admin_tools")
        logger.debug(f"🛠 Adding admin tools button: '{admin_tools_text}' -> {NavAdminTools.MAIN}")
        builder.row(
            InlineKeyboardButton(
                text=admin_tools_text,
                callback_data=NavAdminTools.MAIN,
            )
        )

    keyboard = builder.as_markup()
    logger.debug(f"✅ Main menu keyboard generated with {len(keyboard.inline_keyboard)} rows")
    return keyboard
