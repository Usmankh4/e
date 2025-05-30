import os
import django
import sys
import json
import stripe
import logging
from datetime import datetime, timedelta

# Set up Django environment
sys.path.append('/Users/usmankhan/stack/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from myapp.models import InventoryReservation, ProductVariant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get Stripe API key from environment or set it directly here
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'your_stripe_secret_key_here')

def check_reservations(variant_id=None, session_id=None):
    """Check active reservations for a variant or session"""
    query = InventoryReservation.objects.filter(is_active=True)
    
    if variant_id:
        query = query.filter(variant_id=variant_id)
    
    if session_id:
        query = query.filter(session_id=session_id)
    
    reservations = query.all()
    
    logger.info(f"Found {len(reservations)} active reservations")
    
    for res in reservations:
        variant = res.variant
        logger.info(f"Reservation {res.id}: variant={variant.id}, quantity={res.quantity}, "
                   f"session_id={res.session_id}, created_at={res.created_at}, "
                   f"expires_at={res.expires_at}")
        
        logger.info(f"Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                   f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
    
    return reservations

def create_test_checkout_session(variant_id, quantity=1):
    """Create a test checkout session for a variant"""
    # Get the variant
    variant = ProductVariant.objects.get(id=variant_id)
    
    # Create a checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': variant.stripe_price_id,
                'quantity': quantity,
            }],
            mode='payment',
            success_url='http://localhost:3000/checkout/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/checkout/cancel?session_id={CHECKOUT_SESSION_ID}',
        )
        
        logger.info(f"Created checkout session: {session.id}")
        
        # Create a reservation
        expiration_time = timezone.now() + timedelta(minutes=5)
        reservation = InventoryReservation.objects.create(
            variant=variant,
            quantity=quantity,
            session_id=session.id,
            expires_at=expiration_time,
            is_active=True
        )
        
        # Update variant's reserved stock
        variant.reserved_stock += quantity
        variant.save()
        
        logger.info(f"Created reservation: {reservation.id}")
        logger.info(f"Updated variant reserved_stock: {variant.reserved_stock}")
        
        return session
    
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return None

def simulate_webhook_event(session_id, event_type='checkout.session.canceled'):
    """Simulate a webhook event for a checkout session"""
    try:
        # Get the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Create a webhook event payload
        event = {
            'id': f'evt_test_{int(datetime.now().timestamp())}',
            'type': event_type,
            'data': {
                'object': session
            }
        }
        
        logger.info(f"Simulating {event_type} event for session: {session_id}")
        
        # Make a request to your webhook endpoint
        import requests
        webhook_url = 'http://localhost:8000/myapp/api/webhook/'
        
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': 'test_signature'  # Your webhook handler should bypass signature verification for this test
        }
        
        response = requests.post(
            webhook_url,
            headers=headers,
            data=json.dumps(event)
        )
        
        logger.info(f"Webhook response: {response.status_code} - {response.text}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error simulating webhook event: {str(e)}")
        return None

def test_manual_release(session_id):
    """Test the manual release endpoint"""
    try:
        import requests
        
        release_url = 'http://localhost:8000/myapp/api/release-checkout-reservation/'
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'session_id': session_id
        }
        
        logger.info(f"Testing manual release for session: {session_id}")
        
        response = requests.post(
            release_url,
            headers=headers,
            json=data
        )
        
        logger.info(f"Manual release response: {response.status_code} - {response.text}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error testing manual release: {str(e)}")
        return None

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python test_webhook.py <command> [args]")
        print("Commands:")
        print("  check_reservations [variant_id] [session_id] - Check active reservations")
        print("  create_session <variant_id> [quantity] - Create a test checkout session")
        print("  simulate_webhook <session_id> [event_type] - Simulate a webhook event")
        print("  test_release <session_id> - Test manual release endpoint")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check_reservations":
        variant_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        session_id = sys.argv[3] if len(sys.argv) > 3 else None
        check_reservations(variant_id, session_id)
    
    elif command == "create_session":
        if len(sys.argv) < 3:
            print("Error: variant_id is required")
            sys.exit(1)
        
        variant_id = int(sys.argv[2])
        quantity = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        
        session = create_test_checkout_session(variant_id, quantity)
        if session:
            print(f"Session created: {session.id}")
            print(f"Checkout URL: {session.url}")
    
    elif command == "simulate_webhook":
        if len(sys.argv) < 3:
            print("Error: session_id is required")
            sys.exit(1)
        
        session_id = sys.argv[2]
        event_type = sys.argv[3] if len(sys.argv) > 3 else 'checkout.session.canceled'
        
        simulate_webhook_event(session_id, event_type)
    
    elif command == "test_release":
        if len(sys.argv) < 3:
            print("Error: session_id is required")
            sys.exit(1)
        
        session_id = sys.argv[2]
        test_manual_release(session_id)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
