from __future__ import annotations

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsDev
from app.bot.models import ServicesContainer
from app.bot.routers.misc.keyboard import back_keyboard
from app.bot.utils.constants import (
    MAIN_MESSAGE_ID_KEY,
    SERVER_HOST_KEY,
    SERVER_MAX_CLIENTS_KEY,
    SERVER_NAME_KEY,
)
from app.bot.utils.navigation import NavAdminTools
from app.bot.utils.network import ping_url
from app.bot.utils.validation import is_valid_client_count, is_valid_host
from app.db.models import User
# from app.db.models import Server  # Removed - no longer using VPN servers

from .keyboard import confirm_add_server_keyboard, server_keyboard, servers_keyboard

router = Router(name="admin-tools-server")
logger = logging.getLogger(__name__)

# All server management functions are disabled since we removed VPN functionality

@router.callback_query(F.data == NavAdminTools.SERVER_MANAGEMENT, IsDev())
async def callback_server_management(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    logger.info(f"Dev {user.tg_id} tried to access server management.")
    await state.set_state(None)
    
    # Server management is no longer available since we removed VPN functionality
    text = "🚫 服务器管理功能已禁用\n\n由于已移除VPN功能，服务器管理不再可用。\n请使用产品管理功能来管理数字商品。"
    
    # Return empty servers list
    servers = []
    await callback.message.edit_text(text=text, reply_markup=servers_keyboard(servers))


@router.callback_query(F.data == NavAdminTools.SYNC_SERVERS, IsDev())
async def callback_sync_servers(
    callback: CallbackQuery, services: ServicesContainer, user: User
) -> None:
    logger.info(f"Dev {user.tg_id} tried to sync servers.")
    
    text = "🚫 服务器同步功能已禁用\n\n服务器管理功能已移除。"
    await callback.answer(text=text, show_alert=True)


@router.callback_query(F.data == NavAdminTools.ADD_SERVER, IsDev())
async def callback_add_server(
    callback: CallbackQuery, state: FSMContext, user: User
) -> None:
    logger.info(f"Dev {user.tg_id} tried to add server.")
    
    text = "🚫 添加服务器功能已禁用\n\n服务器管理功能已移除。"
    await callback.answer(text=text, show_alert=True)


@router.callback_query(F.data.startswith(NavAdminTools.SHOW_SERVER), IsDev())
async def callback_show_server(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    logger.info(f"Dev {user.tg_id} tried to show server.")
    
    text = "🚫 服务器详情功能已禁用\n\n服务器管理功能已移除。"
    await callback.answer(text=text, show_alert=True)


@router.callback_query(F.data.startswith(NavAdminTools.PING_SERVER), IsDev())
async def callback_ping_server(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    logger.info(f"Dev {user.tg_id} tried to ping server.")
    
    text = "🚫 服务器测试功能已禁用\n\n服务器管理功能已移除。"
    await callback.answer(text=text, show_alert=True)


@router.callback_query(F.data.startswith(NavAdminTools.DELETE_SERVER), IsDev())
async def callback_delete_server(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    logger.info(f"Dev {user.tg_id} tried to delete server.")
    
    text = "🚫 删除服务器功能已禁用\n\n服务器管理功能已移除。"
    await callback.answer(text=text, show_alert=True)


# All message handlers for server input are also disabled
@router.message(IsDev())
async def handle_disabled_server_input(message: Message, state: FSMContext) -> None:
    """Handle any server input messages by showing disabled message."""
    current_state = await state.get_state()
    if current_state and "server" in current_state.lower():
        await message.answer("🚫 服务器管理功能已禁用\n\n服务器相关的所有功能已移除。")
        await state.clear()
