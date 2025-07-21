"""
Additional keyboards for product purchase functionality.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.routers.misc.keyboard import back_to_main_menu_button
from app.bot.utils.navigation import NavCatalog, NavSubscription


def purchase_confirmation_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """Keyboard for purchase confirmation."""
    builder = InlineKeyboardBuilder()

    # Payment method buttons
    builder.row(
        InlineKeyboardButton(
            text=_("payment:button:telegram_stars"),
            callback_data=f"{NavSubscription.PAY_TELEGRAM_STARS}_{product_id}",
        ),
        InlineKeyboardButton(
            text=_("payment:button:cryptomus"),
            callback_data=f"{NavSubscription.PAY_CRYPTOMUS}_{product_id}",
        ),
    )

    # Back buttons
    builder.row(
        InlineKeyboardButton(
            text=_("misc:button:back"),
            callback_data=f"{NavCatalog.PRODUCT}_{product_id}",
        )
    )
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def shopping_cart_keyboard(cart_items: list) -> InlineKeyboardMarkup:
    """Keyboard for shopping cart view."""
    builder = InlineKeyboardBuilder()

    # Cart items (first 5)
    for item in cart_items[:5]:
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {item['name']} - {item['price']['amount']} {item['price']['currency']}",
                callback_data=f"{NavCatalog.REMOVE_FROM_CART}_{item['id']}",
            )
        )

    if cart_items:
        # Checkout button
        builder.row(
            InlineKeyboardButton(
                text=_("catalog:button:checkout"),
                callback_data=NavCatalog.CHECKOUT,
            )
        )
        
        # Clear cart button
        builder.row(
            InlineKeyboardButton(
                text=_("catalog:button:clear_cart"),
                callback_data=f"{NavCatalog.CLEAR_CART}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=_("misc:button:back"),
            callback_data=NavCatalog.MAIN,
        )
    )
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def product_management_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for admin product management."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("admin:button:add_product"),
            callback_data=f"{NavCatalog.ADD_PRODUCT}",
        ),
        InlineKeyboardButton(
            text=_("admin:button:list_products"),
            callback_data=f"{NavCatalog.LIST_PRODUCTS}",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text=_("admin:button:category_management"),
            callback_data=f"{NavCatalog.MANAGE_CATEGORIES}",
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()