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
    
    def test_refund_transaction_completed(self, test_config):
        """Test refund for a completed transaction."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - completed transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Completed",
                    "amount": 1000.0,
                    "currency": "KES",
                    "payment_method": "M-Pesa"
                }
            )
            
            client = Pesapal(test_config)
            refund_result = client.refund_transaction("tracking_123", amount=500.0, reason="Customer request")
            
            assert refund_result['order_tracking_id'] == "tracking_123"
            assert refund_result['refund_amount'] == 500.0
            assert refund_result['transaction_amount'] == 1000.0
            assert refund_result['request_type'] == 'partial_refund'
            assert refund_result['status'] == 'refund_requested'
            assert 'instructions' in refund_result
            assert 'support_details' in refund_result
    
    def test_refund_transaction_full_amount(self, test_config):
        """Test full refund for a completed transaction."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - completed transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Completed",
                    "amount": 1000.0,
                    "currency": "KES",
                    "payment_method": "M-Pesa"
                }
            )
            
            client = Pesapal(test_config)
            refund_result = client.refund_transaction("tracking_123")  # No amount = full refund
            
            assert refund_result['refund_amount'] == 1000.0
            assert refund_result['request_type'] == 'full_refund'
    
    def test_refund_transaction_not_completed(self, test_config):
        """Test refund attempt for non-completed transaction."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - pending transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Pending",
                    "amount": 1000.0,
                    "currency": "KES"
                }
            )
            
            client = Pesapal(test_config)
            
            with pytest.raises(PesapalError, match="not completed and cannot be refunded"):
                client.refund_transaction("tracking_123")
    
    def test_refund_amount_exceeds_transaction(self, test_config):
        """Test refund with amount exceeding transaction amount."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - completed transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Completed",
                    "amount": 1000.0,
                    "currency": "KES"
                }
            )
            
            client = Pesapal(test_config)
            
            with pytest.raises(PesapalError, match="cannot exceed transaction amount"):
                client.refund_transaction("tracking_123", amount=1500.0)
    
    def test_cancel_order_pending(self, test_config):
        """Test cancellation of pending transaction."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - pending transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Pending",
                    "amount": 1000.0,
                    "currency": "KES"
                }
            )
            
            client = Pesapal(test_config)
            cancel_result = client.cancel_order("tracking_123", reason="Customer changed mind")
            
            assert cancel_result['order_tracking_id'] == "tracking_123"
            assert cancel_result['current_status'] == "Pending"
            assert cancel_result['request_type'] == 'cancellation'
            assert cancel_result['status'] == 'cancellation_requested'
            assert 'instructions' in cancel_result
            assert 'support_details' in cancel_result
    
    def test_cancel_order_completed(self, test_config):
        """Test cancellation attempt for completed transaction."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - completed transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Completed",
                    "amount": 1000.0,
                    "currency": "KES"
                }
            )
            
            client = Pesapal(test_config)
            
            with pytest.raises(PesapalError, match="cannot be cancelled"):
                client.cancel_order("tracking_123")
    
    def test_cancel_order_processing(self, test_config):
        """Test cancellation of processing transaction."""
        with requests_mock.Mocker() as m:
            # Mock auth response
            m.post(
                f"{test_config.api_base_url}/Auth/RequestToken",
                json={"token": "test_token_123", "expiryDate": 3600}
            )
            
            # Mock transaction status response - processing transaction
            m.get(
                f"{test_config.api_base_url}/Transactions/GetTransactionStatus",
                json={
                    "payment_status_description": "Processing",
                    "amount": 1000.0,
                    "currency": "KES"
                }
            )
            
            client = Pesapal(test_config)
            cancel_result = client.cancel_order("tracking_123", reason="Urgent cancellation")
            
            assert cancel_result['current_status'] == "Processing"
            assert cancel_result['status'] == 'cancellation_requested'
    
    def test_refund_invalid_tracking_id(self, test_config):
        """Test refund with invalid tracking ID."""
        client = Pesapal(test_config)
        
        with pytest.raises(ValueError, match="order_tracking_id is required"):
            client.refund_transaction("")
    
    def test_cancel_invalid_tracking_id(self, test_config):
        """Test cancellation with invalid tracking ID."""
        client = Pesapal(test_config)
        
        with pytest.raises(ValueError, match="order_tracking_id is required"):
            client.cancel_order("")
