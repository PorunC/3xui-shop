import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.models import ServicesContainer
from app.bot.utils.navigation import NavCatalog
from app.db.models import User

from .keyboard import catalog_keyboard, category_products_keyboard, product_details_keyboard
from .purchase_keyboard import purchase_confirmation_keyboard

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


@router.callback_query(F.data.startswith(NavCatalog.BUY_PRODUCT))
async def callback_buy_product(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Handle direct product purchase."""
    product_id = callback.data.split("_", 2)[2]
    logger.info(f"User {user.tg_id} wants to buy product: {product_id}")
    
    # Get product details
    products = await services.product.load_products_catalog()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await callback.answer(_("catalog:error:product_not_found"), show_alert=True)
        return
    
    # Check if product is available
    stock = product.get('stock', 0)
    is_active = product.get('is_active', True)
    
    if not is_active or stock <= 0:
        await callback.answer(_("catalog:error:product_unavailable"), show_alert=True)
        return
    
    # Store product selection in user session
    # You'll need to implement session storage, this is a placeholder
    # await services.storage.set_data(user.tg_id, "selected_product", product)
    
    # Redirect to payment flow
    from app.bot.models.subscription_data import SubscriptionData
    from app.bot.utils.navigation import NavSubscription
    
    # Create subscription data for the product
    subscription_data = SubscriptionData(
        user_id=user.tg_id,
        devices=1,  # Products don't use device concept
        duration=product.get('duration_days', 30),
        price=product['price']['amount'],
        state=NavSubscription.PAY,
        product_id=product['id'],
        product_name=product['name']
    )
    
    # Format purchase confirmation
    text = _("catalog:message:purchase_confirmation").format(
        name=product['name'],
        price=product['price']['amount'],
        currency=product['price']['currency'],
        delivery_type=_(f"catalog:delivery:{product.get('delivery_type', 'digital')}")
    )
    
    # Create purchase confirmation keyboard
    from .keyboard import purchase_confirmation_keyboard
    keyboard = purchase_confirmation_keyboard(product_id)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith(NavCatalog.ADD_TO_CART))
async def callback_add_to_cart(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Add product to shopping cart."""
    product_id = callback.data.split("_", 3)[3]
    logger.info(f"User {user.tg_id} adding product {product_id} to cart")
    
    # Get product details
    products = await services.product.load_products_catalog()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await callback.answer(_("catalog:error:product_not_found"), show_alert=True)
        return
    
    # Add to cart (implement cart service later)
    # await services.cart.add_product(user.tg_id, product)
    
    await callback.answer(
        _("catalog:success:added_to_cart").format(name=product['name']), 
        show_alert=True
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
        # Format product details with enhanced display
        features = "\n".join([f"• {feature}" for feature in product.get('features', [])])
        
        # Format duration
        duration_days = product.get('duration_days', 0)
        if duration_days == 0:
            duration_text = _("catalog:duration:lifetime")
        elif duration_days >= 365:
            years = duration_days // 365
            duration_text = _("catalog:duration:years").format(years=years)
        elif duration_days >= 30:
            months = duration_days // 30
            duration_text = _("catalog:duration:months").format(months=months)
        else:
            duration_text = _("catalog:duration:days").format(days=duration_days)
        
        # Format stock status
        stock = product.get('stock', 0)
        if stock > 10:
            stock_text = _("catalog:stock:available")
        elif stock > 0:
            stock_text = _("catalog:stock:limited").format(count=stock)
        else:
            stock_text = _("catalog:stock:out_of_stock")
        
        # Check if product is active
        is_active = product.get('is_active', True)
        status_emoji = "🟢" if is_active else "🔴"
        
        text = _("catalog:message:product_details_enhanced").format(
            status_emoji=status_emoji,
            name=product['name'],
            description=product['description'],
            price=product['price']['amount'],
            currency=product['price']['currency'],
            category=_(f"catalog:category:{product['category']}"),
            duration=duration_text,
            stock_status=stock_text,
            delivery_type=_(f"catalog:delivery:{product.get('delivery_type', 'digital')}"),
            features=features if features else _("catalog:message:no_features")
        )
        
        keyboard = product_details_keyboard(product_id, is_active and stock > 0)
    else:
        text = _("catalog:message:product_not_found")
        keyboard = catalog_keyboard()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith(NavCatalog.BUY_PRODUCT))
async def callback_buy_product(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Handle direct product purchase."""
    product_id = callback.data.split("_", 2)[2]
    logger.info(f"User {user.tg_id} wants to buy product: {product_id}")
    
    # Get product details
    products = await services.product.load_products_catalog()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await callback.answer(_("catalog:error:product_not_found"), show_alert=True)
        return
    
    # Check if product is available
    stock = product.get('stock', 0)
    is_active = product.get('is_active', True)
    
    if not is_active or stock <= 0:
        await callback.answer(_("catalog:error:product_unavailable"), show_alert=True)
        return
    
    # Store product selection in user session
    # You'll need to implement session storage, this is a placeholder
    # await services.storage.set_data(user.tg_id, "selected_product", product)
    
    # Redirect to payment flow
    from app.bot.models.subscription_data import SubscriptionData
    from app.bot.utils.navigation import NavSubscription
    
    # Create subscription data for the product
    subscription_data = SubscriptionData(
        user_id=user.tg_id,
        devices=1,  # Products don't use device concept
        duration=product.get('duration_days', 30),
        price=product['price']['amount'],
        state=NavSubscription.PAY,
        product_id=product['id'],
        product_name=product['name']
    )
    
    # Format purchase confirmation
    text = _("catalog:message:purchase_confirmation").format(
        name=product['name'],
        price=product['price']['amount'],
        currency=product['price']['currency'],
        delivery_type=_(f"catalog:delivery:{product.get('delivery_type', 'digital')}")
    )
    
    # Create purchase confirmation keyboard
    from .keyboard import purchase_confirmation_keyboard
    keyboard = purchase_confirmation_keyboard(product_id)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith(NavCatalog.ADD_TO_CART))
async def callback_add_to_cart(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Add product to shopping cart."""
    product_id = callback.data.split("_", 3)[3]
    logger.info(f"User {user.tg_id} adding product {product_id} to cart")
    
    # Get product details
    products = await services.product.load_products_catalog()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await callback.answer(_("catalog:error:product_not_found"), show_alert=True)
        return
    
    # Add to cart (implement cart service later)
    # await services.cart.add_product(user.tg_id, product)
    
    await callback.answer(
        _("catalog:success:added_to_cart").format(name=product['name']), 
        show_alert=True
    )
