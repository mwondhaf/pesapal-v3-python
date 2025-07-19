#!/usr/bin/env python3
"""
Pesapal Refund and Cancellation Example

This example demonstrates how to use the Pesapal client to:
1. Check transaction status
2. Request refunds for completed transactions
3. Cancel pending transactions

Note: Pesapal API v3 does not provide direct refund/cancellation endpoints.
These methods provide structured guidance for manual processing.
"""

import os
import sys
from pesapal_v3 import Pesapal, PesapalConfig, PesapalError


def main():
    """Main example function."""
    
    # Configuration - use environment variables for security
    config = PesapalConfig(
        consumer_key=os.getenv('PESAPAL_CONSUMER_KEY', 'qkio1BGGYAXTu2JOfm7XSXNruoZsrqEW'),  # Demo key
        consumer_secret=os.getenv('PESAPAL_CONSUMER_SECRET', 'osGQ364R49cXKeOYSpaOnT++rHs='),  # Demo secret
        api_base_url='https://cybqa.pesapal.com/pesapalv3/api'  # Demo environment
        # For production: 'https://pay.pesapal.com/v3/api'
    )
    
    # Example order tracking ID (replace with actual tracking ID)
    order_tracking_id = input("Enter the order tracking ID: ").strip()
    
    if not order_tracking_id:
        print("No tracking ID provided. Using demo tracking ID for demonstration.")
        order_tracking_id = "demo-tracking-123"
    
    try:
        with Pesapal(config) as client:
            print("Pesapal Refund and Cancellation Demo")
            print("=" * 50)
            
            # Step 1: Check transaction status
            print(f"\n1. Checking status for transaction: {order_tracking_id}")
            try:
                status = client.get_transaction_status(order_tracking_id)
                print(f"   Status: {getattr(status, 'payment_status_description', 'Unknown')}")
                print(f"   Amount: {getattr(status, 'amount', 'N/A')}")
                print(f"   Currency: {getattr(status, 'currency', 'N/A')}")
                print(f"   Payment Method: {getattr(status, 'payment_method', 'N/A')}")
            except PesapalError as e:
                print(f"   Error checking status: {e}")
                return
            
            # Step 2: Demonstrate refund functionality
            print(f"\n2. Refund Options")
            print("=" * 30)
            
            action = input("Choose action: (r)efund, (c)ancel, or (s)kip: ").strip().lower()
            
            if action == 'r':
                # Refund example
                print("\nRefund Options:")
                print("1. Full refund")
                print("2. Partial refund")
                
                refund_type = input("Choose refund type (1 or 2): ").strip()
                
                try:
                    if refund_type == "1":
                        # Full refund
                        result = client.refund_transaction(
                            order_tracking_id=order_tracking_id,
                            reason="Customer requested full refund"
                        )
                        print("\nFull Refund Request:")
                    elif refund_type == "2":
                        # Partial refund
                        amount = float(input("Enter refund amount: "))
                        result = client.refund_transaction(
                            order_tracking_id=order_tracking_id,
                            amount=amount,
                            reason="Customer requested partial refund"
                        )
                        print("\nPartial Refund Request:")
                    else:
                        print("Invalid refund type selected.")
                        return
                    
                    # Display refund result
                    print(f"   Order ID: {result['order_tracking_id']}")
                    print(f"   Refund Amount: {result['refund_amount']}")
                    print(f"   Transaction Amount: {result['transaction_amount']}")
                    print(f"   Type: {result['request_type']}")
                    print(f"   Status: {result['status']}")
                    
                    print("\nNext Steps:")
                    for instruction in result['instructions']:
                        print(f"   • {instruction}")
                    
                    print(f"\nSupport Contact:")
                    support = result['support_details']
                    print(f"   Email: {support['support_email']}")
                    print(f"   Phone: {support['merchant_phone']}")
                    
                except PesapalError as e:
                    print(f"   Refund Error: {e}")
                except ValueError as e:
                    print(f"   Input Error: {e}")
            
            elif action == 'c':
                # Cancellation example
                print("\nCancellation Request:")
                
                reason = input("Enter cancellation reason: ").strip() or "Customer cancellation"
                
                try:
                    result = client.cancel_order(
                        order_tracking_id=order_tracking_id,
                        reason=reason
                    )
                    
                    print(f"   Order ID: {result['order_tracking_id']}")
                    print(f"   Current Status: {result['current_status']}")
                    print(f"   Request Status: {result['status']}")
                    print(f"   Reason: {result['reason']}")
                    
                    if 'instructions' in result:
                        print("\nNext Steps:")
                        for instruction in result['instructions']:
                            print(f"   • {instruction}")
                        
                        print(f"\nSupport Contact:")
                        support = result['support_details']
                        print(f"   Email: {support['support_email']}")
                        print(f"   Phone: {support['merchant_phone']}")
                    
                except PesapalError as e:
                    print(f"   Cancellation Error: {e}")
            
            else:
                print("Skipping refund/cancellation demo.")
            
            # Step 3: Additional examples
            print(f"\n3. Additional Examples")
            print("=" * 30)
            
            # Example of error handling
            print("\nExample: Invalid tracking ID handling")
            try:
                client.refund_transaction("")
            except ValueError as e:
                print(f"   Validation Error (expected): {e}")
            
            # Example of refund amount validation
            print("\nExample: Refund amount validation")
            try:
                # This will check the transaction first, then validate the amount
                client.refund_transaction(order_tracking_id, amount=999999999.99)
            except PesapalError as e:
                print(f"   Business Logic Error (expected): {e}")
            
            print("\n" + "=" * 50)
            print("Demo completed successfully!")
            print("\nImportant Notes:")
            print("• Pesapal API v3 doesn't provide direct refund/cancellation endpoints")
            print("• Use the merchant dashboard for actual refund processing")
            print("• Contact Pesapal support for complex refund scenarios")
            print("• Monitor transaction status changes via IPN notifications")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
