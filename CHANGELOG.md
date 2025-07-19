# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
