import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.models import ServicesContainer
from app.bot.utils.navigation import NavCatalog
from app.db.models import User

from .keyboard import catalog_keyboard, category_products_keyboard, product_details_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavCatalog.MAIN)
async def callback_catalog(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Show main catalog with product categories."""
    logger.info(f"🛍️ User {user.tg_id} clicked catalog button -> opening product catalog")
    
    text = _("catalog:message:main")
    logger.debug(f"📝 Catalog main text: '{text}'")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=catalog_keyboard(),
    )
    logger.debug(f"✅ Catalog main page displayed for user {user.tg_id}")


@router.callback_query(F.data.startswith(NavCatalog.CATEGORY))
async def callback_category(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Show products in a specific category."""
    category = callback.data.split("_", 1)[1]
    logger.info(f"User {user.tg_id} browsing category: {category}")
    
    # Get products from the service
    products = await services.product.get_products_by_category(category)
    
    if products:
        text = _("catalog:message:category").format(
            category=_(f"catalog:category:{category}"),
            count=len(products)
        )
        keyboard = category_products_keyboard(category, products)
    else:
        text = _("catalog:message:no_products_in_category").format(
            category=_(f"catalog:category:{category}")
        )
        keyboard = catalog_keyboard()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith(NavCatalog.PRODUCT))
async def callback_product_details(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Show details of a specific product."""
    product_id = callback.data.split("_", 1)[1]
    logger.info(f"User {user.tg_id} viewing product: {product_id}")
    
    # Get product details
    products = await services.product.load_products_catalog()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        # Format product details
        features = "\n".join([f"• {feature}" for feature in product.get('features', [])])
        
        text = _("catalog:message:product_details").format(
            name=product['name'],
            description=product['description'],
            price=product['price']['amount'],
            currency=product['price']['currency'],
            category=_(f"catalog:category:{product['category']}"),
            features=features if features else _("catalog:message:no_features")
        )
        
        keyboard = product_details_keyboard(product_id)
    else:
        text = _("catalog:message:product_not_found")
        keyboard = catalog_keyboard()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )
