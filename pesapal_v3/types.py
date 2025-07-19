"""
Type definitions for the Pesapal Python client.

This module contains all the data classes and type definitions used by the Pesapal client.
"""

from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class PesapalError(Exception):
    """Custom exception for Pesapal API errors."""
    
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.response_data = response_data


@dataclass
class PesapalConfig:
    """Configuration for the Pesapal client."""
    consumer_key: str
    consumer_secret: str
    api_base_url: str = "https://cybqa.pesapal.com/pesapalv3/api"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.consumer_key:
            raise ValueError("consumer_key is required")
        if not self.consumer_secret:
            raise ValueError("consumer_secret is required")
        if not self.api_base_url:
            raise ValueError("api_base_url is required")
        
        # Remove trailing slash if present
        self.api_base_url = self.api_base_url.rstrip('/')


@dataclass
class BillingAddress:
    """Billing address information for payment requests."""
    email_address: str
    phone_number: str
    first_name: str
    last_name: str
    country_code: Optional[str] = None
    line_1: Optional[str] = None
    line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None

    def __post_init__(self):
        """Validate billing address after initialization."""
        if not self.email_address:
            raise ValueError("email_address is required")
        if not self.phone_number:
            raise ValueError("phone_number is required")
        if not self.first_name:
            raise ValueError("first_name is required")
        if not self.last_name:
            raise ValueError("last_name is required")

    def to_dict(self) -> Dict[str, Any]:
        """Convert billing address to dictionary for API requests."""
        result = {
            'email_address': self.email_address,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }
        
        # Add optional fields if present
        optional_fields = [
            'country_code', 'line_1', 'line_2', 
            'city', 'state', 'postal_code'
        ]
        
        for field in optional_fields:
            value = getattr(self, field)
            if value is not None:
                result[field] = value
                
        return result


@dataclass
class IPNData:
    """IPN (Instant Payment Notification) registration data."""
    url: str
    ipn_notification_type: Literal["GET", "POST"] = "POST"

    def __post_init__(self):
        """Validate IPN data after initialization."""
        if not self.url:
            raise ValueError("url is required")
        if self.ipn_notification_type not in ["GET", "POST"]:
            raise ValueError("ipn_notification_type must be 'GET' or 'POST'")


@dataclass
class OrderData:
    """Order submission data for payment requests."""
    id: str
    currency: str
    amount: Union[int, float]
    description: str
    callback_url: str
    notification_id: str
    billing_address: BillingAddress

    def __post_init__(self):
        """Validate order data after initialization."""
        if not self.id:
            raise ValueError("id is required")
        if not self.currency:
            raise ValueError("currency is required")
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise ValueError("amount must be a positive number")
        if not self.description:
            raise ValueError("description is required")
        if not self.callback_url:
            raise ValueError("callback_url is required")
        if not self.notification_id:
            raise ValueError("notification_id is required")
        if not isinstance(self.billing_address, BillingAddress):
            raise ValueError("billing_address must be a BillingAddress instance")


@dataclass
class AuthResponse:
    """Authentication response from Pesapal API."""
    token: str
    expires_in: Optional[int] = None
    token_type: Optional[str] = None
    expiry_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthResponse':
        """Create AuthResponse from API response dictionary."""
        return cls(
            token=data.get('token', ''),
            expires_in=data.get('expires_in'),
            token_type=data.get('token_type'),
            expiry_date=data.get('expiryDate')
        )


@dataclass
class IPNResponse:
    """IPN registration response from Pesapal API."""
    ipn_id: str
    url: str
    created_date: Optional[str] = None
    ipn_notification_type: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IPNResponse':
        """Create IPNResponse from API response dictionary."""
        return cls(
            ipn_id=data.get('ipn_id', ''),
            url=data.get('url', ''),
            created_date=data.get('created_date'),
            ipn_notification_type=data.get('ipn_notification_type'),
            status=data.get('status')
        )


@dataclass
class OrderResponse:
    """Order submission response from Pesapal API."""
    order_tracking_id: str
    merchant_reference: str
    redirect_url: str
    error: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderResponse':
        """Create OrderResponse from API response dictionary."""
        return cls(
            order_tracking_id=data.get('order_tracking_id', ''),
            merchant_reference=data.get('merchant_reference', ''),
            redirect_url=data.get('redirect_url', ''),
            error=data.get('error'),
            status=data.get('status')
        )


@dataclass
class TransactionStatusResponse:
    """Transaction status response from Pesapal API."""
    payment_method: Optional[str] = None
    amount: Optional[Union[int, float]] = None
    created_date: Optional[str] = None
    confirmation_code: Optional[str] = None
    payment_status_description: Optional[str] = None
    description: Optional[str] = None
    message: Optional[str] = None
    payment_account: Optional[str] = None
    call_back_url: Optional[str] = None
    status_code: Optional[int] = None
    merchant_reference: Optional[str] = None
    payment_status_code: Optional[str] = None
    currency: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionStatusResponse':
        """Create TransactionStatusResponse from API response dictionary."""
        return cls(
            payment_method=data.get('payment_method'),
            amount=data.get('amount'),
            created_date=data.get('created_date'),
            confirmation_code=data.get('confirmation_code'),
            payment_status_description=data.get('payment_status_description'),
            description=data.get('description'),
            message=data.get('message'),
            payment_account=data.get('payment_account'),
            call_back_url=data.get('call_back_url'),
            status_code=data.get('status_code'),
            merchant_reference=data.get('merchant_reference'),
            payment_status_code=data.get('payment_status_code'),
            currency=data.get('currency'),
            error=data.get('error'),
            status=data.get('status')
        )
