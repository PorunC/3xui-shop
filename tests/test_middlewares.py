"""
Tests for bot middlewares.
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery, User as TelegramUser

from app.bot.middlewares.database import DBSessionMiddleware
from app.bot.middlewares.throttling import ThrottlingMiddleware
from app.bot.middlewares.maintenance import MaintenanceMiddleware
from app.bot.middlewares.garbage import GarbageMiddleware


class TestDBSessionMiddleware:
    """Tests for DBSessionMiddleware."""
    
    @pytest.fixture
    def db_middleware(self, test_db):
        """Create DBSessionMiddleware instance for testing."""
        return DBSessionMiddleware(session=test_db.session)

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler."""
        return AsyncMock()

    @pytest.fixture
    def mock_event(self):
        """Create a mock event with user."""
        event = Mock(spec=TelegramObject)
        event.event = Mock()
        event.event.from_user = Mock(spec=TelegramUser)
        event.event.from_user.id = 123456789
        event.event.from_user.first_name = "Test User"
        event.event.from_user.username = "testuser"
        event.event.from_user.language_code = "en"
        event.event.from_user.is_bot = False
        return event

    @pytest.fixture
    def mock_bot_event(self):
        """Create a mock event from bot."""
        event = Mock(spec=TelegramObject)
        event.event = Mock()
        event.event.from_user = Mock(spec=TelegramUser)
        event.event.from_user.id = 987654321
        event.event.from_user.is_bot = True
        return event

    async def test_middleware_with_new_user(self, db_middleware, mock_handler, mock_event):
        """Test middleware with new user."""
        data: Dict[str, Any] = {}
        
        with patch('app.db.models.User.get', return_value=None), \
             patch('app.db.models.User.create') as mock_create:
            
            mock_user = Mock()
            mock_user.tg_id = 123456789
            mock_create.return_value = mock_user
            
            await db_middleware(mock_handler, mock_event, data)
            
            # Verify user creation was attempted
            mock_create.assert_called_once()
            
            # Verify handler was called
            mock_handler.assert_called_once_with(mock_event, data)

    async def test_middleware_with_existing_user(self, db_middleware, mock_handler, mock_event):
        """Test middleware with existing user."""
        data: Dict[str, Any] = {}
        
        mock_user = Mock()
        mock_user.tg_id = 123456789
        
        with patch('app.db.models.User.get', return_value=mock_user), \
             patch('app.db.models.User.create') as mock_create:
            
            await db_middleware(mock_handler, mock_event, data)
            
            # Verify user creation was NOT attempted
            mock_create.assert_not_called()
            
            # Verify handler was called
            mock_handler.assert_called_once_with(mock_event, data)

    async def test_middleware_with_bot_user(self, db_middleware, mock_handler, mock_bot_event):
        """Test middleware with bot user (should be ignored)."""
        data: Dict[str, Any] = {}
        
        with patch('app.db.models.User.get') as mock_get, \
             patch('app.db.models.User.create') as mock_create:
            
            await db_middleware(mock_handler, mock_bot_event, data)
            
            # Verify no database operations for bot users
            mock_get.assert_not_called()
            mock_create.assert_not_called()
            
            # Verify handler was called
            mock_handler.assert_called_once_with(mock_bot_event, data)

    async def test_middleware_with_no_user(self, db_middleware, mock_handler):
        """Test middleware with event that has no user."""
        event = Mock(spec=TelegramObject)
        event.event = Mock()
        event.event.from_user = None
        data: Dict[str, Any] = {}
        
        with patch('app.db.models.User.get') as mock_get:
            await db_middleware(mock_handler, event, data)
            
            # Verify no database operations when no user
            mock_get.assert_not_called()
            
            # Verify handler was called
            mock_handler.assert_called_once_with(event, data)


class TestThrottlingMiddleware:
    """Tests for ThrottlingMiddleware."""
    
    @pytest.fixture
    def throttling_middleware(self):
        """Create ThrottlingMiddleware instance for testing."""
        return ThrottlingMiddleware(default_ttl=1.0)

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler."""
        return AsyncMock()

    @pytest.fixture
    def mock_update(self):
        """Create a mock update with user."""
        update = Mock(spec=Update)
        update.event = Mock()
        update.event.from_user = Mock(spec=TelegramUser)
        update.event.from_user.id = 123456789
        update.pre_checkout_query = None
        update.message = None
        return update

    async def test_middleware_allows_first_request(self, throttling_middleware, mock_handler, mock_update):
        """Test that first request is allowed."""
        data: Dict[str, Any] = {"handler": mock_handler}
        
        with patch('aiogram.dispatcher.flags.get_flag', return_value="default"):
            result = await throttling_middleware(mock_handler, mock_update, data)
            
            # First request should be allowed
            mock_handler.assert_called_once_with(mock_update, data)

    async def test_middleware_throttles_subsequent_requests(self, throttling_middleware, mock_handler, mock_update):
        """Test that subsequent requests are throttled."""
        data: Dict[str, Any] = {"handler": mock_handler}
        
        with patch('aiogram.dispatcher.flags.get_flag', return_value="default"):
            # First request
            await throttling_middleware(mock_handler, mock_update, data)
            mock_handler.reset_mock()
            
            # Second request (should be throttled)
            result = await throttling_middleware(mock_handler, mock_update, data)
            
            # Second request should be throttled (returns None)
            assert result is None
            mock_handler.assert_not_called()

    async def test_middleware_skips_pre_checkout_query(self, throttling_middleware, mock_handler):
        """Test that pre-checkout queries are not throttled."""
        update = Mock(spec=Update)
        update.pre_checkout_query = Mock()
        data: Dict[str, Any] = {}
        
        await throttling_middleware(mock_handler, update, data)
        
        # Pre-checkout query should always be allowed
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_skips_successful_payment(self, throttling_middleware, mock_handler):
        """Test that successful payment events are not throttled."""
        update = Mock(spec=Update)
        update.pre_checkout_query = None
        update.message = Mock()
        update.message.successful_payment = Mock()
        data: Dict[str, Any] = {}
        
        await throttling_middleware(mock_handler, update, data)
        
        # Successful payment should always be allowed
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_with_non_update_event(self, throttling_middleware, mock_handler):
        """Test middleware with non-Update event."""
        event = Mock(spec=TelegramObject)  # Not an Update
        data: Dict[str, Any] = {}
        
        await throttling_middleware(mock_handler, event, data)
        
        # Non-Update events should be allowed
        mock_handler.assert_called_once_with(event, data)


class TestMaintenanceMiddleware:
    """Tests for MaintenanceMiddleware."""
    
    @pytest.fixture
    def maintenance_middleware(self):
        """Create MaintenanceMiddleware instance for testing."""
        # Reset maintenance mode before each test
        MaintenanceMiddleware.active = False
        return MaintenanceMiddleware()

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler."""
        return AsyncMock()

    @pytest.fixture
    def mock_update_with_message(self):
        """Create a mock update with message."""
        update = Mock(spec=Update)
        update.event = Mock()
        update.event.from_user = Mock(spec=TelegramUser)
        update.event.from_user.id = 123456789
        update.bot = Mock()
        update.bot.id = 987654321
        update.message = Mock()
        update.message.text = "test message"
        update.callback_query = None
        return update

    async def test_middleware_inactive_maintenance(self, maintenance_middleware, mock_handler, mock_update_with_message):
        """Test middleware when maintenance is inactive."""
        MaintenanceMiddleware.active = False
        data: Dict[str, Any] = {}
        
        with patch('app.bot.filters.IsAdmin.__call__', return_value=False):
            await maintenance_middleware(mock_handler, mock_update_with_message, data)
            
            # Should allow request when maintenance is inactive
            mock_handler.assert_called_once_with(mock_update_with_message, data)

    async def test_middleware_active_maintenance_admin_user(self, maintenance_middleware, mock_handler, mock_update_with_message):
        """Test middleware with admin user during maintenance."""
        MaintenanceMiddleware.active = True
        data: Dict[str, Any] = {}
        
        with patch('app.bot.filters.IsAdmin.__call__', return_value=True):
            await maintenance_middleware(mock_handler, mock_update_with_message, data)
            
            # Admin should be allowed during maintenance
            mock_handler.assert_called_once_with(mock_update_with_message, data)

    async def test_middleware_active_maintenance_regular_user(self, maintenance_middleware, mock_handler, mock_update_with_message):
        """Test middleware with regular user during maintenance."""
        MaintenanceMiddleware.active = True
        data: Dict[str, Any] = {}
        
        with patch('app.bot.filters.IsAdmin.__call__', return_value=False), \
             patch('app.bot.services.NotificationService.notify_by_message') as mock_notify:
            
            result = await maintenance_middleware(mock_handler, mock_update_with_message, data)
            
            # Regular user should be blocked during maintenance
            assert result is None
            mock_handler.assert_not_called()
            mock_notify.assert_called_once()

    async def test_set_maintenance_mode(self, maintenance_middleware):
        """Test setting maintenance mode."""
        # Test enabling maintenance
        MaintenanceMiddleware.set_mode(True)
        assert MaintenanceMiddleware.active is True
        
        # Test disabling maintenance
        MaintenanceMiddleware.set_mode(False)
        assert MaintenanceMiddleware.active is False

    async def test_maintenance_with_callback_query(self, maintenance_middleware, mock_handler):
        """Test maintenance middleware with callback query."""
        update = Mock(spec=Update)
        update.event = Mock()
        update.event.from_user = Mock(spec=TelegramUser)
        update.event.from_user.id = 123456789
        update.bot = Mock()
        update.bot.id = 987654321
        update.message = None
        update.callback_query = Mock()
        update.callback_query.message = Mock()
        
        MaintenanceMiddleware.active = True
        data: Dict[str, Any] = {}
        
        with patch('app.bot.filters.IsAdmin.__call__', return_value=False), \
             patch('app.bot.services.NotificationService.notify_by_message') as mock_notify:
            
            result = await maintenance_middleware(mock_handler, update, data)
            
            # Should be blocked and notification sent
            assert result is None
            mock_notify.assert_called_once()


class TestGarbageMiddleware:
    """Tests for GarbageMiddleware."""
    
    @pytest.fixture
    def garbage_middleware(self):
        """Create GarbageMiddleware instance for testing."""
        return GarbageMiddleware()

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler."""
        return AsyncMock()

    async def test_middleware_deletes_non_start_messages(self, garbage_middleware, mock_handler):
        """Test that non-/start messages are deleted."""
        update = Mock(spec=Update)
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 123456789
        update.message.text = "hello"
        update.message.forward_from = None
        update.message.delete = AsyncMock()
        update.bot = Mock()
        update.bot.id = 987654321
        
        data: Dict[str, Any] = {}
        
        await garbage_middleware(mock_handler, update, data)
        
        # Message should be deleted
        update.message.delete.assert_called_once()
        # Handler should still be called
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_preserves_start_messages(self, garbage_middleware, mock_handler):
        """Test that /start messages are preserved."""
        update = Mock(spec=Update)
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 123456789
        update.message.text = "/start"
        update.message.forward_from = None
        update.message.delete = AsyncMock()
        update.bot = Mock()
        update.bot.id = 987654321
        
        data: Dict[str, Any] = {}
        
        await garbage_middleware(mock_handler, update, data)
        
        # Message should NOT be deleted
        update.message.delete.assert_not_called()
        # Handler should be called
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_deletes_forwarded_messages(self, garbage_middleware, mock_handler):
        """Test that forwarded messages are deleted."""
        update = Mock(spec=Update)
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 123456789
        update.message.text = "some text"
        update.message.forward_from = Mock()  # This makes it a forwarded message
        update.message.delete = AsyncMock()
        update.bot = Mock()
        update.bot.id = 987654321
        
        data: Dict[str, Any] = {}
        
        await garbage_middleware(mock_handler, update, data)
        
        # Forwarded message should be deleted
        update.message.delete.assert_called_once()
        # Handler should still be called
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_skips_bot_messages(self, garbage_middleware, mock_handler):
        """Test that bot messages are not processed."""
        update = Mock(spec=Update)
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 987654321  # Same as bot.id
        update.message.text = "bot message"
        update.message.forward_from = None
        update.message.delete = AsyncMock()
        update.bot = Mock()
        update.bot.id = 987654321
        
        data: Dict[str, Any] = {}
        
        await garbage_middleware(mock_handler, update, data)
        
        # Bot messages should not be deleted
        update.message.delete.assert_not_called()
        # Handler should still be called
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_handles_delete_error(self, garbage_middleware, mock_handler):
        """Test middleware handles deletion errors gracefully."""
        update = Mock(spec=Update)
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 123456789
        update.message.text = "test message"
        update.message.forward_from = None
        update.message.delete = AsyncMock(side_effect=Exception("Delete failed"))
        update.bot = Mock()
        update.bot.id = 987654321
        
        data: Dict[str, Any] = {}
        
        # Should not raise exception
        await garbage_middleware(mock_handler, update, data)
        
        # Handler should still be called despite delete error
        mock_handler.assert_called_once_with(update, data)

    async def test_middleware_with_non_update_event(self, garbage_middleware, mock_handler):
        """Test middleware with non-Update event."""
        event = Mock(spec=TelegramObject)  # Not an Update
        data: Dict[str, Any] = {}
        
        await garbage_middleware(mock_handler, event, data)
        
        # Non-Update events should be allowed without processing
        mock_handler.assert_called_once_with(event, data)

    async def test_middleware_with_update_no_message(self, garbage_middleware, mock_handler):
        """Test middleware with Update that has no message."""
        update = Mock(spec=Update)
        update.message = None  # No message
        data: Dict[str, Any] = {}
        
        await garbage_middleware(mock_handler, update, data)
        
        # Should be allowed without processing
        mock_handler.assert_called_once_with(update, data)


class TestMiddlewareIntegration:
    """Integration tests for middleware components."""
    
    async def test_middleware_chain(self, test_db):
        """Test that multiple middlewares can work together."""
        # Create middleware instances
        db_middleware = DBSessionMiddleware(session=test_db.session)
        throttling_middleware = ThrottlingMiddleware(default_ttl=1.0)
        maintenance_middleware = MaintenanceMiddleware()
        garbage_middleware = GarbageMiddleware()
        
        # Create mock components
        handler = AsyncMock()
        
        update = Mock(spec=Update)
        update.event = Mock()
        update.event.from_user = Mock(spec=TelegramUser)
        update.event.from_user.id = 123456789
        update.event.from_user.first_name = "Test"
        update.event.from_user.username = "test"
        update.event.from_user.language_code = "en"
        update.event.from_user.is_bot = False
        update.pre_checkout_query = None
        update.message = Mock()
        update.message.from_user = update.event.from_user
        update.message.text = "/start"
        update.message.forward_from = None
        update.message.delete = AsyncMock()
        update.bot = Mock()
        update.bot.id = 987654321
        
        data: Dict[str, Any] = {"handler": handler}
        
        # Test middleware chain
        MaintenanceMiddleware.active = False
        
        with patch('app.db.models.User.get', return_value=None), \
             patch('app.db.models.User.create') as mock_create, \
             patch('aiogram.dispatcher.flags.get_flag', return_value="default"):
            
            mock_user = Mock()
            mock_user.tg_id = 123456789
            mock_create.return_value = mock_user
            
            # Process through middleware chain
            async def chain_handler(event, data):
                return await garbage_middleware(handler, event, data)
            
            async def maintenance_chain(event, data):
                return await maintenance_middleware(chain_handler, event, data)
            
            async def throttle_chain(event, data):
                return await throttling_middleware(maintenance_chain, event, data)
            
            result = await db_middleware(throttle_chain, update, data)
            
            # Verify all middlewares processed the request
            handler.assert_called_once()
            mock_create.assert_called_once()  # DB middleware created user
            update.message.delete.assert_not_called()  # Garbage middleware preserved /start message

    async def test_middleware_blocking(self, test_db):
        """Test that middleware can block request propagation."""
        throttling_middleware = ThrottlingMiddleware(default_ttl=1.0)
        handler = AsyncMock()
        
        update = Mock(spec=Update)
        update.event = Mock()
        update.event.from_user = Mock(spec=TelegramUser)
        update.event.from_user.id = 123456789
        update.pre_checkout_query = None
        update.message = None
        
        data: Dict[str, Any] = {"handler": handler}
        
        with patch('aiogram.dispatcher.flags.get_flag', return_value="default"):
            # First request - should pass
            result1 = await throttling_middleware(handler, update, data)
            handler.assert_called_once()
            
            handler.reset_mock()
            
            # Second request - should be blocked
            result2 = await throttling_middleware(handler, update, data)
            assert result2 is None
            handler.assert_not_called()