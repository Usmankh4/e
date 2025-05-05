import json
import stripe
import logging
import os
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import ProductVariant, InventoryReservation, InventoryChange

logger = logging.getLogger(__name__)

# Configure Stripe with the API key safely
logger.info("Initializing Stripe webhook handler")
if not stripe.api_key:
    stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv('STRIPE_SECRET_KEY')

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        handle_checkout_completed(event['data']['object'])
    elif event['type'] == 'checkout.session.expired':
        handle_checkout_expired(event['data']['object'])
    elif event['type'] == 'checkout.session.async_payment_failed':
        handle_checkout_expired(event['data']['object'])  # Treat as expired to release inventory
    elif event['type'] == 'payment_intent.canceled':
        handle_checkout_expired(event['data']['object'])  # Treat as expired to release inventory
    elif event['type'] == 'checkout.session.async_payment_succeeded':
        handle_checkout_completed(event['data']['object'])
    
    return HttpResponse(status=200)

@transaction.atomic
def handle_checkout_completed(session):
    """
    Handle the checkout.session.completed event
    """
    try:
        session_id = session['id']
        
        # Get all reservations for this session
        reservations = InventoryReservation.objects.filter(
            session_id=session_id,
            is_active=True
        )
        
        if not reservations.exists():
            logger.warning(f"No active reservations found for session {session_id}")
            return
        
        # Process each reservation
        for reservation in reservations:
            # Mark the reservation as inactive (fulfilled)
            reservation.is_active = False
            reservation.order_id = session_id
            reservation.save()
            
            # Update the variant's stock
            variant = reservation.variant
            variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
            # No need to update count_in_stock as it was already reserved
            variant.save()
            
            # Record the inventory change
            InventoryChange.objects.create(
                variant=variant,
                quantity=-reservation.quantity,  # Negative because it's a decrease
                reason='purchase',
                notes=f"Purchase from session {session_id}"
            )
            
        logger.info(f"Successfully processed checkout session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing checkout completion: {str(e)}")
        raise

@transaction.atomic
def handle_checkout_expired(session):
    """
    Handle the checkout.session.expired event
    """
    try:
        session_id = session['id']
        
        # Get all reservations for this session
        reservations = InventoryReservation.objects.filter(
            session_id=session_id,
            is_active=True
        )
        
        if not reservations.exists():
            logger.warning(f"No active reservations found for expired session {session_id}")
            return
        
        # Process each reservation
        for reservation in reservations:
            # Mark the reservation as inactive
            reservation.is_active = False
            reservation.save()
            
            # Release the reserved stock
            variant = reservation.variant
            variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
            variant.save()
            
            # Record the inventory change
            InventoryChange.objects.create(
                variant=variant,
                quantity=reservation.quantity,  # Positive because it's a release
                reason='release',
                notes=f"Released reservation for expired session {session_id}"
            )
            
        logger.info(f"Successfully released reservations for expired session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing checkout expiration: {str(e)}")
        raise
