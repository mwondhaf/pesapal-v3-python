# Pesapal Python Client for API v3

[![PyPI version](https://badge.fury.io/py/pesapal-v3.svg)](https://badge.fury.io/py/pesapal-v3)
[![Python Support](https://img.shields.io/pypi/pyversions/pesapal-v3.svg)](https://pypi.org/project/pesapal-v3/)

A lightweight, easy-to-use Python client for integrating Pesapal payment services into your applications. Perfect for beginners and experienced developers alike!

## 🚀 Features
- ✅ Simple, easy-to-use API for Pesapal integration
- ✅ Handles authentication, IPN registration, payment initiation, and transaction status
- ✅ Written in Python with full type hints for better IDE support
- ✅ Comprehensive error handling and logging
- ✅ Context manager support for proper resource cleanup
- ✅ Beginner-friendly with detailed examples

## 📦 Installation

```bash
pip install pesapal-v3
```

## 🎯 Quick Start

### Basic Setup

```python
from pesapal_v3 import Pesapal, PesapalConfig, OrderData, BillingAddress, IPNData

# Initialize the client
config = PesapalConfig(
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET',
    api_base_url='https://cybqa.pesapal.com/pesapalv3/api'  # Sandbox URL
    # For production: 'https://pay.pesapal.com/v3/api'
)

pesapal = Pesapal(config)
```

### Authentication

The client handles authentication automatically, but you can explicitly get a token if needed:

```python
token = pesapal.get_auth_token()
print(f"Auth token: {token}")
```

### Register an IPN URL

```python
from pesapal_v3 import IPNData

ipn_data = IPNData(
    url='https://yourdomain.com/payment-notification',
    ipn_notification_type='POST'  # or 'GET'
)

response = pesapal.register_ipn(ipn_data)
print(f"IPN ID: {response.ipn_id}")
```

### Initiate a Payment

```python
from pesapal_v3 import OrderData, BillingAddress

# Create billing address
billing_address = BillingAddress(
    email_address='customer@example.com',
    phone_number='254700000000',
    first_name='John',
    last_name='Doe'
)

# Create order
order_data = OrderData(
    id='unique-order-id',  # Your unique order ID
    currency='KES',
    amount=1000,
    description='Payment for goods',
    callback_url='https://yourdomain.com/payment-callback',
    notification_id='your-ipn-id',  # From register_ipn response
    billing_address=billing_address
)

response = pesapal.submit_order(order_data)
print(f"Redirect URL: {response.redirect_url}")
print(f"Order Tracking ID: {response.order_tracking_id}")
```

### Get Transaction Status

```python
status = pesapal.get_transaction_status('ORDER_TRACKING_ID')
print(f"Payment Status: {status.status}")
print(f"Amount: {status.amount} {status.currency}")
```

## 🚀 Quick Start Guide for Beginners

### Step 1: Get Your Pesapal Credentials
1. Sign up at [Pesapal Developer Portal](https://developer.pesapal.com/)
2. Create a new app in your dashboard
3. Copy your Consumer Key and Consumer Secret

### Step 2: Setup Your Project
1. Install the package: `pip install pesapal-v3`
2. Create a `.env` file with your credentials
3. Initialize the Pesapal client in your code

### Step 3: Register IPN (One-time setup)
1. Create an endpoint in your app to handle payment notifications
2. Register this URL with Pesapal using `register_ipn()`
3. Save the returned IPN ID for future payments

### Step 4: Process Payments
1. Create a payment form to collect customer details
2. Use `submit_order()` to initiate the payment
3. Redirect users to the returned Pesapal payment URL
4. Handle the callback when users return from payment

### Step 5: Verify Payments
1. Use `get_transaction_status()` to check payment status
2. Update your database based on the payment result
3. Send confirmation to your customer

## 📚 Complete Flask Example

Here's a complete example using Flask:

```python
import os
from flask import Flask, request, redirect, jsonify
from pesapal_v3 import Pesapal, PesapalConfig, IPNData, OrderData, BillingAddress

app = Flask(__name__)

# Initialize Pesapal client
config = PesapalConfig(
    consumer_key=os.getenv('PESAPAL_CONSUMER_KEY'),
    consumer_secret=os.getenv('PESAPAL_CONSUMER_SECRET'),
    api_base_url=os.getenv('PESAPAL_API_URL', 'https://cybqa.pesapal.com/pesapalv3/api')
)
pesapal = Pesapal(config)

# Store IPN ID (use database in production)
ipn_id = None

@app.route('/register-ipn', methods=['POST'])
def register_ipn():
    global ipn_id
    try:
        ipn_data = IPNData(
            url=f"{request.host_url}payment-notification",
            ipn_notification_type='POST'
        )
        response = pesapal.register_ipn(ipn_data)
        ipn_id = response.ipn_id
        return jsonify({"success": True, "ipn_id": ipn_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/initiate-payment', methods=['POST'])
def initiate_payment():
    try:
        data = request.get_json()
        
        billing_address = BillingAddress(
            email_address=data['email'],
            phone_number=data['phone'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        order_data = OrderData(
            id=f"order-{data['order_id']}",
            currency=data.get('currency', 'KES'),
            amount=float(data['amount']),
            description=data.get('description', 'Payment for goods'),
            callback_url=f"{request.host_url}payment-callback",
            notification_id=ipn_id,
            billing_address=billing_address
        )
        
        response = pesapal.submit_order(order_data)
        return jsonify({
            "success": True,
            "redirect_url": response.redirect_url,
            "order_tracking_id": response.order_tracking_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/payment-callback')
def payment_callback():
    order_tracking_id = request.args.get('OrderTrackingId')
    if order_tracking_id:
        status = pesapal.get_transaction_status(order_tracking_id)
        return f"Payment Status: {status.status}"
    return "No tracking ID provided"

@app.route('/payment-notification', methods=['POST'])
def payment_notification():
    # Handle IPN notification
    data = request.get_json()
    print(f"IPN received: {data}")
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
```

## 🔧 API Reference

### `Pesapal(config)`
Main client class for interacting with Pesapal API.

**Methods:**
- `get_auth_token(force_refresh=False)` - Get authentication token
- `register_ipn(ipn_data)` - Register IPN URL
- `submit_order(order_data)` - Submit order for payment
- `get_transaction_status(order_tracking_id)` - Get transaction status

### Data Classes

**`PesapalConfig`**
- `consumer_key: str` - Your Pesapal consumer key
- `consumer_secret: str` - Your Pesapal consumer secret  
- `api_base_url: str` - Pesapal API base URL

**`BillingAddress`**
- `email_address: str` - Customer email
- `phone_number: str` - Customer phone
- `first_name: str` - Customer first name
- `last_name: str` - Customer last name

**`IPNData`**
- `url: str` - Your IPN callback URL
- `ipn_notification_type: str` - 'POST' or 'GET'

**`OrderData`**
- `id: str` - Unique order identifier
- `currency: str` - Currency code (e.g., 'KES', 'UGX')
- `amount: float` - Payment amount
- `description: str` - Payment description
- `callback_url: str` - User return URL
- `notification_id: str` - IPN ID from registration
- `billing_address: BillingAddress` - Customer billing info

## 🎯 Environment Setup

### Getting Pesapal Credentials

1. **Sign up** at [Pesapal Developer Portal](https://developer.pesapal.com/)
2. **Create an app** in your dashboard
3. **Get your credentials**:
   - Consumer Key
   - Consumer Secret
4. **Choose environment**:
   - **Sandbox**: `https://cybqa.pesapal.com/pesapalv3/api` (for testing)
   - **Production**: `https://pay.pesapal.com/v3/api` (for live payments)

### Environment Variables Best Practices

```bash
# .env file
PESAPAL_CONSUMER_KEY=your_consumer_key
PESAPAL_CONSUMER_SECRET=your_consumer_secret
PESAPAL_API_URL=https://cybqa.pesapal.com/pesapalv3/api
```

```python
import os
from pesapal_v3 import PesapalConfig

config = PesapalConfig(
    consumer_key=os.getenv('PESAPAL_CONSUMER_KEY'),
    consumer_secret=os.getenv('PESAPAL_CONSUMER_SECRET'),
    api_base_url=os.getenv('PESAPAL_API_URL')
)
```

## 🚨 Important Notes

### Payment Flow
1. **Register IPN** (one-time setup)
2. **Initiate payment** (creates payment request)
3. **Redirect user** to Pesapal payment page
4. **Handle callback** (user returns from Pesapal)
5. **Process IPN** (Pesapal sends payment updates)

### Security Considerations
- Always validate payment status on your server
- Never trust client-side payment confirmations
- Use HTTPS for all callback URLs
- Store sensitive data in environment variables
- Implement proper error handling

### Context Manager Usage (Recommended)

```python
with Pesapal(config) as client:
    # Client automatically handles authentication and cleanup
    response = client.submit_order(order_data)
    # Resources are automatically cleaned up when exiting the context
```

## 📚 Examples

Check out the `examples/` directory for complete implementations:

- **`simple_example.py`** - Basic usage without web framework
- **`flask_example.py`** - Complete Flask web application
- **`examples/README.md`** - Detailed setup instructions

## 🤝 Contributing

```python
# Recommended: Use context manager for automatic cleanup
with Pesapal(config) as client:
    token = client.get_auth_token()
    # ... other operations
# Session is automatically closed
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=pesapal_v3
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: [Pesapal API Documentation](https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference)
- **Issues**: [GitHub Issues](https://github.com/mwondhaf/pesapal-v3-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mwondhaf/pesapal-v3-python/discussions)

## 👨‍💻 Maintainer

**Francis Mwondha**
- GitHub: [@mwondhaf](https://github.com/mwondhaf)
- Repository: [pesapal-v3-python](https://github.com/mwondhaf/pesapal-v3-python)

---

**Made with ❤️ for the Python developer community**
# pesapal-v3-python
