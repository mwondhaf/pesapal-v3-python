# Pesapal Python Examples

This directory contains example implementations showing how to use the `pesapal-v3` package in different scenarios.

## Examples

### 1. Simple Example (`simple_example.py`)

A basic Python script demonstrating core functionality:
- Authentication and token management
- IPN registration
- Order submission
- Transaction status checking
- Error handling

**Run:**
```bash
python simple_example.py
```

**Requirements:**
- pesapal-v3

### 2. Flask Web Application (`flask_example.py`)

A complete web application example with:
- Payment form interface
- IPN handling
- Payment callbacks
- Transaction status display

**Run:**
```bash
pip install flask python-dotenv
python flask_example.py
```

**Requirements:**
- flask
- python-dotenv
- pesapal-v3

## Setup

1. **Install the package:**
   ```bash
   pip install pesapal-v3
   ```

2. **Set environment variables:**
   ```bash
   export PESAPAL_CONSUMER_KEY="your_consumer_key"
   export PESAPAL_CONSUMER_SECRET="your_consumer_secret"
   export PESAPAL_API_URL="https://cybqa.pesapal.com/pesapalv3/api"  # Demo environment
   ```

3. **For production, use:**
   ```bash
   export PESAPAL_API_URL="https://pay.pesapal.com/v3/api"
   ```

## Configuration Options

### Basic Configuration
```python
from pesapal_v3 import PesapalConfig

config = PesapalConfig(
    consumer_key="your_key",
    consumer_secret="your_secret"
)
```

### Advanced Configuration
```python
config = PesapalConfig(
    consumer_key="your_key",
    consumer_secret="your_secret",
    api_base_url="https://pay.pesapal.com/v3/api",  # Production
    timeout=30,  # Request timeout in seconds
    max_retries=3  # Maximum retry attempts
)
```

## Common Patterns

### Context Manager Usage
```python
with Pesapal(config) as client:
    # Client automatically handles authentication
    # and cleanup when exiting the context
    response = client.submit_order(order_data)
```

### Manual Client Management
```python
client = Pesapal(config)
try:
    response = client.submit_order(order_data)
finally:
    client.close()  # Important: clean up resources
```

### Error Handling
```python
from pesapal_v3 import PesapalError

try:
    response = client.submit_order(order_data)
except PesapalError as e:
    print(f"API Error: {e.message}")
    print(f"Status: {e.status_code}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PESAPAL_CONSUMER_KEY` | Your Pesapal consumer key | Required |
| `PESAPAL_CONSUMER_SECRET` | Your Pesapal consumer secret | Required |
| `PESAPAL_API_URL` | API base URL | Demo environment |

## Testing

Use the demo environment for testing:
- API URL: `https://cybqa.pesapal.com/pesapalv3/api`
- Use test credentials from your Pesapal dashboard

## Support

- [Pesapal API Documentation](https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference)
- [Package Repository](https://github.com/mwondhaf/pesapal-v3-python)
- [Issue Tracker](https://github.com/mwondhaf/pesapal-v3-python/issues)
