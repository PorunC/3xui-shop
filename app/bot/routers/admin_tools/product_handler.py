import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.utils.navigation import NavAdminTools
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.PRODUCT_MANAGEMENT, IsAdmin())
async def callback_product_management(
    callback: CallbackQuery, 
    user: User, 
    services: ServicesContainer
) -> None:
    """Product management main page."""
    logger.info(f"Admin {user.tg_id} opened product management.")
    
    # Get current product count
    products = await services.product.load_products_catalog()
    product_count = len(products)
    
    text = _("admin_tools:message:product_management").format(count=product_count)
    
    # For now, just show a development message
    await callback.message.edit_text(
        text=f"📦 Product Management\n\nCurrently managing {product_count} products.\n\n🚧 Advanced product management features coming soon!",
        reply_markup=None,
    )
