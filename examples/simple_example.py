"""
Simple Python script example for Pesapal Python client.

This example demonstrates basic usage of the pesapal-v3 client
without web framework dependencies.

To run this example:
1. Install the package: pip install git+https://github.com/mwondhaf/pesapal-v3-python.git
2. Set your credentials as environment variables
3. Run: python simple_example.py
"""

import os
from pesapal_v3 import (
    Pesapal, 
    PesapalConfig, 
    IPNData, 
    OrderData, 
    BillingAddress,
    PesapalError
)

def main():
    # Configuration
    config = PesapalConfig(
        consumer_key=os.getenv('PESAPAL_CONSUMER_KEY', 'your_consumer_key'),
        consumer_secret=os.getenv('PESAPAL_CONSUMER_SECRET', 'your_consumer_secret'),
        api_base_url=os.getenv('PESAPAL_API_URL', 'https://cybqa.pesapal.com/pesapalv3/api')
    )
    
    print("🚀 Pesapal Python Client Example")
    print("================================")
    
    try:
        # Using context manager for automatic cleanup
        with Pesapal(config) as client:
            
            # Step 1: Register IPN URL
            print("\n1. Registering IPN URL...")
            ipn_data = IPNData(
                url="https://your-app.com/payment-notification",
                ipn_notification_type="POST"
            )
            
            ipn_response = client.register_ipn(ipn_data)
            print(f"   ✅ IPN registered with ID: {ipn_response.ipn_id}")
            
            # Step 2: Create billing address
            print("\n2. Creating billing address...")
            billing_address = BillingAddress(
                email_address="customer@example.com",
                phone_number="254700000000",
                first_name="John",
                last_name="Doe",
                country_code="KE",
                city="Nairobi",
                state="Nairobi",
                postal_code="00100",
                zip_code="00100"
            )
            print(f"   ✅ Billing address created for {billing_address.first_name} {billing_address.last_name}")
            
            # Step 3: Create order
            print("\n3. Creating payment order...")
            order_data = OrderData(
                id="demo-order-001",
                currency="KES",
                amount=100.0,
                description="Test payment for demo purposes",
                callback_url="https://your-app.com/payment-callback",
                notification_id=ipn_response.ipn_id,
                billing_address=billing_address
            )
            
            order_response = client.submit_order(order_data)
            print(f"   ✅ Order submitted with tracking ID: {order_response.order_tracking_id}")
            print(f"   🔗 Payment URL: {order_response.redirect_url}")
            
            # Step 4: Get transaction status
            print("\n4. Checking transaction status...")
            status = client.get_transaction_status(order_response.order_tracking_id)
            print(f"   📊 Status: {status.status}")
            print(f"   💰 Amount: {status.currency} {status.amount}")
            print(f"   📅 Created: {status.created_date}")
            
            # Step 5: List IPN endpoints
            print("\n5. Listing registered IPN endpoints...")
            ipn_list = client.get_ipn_list()
            print(f"   📋 Total IPNs: {len(ipn_list)}")
            for i, ipn in enumerate(ipn_list[:3], 1):  # Show first 3
                print(f"      {i}. {ipn.url} (ID: {ipn.ipn_id})")
            
    except PesapalError as e:
        print(f"\n❌ Pesapal API Error: {e.message}")
        if hasattr(e, 'status_code'):
            print(f"   Status Code: {e.status_code}")
        if hasattr(e, 'response_data'):
            print(f"   Response: {e.response_data}")
            
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
    
    print("\n" + "="*50)
    print("Example completed!")
    print("\n💡 Tips:")
    print("  - Set PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET environment variables")
    print("  - Use the demo environment for testing")
    print("  - Check the payment URL in a browser to complete the payment flow")

if __name__ == "__main__":
    main()
