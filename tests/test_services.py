"""
Tests for bot services.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, mock_open
from pathlib import Path

from app.bot.services.plan import PlanService
from app.bot.services.product import ProductService
from app.bot.services.notification import NotificationService
from app.bot.services.referral import ReferralService
from app.bot.services.subscription import SubscriptionService
from app.bot.services.payment_stats import PaymentStatsService
from app.bot.services.invite_stats import InviteStatsService
from app.bot.utils.constants import Currency


class TestPlanService:
    """Tests for PlanService."""
    
    def test_init_with_valid_file(self, temp_dir):
        """Test PlanService initialization with valid file."""
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
        
        plan_service = PlanService(file_path=str(plans_file))
        
        assert plan_service.data == plans_data
        assert plan_service.get_durations() == [30, 90, 365]

    def test_init_with_invalid_file(self, temp_dir):
        """Test PlanService initialization with invalid file."""
        plans_file = temp_dir / "invalid.json"
        plans_file.write_text("invalid json content")
        
        with pytest.raises(ValueError):
            PlanService(file_path=str(plans_file))

    def test_get_plan(self, temp_dir):
        """Test getting a plan by devices count."""
        plans_file = temp_dir / "plans.json"
        plans_data = {
            "durations": [30, 90],
            "plans": [
                {
                    "devices": 1,
                    "prices": {"USD": {"30": 10, "90": 25}}
                },
                {
                    "devices": 3,
                    "prices": {"USD": {"30": 25, "90": 60}}
                }
            ]
        }
        plans_file.write_text(json.dumps(plans_data))
        
        plan_service = PlanService(file_path=str(plans_file))
        
        plan = plan_service.get_plan(1)
        assert plan is not None
        assert plan.devices == 1
        
        plan = plan_service.get_plan(3)
        assert plan is not None
        assert plan.devices == 3
        
        plan = plan_service.get_plan(5)
        assert plan is None

    def test_get_all_plans(self, temp_dir):
        """Test getting all plans."""
        plans_file = temp_dir / "plans.json"
        plans_data = {
            "durations": [30],
            "plans": [
                {"devices": 1, "prices": {"USD": {"30": 10}}},
                {"devices": 3, "prices": {"USD": {"30": 25}}}
            ]
        }
        plans_file.write_text(json.dumps(plans_data))
        
        plan_service = PlanService(file_path=str(plans_file))
        plans = plan_service.get_all_plans()
        
        assert len(plans) == 2
        assert plans[0].devices == 1
        assert plans[1].devices == 3


class TestProductService:
    """Tests for ProductService."""
    
    @pytest.fixture
    def product_service(self, test_config, test_db, mock_bot):
        """Create ProductService instance for testing."""
        return ProductService(
            config=test_config,
            session=test_db.session,
            bot=mock_bot
        )

    async def test_get_product_catalog(self, product_service):
        """Test getting product catalog."""
        with patch("builtins.open", mock_open(read_data=json.dumps({
            "categories": ["software", "gaming"],
            "products": [
                {
                    "id": "test_product",
                    "name": "Test Product",
                    "description": "A test product",
                    "category": "software",
                    "price": {"amount": 100, "currency": "USD"},
                    "duration_days": 30,
                    "delivery_type": "license_key",
                    "is_active": True
                }
            ]
        }))):
            catalog = await product_service.get_product_catalog()
            
            assert "categories" in catalog
            assert "products" in catalog
            assert len(catalog["products"]) == 1
            assert catalog["products"][0]["id"] == "test_product"

    async def test_get_product_by_id(self, product_service):
        """Test getting product by ID."""
        test_products = [
            {
                "id": "product_1",
                "name": "Product 1",
                "category": "software",
                "price": {"amount": 100, "currency": "USD"},
                "is_active": True
            }
        ]
        
        with patch.object(product_service, 'products', test_products):
            product = await product_service.get_product_by_id("product_1")
            
            assert product is not None
            assert product["id"] == "product_1"
            assert product["name"] == "Product 1"
            
            nonexistent = await product_service.get_product_by_id("nonexistent")
            assert nonexistent is None

    async def test_deliver_product(self, product_service, test_user):
        """Test product delivery."""
        product = {
            "id": "test_product",
            "delivery_type": "license_key",
            "delivery_template": "Your key: {license_key}",
            "key_format": "XXXX-XXXX"
        }
        
        with patch.object(product_service, '_generate_license_key', return_value="TEST-KEY"):
            delivery_info = await product_service.deliver_product(product, test_user)
            
            assert delivery_info is not None
            assert "Your key: TEST-KEY" in delivery_info

    async def test_get_user_subscription_info(self, product_service, test_user):
        """Test getting user subscription info."""
        # Mock subscription data
        with patch.object(product_service, 'user_subscriptions', {test_user.tg_id: {
            'status': 'active',
            'expires_at': '2024-12-31',
            'product_id': 'test_product'
        }}):
            info = await product_service.get_user_subscription_info(test_user)
            
            assert info is not None
            assert info['status'] == 'active'
            assert info['product_id'] == 'test_product'


class TestNotificationService:
    """Tests for NotificationService."""
    
    @pytest.fixture
    def notification_service(self, test_config, mock_bot):
        """Create NotificationService instance for testing."""
        return NotificationService(config=test_config, bot=mock_bot)

    async def test_notify_developer(self, notification_service, mock_bot):
        """Test developer notification."""
        await notification_service.notify_developer("Test notification")
        
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert kwargs['chat_id'] == int(notification_service.config.bot.DEV_ID)
        assert "Test notification" in kwargs['text']

    async def test_notify_support(self, notification_service, mock_bot):
        """Test support notification."""
        await notification_service.notify_support("Support message")
        
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert kwargs['chat_id'] == int(notification_service.config.bot.SUPPORT_ID)
        assert "Support message" in kwargs['text']

    async def test_show_popup(self, notification_service, mock_callback_query):
        """Test popup notification."""
        await notification_service.show_popup(
            callback=mock_callback_query,
            text="Popup message"
        )
        
        mock_callback_query.answer.assert_called_once_with(
            text="Popup message",
            show_alert=False
        )

    async def test_show_alert(self, notification_service, mock_callback_query):
        """Test alert notification."""
        await notification_service.show_alert(
            callback=mock_callback_query,
            text="Alert message"
        )
        
        mock_callback_query.answer.assert_called_once_with(
            text="Alert message",
            show_alert=True
        )


class TestReferralService:
    """Tests for ReferralService."""
    
    @pytest.fixture
    def referral_service(self, test_config, test_db):
        """Create ReferralService instance for testing."""
        return ReferralService(config=test_config, session=test_db.session)

    async def test_is_referred_trial_available(self, referral_service, test_user):
        """Test checking if referred trial is available."""
        # Mock referral existence
        with patch('app.db.models.Referral.get_by_referred_tg_id', return_value=Mock()):
            result = await referral_service.is_referred_trial_available(test_user)
            assert isinstance(result, bool)

    async def test_create_referral_reward(self, referral_service):
        """Test creating referral reward."""
        with patch('app.db.models.ReferrerReward.create') as mock_create:
            await referral_service.create_referral_reward(
                referrer_tg_id=111,
                referred_tg_id=222,
                reward_days=30
            )
            
            mock_create.assert_called_once()

    async def test_get_referral_stats(self, referral_service):
        """Test getting referral statistics."""
        with patch('app.db.models.Referral.get_user_referrals', return_value=[Mock(), Mock()]):
            stats = await referral_service.get_referral_stats(user_id=123)
            
            assert 'total_referrals' in stats
            assert stats['total_referrals'] >= 0


class TestSubscriptionService:
    """Tests for SubscriptionService."""
    
    @pytest.fixture
    def subscription_service(self, test_config, test_db):
        """Create SubscriptionService instance for testing."""
        return SubscriptionService(config=test_config, session=test_db.session)

    async def test_is_trial_available(self, subscription_service, test_user):
        """Test checking if trial is available."""
        # User hasn't used trial yet
        test_user.is_trial_used = False
        result = await subscription_service.is_trial_available(test_user)
        assert result is True
        
        # User has used trial
        test_user.is_trial_used = True
        result = await subscription_service.is_trial_available(test_user)
        assert result is False

    async def test_activate_trial(self, subscription_service, test_user, test_db):
        """Test trial activation."""
        async with test_db.session() as session:
            result = await subscription_service.activate_trial(session, test_user)
            
            assert result is True
            # In real implementation, this would update user's trial status


class TestPaymentStatsService:
    """Tests for PaymentStatsService."""
    
    @pytest.fixture
    def payment_stats_service(self, test_db):
        """Create PaymentStatsService instance for testing."""
        return PaymentStatsService(session=test_db.session)

    async def test_get_total_revenue(self, payment_stats_service):
        """Test getting total revenue."""
        with patch('app.db.models.Transaction.get_completed_transactions', return_value=[]):
            revenue = await payment_stats_service.get_total_revenue()
            assert revenue >= 0

    async def test_get_payment_stats(self, payment_stats_service):
        """Test getting payment statistics."""
        with patch('app.db.models.Transaction.get_all_transactions', return_value=[]):
            stats = await payment_stats_service.get_payment_stats()
            
            assert isinstance(stats, dict)
            assert 'total_transactions' in stats


class TestInviteStatsService:
    """Tests for InviteStatsService."""
    
    @pytest.fixture
    def invite_stats_service(self, test_db):
        """Create InviteStatsService instance for testing."""
        return InviteStatsService(session=test_db.session)

    async def test_get_invite_stats(self, invite_stats_service):
        """Test getting invite statistics."""
        with patch('app.db.models.Invite.get_all_invites', return_value=[]):
            stats = await invite_stats_service.get_invite_stats()
            
            assert isinstance(stats, dict)
            assert 'total_invites' in stats

    async def test_create_invite(self, invite_stats_service):
        """Test creating an invite."""
        with patch('app.db.models.Invite.create') as mock_create:
            await invite_stats_service.create_invite(
                name="Test Invite",
                hash_code="test123"
            )
            
            mock_create.assert_called_once()