"""Test configuration and fixtures."""

import pytest
from pesapal_v3 import PesapalConfig, BillingAddress, IPNData, OrderData

@pytest.fixture
def test_config():
    """Create a test configuration."""
    return PesapalConfig(
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        api_base_url="https://cybqa.pesapal.com/pesapalv3/api"
    )

@pytest.fixture
def test_billing_address():
    """Create a test billing address."""
    return BillingAddress(
        email_address="test@example.com",
        phone_number="254700000000",
        first_name="John",
        last_name="Doe"
    )

@pytest.fixture
def test_ipn_data():
    """Create test IPN data."""
    return IPNData(
        url="https://example.com/ipn",
        ipn_notification_type="POST"
    )

@pytest.fixture
def test_order_data(test_billing_address):
    """Create test order data."""
    return OrderData(
        id="test-order-123",
        currency="KES",
        amount=1000.0,
        description="Test payment",
        callback_url="https://example.com/callback",
        notification_id="test-ipn-id",
        billing_address=test_billing_address
    )
