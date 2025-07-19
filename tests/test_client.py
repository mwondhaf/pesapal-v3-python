"""Tests for the Pesapal client."""

import json
import pytest
import requests_mock
from pesapal_v3 import Pesapal, PesapalError

class TestPesapalClient:
    """Test cases for the main Pesapal client."""
    
    def test_client_initialization(self, test_config):
        """Test client initialization."""
        client = Pesapal(test_config)
        assert client.config == test_config
        assert client._token is None
        assert client._token_expires_at is None
    
    def test_authentication_success(self, test_config):
        """Test successful authentication."""
        with requests_mock.Mocker() as m:
            # Mock successful auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            client = Pesapal(test_config)
            token = client.get_auth_token()
            
            assert token == "test_token_123"
            assert client._token == "test_token_123"
    
    def test_authentication_failure(self, test_config):
        """Test authentication failure."""
        with requests_mock.Mocker() as m:
            # Mock failed auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"error": "Invalid credentials"},
                status_code=401
            )
            
            client = Pesapal(test_config)
            
            with pytest.raises(PesapalError):
                client.get_auth_token()
    
    def test_ipn_registration(self, test_config, test_ipn_data):
        """Test IPN registration."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock IPN registration response
            m.post(
                f"{test_config.api_base_url}/URLSetup/RegisterIPN",
                json={
                    "ipn_id": "test_ipn_123",
                    "url": "https://example.com/ipn",
                    "status": "Active"
                }
            )
            
            client = Pesapal(test_config)
            response = client.register_ipn(test_ipn_data)
            
            assert response.ipn_id == "test_ipn_123"
            assert response.url == "https://example.com/ipn"
            assert response.status == "Active"
    
    def test_order_submission(self, test_config, test_order_data):
        """Test order submission."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock order submission response
            m.post(
                f"{test_config.api_base_url}/Transactions/SubmitOrderRequest",
                json={
                    "order_tracking_id": "tracking_123",
                    "merchant_reference": "test-order-123",
                    "redirect_url": "https://pesapal.com/payment/tracking_123",
                    "status": "Pending"
                }
            )
            
            client = Pesapal(test_config)
            response = client.submit_order(test_order_data)
            
            assert response.order_tracking_id == "tracking_123"
            assert response.merchant_reference == "test-order-123"
            assert "pesapal.com" in response.redirect_url
    
    def test_transaction_status(self, test_config):
        """Test transaction status check."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "status": "COMPLETED",
                    "amount": 1000.0,
                    "currency": "KES",
                    "payment_method": "M-Pesa"
                }
            )
            
            client = Pesapal(test_config)
            response = client.get_transaction_status("tracking_123")
            
            assert response.status == "COMPLETED"
            assert response.amount == 1000.0
            assert response.currency == "KES"
            assert response.payment_method == "M-Pesa"
    
    def test_context_manager(self, test_config):
        """Test context manager usage."""
        with Pesapal(test_config) as client:
            assert client.session is not None
        # Session should be closed after context exit
