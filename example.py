"""
Example usage of the Pesapal Python client.

This example demonstrates how to use the pesapal-py-v3 package
to integrate Pesapal payments in a Python application.
"""

import os
from pesapal_py_v3 import (
    Pesapal, 
    PesapalConfig, 
    IPNData, 
    OrderData, 
    BillingAddress,
    PesapalError
)

def main():
    """Main example function."""
    
    # Configuration
    config = PesapalConfig(
        consumer_key=os.getenv('PESAPAL_CONSUMER_KEY', 'your_consumer_key'),
        consumer_secret=os.getenv('PESAPAL_CONSUMER_SECRET', 'your_consumer_secret'),
        api_base_url='https://cybqa.pesapal.com/pesapalv3/api'  # Sandbox
    )
    
    # Initialize client using context manager (recommended)
    with Pesapal(config) as client:
        try:
            # Step 1: Get authentication token
            print("Getting authentication token...")
            token = client.get_auth_token()
            print(f"✅ Token obtained: {token[:20]}...")
            
            # Step 2: Register IPN URL (do this once)
            print("\nRegistering IPN URL...")
            ipn_data = IPNData(
                url='https://yourdomain.com/payment-notification',
                ipn_notification_type='POST'
            )
            
            ipn_response = client.register_ipn(ipn_data)
            print(f"✅ IPN registered with ID: {ipn_response.ipn_id}")
            
            # Step 3: Create and submit an order
            print("\nSubmitting order...")
            
            # Create billing address
            billing_address = BillingAddress(
                email_address='customer@example.com',
                phone_number='254700000000',
                first_name='John',
                last_name='Doe'
            )
            
            # Create order data
            order_data = OrderData(
                id='example-order-001',
                currency='KES',
                amount=1000.0,
                description='Payment for example goods',
                callback_url='https://yourdomain.com/payment-callback',
                notification_id=ipn_response.ipn_id,
                billing_address=billing_address
            )
            
            order_response = client.submit_order(order_data)
            print(f"✅ Order submitted successfully!")
            print(f"   Order Tracking ID: {order_response.order_tracking_id}")
            print(f"   Redirect URL: {order_response.redirect_url}")
            
            # Step 4: Check transaction status
            print("\nChecking transaction status...")
            status = client.get_transaction_status(order_response.order_tracking_id)
            print(f"✅ Transaction status: {status.status}")
            if status.amount:
                print(f"   Amount: {status.currency} {status.amount}")
            
        except PesapalError as e:
            print(f"❌ Pesapal API error: {e.message}")
            if e.response_data:
                print(f"   Response data: {e.response_data}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

if __name__ == '__main__':
    main()
