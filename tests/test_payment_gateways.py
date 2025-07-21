"""
Tests for payment gateways.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from aioresponses import aioresponses

from app.bot.payment_gateways.gateway_factory import GatewayFactory
from app.bot.payment_gateways.telegram_stars import TelegramStars
from app.bot.payment_gateways.cryptomus import Cryptomus
from app.bot.models import SubscriptionData
from app.bot.utils.constants import Currency
from app.bot.utils.navigation import NavSubscription


class TestGatewayFactory:
    """Tests for GatewayFactory."""
    
    def test_register_gateway(self):
        """Test gateway registration."""
        factory = GatewayFactory()
        
        mock_gateway = Mock()
        mock_gateway.callback = "test_gateway"
        
        factory.register_gateway(mock_gateway)
        
        assert "test_gateway" in factory._gateways
        assert factory._gateways["test_gateway"] == mock_gateway

    def test_get_gateway(self):
        """Test getting a registered gateway."""
        factory = GatewayFactory()
        
        mock_gateway = Mock()
        mock_gateway.callback = "test_gateway"
        factory._gateways["test_gateway"] = mock_gateway
        
        retrieved = factory.get_gateway("test_gateway")
        assert retrieved == mock_gateway

    def test_get_nonexistent_gateway(self):
        """Test getting a non-existent gateway raises error."""
        factory = GatewayFactory()
        
        with pytest.raises(ValueError, match="Gateway nonexistent is not registered"):
            factory.get_gateway("nonexistent")

    def test_get_gateways(self):
        """Test getting all gateways."""
        factory = GatewayFactory()
        
        gateway1 = Mock()
        gateway1.callback = "gateway1"
        gateway2 = Mock()
        gateway2.callback = "gateway2"
        
        factory._gateways = {"gateway1": gateway1, "gateway2": gateway2}
        
        gateways = factory.get_gateways()
        assert len(gateways) == 2
        assert gateway1 in gateways
        assert gateway2 in gateways


class TestTelegramStars:
    """Tests for TelegramStars payment gateway."""
    
    @pytest.fixture
    def telegram_stars(self, test_config, test_db, test_storage, mock_bot, test_i18n, test_services):
        """Create TelegramStars instance for testing."""
        return TelegramStars(
            app=None,  # Not needed for unit tests
            config=test_config,
            session=test_db.session,
            storage=test_storage,
            bot=mock_bot,
            i18n=test_i18n,
            services=test_services
        )

    def test_initialization(self, telegram_stars):
        """Test TelegramStars initialization."""
        assert telegram_stars.currency == Currency.XTR
        assert telegram_stars.callback == NavSubscription.PAY_TELEGRAM_STARS
        assert telegram_stars.name is not None

    async def test_create_payment_dev_mode(self, telegram_stars):
        """Test payment creation in dev mode."""
        subscription_data = SubscriptionData(
            user_id=123456789,  # This matches BOT_DEV_ID in test config
            devices=1,
            duration=30,
            price=1000,
            state=NavSubscription.PAY_TELEGRAM_STARS
        )
        
        with patch('app.bot.filters.is_dev.IsDev.__call__', return_value=True):
            mock_bot = Mock()
            mock_bot.send_invoice = AsyncMock()
            telegram_stars.bot = mock_bot
            
            payment_url = await telegram_stars.create_payment(subscription_data)
            
            mock_bot.send_invoice.assert_called_once()
            call_args = mock_bot.send_invoice.call_args
            
            # In dev mode, amount should be 1 star
            assert call_args.kwargs['prices'][0].amount == 1

    async def test_create_payment_normal_mode(self, telegram_stars):
        """Test payment creation in normal mode."""
        subscription_data = SubscriptionData(
            user_id=987654321,  # Different from BOT_DEV_ID
            devices=1,
            duration=30,
            price=1000,
            state=NavSubscription.PAY_TELEGRAM_STARS
        )
        
        with patch('app.bot.filters.is_dev.IsDev.__call__', return_value=False):
            mock_bot = Mock()
            mock_bot.send_invoice = AsyncMock()
            telegram_stars.bot = mock_bot
            
            payment_url = await telegram_stars.create_payment(subscription_data)
            
            mock_bot.send_invoice.assert_called_once()
            call_args = mock_bot.send_invoice.call_args
            
            # In normal mode, amount should match the price
            assert call_args.kwargs['prices'][0].amount == 1000

    async def test_handle_payment_succeeded(self, telegram_stars):
        """Test handling successful payment."""
        payment_id = "test_payment_123"
        
        # Mock the services and their methods
        telegram_stars.services.subscription = Mock()
        telegram_stars.services.subscription.process_payment = AsyncMock()
        telegram_stars.services.notification = Mock()
        telegram_stars.services.notification.notify_developer = AsyncMock()
        
        await telegram_stars.handle_payment_succeeded(payment_id)
        
        # Verify notification was sent
        telegram_stars.services.notification.notify_developer.assert_called_once()


class TestCryptomus:
    """Tests for Cryptomus payment gateway."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock aiohttp application."""
        app = Mock()
        app.router = Mock()
        app.router.add_post = Mock()
        return app

    @pytest.fixture
    def cryptomus(self, mock_app, test_config, test_db, test_storage, mock_bot, test_i18n, test_services):
        """Create Cryptomus instance for testing."""
        # Set up Cryptomus credentials in config
        test_config.cryptomus.API_KEY = "test_api_key"
        test_config.cryptomus.MERCHANT_ID = "test_merchant_id"
        
        return Cryptomus(
            app=mock_app,
            config=test_config,
            session=test_db.session,
            storage=test_storage,
            bot=mock_bot,
            i18n=test_i18n,
            services=test_services
        )

    def test_initialization(self, cryptomus):
        """Test Cryptomus initialization."""
        assert cryptomus.currency == Currency.USD
        assert cryptomus.callback == NavSubscription.PAY_CRYPTOMUS
        assert cryptomus.api_key == "test_api_key"
        assert cryptomus.merchant_id == "test_merchant_id"

    async def test_create_payment(self, cryptomus):
        """Test payment creation."""
        subscription_data = SubscriptionData(
            user_id=123456789,
            devices=1,
            duration=30,
            price=25.00,
            state=NavSubscription.PAY_CRYPTOMUS
        )
        
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
        
        with aioresponses() as m:
            m.post(
                "https://api.cryptomus.com/v1/payment",
                payload=mock_response,
                status=200
            )
            
            payment_url = await cryptomus.create_payment(subscription_data)
            
            assert payment_url == "https://pay.cryptomus.com/pay/test-uuid-123"

    async def test_create_payment_api_error(self, cryptomus):
        """Test payment creation with API error."""
        subscription_data = SubscriptionData(
            user_id=123456789,
            devices=1,
            duration=30,
            price=25.00,
            state=NavSubscription.PAY_CRYPTOMUS
        )
        
        mock_error_response = {
            "state": 1,
            "errors": ["Invalid merchant"]
        }
        
        with aioresponses() as m:
            m.post(
                "https://api.cryptomus.com/v1/payment",
                payload=mock_error_response,
                status=400
            )
            
            with pytest.raises(Exception):
                await cryptomus.create_payment(subscription_data)

    def test_generate_signature(self, cryptomus):
        """Test signature generation."""
        data = {"amount": "25.00", "currency": "USD"}
        
        signature = cryptomus._generate_signature(data)
        
        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_verify_signature(self, cryptomus):
        """Test signature verification."""
        data = {"amount": "25.00", "currency": "USD"}
        signature = cryptomus._generate_signature(data)
        
        # Should verify correctly with correct signature
        assert cryptomus._verify_signature(data, signature) is True
        
        # Should fail with incorrect signature
        assert cryptomus._verify_signature(data, "wrong_signature") is False

    async def test_webhook_handler_valid(self, cryptomus):
        """Test webhook handler with valid request."""
        webhook_data = {
            "uuid": "test-uuid",
            "order_id": "test-order",
            "amount": "25.00",
            "currency": "USD",
            "status": "paid"
        }
        
        # Mock request object
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value=webhook_data)
        mock_request.headers = {"sign": cryptomus._generate_signature(webhook_data)}
        
        # Mock services
        cryptomus.services.subscription = Mock()
        cryptomus.services.subscription.process_payment = AsyncMock()
        
        with patch.object(cryptomus, '_verify_signature', return_value=True):
            response = await cryptomus.webhook_handler(mock_request)
            
            assert response.status == 200

    async def test_webhook_handler_invalid_signature(self, cryptomus):
        """Test webhook handler with invalid signature."""
        webhook_data = {
            "uuid": "test-uuid",
            "status": "paid"
        }
        
        mock_request = Mock()
        mock_request.json = AsyncMock(return_value=webhook_data)
        mock_request.headers = {"sign": "invalid_signature"}
        
        with patch.object(cryptomus, '_verify_signature', return_value=False):
            response = await cryptomus.webhook_handler(mock_request)
            
            assert response.status == 400

    async def test_handle_payment_succeeded(self, cryptomus):
        """Test handling successful payment."""
        payment_data = {
            "uuid": "test-uuid",
            "order_id": "test-order",
            "amount": "25.00",
            "status": "paid"
        }
        
        # Mock services
        cryptomus.services.subscription = Mock()
        cryptomus.services.subscription.process_payment = AsyncMock()
        cryptomus.services.notification = Mock()
        cryptomus.services.notification.notify_developer = AsyncMock()
        
        await cryptomus.handle_payment_succeeded(payment_data)
        
        # Verify notification was sent
        cryptomus.services.notification.notify_developer.assert_called_once()


class TestPaymentGatewayIntegration:
    """Integration tests for payment gateways."""
    
    async def test_gateway_factory_registration(self, test_config, test_db, test_storage, mock_bot, test_i18n, test_services):
        """Test that gateways are properly registered in factory."""
        factory = GatewayFactory()
        
        # Create mock app for Cryptomus
        mock_app = Mock()
        mock_app.router = Mock()
        mock_app.router.add_post = Mock()
        
        # Enable both payment methods in config
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
        
        # Verify both gateways are registered
        gateways = factory.get_gateways()
        assert len(gateways) == 2
        
        # Verify specific gateways can be retrieved
        stars_gateway = factory.get_gateway(NavSubscription.PAY_TELEGRAM_STARS)
        cryptomus_gateway = factory.get_gateway(NavSubscription.PAY_CRYPTOMUS)
        
        assert isinstance(stars_gateway, TelegramStars)
        assert isinstance(cryptomus_gateway, Cryptomus)