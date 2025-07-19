"""
Pesapal API Client for Python

A Python client for interacting with the Pesapal API v3.
Provides authentication, IPN registration, payment initiation, and transaction status checking.

Repository: https://github.com/mwondhaf/pesapal-v3-python
"""

from .client import Pesapal
from .types import (
    PesapalConfig,
    IPNData,
    OrderData,
    BillingAddress,
    AuthResponse,
    IPNResponse,
    OrderResponse,
    TransactionStatusResponse,
    PesapalError,
)

__version__ = "1.1.0"
__author__ = "Francis Mwondha"
__email__ = "mwondha@example.com"

__all__ = [
    "Pesapal",
    "PesapalConfig",
    "IPNData", 
    "OrderData",
    "BillingAddress",
    "AuthResponse",
    "IPNResponse",
    "OrderResponse", 
    "TransactionStatusResponse",
    "PesapalError",
]
