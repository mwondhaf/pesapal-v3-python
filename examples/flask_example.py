"""
Flask example for Pesapal Python client.

This example demonstrates how to integrate Pesapal payments
in a Flask web application using the pesapal-v3 client.

To run this example:
1. Install dependencies: pip install flask pesapal-v3 python-dotenv
2. Create a .env file with your Pesapal credentials
3. Run: python flask_example.py
"""

import os
from flask import Flask, request, redirect, jsonify, render_template_string
from pesapal_v3 import Pesapal, PesapalConfig, IPNData, OrderData, BillingAddress, PesapalError

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Initialize Pesapal client
config = PesapalConfig(
    consumer_key=os.getenv('PESAPAL_CONSUMER_KEY', 'your_consumer_key'),
    consumer_secret=os.getenv('PESAPAL_CONSUMER_SECRET', 'your_consumer_secret'),
    api_base_url=os.getenv('PESAPAL_API_URL', 'https://cybqa.pesapal.com/pesapalv3/api')
)

# Store IPN ID (use database in production)
ipn_id = None

@app.route('/')
def home():
    """Simple payment form."""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pesapal Payment Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007cba; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
            .setup-btn { background: #28a745; margin-bottom: 20px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>Pesapal Payment Demo</h1>
        
        <button class="setup-btn" onclick="setupIPN()">Setup IPN (Do this first!)</button>
        <div id="ipn-status"></div>
        
        <h2>Make a Payment</h2>
        <form id="payment-form">
            <div class="form-group">
                <label>Amount (KES):</label>
                <input type="number" id="amount" required min="1" value="100">
            </div>
            <div class="form-group">
                <label>Email:</label>
                <input type="email" id="email" required value="test@example.com">
            </div>
            <div class="form-group">
                <label>First Name:</label>
                <input type="text" id="firstName" required value="John">
            </div>
            <div class="form-group">
                <label>Last Name:</label>
                <input type="text" id="lastName" required value="Doe">
            </div>
            <div class="form-group">
                <label>Phone Number:</label>
                <input type="tel" id="phone" required value="254700000000">
            </div>
            <button type="submit">Pay Now</button>
        </form>

        <script>
            async function setupIPN() {
                try {
                    const response = await fetch('/register-ipn', { method: 'POST' });
                    const result = await response.json();
                    
                    const statusDiv = document.getElementById('ipn-status');
                    if (result.success) {
                        statusDiv.innerHTML = '<div class="status success">✅ IPN registered successfully!</div>';
                    } else {
                        statusDiv.innerHTML = '<div class="status error">❌ Failed to register IPN: ' + result.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('ipn-status').innerHTML = 
                        '<div class="status error">❌ Error: ' + error.message + '</div>';
                }
            }

            document.getElementById('payment-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = {
                    amount: document.getElementById('amount').value,
                    email: document.getElementById('email').value,
                    first_name: document.getElementById('firstName').value,
                    last_name: document.getElementById('lastName').value,
                    phone: document.getElementById('phone').value
                };

                try {
                    const response = await fetch('/initiate-payment', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        // Redirect to Pesapal payment page
                        window.location.href = result.redirect_url;
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/register-ipn', methods=['POST'])
def register_ipn():
    """Register IPN URL with Pesapal."""
    global ipn_id
    
    try:
        with Pesapal(config) as client:
            ipn_data = IPNData(
                url=f"{request.host_url}payment-notification",
                ipn_notification_type='POST'
            )
            response = client.register_ipn(ipn_data)
            ipn_id = response.ipn_id
            
            return jsonify({
                "success": True, 
                "ipn_id": ipn_id,
                "message": "IPN registered successfully"
            })
            
    except PesapalError as e:
        return jsonify({
            "success": False, 
            "error": f"Pesapal API error: {e.message}"
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": f"Unexpected error: {str(e)}"
        })

@app.route('/initiate-payment', methods=['POST'])
def initiate_payment():
    """Initiate a payment request."""
    try:
        data = request.get_json()
        
        if not ipn_id:
            return jsonify({
                "success": False,
                "error": "IPN not registered. Please register IPN first."
            })
        
        # Create billing address
        billing_address = BillingAddress(
            email_address=data['email'],
            phone_number=data['phone'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Create order data
        order_data = OrderData(
            id=f"order-{data.get('order_id', 'demo')}",
            currency=data.get('currency', 'KES'),
            amount=float(data['amount']),
            description=data.get('description', 'Payment for goods'),
            callback_url=f"{request.host_url}payment-callback",
            notification_id=ipn_id,
            billing_address=billing_address
        )
        
        with Pesapal(config) as client:
            response = client.submit_order(order_data)
            
            return jsonify({
                "success": True,
                "redirect_url": response.redirect_url,
                "order_tracking_id": response.order_tracking_id
            })
            
    except PesapalError as e:
        return jsonify({
            "success": False,
            "error": f"Pesapal API error: {e.message}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        })

@app.route('/payment-callback')
def payment_callback():
    """Handle payment callback from Pesapal."""
    order_tracking_id = request.args.get('OrderTrackingId')
    
    if not order_tracking_id:
        return "No order tracking ID provided", 400
    
    try:
        with Pesapal(config) as client:
            status = client.get_transaction_status(order_tracking_id)
            
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Payment Result</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                    .success { color: #28a745; }
                    .pending { color: #ffc107; }
                    .failed { color: #dc3545; }
                </style>
            </head>
            <body>
                <h1 class="{{ status_class }}">Payment {{ status_text }}</h1>
                <p>Status: <strong>{{ status.status }}</strong></p>
                {% if status.amount %}
                <p>Amount: <strong>{{ status.currency }} {{ status.amount }}</strong></p>
                {% endif %}
                <p>Order Tracking ID: <strong>{{ order_tracking_id }}</strong></p>
                <a href="/" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Return to Home</a>
            </body>
            </html>
            ''', 
            status=status,
            order_tracking_id=order_tracking_id,
            status_class="success" if status.status == "COMPLETED" else "pending" if status.status == "PENDING" else "failed",
            status_text="Successful!" if status.status == "COMPLETED" else "Pending" if status.status == "PENDING" else "Failed"
            )
            
    except PesapalError as e:
        return f"Error checking payment status: {e.message}", 500
    except Exception as e:
        return f"Unexpected error: {str(e)}", 500

@app.route('/payment-notification', methods=['POST'])
def payment_notification():
    """Handle IPN notification from Pesapal."""
    try:
        data = request.get_json()
        print(f"IPN Notification received: {data}")
        
        # Here you would typically:
        # 1. Verify the notification
        # 2. Update your database
        # 3. Send customer notifications
        
        order_tracking_id = data.get('OrderTrackingId')
        if order_tracking_id:
            with Pesapal(config) as client:
                status = client.get_transaction_status(order_tracking_id)
                print(f"Updated payment status: {status.status}")
        
        return "OK", 200
        
    except Exception as e:
        print(f"Error processing IPN: {str(e)}")
        return "OK", 200  # Always return OK to acknowledge receipt

if __name__ == '__main__':
    print("🚀 Starting Pesapal Flask Demo")
    print("📝 Steps to test:")
    print("1. Visit http://localhost:5000")
    print("2. Click 'Setup IPN' button first")
    print("3. Fill the payment form and submit")
    print()
    print("⚠️  Make sure to set your environment variables:")
    print("   PESAPAL_CONSUMER_KEY=your_key")
    print("   PESAPAL_CONSUMER_SECRET=your_secret")
    print()
    
    app.run(debug=True, port=5000)
