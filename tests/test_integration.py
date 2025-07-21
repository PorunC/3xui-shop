"""
Integration tests for the 3xui-shop application.
These tests verify that different components work together correctly.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, User as TelegramUser, CallbackQuery
from aioresponses import aioresponses

from app.bot.models import SubscriptionData, ServicesContainer
from app.bot.payment_gateways import GatewayFactory, TelegramStars, Cryptomus
from app.bot.services import PlanService, NotificationService
from app.bot.utils.constants import Currency, TransactionStatus
from app.bot.utils.navigation import NavSubscription
from app.db.models import User, Transaction


class TestPaymentFlowIntegration:
    """Test complete payment flow integration."""
    
    async def test_telegram_stars_payment_flow(self, test_config, test_db, test_storage, mock_bot, test_i18n, test_services):
        """Test complete Telegram Stars payment flow."""
        # Create gateway
        telegram_stars = TelegramStars(
            app=None,
            config=test_config,
            session=test_db.session,
            storage=test_storage,
            bot=mock_bot,
            i18n=test_i18n,
            services=test_services
        )
        
        # Create subscription data
        subscription_data = SubscriptionData(
            user_id=123456789,
            devices=1,
            duration=30,
            price=1000,
            state=NavSubscription.PAY_TELEGRAM_STARS
        )
        
        # Mock bot send_invoice
        mock_bot.send_invoice = AsyncMock()
        
        # Test payment creation
        with patch('app.bot.filters.is_dev.IsDev.__call__', return_value=False):
            payment_url = await telegram_stars.create_payment(subscription_data)
            
            # Verify invoice was sent
            mock_bot.send_invoice.assert_called_once()
            
            # Verify invoice parameters
            call_args = mock_bot.send_invoice.call_args
            assert call_args.kwargs['chat_id'] == subscription_data.user_id
            assert call_args.kwargs['prices'][0].amount == subscription_data.price

        # Test payment success handling
        payment_id = "test_payment_123"
        test_services.subscription = Mock()
        test_services.subscription.process_payment = AsyncMock()
        test_services.notification = Mock()
        test_services.notification.notify_developer = AsyncMock()
        
        await telegram_stars.handle_payment_succeeded(payment_id)
        
        # Verify developer notification
        test_services.notification.notify_developer.assert_called_once()

    async def test_cryptomus_payment_flow(self, test_config, test_db, test_storage, mock_bot, test_i18n, test_services):
        """Test complete Cryptomus payment flow."""
        # Set up Cryptomus config
        test_config.cryptomus.API_KEY = "test_api_key"
        test_config.cryptomus.MERCHANT_ID = "test_merchant_id"
        
        # Create mock app
        mock_app = Mock()
        mock_app.router = Mock()
        mock_app.router.add_post = Mock()
        
        # Create gateway
        cryptomus = Cryptomus(
            app=mock_app,
            config=test_config,
            session=test_db.session,
            storage=test_storage,
            bot=mock_bot,
            i18n=test_i18n,
            services=test_services
        )
        
        # Create subscription data
        subscription_data = SubscriptionData(
            user_id=123456789,
            devices=1,
            duration=30,
            price=25.00,
            state=NavSubscription.PAY_CRYPTOMUS
        )
        
        # Mock API response
        mock_response = {
            "state": 0,
            "result": {
                "uuid": "test-uuid-123",
                "order_id": "test-order-123",
                "amount": "25.00",
                "currency": "USD",
                "url": "https://pay.cryptomus.com/pay/test-uuid-123"
            }
        }
        
        # Test payment creation
        with aioresponses() as m:
            m.post(
                "https://api.cryptomus.com/v1/payment",
                payload=mock_response,
                status=200
            )
            
            payment_url = await cryptomus.create_payment(subscription_data)
            assert payment_url == "https://pay.cryptomus.com/pay/test-uuid-123"
        
        # Test webhook handling
        webhook_data = {
            "uuid": "test-uuid",
            "order_id": "test-order",
            "amount": "25.00",
            "currency": "USD",
            "status": "paid"
        }
        
        # Mock request
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value=webhook_data)
        mock_request.headers = {"sign": cryptomus._generate_signature(webhook_data)}
        
        # Mock services
        test_services.subscription = Mock()
        test_services.subscription.process_payment = AsyncMock()
        
        with patch.object(cryptomus, '_verify_signature', return_value=True):
            response = await cryptomus.webhook_handler(mock_request)
            assert response.status == 200


class TestServiceIntegration:
    """Test integration between different services."""
    
    async def test_plan_service_with_subscription_service(self, temp_dir, test_config, test_db):
        """Test PlanService working with SubscriptionService."""
        # Create test plans file
        plans_file = temp_dir / "plans.json"
        plans_data = {
            "durations": [30, 90, 365],
            "plans": [
                {
                    "devices": 1,
                    "prices": {
                        "USD": {"30": 10, "90": 25, "365": 90},
                        "RUB": {"30": 800, "90": 2000, "365": 7200}
                    }
                }
            ]
        }
        plans_file.write_text(json.dumps(plans_data))
        
        # Create services
        plan_service = PlanService(file_path=str(plans_file))
        
        from app.bot.services.subscription import SubscriptionService
        subscription_service = SubscriptionService(config=test_config, session=test_db.session)
        
        # Test plan retrieval and pricing
        plan = plan_service.get_plan(1)
        assert plan is not None
        assert plan.devices == 1
        
        # Test price calculation for different durations
        price_30 = plan.get_price(Currency.USD, 30)
        price_90 = plan.get_price(Currency.USD, 90)
        price_365 = plan.get_price(Currency.USD, 365)
        
        assert price_30 == 10
        assert price_90 == 25
        assert price_365 == 90

    async def test_notification_service_with_bot_integration(self, test_config, mock_bot):
        """Test NotificationService integration with bot."""
        notification_service = NotificationService(config=test_config, bot=mock_bot)
        
        # Test developer notification
        await notification_service.notify_developer("Test developer message")
        
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert kwargs['chat_id'] == int(test_config.bot.DEV_ID)
        assert "Test developer message" in kwargs['text']
        
        # Reset mock
        mock_bot.send_message.reset_mock()
        
        # Test support notification
        await notification_service.notify_support("Test support message")
        
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert kwargs['chat_id'] == int(test_config.bot.SUPPORT_ID)
        assert "Test support message" in kwargs['text']


class TestDatabaseIntegration:
    """Test database operations integration."""
    
    async def test_user_transaction_relationship(self, test_db):
        """Test User and Transaction model relationships."""
        async with test_db.session() as session:
            # Create user
            user = await User.create(
                session=session,
                tg_id=123456789,
                first_name="Test User",
                username="testuser",
                language_code="en"
            )
            
            # Create transactions for user
            transaction1 = await Transaction.create(
                session=session,
                tg_id=user.tg_id,
                subscription="subscription_data_1",
                payment_id="payment_1",
                status=TransactionStatus.PENDING
            )
            
            transaction2 = await Transaction.create(
                session=session,
                tg_id=user.tg_id,
                subscription="subscription_data_2", 
                payment_id="payment_2",
                status=TransactionStatus.COMPLETED
            )
            
            # Test getting user transactions
            user_transactions = await Transaction.get_user_transactions(
                session=session,
                tg_id=user.tg_id
            )
            
            assert len(user_transactions) == 2
            assert all(t.tg_id == user.tg_id for t in user_transactions)
            
            # Test transaction statuses
            statuses = [t.status for t in user_transactions]
            assert TransactionStatus.PENDING in statuses
            assert TransactionStatus.COMPLETED in statuses

    async def test_referral_system_integration(self, test_db):
        """Test referral system database integration."""
        from app.db.models import Referral, ReferrerReward
        
        async with test_db.session() as session:
            # Create referrer and referred users
            referrer = await User.create(
                session=session,
                tg_id=111111111,
                first_name="Referrer User",
                username="referrer"
            )
            
            referred = await User.create(
                session=session,
                tg_id=222222222,
                first_name="Referred User", 
                username="referred"
            )
            
            # Create referral relationship
            referral = await Referral.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred.tg_id
            )
            
            # Create referrer reward
            reward = await ReferrerReward.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred.tg_id,
                reward_days=30
            )
            
            # Test referral retrieval
            user_referrals = await Referral.get_user_referrals(
                session=session,
                referrer_tg_id=referrer.tg_id
            )
            
            assert len(user_referrals) == 1
            assert user_referrals[0].referred_tg_id == referred.tg_id
            
            # Test unprocessed rewards
            unprocessed_rewards = await ReferrerReward.get_unprocessed_rewards(session=session)
            assert len(unprocessed_rewards) >= 1
            assert any(r.referrer_tg_id == referrer.tg_id for r in unprocessed_rewards)


class TestPaymentGatewayIntegration:
    """Test payment gateway factory integration."""
    
    async def test_gateway_factory_with_services(self, test_config, test_db, test_storage, mock_bot, test_i18n, test_services):
        """Test GatewayFactory integration with services."""
        factory = GatewayFactory()
        
        # Create mock app for Cryptomus
        mock_app = Mock()
        mock_app.router = Mock()
        mock_app.router.add_post = Mock()
        
        # Configure payment methods
        test_config.shop.PAYMENT_STARS_ENABLED = True
        test_config.shop.PAYMENT_CRYPTOMUS_ENABLED = True
        test_config.cryptomus.API_KEY = "test_key"
        test_config.cryptomus.MERCHANT_ID = "test_merchant"
        
        # Register gateways
        factory.register_gateways(
            app=mock_app,
            config=test_config,
            session=test_db.session,
            storage=test_storage,
            bot=mock_bot,
            i18n=test_i18n,
            services=test_services
        )
        
        # Test gateway retrieval
        gateways = factory.get_gateways()
        assert len(gateways) == 2
        
        # Test specific gateway functionality
        stars_gateway = factory.get_gateway(NavSubscription.PAY_TELEGRAM_STARS)
        cryptomus_gateway = factory.get_gateway(NavSubscription.PAY_CRYPTOMUS)
        
        assert isinstance(stars_gateway, TelegramStars)
        assert isinstance(cryptomus_gateway, Cryptomus)
        
        # Test gateway configuration
        assert stars_gateway.currency == Currency.XTR
        assert cryptomus_gateway.currency == Currency.USD
        assert cryptomus_gateway.api_key == "test_key"
        assert cryptomus_gateway.merchant_id == "test_merchant"


class TestMiddlewareIntegration:
    """Test middleware integration with handlers."""
    
    async def test_database_middleware_user_creation(self, test_db):
        """Test database middleware creates users properly."""
        from app.bot.middlewares.database import DBSessionMiddleware
        
        middleware = DBSessionMiddleware(session=test_db.session)
        
        # Create mock handler
        handler = AsyncMock()
        
        # Create mock event with user
        event = Mock()
        event.event = Mock()
        event.event.from_user = Mock()
        event.event.from_user.id = 123456789
        event.event.from_user.first_name = "Test User"
        event.event.from_user.username = "testuser"
        event.event.from_user.language_code = "en"
        event.event.from_user.is_bot = False
        
        data = {}
        
        # Process through middleware
        await middleware(handler, event, data)
        
        # Verify user was created and added to data
        assert "user" in data
        assert "session" in data
        assert "is_new_user" in data
        assert data["user"].tg_id == 123456789
        assert data["is_new_user"] is True
        
        # Verify handler was called
        handler.assert_called_once_with(event, data)

    async def test_throttling_middleware_integration(self):
        """Test throttling middleware with multiple requests."""
        from app.bot.middlewares.throttling import ThrottlingMiddleware
        from aiogram.types import Update
        
        middleware = ThrottlingMiddleware(default_ttl=0.1)  # Short TTL for testing
        handler = AsyncMock()
        
        # Create mock update
        update = Mock(spec=Update)
        update.event = Mock()
        update.event.from_user = Mock()
        update.event.from_user.id = 123456789
        update.pre_checkout_query = None
        update.message = None
        
        data = {"handler": handler}
        
        with patch('aiogram.dispatcher.flags.get_flag', return_value="default"):
            # First request should pass
            result1 = await middleware(handler, update, data)
            handler.assert_called_once()
            
            handler.reset_mock()
            
            # Second request should be throttled
            result2 = await middleware(handler, update, data)
            assert result2 is None
            handler.assert_not_called()


class TestEndToEndScenarios:
    """End-to-end integration test scenarios."""
    
    async def test_new_user_subscription_flow(self, test_db, test_config, mock_bot, test_i18n, test_services, temp_dir):
        """Test complete flow for new user creating subscription."""
        from app.bot.middlewares.database import DBSessionMiddleware
        
        # Set up services
        plans_file = temp_dir / "plans.json"
        plans_data = {
            "durations": [30],
            "plans": [{"devices": 1, "prices": {"USD": {"30": 10}}}]
        }
        plans_file.write_text(json.dumps(plans_data))
        
        plan_service = PlanService(file_path=str(plans_file))
        
        # Set up middleware
        db_middleware = DBSessionMiddleware(session=test_db.session)
        
        # Mock new user event
        event = Mock()
        event.event = Mock()
        event.event.from_user = Mock()
        event.event.from_user.id = 123456789
        event.event.from_user.first_name = "New User"
        event.event.from_user.username = "newuser"
        event.event.from_user.language_code = "en"
        event.event.from_user.is_bot = False
        
        # Process through database middleware
        data = {}
        handler = AsyncMock()
        await db_middleware(handler, event, data)
        
        # Verify new user was created
        assert "user" in data
        assert data["is_new_user"] is True
        user = data["user"]
        assert user.tg_id == 123456789
        
        # Test subscription creation
        plan = plan_service.get_plan(1)
        assert plan is not None
        
        subscription_data = SubscriptionData(
            user_id=user.tg_id,
            devices=plan.devices,
            duration=30,
            price=plan.get_price(Currency.USD, 30),
            state=NavSubscription.PAY_TELEGRAM_STARS
        )
        
        # Test payment gateway creation
        gateway_factory = GatewayFactory()
        test_config.shop.PAYMENT_STARS_ENABLED = True
        
        telegram_stars = TelegramStars(
            app=None,
            config=test_config,
            session=test_db.session,
            storage=None,
            bot=mock_bot,
            i18n=test_i18n,
            services=test_services
        )
        
        gateway_factory.register_gateway(telegram_stars)
        
        # Mock payment creation
        mock_bot.send_invoice = AsyncMock()
        
        with patch('app.bot.filters.is_dev.IsDev.__call__', return_value=False):
            await telegram_stars.create_payment(subscription_data)
            mock_bot.send_invoice.assert_called_once()

    async def test_error_handling_integration(self, test_db):
        """Test error handling across components."""
        from app.bot.middlewares.database import DBSessionMiddleware
        
        # Test database middleware with database error
        middleware = DBSessionMiddleware(session=test_db.session)
        handler = AsyncMock()
        
        event = Mock()
        event.event = Mock() 
        event.event.from_user = Mock()
        event.event.from_user.id = 123456789
        event.event.from_user.first_name = None  # This might cause issues
        event.event.from_user.username = None
        event.event.from_user.language_code = "en"
        event.event.from_user.is_bot = False
        
        data = {}
        
        # Should handle gracefully even with minimal user data
        await middleware(handler, event, data)
        
        # Handler should still be called
        handler.assert_called_once_with(event, data)

    async def test_performance_integration(self, test_db):
        """Test system performance under load."""
        from app.bot.middlewares.database import DBSessionMiddleware
        import asyncio
        
        middleware = DBSessionMiddleware(session=test_db.session)
        
        async def process_user_request(user_id: int):
            """Simulate processing a user request."""
            event = Mock()
            event.event = Mock()
            event.event.from_user = Mock()
            event.event.from_user.id = user_id
            event.event.from_user.first_name = f"User{user_id}"
            event.event.from_user.username = f"user{user_id}"
            event.event.from_user.language_code = "en"
            event.event.from_user.is_bot = False
            
            handler = AsyncMock()
            data = {}
            
            await middleware(handler, event, data)
            return data["user"] if "user" in data else None
        
        # Process multiple concurrent requests
        user_ids = list(range(100000, 100010))  # 10 different users
        
        start_time = datetime.now()
        tasks = [process_user_request(user_id) for user_id in user_ids]
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # Verify all requests completed
        assert len(results) == len(user_ids)
        assert all(user is not None for user in results)
        
        # Verify reasonable performance (should complete quickly)
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 5.0  # Should complete within 5 seconds