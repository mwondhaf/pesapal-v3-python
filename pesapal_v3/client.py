"""
Pesapal API client implementation.

This module contains the main Pesapal client class that provides methods
for authentication, IPN registration, order submission, and transaction status checking.
"""

import json
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests

from .types import (
    PesapalConfig,
    IPNData,
    OrderData,
    AuthResponse,
    IPNResponse,
    OrderResponse,
    TransactionStatusResponse,
    PesapalError,
)

# Set up logging
logger = logging.getLogger(__name__)


class Pesapal:
    """
    Pesapal API client for Python.
    
    This client provides methods to interact with the Pesapal API v3,
    including authentication, IPN registration, order submission, and
    transaction status checking.
    
    Example:
        >>> from pesapal_py_v3 import Pesapal, PesapalConfig
        >>> config = PesapalConfig(
        ...     consumer_key="your_key",
        ...     consumer_secret="your_secret"
        ... )
        >>> client = Pesapal(config)
        >>> token = client.get_auth_token()
    """

    def __init__(self, config: PesapalConfig):
        """
        Initialize the Pesapal client.
        
        Args:
            config: PesapalConfig object containing API credentials and base URL
            
        Raises:
            ValueError: If config is invalid
        """
        if not isinstance(config, PesapalConfig):
            raise ValueError("config must be a PesapalConfig instance")
            
        self.config = config
        self._token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        
        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'pesapal-py-v3/1.0.0'
        })
        
        # Set reasonable timeouts
        self.session.timeout = (10, 30)  # (connect, read) timeout in seconds

    def _is_token_valid(self) -> bool:
        """Check if the current token is valid and not expired."""
        if not self._token:
            return False
        
        if self._token_expires_at and time.time() >= self._token_expires_at:
            logger.debug("Token has expired")
            return False
            
        return True

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = True
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Pesapal API.
        
        Args:
            method: HTTP method ('GET', 'POST', etc.)
            endpoint: API endpoint (relative to base URL)
            data: Request body data (for POST requests)
            params: Query parameters (for GET requests)
            authenticated: Whether to include authentication headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            PesapalError: If the request fails
        """
        url = urljoin(f"{self.config.api_base_url}/", endpoint)
        
        headers = self.session.headers.copy()
        
        if authenticated:
            if not self._is_token_valid():
                self._refresh_token()
            headers['Authorization'] = f'Bearer {self._token}'
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                response_data = response.json()
            except ValueError as e:
                raise PesapalError(f"Invalid JSON response: {str(e)}")
            
            # Check for API-level errors
            if isinstance(response_data, dict) and response_data.get('error'):
                error_msg = response_data.get('error', {}).get('message', 'Unknown API error')
                raise PesapalError(f"API error: {error_msg}", response_data)
            
            return response_data
            
        except requests.exceptions.Timeout:
            raise PesapalError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise PesapalError("Connection error - check your internet connection")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            try:
                error_data = e.response.json() if e.response else {}
            except ValueError:
                error_data = {}
            
            error_msg = f"HTTP {status_code} error"
            if error_data.get('message'):
                error_msg += f": {error_data['message']}"
                
            raise PesapalError(error_msg, error_data)
        except requests.exceptions.RequestException as e:
            raise PesapalError(f"Request failed: {str(e)}")

    def _refresh_token(self) -> None:
        """Refresh the authentication token."""
        logger.debug("Refreshing authentication token")
        
        payload = {
            'consumer_key': self.config.consumer_key,
            'consumer_secret': self.config.consumer_secret
        }

        response_data = self._make_request(
            method='POST',
            endpoint='Auth/RequestToken',
            data=payload,
            authenticated=False
        )
        
        if 'token' not in response_data:
            raise PesapalError(f"Authentication failed: {response_data}")
        
        self._token = response_data['token']
        
        # Set token expiration (default to 1 hour if not provided)
        expires_in = response_data.get('expiryDate', 3600)
        if isinstance(expires_in, (int, float)):
            self._token_expires_at = time.time() + expires_in
        
        logger.debug("Token refreshed successfully")

    def get_auth_token(self, force_refresh: bool = False) -> str:
        """
        Get authentication token from Pesapal API.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Authentication token string
            
        Raises:
            PesapalError: If authentication fails
        """
        if force_refresh or not self._is_token_valid():
            self._refresh_token()
        
        return self._token

    def register_ipn(self, ipn_data: IPNData) -> IPNResponse:
        """
        Register an IPN URL with Pesapal.
        
        Args:
            ipn_data: IPNData object containing IPN details
            
        Returns:
            IPNResponse object with registration details
            
        Raises:
            PesapalError: If IPN registration fails
        """
        if not isinstance(ipn_data, IPNData):
            raise ValueError("ipn_data must be an IPNData instance")
        
        payload = {
            'url': ipn_data.url,
            'ipn_notification_type': ipn_data.ipn_notification_type
        }

        response_data = self._make_request(
            method='POST',
            endpoint='URLSetup/RegisterIPN',
            data=payload
        )
        
        return IPNResponse.from_dict(response_data)

    def submit_order(self, order_data: OrderData) -> OrderResponse:
        """
        Submit an order to Pesapal for payment processing.
        
        Args:
            order_data: OrderData object containing order details
            
        Returns:
            OrderResponse object with order submission details
            
        Raises:
            PesapalError: If order submission fails
        """
        if not isinstance(order_data, OrderData):
            raise ValueError("order_data must be an OrderData instance")
        
        payload = {
            'id': order_data.id,
            'currency': order_data.currency,
            'amount': order_data.amount,
            'description': order_data.description,
            'callback_url': order_data.callback_url,
            'notification_id': order_data.notification_id,
            'billing_address': order_data.billing_address.to_dict()
        }

        response_data = self._make_request(
            method='POST',
            endpoint='Transactions/SubmitOrderRequest',
            data=payload
        )
        
        return OrderResponse.from_dict(response_data)

    def get_transaction_status(self, order_tracking_id: str) -> TransactionStatusResponse:
        """
        Get the status of a transaction.
        
        Args:
            order_tracking_id: The order tracking ID returned from submit_order
            
        Returns:
            TransactionStatusResponse object with transaction status details
            
        Raises:
            PesapalError: If status check fails
        """
        if not order_tracking_id:
            raise ValueError("order_tracking_id is required")
        
        params = {'orderTrackingId': order_tracking_id}

        response_data = self._make_request(
            method='GET',
            endpoint='Transactions/GetTransactionStatus',
            params=params
        )
        
        return TransactionStatusResponse.from_dict(response_data)

    def refund_transaction(self, order_tracking_id: str, amount: Optional[float] = None, reason: str = "Customer refund") -> Dict[str, Any]:
        """
        Initiate a refund for a completed transaction.
        
        Note: Pesapal API v3 does not have explicit refund endpoints in the public documentation.
        This method checks transaction status and provides guidance for manual refund processing.
        For actual refunds, contact Pesapal support or use the merchant dashboard.
        
        Args:
            order_tracking_id: The order tracking ID of the transaction to refund
            amount: Optional partial refund amount. If None, full refund is requested
            reason: Reason for the refund
            
        Returns:
            Dict containing refund request details and next steps
            
        Raises:
            PesapalError: If transaction status check fails or transaction cannot be refunded
        """
        if not order_tracking_id:
            raise ValueError("order_tracking_id is required")
        
        # First, check the transaction status
        try:
            status = self.get_transaction_status(order_tracking_id)
        except Exception as e:
            raise PesapalError(f"Failed to check transaction status: {str(e)}")
        
        # Check if transaction is eligible for refund
        if not hasattr(status, 'payment_status_description') or status.payment_status_description != 'Completed':
            raise PesapalError(f"Transaction with ID {order_tracking_id} is not completed and cannot be refunded. Status: {getattr(status, 'payment_status_description', 'Unknown')}")
        
        # Calculate refund amount
        transaction_amount = getattr(status, 'amount', 0)
        refund_amount = amount if amount is not None else transaction_amount
        
        if amount is not None and amount > transaction_amount:
            raise PesapalError(f"Refund amount ({amount}) cannot exceed transaction amount ({transaction_amount})")
        
        # Prepare refund request data
        refund_data = {
            'order_tracking_id': order_tracking_id,
            'transaction_amount': transaction_amount,
            'refund_amount': refund_amount,
            'reason': reason,
            'request_type': 'partial_refund' if amount is not None else 'full_refund',
            'status': 'refund_requested',
            'timestamp': time.time(),
            'instructions': [
                'Pesapal API v3 does not provide direct refund endpoints.',
                'To process this refund, please:',
                '1. Log into your Pesapal merchant dashboard',
                '2. Navigate to Transactions > Find this transaction',
                '3. Use the refund option in the dashboard',
                'Or contact Pesapal support with the following details:'
            ],
            'support_details': {
                'order_tracking_id': order_tracking_id,
                'refund_amount': refund_amount,
                'reason': reason,
                'support_email': 'support@pesapal.com',
                'merchant_phone': '+254-70-619-1729'
            }
        }
        
        logger.info(f"Refund requested for transaction {order_tracking_id}: {refund_amount} (reason: {reason})")
        
        return refund_data

    def cancel_order(self, order_tracking_id: str, reason: str = "Customer cancellation") -> Dict[str, Any]:
        """
        Cancel a pending transaction.
        
        Note: Pesapal API v3 does not have explicit cancellation endpoints in the public documentation.
        This method checks transaction status and provides guidance for cancellation.
        
        Args:
            order_tracking_id: The order tracking ID of the transaction to cancel
            reason: Reason for the cancellation
            
        Returns:
            Dict containing cancellation request details and next steps
            
        Raises:
            PesapalError: If transaction status check fails or transaction cannot be cancelled
        """
        if not order_tracking_id:
            raise ValueError("order_tracking_id is required")
        
        # Check current transaction status
        try:
            status = self.get_transaction_status(order_tracking_id)
        except Exception as e:
            raise PesapalError(f"Failed to check transaction status: {str(e)}")
        
        # Check if transaction can be cancelled
        status_description = getattr(status, 'payment_status_description', 'Unknown')
        
        if status_description in ['Completed', 'Failed']:
            raise PesapalError(f"Transaction with ID {order_tracking_id} cannot be cancelled. Status: {status_description}")
        
        if status_description in ['Pending', 'Processing']:
            # Transaction can potentially be cancelled
            cancellation_data = {
                'order_tracking_id': order_tracking_id,
                'current_status': status_description,
                'reason': reason,
                'request_type': 'cancellation',
                'status': 'cancellation_requested',
                'timestamp': time.time(),
                'instructions': [
                    'Pesapal API v3 does not provide direct cancellation endpoints.',
                    'For pending/processing transactions, consider:',
                    '1. Contact customer to stop any payment attempts',
                    '2. Monitor transaction status - pending transactions may expire automatically',
                    '3. If needed, contact Pesapal support for manual cancellation',
                    '4. Use merchant dashboard to manage the transaction'
                ],
                'support_details': {
                    'order_tracking_id': order_tracking_id,
                    'reason': reason,
                    'support_email': 'support@pesapal.com',
                    'merchant_phone': '+254-70-619-1729'
                }
            }
            
            logger.info(f"Cancellation requested for transaction {order_tracking_id} (status: {status_description}, reason: {reason})")
            
            return cancellation_data
        
        # For other statuses, provide generic guidance
        return {
            'order_tracking_id': order_tracking_id,
            'current_status': status_description,
            'reason': reason,
            'status': 'cancellation_not_applicable',
            'message': f"Transaction status '{status_description}' does not require cancellation",
            'timestamp': time.time()
        }

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
