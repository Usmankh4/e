#!/usr/bin/env python
import os
import json
import stripe
import requests
import argparse
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def create_test_checkout_session():
    """Create a test checkout session"""
    print("Creating test checkout session...")
    
    try:
        # Create a checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Test Product',
                    },
                    'unit_amount': 2000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:3000/checkout/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/checkout/cancel?session_id={CHECKOUT_SESSION_ID}',
        )
        
        print(f"✅ Checkout session created with ID: {session.id}")
        print(f"Checkout URL: {session.url}")
        
        return session.id
    except Exception as e:
        print(f"❌ Error creating checkout session: {str(e)}")
        return None

def expire_checkout_session(session_id):
    """Expire a checkout session"""
    print(f"Expiring checkout session {session_id}...")
    
    try:
        # Expire the session
        session = stripe.checkout.Session.expire(session_id)
        print(f"✅ Session {session_id} expired")
        return True
    except Exception as e:
        print(f"❌ Error expiring session: {str(e)}")
        return False

def test_webhook_endpoint(session_id, webhook_url, webhook_secret):
    """Test the webhook endpoint with a constructed event"""
    print(f"Testing webhook endpoint with session {session_id}...")
    
    try:
        # Retrieve the session to get its data
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Construct a mock event
        event = {
            'id': f'evt_test_{datetime.now().timestamp()}',
            'object': 'event',
            'api_version': '2023-10-16',
            'created': int(datetime.now().timestamp()),
            'data': {
                'object': session
            },
            'livemode': False,
            'pending_webhooks': 1,
            'request': {
                'id': None,
                'idempotency_key': None
            },
            'type': 'checkout.session.expired'
        }
        
        # Sign the payload
        payload = json.dumps(event)
        signature = stripe.WebhookSignature.generate_signature(
            payload.encode('utf-8'),
            webhook_secret,
            int(datetime.now().timestamp())
        )
        
        # Send the webhook
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': signature
        }
        
        response = requests.post(webhook_url, headers=headers, data=payload)
        
        print(f"Webhook response status: {response.status_code}")
        print(f"Webhook response body: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return False

def check_inventory_reservation(session_id, api_url):
    """Check if there are any active inventory reservations for the session"""
    print(f"Checking inventory reservations for session {session_id}...")
    
    try:
        # Call your custom API endpoint to check reservations
        response = requests.post(
            f"{api_url}/api/release-checkout-reservation/", 
            json={'session_id': session_id}
        )
        
        print(f"Reservation check response status: {response.status_code}")
        print(f"Reservation check response body: {response.text}")
        
        return response.json()
    except Exception as e:
        print(f"❌ Error checking reservations: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Stripe webhook functionality')
    parser.add_argument('--action', choices=['create', 'expire', 'webhook', 'check', 'all'], 
                        default='all', help='Action to perform')
    parser.add_argument('--session-id', help='Existing session ID to use')
    parser.add_argument('--webhook-url', default='http://localhost:8000/webhook/', 
                        help='Webhook URL to test')
    parser.add_argument('--api-url', default='http://localhost:8000', 
                        help='Base API URL')
    
    args = parser.parse_args()
    
    # Get webhook secret from environment
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        print("❌ STRIPE_WEBHOOK_SECRET not found in environment")
        exit(1)
    
    session_id = args.session_id
    
    if args.action in ['create', 'all'] and not session_id:
        session_id = create_test_checkout_session()
        if not session_id:
            exit(1)
    
    if args.action in ['expire', 'all'] and session_id:
        if not expire_checkout_session(session_id):
            exit(1)
    
    if args.action in ['webhook', 'all'] and session_id:
        if not test_webhook_endpoint(session_id, args.webhook_url, webhook_secret):
            exit(1)
    
    if args.action in ['check', 'all'] and session_id:
        result = check_inventory_reservation(session_id, args.api_url)
        if not result:
            exit(1)
    
    print("✅ All tests completed successfully")
