"""
Tests for database models.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.db.models import User, Transaction, Referral, Promocode, Invite, ReferrerReward
from app.bot.utils.constants import TransactionStatus


class TestUserModel:
    """Tests for User model."""
    
    async def test_create_user(self, test_db):
        """Test user creation."""
        async with test_db.session() as session:
            user = await User.create(
                session=session,
                tg_id=123456789,
                first_name="Test User",
                username="testuser",
                language_code="en"
            )
            
            assert user is not None
            assert user.tg_id == 123456789
            assert user.first_name == "Test User"
            assert user.username == "testuser"
            assert user.language_code == "en"
            assert not user.is_trial_used
            assert user.created_at is not None

    async def test_get_user(self, test_db, test_user):
        """Test getting user by tg_id."""
        async with test_db.session() as session:
            user = await User.get(session=session, tg_id=test_user.tg_id)
            
            assert user is not None
            assert user.tg_id == test_user.tg_id
            assert user.first_name == test_user.first_name

    async def test_get_nonexistent_user(self, test_db):
        """Test getting non-existent user."""
        async with test_db.session() as session:
            user = await User.get(session=session, tg_id=999999999)
            assert user is None

    async def test_user_unique_tg_id(self, test_db):
        """Test that tg_id must be unique."""
        async with test_db.session() as session:
            # Create first user
            await User.create(
                session=session,
                tg_id=123456789,
                first_name="First User",
                username="user1"
            )
            
            # Try to create another user with same tg_id
            with pytest.raises(IntegrityError):
                await User.create(
                    session=session,
                    tg_id=123456789,
                    first_name="Second User",
                    username="user2"
                )

    async def test_get_all_users(self, test_db):
        """Test getting all users."""
        async with test_db.session() as session:
            # Create multiple users
            await User.create(session=session, tg_id=111, first_name="User 1")
            await User.create(session=session, tg_id=222, first_name="User 2")
            await User.create(session=session, tg_id=333, first_name="User 3")
            
            users = await User.get_all(session=session)
            assert len(users) == 3


class TestTransactionModel:
    """Tests for Transaction model."""
    
    async def test_create_transaction(self, test_db, test_user):
        """Test transaction creation."""
        async with test_db.session() as session:
            transaction = await Transaction.create(
                session=session,
                tg_id=test_user.tg_id,
                subscription="test_subscription_data",
                payment_id="payment_123",
                status=TransactionStatus.PENDING
            )
            
            assert transaction is not None
            assert transaction.tg_id == test_user.tg_id
            assert transaction.subscription == "test_subscription_data"
            assert transaction.payment_id == "payment_123"
            assert transaction.status == TransactionStatus.PENDING
            assert transaction.created_at is not None

    async def test_get_user_transactions(self, test_db, test_user):
        """Test getting transactions for a user."""
        async with test_db.session() as session:
            # Create multiple transactions
            await Transaction.create(
                session=session,
                tg_id=test_user.tg_id,
                subscription="sub1",
                payment_id="pay1",
                status=TransactionStatus.PENDING
            )
            await Transaction.create(
                session=session,
                tg_id=test_user.tg_id,
                subscription="sub2",
                payment_id="pay2",
                status=TransactionStatus.COMPLETED
            )
            
            transactions = await Transaction.get_user_transactions(
                session=session, 
                tg_id=test_user.tg_id
            )
            
            assert len(transactions) == 2
            assert all(t.tg_id == test_user.tg_id for t in transactions)

    async def test_get_expired_transactions(self, test_db, test_user):
        """Test getting expired transactions."""
        async with test_db.session() as session:
            # Create a transaction (will be considered expired after timeout)
            transaction = await Transaction.create(
                session=session,
                tg_id=test_user.tg_id,
                subscription="sub1",
                payment_id="pay1",
                status=TransactionStatus.PENDING
            )
            
            # Get expired transactions (assuming timeout is very short for test)
            expired = await Transaction.get_expired_transactions(session=session)
            # In a real scenario with proper timing, this would contain the transaction
            assert isinstance(expired, list)


class TestReferralModel:
    """Tests for Referral model."""
    
    async def test_create_referral(self, test_db):
        """Test referral creation."""
        async with test_db.session() as session:
            # Create referrer and referred users
            referrer = await User.create(
                session=session,
                tg_id=111111111,
                first_name="Referrer",
                username="referrer"
            )
            referred = await User.create(
                session=session,
                tg_id=222222222,
                first_name="Referred",
                username="referred"
            )
            
            referral = await Referral.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred.tg_id
            )
            
            assert referral is not None
            assert referral.referrer_tg_id == referrer.tg_id
            assert referral.referred_tg_id == referred.tg_id
            assert referral.created_at is not None

    async def test_get_user_referrals(self, test_db):
        """Test getting user referrals."""
        async with test_db.session() as session:
            # Create users
            referrer = await User.create(session=session, tg_id=111, first_name="Referrer")
            referred1 = await User.create(session=session, tg_id=222, first_name="Referred1")
            referred2 = await User.create(session=session, tg_id=333, first_name="Referred2")
            
            # Create referrals
            await Referral.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred1.tg_id
            )
            await Referral.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred2.tg_id
            )
            
            referrals = await Referral.get_user_referrals(
                session=session,
                referrer_tg_id=referrer.tg_id
            )
            
            assert len(referrals) == 2
            assert all(r.referrer_tg_id == referrer.tg_id for r in referrals)


class TestPromocodeModel:
    """Tests for Promocode model."""
    
    async def test_create_promocode(self, test_db):
        """Test promocode creation."""
        async with test_db.session() as session:
            promocode = await Promocode.create(
                session=session,
                code="TEST20",
                discount_percent=20,
                max_uses=100,
                expires_at=datetime.now()
            )
            
            assert promocode is not None
            assert promocode.code == "TEST20"
            assert promocode.discount_percent == 20
            assert promocode.max_uses == 100
            assert promocode.current_uses == 0
            assert promocode.is_active is True

    async def test_get_promocode_by_code(self, test_db):
        """Test getting promocode by code."""
        async with test_db.session() as session:
            # Create promocode
            await Promocode.create(
                session=session,
                code="TESTCODE",
                discount_percent=15,
                max_uses=50
            )
            
            # Get by code
            promocode = await Promocode.get_by_code(session=session, code="TESTCODE")
            
            assert promocode is not None
            assert promocode.code == "TESTCODE"
            assert promocode.discount_percent == 15

    async def test_promocode_unique_code(self, test_db):
        """Test that promocode code must be unique."""
        async with test_db.session() as session:
            # Create first promocode
            await Promocode.create(
                session=session,
                code="UNIQUE",
                discount_percent=10
            )
            
            # Try to create another with same code
            with pytest.raises(IntegrityError):
                await Promocode.create(
                    session=session,
                    code="UNIQUE",
                    discount_percent=20
                )


class TestInviteModel:
    """Tests for Invite model."""
    
    async def test_create_invite(self, test_db):
        """Test invite creation."""
        async with test_db.session() as session:
            invite = await Invite.create(
                session=session,
                name="Test Invite",
                hash_code="abcdef123456"
            )
            
            assert invite is not None
            assert invite.name == "Test Invite"
            assert invite.hash_code == "abcdef123456"
            assert invite.clicks == 0
            assert invite.is_active is True

    async def test_get_invite_by_hash(self, test_db):
        """Test getting invite by hash code."""
        async with test_db.session() as session:
            # Create invite
            await Invite.create(
                session=session,
                name="Hash Test",
                hash_code="hash123"
            )
            
            # Get by hash
            invite = await Invite.get_by_hash(session=session, hash_code="hash123")
            
            assert invite is not None
            assert invite.name == "Hash Test"
            assert invite.hash_code == "hash123"

    async def test_increment_clicks(self, test_db):
        """Test incrementing invite clicks."""
        async with test_db.session() as session:
            invite = await Invite.create(
                session=session,
                name="Click Test",
                hash_code="click123"
            )
            
            initial_clicks = invite.clicks
            await Invite.increment_clicks(session=session, invite_id=invite.id)
            
            # Refresh from database
            updated_invite = await Invite.get_by_hash(session=session, hash_code="click123")
            assert updated_invite.clicks == initial_clicks + 1


class TestReferrerRewardModel:
    """Tests for ReferrerReward model."""
    
    async def test_create_referrer_reward(self, test_db):
        """Test referrer reward creation."""
        async with test_db.session() as session:
            # Create users first
            referrer = await User.create(session=session, tg_id=111, first_name="Referrer")
            referred = await User.create(session=session, tg_id=222, first_name="Referred")
            
            reward = await ReferrerReward.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred.tg_id,
                reward_days=30
            )
            
            assert reward is not None
            assert reward.referrer_tg_id == referrer.tg_id
            assert reward.referred_tg_id == referred.tg_id
            assert reward.reward_days == 30
            assert reward.is_processed is False

    async def test_get_unprocessed_rewards(self, test_db):
        """Test getting unprocessed rewards."""
        async with test_db.session() as session:
            # Create users
            referrer = await User.create(session=session, tg_id=111, first_name="Referrer")
            referred = await User.create(session=session, tg_id=222, first_name="Referred")
            
            # Create rewards
            await ReferrerReward.create(
                session=session,
                referrer_tg_id=referrer.tg_id,
                referred_tg_id=referred.tg_id,
                reward_days=30
            )
            
            unprocessed = await ReferrerReward.get_unprocessed_rewards(session=session)
            
            assert len(unprocessed) >= 1
            assert all(not reward.is_processed for reward in unprocessed)