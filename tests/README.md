# Test Suite for 3xui-shop

This directory contains comprehensive unit and integration tests for the 3xui-shop digital products Telegram bot.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_models.py`** - Database model tests
- **`test_services.py`** - Business logic service tests  
- **`test_middlewares.py`** - Telegram bot middleware tests
- **`test_payment_gateways.py`** - Payment gateway functionality tests
- **`test_utils.py`** - Utility function tests
- **`test_integration.py`** - End-to-end integration tests

### Test Coverage Areas

#### Core Database Models (`test_models.py`)
- User model creation, retrieval, and validation
- Transaction model with various statuses
- Referral system relationships
- Promocode functionality
- Invite tracking system
- Referrer reward processing

#### Business Services (`test_services.py`)
- Plan management and pricing
- Product catalog handling
- Notification system
- Referral reward processing
- Subscription management
- Payment statistics
- Invite analytics

#### Bot Middlewares (`test_middlewares.py`)
- Database session management and user creation
- Request throttling and rate limiting
- Maintenance mode handling
- Message garbage collection
- Middleware chaining and blocking

#### Payment Gateways (`test_payment_gateways.py`)
- Telegram Stars payment processing
- Cryptomus cryptocurrency payments
- Gateway factory pattern
- Payment webhooks and callbacks
- Signature verification
- Error handling and retries

#### Utility Functions (`test_utils.py`)
- Data formatting (sizes, time, subscriptions)
- Input validation (hosts, IDs, text)
- Time manipulation and calculations
- Network utilities and URL parsing

#### Integration Tests (`test_integration.py`)
- Complete payment flows
- Service interactions
- Database relationships
- Middleware integration
- End-to-end user scenarios
- Error handling across components
- Performance under load

## Running Tests

### Prerequisites

Ensure you have installed the test dependencies from `pyproject.toml`:

```bash
pip install -e ".[dev]"
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestUserModel

# Run specific test function
pytest tests/test_models.py::TestUserModel::test_create_user
```

### Test Coverage

```bash
# Run tests with coverage report
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

### Running Specific Test Types

```bash
# Run only unit tests (exclude integration)
pytest -k "not test_integration"

# Run only integration tests
pytest tests/test_integration.py

# Run tests for specific component
pytest -k "payment"
```

### Test Configuration Options

```bash
# Run tests in parallel (if pytest-xdist installed)
pytest -n 4

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run only failed tests from last run
pytest --lf

# Re-run failed tests first
pytest --ff
```

## Test Configuration

### Environment Variables

Tests use environment variables defined in `conftest.py`:

- `BOT_TOKEN` - Test bot token (fake)
- `BOT_DEV_ID` / `BOT_SUPPORT_ID` - Test user IDs
- `DB_NAME` - In-memory SQLite for testing
- `REDIS_HOST` - Fake Redis instance
- Payment gateway credentials for testing

### Test Fixtures

#### Database Fixtures
- `test_db` - Isolated SQLite database per test
- `test_user` - Pre-created test user
- `test_config` - Test configuration with safe values

#### Bot Fixtures  
- `mock_bot` - Mocked aiogram Bot instance
- `test_storage` - Fake Redis FSM storage
- `test_i18n` - Mocked internationalization
- `test_services` - Service container with mocks

#### Utility Fixtures
- `temp_dir` - Temporary directory for test files
- `mock_message` / `mock_callback_query` - Telegram event mocks

## Writing New Tests

### Test Naming Convention

- Test files: `test_<component>.py`
- Test classes: `Test<ClassName>`  
- Test methods: `test_<functionality>_<scenario>`

Example:
```python
class TestPaymentGateway:
    async def test_create_payment_success(self):
        """Test successful payment creation."""
        pass
        
    async def test_create_payment_api_error(self):
        """Test payment creation with API error.""" 
        pass
```

### Async Test Functions

Most tests are async due to the async nature of the application:

```python
async def test_database_operation(self, test_db):
    async with test_db.session() as session:
        # Test database operations
        pass
```

### Mocking Guidelines

- Use `unittest.mock.Mock` for simple objects
- Use `unittest.mock.AsyncMock` for async callables
- Use `patch` decorator for replacing imports
- Use `aioresponses` for HTTP API calls

```python
from unittest.mock import Mock, AsyncMock, patch
from aioresponses import aioresponses

@patch('app.module.external_function')
async def test_with_mock(self, mock_func):
    mock_func.return_value = "mocked result"
    # Test code
```

### Database Testing

```python
async def test_model_creation(self, test_db):
    async with test_db.session() as session:
        model = await Model.create(
            session=session,
            field="value"
        )
        assert model.field == "value"
```

### Payment Gateway Testing

```python
async def test_payment_api_call(self):
    with aioresponses() as m:
        m.post("https://api.example.com/payment", 
               payload={"status": "success"})
        
        result = await gateway.create_payment(data)
        assert result is not None
```

## Test Data Management

### Test Isolation

Each test runs in isolation:
- Fresh database for each test function
- Clean Redis instance
- Independent temporary directories
- Reset mocks between tests

### Test Data Creation

Create test data within tests or use fixtures:

```python
@pytest.fixture
async def test_subscription(self, test_db, test_user):
    async with test_db.session() as session:
        return await Subscription.create(
            session=session,
            user_id=test_user.tg_id,
            # ... other fields
        )
```

## Debugging Tests

### Common Issues

1. **Database Connection Errors**
   - Ensure `test_db` fixture is used
   - Check async session usage

2. **Mock Not Being Called**
   - Verify import paths in patches
   - Check if method is being called correctly

3. **Async/Await Issues**  
   - Ensure async functions use `await`
   - Use `AsyncMock` for async callables

### Debugging Tools

```bash
# Run with Python debugger
pytest --pdb

# Run with enhanced tracebacks
pytest --tb=long

# Show print statements
pytest -s
```

## Continuous Integration

Tests are designed to run in CI environments:

- No external dependencies
- Fast execution (< 2 minutes)
- Isolated test environment
- Clear pass/fail criteria

For CI configuration, ensure:
- Python 3.11+ environment
- Install dependencies with `pip install -e ".[dev]"`
- Run `pytest --cov=app` for coverage reporting

## Performance Considerations

Test suite is optimized for:
- **Speed** - Uses in-memory SQLite and fake Redis
- **Isolation** - Each test is independent 
- **Coverage** - Comprehensive testing of all components
- **Reliability** - Deterministic behavior

Target execution time: < 2 minutes for full suite