"""
Pytest configuration and shared fixtures for 3xui-shop tests.
"""
import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import fakeredis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Config, load_config
from app.db.database import Database
from app.db.models import Base, User


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_config(temp_dir: Path) -> Config:
    """Create a test configuration."""
    # Set test environment variables
    os.environ.update({
        "BOT_TOKEN": "1234567890:test_token_for_testing_only",
        "BOT_DEV_ID": "123456789",
        "BOT_SUPPORT_ID": "123456789",
        "BOT_DOMAIN": "test.example.com",
        "BOT_PORT": "8080",
        "SHOP_EMAIL": "test@example.com",
        "SHOP_CURRENCY": "USD",
        "SHOP_TRIAL_ENABLED": "True",
        "SHOP_TRIAL_PERIOD": "3",
        "SHOP_REFERRED_TRIAL_ENABLED": "False",
        "SHOP_REFERRED_TRIAL_PERIOD": "7",
        "SHOP_REFERRER_REWARD_ENABLED": "True",
        "SHOP_REFERRER_LEVEL_ONE_PERIOD": "10",
        "SHOP_REFERRER_LEVEL_TWO_PERIOD": "3",
        "SHOP_PAYMENT_STARS_ENABLED": "True",
        "SHOP_PAYMENT_CRYPTOMUS_ENABLED": "False",
        "DB_NAME": ":memory:",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "LOG_LEVEL": "DEBUG"
    })
    
    # Create test plans.json
    test_plans = temp_dir / "plans.json"
    test_plans.write_text('''
    {
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
    ''')
    
    # Create test products.json
    test_products = temp_dir / "products.json"
    test_products.write_text('''
    {
        "categories": ["software", "gaming", "digital"],
        "products": [
            {
                "id": "test_product_1",
                "name": "Test Software License",
                "description": "A test software license",
                "category": "software",
                "price": {"amount": 999, "currency": "USD"},
                "duration_days": 365,
                "delivery_type": "license_key",
                "delivery_template": "Your license: {license_key}",
                "key_format": "XXXX-XXXX-XXXX",
                "stock": 10,
                "is_active": true
            }
        ]
    }
    ''')
    
    return load_config()


@pytest.fixture
async def test_db(temp_dir: Path):
    """Create a test database."""
    db_path = temp_dir / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a simple mock database class for testing
    class TestDatabase:
        def __init__(self, engine, session_factory):
            self.engine = engine
            self.session = session_factory
        
        async def close(self):
            await self.engine.dispose()
    
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    db = TestDatabase(engine, session_factory)
    
    yield db
    
    # Cleanup
    await db.close()


@pytest.fixture
def fake_redis():
    """Create a fake Redis instance for testing."""
    return fakeredis.FakeRedis()


@pytest.fixture
def mock_bot() -> Bot:
    """Create a mock bot instance."""
    bot = MagicMock(spec=Bot)
    bot.id = 123456789
    bot.username = "test_bot"
    bot.token = "1234567890:test_token_for_testing_only"
    
    # Mock async methods
    bot.get_me = AsyncMock()
    bot.send_message = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.delete_message = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    bot.set_webhook = AsyncMock()
    bot.delete_webhook = AsyncMock()
    bot.get_webhook_info = AsyncMock()
    
    return bot


@pytest.fixture
async def test_storage(fake_redis) -> RedisStorage:
    """Create a test Redis storage."""
    return RedisStorage(redis=fake_redis)


@pytest.fixture
def test_i18n() -> I18n:
    """Create a test i18n instance."""
    # Use a mock I18n for testing
    i18n = MagicMock(spec=I18n)
    i18n.get = MagicMock(return_value="Test Message")
    return i18n


@pytest.fixture
async def test_services(test_config: Config, test_db: Database, mock_bot: Bot):
    """Create a test services container."""
    # Create a mock services container to avoid circular imports
    services = MagicMock()
    services.plan = MagicMock()
    services.product = MagicMock()
    services.notification = MagicMock()
    services.referral = MagicMock()
    services.subscription = MagicMock()
    services.payment_stats = MagicMock()
    services.invite_stats = MagicMock()
    return services


@pytest.fixture
def test_gateway_factory(test_config: Config, test_db: Database, test_storage: RedisStorage, 
                        mock_bot: Bot, test_i18n: I18n, test_services):
    """Create a test gateway factory."""
    # Create a mock gateway factory to avoid circular imports
    from unittest.mock import MagicMock
    factory = MagicMock()
    
    # We'll mock the gateway registration since we don't want real payment gateways in tests
    mock_gateway = MagicMock()
    mock_gateway.name = "Test Gateway"
    mock_gateway.callback = "test_gateway"
    factory._gateways = {"test_gateway": mock_gateway}
    factory.get_gateways.return_value = [mock_gateway]
    factory.get_gateway.return_value = mock_gateway
    
    return factory


@pytest.fixture
def test_dispatcher(test_config: Config, test_db: Database, test_storage: RedisStorage,
                   mock_bot: Bot, test_services, test_gateway_factory):
    """Create a test dispatcher."""
    # Mock dispatcher to avoid complex initialization
    dispatcher = MagicMock()
    dispatcher.config = test_config
    dispatcher.db = test_db
    dispatcher.storage = test_storage
    dispatcher.bot = mock_bot
    dispatcher.services = test_services
    dispatcher.gateway_factory = test_gateway_factory
    return dispatcher


@pytest.fixture
async def test_user(test_db: Database) -> User:
    """Create a test user."""
    async with test_db.session() as session:
        user = await User.create(
            session=session,
            tg_id=123456789,
            first_name="Test",
            username="testuser",
            language_code="en"
        )
        return user


@pytest.fixture
def mock_message():
    """Create a mock Telegram message."""
    message = MagicMock()
    message.message_id = 1
    message.from_user.id = 123456789
    message.from_user.first_name = "Test"
    message.from_user.username = "testuser"
    message.from_user.language_code = "en"
    message.from_user.is_bot = False
    message.chat.id = 123456789
    message.text = "/start"
    message.date = None
    
    # Mock async methods
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.delete = AsyncMock()
    
    return message


@pytest.fixture
def mock_callback_query(mock_message):
    """Create a mock Telegram callback query."""
    callback = MagicMock()
    callback.id = "test_callback_id"
    callback.from_user.id = 123456789
    callback.from_user.first_name = "Test"
    callback.from_user.username = "testuser"
    callback.from_user.language_code = "en"
    callback.from_user.is_bot = False
    callback.message = mock_message
    callback.data = "test_callback_data"
    
    # Mock async methods
    callback.answer = AsyncMock()
    callback.edit_message_text = AsyncMock()
    callback.message.edit_text = AsyncMock()
    
    return callback