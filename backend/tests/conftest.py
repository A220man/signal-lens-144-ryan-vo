import pytest
from app.api.hooks import reset_hook_store


@pytest.fixture(autouse=True)
def reset_hook_store_before_each_test():
    """Reset the in-memory hook store before each test for isolation."""
    reset_hook_store()
    yield
    # Clean up after test
    reset_hook_store()
