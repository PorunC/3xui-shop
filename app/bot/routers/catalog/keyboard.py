from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.routers.misc.keyboard import back_to_main_menu_button
from app.bot.utils.navigation import NavCatalog, NavSubscription


def catalog_keyboard() -> InlineKeyboardMarkup:
    """Main catalog keyboard with product categories."""
    builder = InlineKeyboardBuilder()

    # Product categories
    builder.row(
        InlineKeyboardButton(
            text=_("catalog:button:software"),
            callback_data=f"{NavCatalog.CATEGORY}_software",
        ),
        InlineKeyboardButton(
            text=_("catalog:button:gaming"),
            callback_data=f"{NavCatalog.CATEGORY}_gaming",
        ),
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("catalog:button:subscription"),
            callback_data=f"{NavCatalog.CATEGORY}_subscription",
        ),
        InlineKeyboardButton(
            text=_("catalog:button:digital"),
            callback_data=f"{NavCatalog.CATEGORY}_digital",
        ),
    )
    
    builder.row(
        InlineKeyboardButton(
            text=_("catalog:button:education"),
            callback_data=f"{NavCatalog.CATEGORY}_education",
        ),
    )

    # Direct purchase button
    builder.row(
        InlineKeyboardButton(
            text=_("catalog:button:buy_products"),
            callback_data=NavSubscription.MAIN,
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def category_products_keyboard(category: str, products: list) -> InlineKeyboardMarkup:
    """Keyboard showing products in a specific category."""
    builder = InlineKeyboardBuilder()

    for product in products:
        builder.row(
            InlineKeyboardButton(
                text=f"{product['name']} - {product['price']['amount']} {product['price']['currency']}",
                callback_data=f"{NavCatalog.PRODUCT}_{product['id']}",
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


def product_details_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """Keyboard for individual product details."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("catalog:button:buy_now"),
            callback_data=NavSubscription.MAIN,
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
