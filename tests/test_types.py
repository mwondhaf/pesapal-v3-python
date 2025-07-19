"""Tests for type definitions and data classes."""

import pytest
from pesapal_v3.types import (
    PesapalConfig,
    BillingAddress, 
    IPNData,
    OrderData,
    PesapalError,
    AuthResponse,
    IPNResponse,
    OrderResponse,
    TransactionStatusResponse,
)

class TestPesapalConfig:
    """Test PesapalConfig data class."""
    
    def test_valid_config(self):
        """Test creating a valid config."""
        config = PesapalConfig(
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        assert config.consumer_key == "test_key"
        assert config.consumer_secret == "test_secret"
        assert config.api_base_url == "https://cybqa.pesapal.com/pesapalv3/api"
    
    def test_custom_api_url(self):
        """Test config with custom API URL."""
        config = PesapalConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
            api_base_url="https://custom.api.com/"
        )
        # Should strip trailing slash
        assert config.api_base_url == "https://custom.api.com"
    
    def test_invalid_config(self):
        """Test validation errors."""
        with pytest.raises(ValueError, match="consumer_key is required"):
            PesapalConfig(consumer_key="", consumer_secret="test")
        
        with pytest.raises(ValueError, match="consumer_secret is required"):
            PesapalConfig(consumer_key="test", consumer_secret="")

class TestBillingAddress:
    """Test BillingAddress data class."""
    
    def test_valid_address(self):
        """Test creating a valid billing address."""
        addr = BillingAddress(
            email_address="test@example.com",
            phone_number="254700000000",
            first_name="John",
            last_name="Doe"
        )
        assert addr.email_address == "test@example.com"
        assert addr.phone_number == "254700000000"
    
    def test_address_to_dict(self):
        """Test converting address to dictionary."""
        addr = BillingAddress(
            email_address="test@example.com",
            phone_number="254700000000",
            first_name="John",
            last_name="Doe",
            city="Nairobi"
        )
        result = addr.to_dict()
        
        assert result["email_address"] == "test@example.com"
        assert result["city"] == "Nairobi"
        assert "line_1" not in result  # Should not include None values
    
    def test_invalid_address(self):
        """Test validation errors."""
        with pytest.raises(ValueError, match="email_address is required"):
            BillingAddress(
                email_address="",
                phone_number="254700000000",
                first_name="John",
                last_name="Doe"
            )

class TestIPNData:
    """Test IPNData data class."""
    
    def test_valid_ipn_data(self):
        """Test creating valid IPN data."""
        ipn = IPNData(url="https://example.com/ipn")
        assert ipn.url == "https://example.com/ipn"
        assert ipn.ipn_notification_type == "POST"  # Default
    
    def test_invalid_notification_type(self):
        """Test invalid notification type."""
        with pytest.raises(ValueError, match="must be 'GET' or 'POST'"):
            IPNData(url="https://example.com/ipn", ipn_notification_type="INVALID")

class TestOrderData:
    """Test OrderData data class."""
    
    def test_valid_order(self, test_billing_address):
        """Test creating valid order data."""
        order = OrderData(
            id="test-123",
            currency="KES",
            amount=1000.0,
            description="Test payment",
            callback_url="https://example.com/callback",
            notification_id="ipn-123",
            billing_address=test_billing_address
        )
        assert order.id == "test-123"
        assert order.amount == 1000.0
    
    def test_invalid_amount(self, test_billing_address):
        """Test validation of amount."""
        with pytest.raises(ValueError, match="amount must be a positive number"):
            OrderData(
                id="test-123",
                currency="KES",
                amount=-100,  # Invalid negative amount
                description="Test payment",
                callback_url="https://example.com/callback",
                notification_id="ipn-123",
                billing_address=test_billing_address
            )

class TestResponseClasses:
    """Test response data classes."""
    
    def test_auth_response_from_dict(self):
        """Test creating AuthResponse from dict."""
        data = {"token": "test_token", "expiryDate": 3600}
        response = AuthResponse.from_dict(data)
        
        assert response.token == "test_token"
        assert response.expiry_date == 3600
    
    def test_ipn_response_from_dict(self):
        """Test creating IPNResponse from dict."""
        data = {
            "ipn_id": "ipn_123",
            "url": "https://example.com/ipn",
            "status": "Active"
        }
        response = IPNResponse.from_dict(data)
        
        assert response.ipn_id == "ipn_123"
        assert response.status == "Active"
    
    def test_order_response_from_dict(self):
        """Test creating OrderResponse from dict."""
        data = {
            "order_tracking_id": "track_123",
            "merchant_reference": "order_123",
            "redirect_url": "https://pesapal.com/payment/track_123"
        }
        response = OrderResponse.from_dict(data)
        
        assert response.order_tracking_id == "track_123"
        assert response.redirect_url == "https://pesapal.com/payment/track_123"
    
    def test_transaction_status_from_dict(self):
        """Test creating TransactionStatusResponse from dict."""
        data = {
            "status": "COMPLETED",
            "amount": 1000.0,
            "currency": "KES",
            "payment_method": "M-Pesa"
        }
        response = TransactionStatusResponse.from_dict(data)
        
        assert response.status == "COMPLETED"
        assert response.amount == 1000.0
        assert response.payment_method == "M-Pesa"

class TestPesapalError:
    """Test PesapalError exception."""
    
    def test_error_creation(self):
        """Test creating PesapalError."""
        error = PesapalError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.response_data is None
    
    def test_error_with_response_data(self):
        """Test error with response data."""
        response_data = {"error": "Invalid request"}
        error = PesapalError("Test error", response_data)
        
        assert error.message == "Test error"
        assert error.response_data == response_data
