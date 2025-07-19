# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-19

### Added
- **Refund functionality**: New `refund_transaction()` method for requesting refunds
  - Supports both full and partial refunds
  - Validates transaction status before refund requests
  - Provides structured guidance for manual refund processing via merchant dashboard
  - Includes comprehensive error handling and validation
  
- **Order cancellation**: New `cancel_order()` method for cancelling pending transactions
  - Checks transaction status to determine cancellation eligibility
  - Provides guidance for different transaction states (pending, processing, completed, failed)
  - Includes support contact information for manual processing
  
- **Enhanced error handling**: Improved error messages and validation
  - Better error messages for refund/cancellation edge cases
  - Validation for refund amounts exceeding transaction amounts
  - Clear guidance when transactions cannot be refunded/cancelled
  
- **New example**: `refund_cancel_example.py` demonstrating the new functionality
  - Interactive demo showing refund and cancellation workflows
  - Comprehensive error handling examples
  - Support contact guidance for manual processing

### Changed
- **Documentation**: Updated README.md with new API methods and examples
  - Added refund and cancellation usage examples with code snippets
  - Enhanced API reference section with new methods
  - Updated examples overview to include refund/cancellation demo
  
- **Tests**: Added comprehensive test coverage for new functionality (10 new tests)
  - Tests for successful refund scenarios (full and partial)
  - Tests for refund error conditions and validation
  - Tests for cancellation workflows and edge cases
  - Input validation tests for invalid tracking IDs

### Technical Notes
- **Important**: Pesapal API v3 does not provide direct refund/cancellation endpoints in public documentation
- These methods provide structured guidance for manual processing via Pesapal merchant dashboard or support
- All refund/cancellation operations require manual intervention through Pesapal support or dashboard
- The methods validate transaction status and provide clear next steps with contact information

## [1.0.0] - 2025-01-19

### Added
- Initial release of pesapal-py-v3 Python client
- Support for Pesapal API v3 authentication
- IPN (Instant Payment Notification) registration
- Order submission for payment processing
- Transaction status checking
- Complete type hints for better IDE support
- Comprehensive error handling with custom PesapalError
- Context manager support for proper resource cleanup
- Full test suite with 23+ test cases
- Beginner-friendly documentation with Flask example
- Support for Python 3.7+

### Features
- **Authentication**: Automatic token management with refresh
- **IPN Registration**: Register callback URLs for payment notifications
- **Payment Processing**: Submit orders and get redirect URLs
- **Status Checking**: Query transaction status and payment details
- **Error Handling**: Meaningful error messages with context
- **Type Safety**: Full type hints for better development experience
- **Logging**: Built-in logging for debugging and monitoring

### Documentation
- Complete README with examples
- Flask application example
- API reference documentation
- Testing instructions
- Contributing guidelines

### Repository
- GitHub: https://github.com/mwondhaf/pesapal-v3-python
- PyPI Package: pesapal-v3
