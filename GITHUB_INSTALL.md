# GitHub Installation Guide

## Installation from GitHub

You can install the Pesapal Python V3 client directly from GitHub using pip:

### Latest Release
```bash
pip install git+https://github.com/mwondhaf/pesapal-v3-python.git
```

### Specific Version (Tag)
```bash
pip install git+https://github.com/mwondhaf/pesapal-v3-python.git@v1.1.0
```

### Development Version (Latest Commit)
```bash
pip install git+https://github.com/mwondhaf/pesapal-v3-python.git@main
```

## Verification

After installation, you can verify the package is working correctly:

```python
# Test import
import pesapal_v3
print(f"Installed version: {pesapal_v3.__version__}")

# Test client creation
from pesapal_v3 import Pesapal, PesapalConfig

config = PesapalConfig(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    api_base_url="https://cybqa.pesapal.com/pesapalv3/api"  # sandbox
)

client = Pesapal(config)
print("✅ Pesapal client created successfully!")
```

## Requirements

- Python 3.7+
- Git (for GitHub installation)
- Internet connection

## Troubleshooting

### Installation Issues
1. **Permission errors**: Use `pip install --user` if you get permission errors
2. **Git not found**: Make sure Git is installed and available in your PATH
3. **SSL errors**: Try `pip install --trusted-host pypi.org --trusted-host pypi.python.org`

### Import Issues
1. **Module not found**: Make sure you're using the correct Python environment
2. **Version conflicts**: Try installing in a virtual environment

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv pesapal_env

# Activate (Linux/Mac)
source pesapal_env/bin/activate

# Activate (Windows)
pesapal_env\Scripts\activate

# Install package
pip install git+https://github.com/mwondhaf/pesapal-v3-python.git

# Verify installation
python -c "import pesapal_v3; print('Success!')"
```

## Features Available

- **Authentication**: Automatic token management with refresh
- **Order Management**: Submit orders and track status
- **Refunds**: Request transaction refunds (manual processing required)
- **Cancellations**: Cancel pending orders (manual processing required)
- **IPN Support**: Register IPN callbacks for payment notifications

For detailed usage examples, see the main README.md file.
