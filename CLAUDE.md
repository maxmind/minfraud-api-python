# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**minfraud-api-python** is MaxMind's official Python client library for the minFraud fraud detection services:
- **minFraud Score, Insights, and Factors**: Transaction risk assessment web services
- **Report Transaction**: API for reporting fraudulent transactions to improve detection

The library provides both synchronous and asynchronous clients that validate transaction data, communicate with the minFraud API, and return strongly-typed response models.

**Key Technologies:**
- Python 3.10+ (type hints throughout, uses modern Python features)
- Requests library for sync web service client
- aiohttp for async web service client
- voluptuous for request validation
- email_validator for email validation
- geoip2 library for IP geolocation data models (dependency)
- pytest for testing
- ruff for linting and formatting
- mypy for static type checking
- uv for dependency management and building

## Code Architecture

### Package Structure

```
src/minfraud/
├── models.py           # Response models (Score, Insights, Factors, etc.)
├── webservice.py       # HTTP clients (sync Client and async AsyncClient)
├── request.py          # Request preparation and email normalization
├── validation.py       # Request validation schemas (voluptuous)
├── errors.py           # Custom exceptions for error handling
└── version.py          # Version information
```

### Key Design Patterns

#### 1. **Client Architecture**

Two client types for different use cases:
- **`Client`** (sync) - Uses `requests` library for synchronous API calls
- **`AsyncClient`** (async) - Uses `aiohttp` for asynchronous API calls

Both clients:
- Extend `BaseClient` which handles URI construction and error handling
- Accept account ID, license key, optional host (for sandbox), locales, and timeout
- Support context manager protocol (`with` / `async with`)
- Provide methods: `score()`, `insights()`, `factors()`, `report()`

#### 2. **Request Validation and Preparation**

Two-stage process before sending to API:

**Validation** (`validation.py`):
- Uses `voluptuous` schemas to validate transaction structure
- Validates field types, formats, and value ranges
- Can be disabled by passing `validate=False` to client methods
- Raises `InvalidRequestError` if validation fails

**Preparation** (`request.py`):
- `prepare_transaction()` - Prepares Score/Insights/Factors requests
- `prepare_report()` - Prepares Report Transaction requests
- `hash_email()` - Normalizes and hashes email addresses with sophisticated logic:
  - Typo correction (e.g., `gmai.com` → `gmail.com`)
  - Equivalent domain normalization (e.g., `googlemail.com` → `gmail.com`)
  - Gmail dot removal (e.g., `f.o.o@gmail.com` → `foo@gmail.com`)
  - Yahoo/AOL alias removal (e.g., `foo-bar@yahoo.com` → `foo@yahoo.com`)
  - Fastmail subdomain handling
  - TLD typo correction (e.g., `.comcom` → `.com`)

#### 3. **Response Models**

All response models in `models.py` inherit from `_Serializable` which provides:
- `to_dict()` - Recursive serialization to plain dicts
- `__eq__()`, `__ne__()`, `__hash__()` - Comparison and hashing

**Model Hierarchy:**
- `Score` - Base response with risk score and basic info
  - Contains: `id`, `risk_score`, `funds_remaining`, `queries_remaining`, `ip_address`, `warnings`, `disposition`
- `Insights` extends `Score` - Adds detailed fraud insights
  - Adds: `credit_card`, `device`, `email`, `shipping_address`, `billing_address`, `billing_phone`, `shipping_phone`
- `Factors` extends `Insights` - Adds risk factor subscores and additional data
  - Adds: `subscores` (deprecated), `risk_score_reasons`

**Component Models:**
- `ScoreIPAddress` - Simple IP risk info for Score
- `IPAddress` extends `geoip2.models.Insights` - Full GeoIP2 data plus minFraud risk
- `CreditCard`, `Device`, `Email`, `EmailDomain`, `Phone` - Transaction component data
- `BillingAddress`, `ShippingAddress` - Address information
- `Disposition` - Custom rules disposition
- `ServiceWarning` - API warnings
- `IPRiskReason`, `RiskScoreReason`, `Reason` - Risk explanation objects

#### 4. **Constructor Pattern**

Models use keyword-only arguments (except for special cases):

```python
def __init__(
    self,
    *,
    field_name: str | None = None,
    is_flag: bool | None = None,
    # ... other keyword-only parameters
    **_: Any,  # ignore unknown keys
) -> None:
```

Key points:
- Use `*` to enforce keyword-only arguments
- Accept `**_: Any` to ignore unknown keys from the API (forward compatibility)
- Use `| None = None` for optional parameters
- Boolean fields can be `None` if not provided by API

#### 5. **Serialization with to_dict()**

All model classes inherit from `_Serializable` which provides `to_dict()`:

```python
def to_dict(self) -> dict[str, Any]:
    # Returns a dict suitable for JSON serialization
    # - Skips None values
    # - Recursively calls to_dict() on nested objects
    # - Handles lists of objects
```

#### 6. **Error Handling**

Custom exception hierarchy (all in `errors.py`):
- `MinFraudError` (base) - Generic errors
  - `AuthenticationError` - Invalid credentials
  - `HTTPError` - HTTP transport errors (includes status, URI, content)
  - `InvalidRequestError` - Invalid request data or validation failure
  - `InsufficientFundsError` - Account out of funds
  - `PermissionRequiredError` - Account lacks service permission

Clients handle HTTP status codes:
- 400-499: Parsed as specific error types based on error code in JSON response
- 500-599: Raised as `HTTPError` with status and body
- Success (200): Response JSON parsed into model objects

#### 7. **GeoIP2 Integration**

minFraud models extend GeoIP2 models:
- `IPAddress` extends `geoip2.models.Insights` - Adds `risk` and `risk_reasons`
- `GeoIP2Location` extends `geoip2.records.Location` - Adds `local_time`

This allows minFraud responses to include full GeoIP2 data (city, country, ISP, etc.) alongside fraud data.

## Testing Conventions

### Running Tests

```bash
# Install dependencies using uv
uv sync --all-groups

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_models.py

# Run specific test class or method
uv run pytest tests/test_models.py::TestModels::test_insights_full

# Run tests with coverage
uv run pytest --cov=minfraud --cov-report=html
```

### Linting and Type Checking

```bash
# Run all linting checks (mypy, ruff check, ruff format check)
uv run tox -e lint

# Run mypy type checking
uv run mypy src tests

# Run ruff linting
uv run ruff check

# Auto-fix ruff issues
uv run ruff check --fix

# Check formatting
uv run ruff format --check --diff .

# Apply formatting
uv run ruff format .
```

### Running Tests Across Python Versions

```bash
# Run tests on all supported Python versions (3.10-3.14)
uv run tox

# Run on specific Python version
uv run tox -e 3.11

# Run lint environment
uv run tox -e lint
```

### Test Structure

Tests are organized by component:
- `tests/test_models.py` - Response model tests
- `tests/test_webservice.py` - Web service client tests (sync and async)
- `tests/test_request.py` - Request preparation and email hashing tests
- `tests/test_validation.py` - Request validation tests
- `tests/data/` - Test fixtures and mock response data

### Test Patterns

When adding new fields to models:
1. Update the test method to include the new field in the constructor call
2. Add assertions to verify the field is properly populated
3. Test both presence and absence of the field (None handling)
4. Verify `to_dict()` serialization includes the field correctly

Example:
```python
def test_email(self) -> None:
    first_seen = "2016-01-01"
    email = Email(
        first_seen=first_seen,
        is_disposable=True,
        is_free=True,
        is_high_risk=False,
    )

    assert first_seen == email.first_seen
    assert True == email.is_disposable
    assert True == email.is_free
    assert False == email.is_high_risk
```

## Working with This Codebase

### Adding New Fields to Existing Models

1. **Add the parameter to `__init__`** with proper type hints:
   ```python
   def __init__(
       self,
       # ... existing params
       *,
       new_field: str | None = None,
       # ... other params
       **_: Any,
   ) -> None:
   ```

2. **Assign the field in the constructor**:
   ```python
   self.new_field = new_field
   ```

3. **Add class-level type annotation** with docstring:
   ```python
   new_field: str | None
   """Description of the field, its source, and availability."""
   ```

4. **`to_dict()` handles serialization automatically** via `_Serializable` base class

5. **Update tests** to include the new field in test data and assertions

6. **Update HISTORY.rst** with the change

### Adding New Models

When creating a new model class:

1. **Determine appropriate base class** (`_Serializable`, `Score`, `Insights`, etc.)
2. **Follow the constructor pattern** from existing models
3. **Use type hints** for all attributes
4. **Use keyword-only arguments** with `*` separator
5. **Accept `**_: Any`** to ignore unknown API keys
6. **Provide comprehensive docstrings** for all attributes
7. **Add corresponding tests** with full coverage

### Updating Validation Schemas

When the minFraud API adds new input fields or values:

1. **Locate the appropriate schema** in `validation.py`
2. **Add new field** with appropriate validator
3. **For enum values** (e.g., payment processors), add to the `In()` list
4. **Update HISTORY.rst** with the validation change

Example:
```python
# Adding a new payment processor
_payment_processor = In([
    "stripe",
    "braintree",
    # ... existing processors
    "new_processor",  # New addition
])
```

### Email Normalization

When adding email normalization rules to `request.py`:

1. **Update appropriate constant** (`_TYPO_DOMAINS`, `_EQUIVALENT_DOMAINS`, etc.)
2. **Add normalization logic** to `_clean_domain()` or `_clean_email_address()`
3. **Add tests** to `tests/test_request.py` with examples
4. **Document in HISTORY.rst**

### HISTORY.rst Format

Always update `HISTORY.rst` for user-facing changes.

**Important**: Do not add a date to changelog entries until release time. A version number without a date indicates an unreleased version. Only add the date when the version is actually released.

Format:
```rst
3.2.0
++++++++++++++++++

* IMPORTANT: Python 3.10 or greater is required. If you are using an older
  version, please use an earlier release.
* Added ``new_processor`` to the ``/payment/processor`` validation.
* Added a new ``field_name`` attribute to ``minfraud.models.ModelName``.
  This field provides information about...
```

## Common Pitfalls and Solutions

### Problem: Incorrect Type Hints
Using wrong type hints can cause mypy errors or allow invalid data.

**Solution**: Follow these patterns:
- Optional values: `Type | None` (e.g., `int | None`, `str | None`)
- Booleans can be optional: `bool | None` (API may not provide them)
- Lists: `list[Type]` for return types
- Sequences: `Sequence[Type]` for parameters
- Use modern Python 3.10+ union syntax: `X | Y` instead of `Union[X, Y]`

### Problem: Validation Not Updated
Adding fields to models but forgetting to update validation schemas.

**Solution**:
- Check if the field is an input field (validation needed) or output field (no validation)
- Input fields must be added to appropriate schema in `validation.py`
- Output-only fields just need to be added to the model

### Problem: Test Failures After Adding Fields
Tests fail because fixtures don't include new fields.

**Solution**: Update all related tests:
1. Add field to constructor calls in tests
2. Add assertions for the new field
3. Test None case if field is optional
4. Verify `to_dict()` serialization

### Problem: Missing Email Normalization Test
Added email normalization but didn't verify it works.

**Solution**:
- Add test cases to `tests/test_request.py`
- Test both the raw email and the hashed version
- Verify edge cases (empty strings, already normalized, etc.)

### Problem: Breaking Changes to Constructor
Adding required parameters breaks existing code.

**Solution**:
- Always add new parameters as optional with defaults
- Use keyword-only arguments (after `*`)
- Never add required positional parameters to existing constructors
- Use `**_: Any` to silently accept unknown parameters from API

## Code Style Requirements

- **ruff** enforces all style rules (configured in `pyproject.toml`)
- **Type hints required** for all functions and class attributes
- **Docstrings required** for all public classes, methods, and attributes
- **Line length**: 88 characters (Black-compatible via ruff)
- No unused imports or variables
- Use modern Python features (3.10+ type union syntax: `X | Y` instead of `Union[X, Y]`)
- Per-file ignores configured in `pyproject.toml`:
  - `models.py`: Allows `Any` in type hints (`ANN401`) and many parameters (`PLR0913`)
  - `tests/*`: Skips return type annotations (`ANN201`) and docstrings (`D`)

## Development Workflow

### Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies including dev and lint groups
uv sync --all-groups
```

### Before Committing

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check --fix

# Type check
uv run mypy src tests

# Run tests
uv run pytest

# Or run everything via tox
uv run tox
```

### Version Requirements

- **Python 3.10+** required (as of version 3.2.0)
- Uses modern Python features (`match` statements, `X | Y` union syntax)
- Target compatibility: Python 3.10-3.14

## Additional Resources

- [API Documentation](https://minfraud.readthedocs.io/)
- [minFraud Web Services Docs](https://dev.maxmind.com/minfraud/)
- [Report Transaction API](https://dev.maxmind.com/minfraud/report-a-transaction)
- GitHub Issues: https://github.com/maxmind/minfraud-api-python/issues
