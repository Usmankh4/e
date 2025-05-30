import json
import stripe
import logging
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework import status

from .models import Product, ProductVariant, InventoryReservation

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

# Log Stripe configuration status without exposing any secrets
logger.info("Stripe API configuration initialized")

# Fallback to environment variable if not in settings (without hardcoding)
if not settings.STRIPE_SECRET_KEY:
    logger.warning("Stripe API key not found in settings, checking environment variables")

@csrf_exempt
@require_POST
@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    """
    Create a Stripe checkout session for the items in the cart
    No inventory reservations are made - stock is only reduced when payment is confirmed
    """
    try:
        # Ensure Stripe API key is set
        if not stripe.api_key:
            stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv('STRIPE_SECRET_KEY')
            logger.info("Setting Stripe API key from configuration")
            
        # Log the request for debugging
        logger.info(f"Received checkout request: {request.body.decode('utf-8')}")
        
        # Check if Stripe API key is set
        if not stripe.api_key:
            logger.error("Stripe API key is not set")
            return JsonResponse(
                {'error': 'Stripe API key is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        data = json.loads(request.body)
        cart_items = data.get('items', [])
        success_url = data.get('success_url', settings.STRIPE_SUCCESS_URL)
        cancel_url = data.get('cancel_url', settings.STRIPE_CANCEL_URL)
        
        # Ensure the cancel_url includes the session_id parameter
        if '?' not in cancel_url:
            cancel_url = f"{cancel_url}?session_id={{CHECKOUT_SESSION_ID}}"
        elif 'session_id=' not in cancel_url:
            cancel_url = f"{cancel_url}&session_id={{CHECKOUT_SESSION_ID}}"
       
        logger.info(f"Processing cart items: {cart_items}")
        logger.info(f"Success URL: {success_url}, Cancel URL: {cancel_url}")
       
        if not cart_items:
            return JsonResponse(
                {'error': 'No items in cart'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        # Prepare line items for checkout
        line_items = []
        
        # Process each item in the cart
        for item in cart_items:
            variant_id = item.get('variant_id')
            quantity = int(item.get('quantity', 1))
            
            # Log the variant_id for debugging
            logger.info(f"Processing cart item with variant_id: {variant_id}, type: {type(variant_id)}")
            
            # Get the variant
            try:
                # Try to convert variant_id to int if it's a string
                if isinstance(variant_id, str) and variant_id.isdigit():
                    variant_id = int(variant_id)
                
                variant = ProductVariant.objects.get(id=variant_id)
                logger.info(f"Found variant: {variant.id} - {variant.product.name}")
            except ProductVariant.DoesNotExist:
                return JsonResponse(
                    {'error': f'Variant with ID {variant_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
           
            # Check if there's enough stock (just for validation)
            if variant.count_in_stock < quantity:
                return JsonResponse(
                    {'error': f'Not enough stock for {variant.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add to line items
            if variant.stripe_price_id:
                line_items.append({
                    'price': variant.stripe_price_id,
                    'quantity': quantity,
                })
            else:
                # Create price data on the fly
                logger.info(f"Creating price data on the fly for variant {variant.id}")
                price_in_cents = int(float(variant.price) * 100)
                
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{variant.product.name} - {variant.color} {variant.storage}",
                            'description': f"{variant.product.name} with {variant.color} color and {variant.storage} storage",
                            'metadata': {
                                'variant_id': str(variant.id),
                                'product_id': str(variant.product.id),
                                'color': variant.color,
                                'storage': variant.storage
                            }
                        },
                        'unit_amount': price_in_cents,
                    },
                    'quantity': quantity,
                })
        
        # Create the checkout session with all line items
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'items': json.dumps([{
                    'variant_id': item.get('variant_id'),
                    'quantity': item.get('quantity', 1)
                } for item in cart_items])
            }
        )
        
        # Reserve inventory for this session
        try:
            with transaction.atomic():
                for item in cart_items:
                    variant_id = item.get('variant_id')
                    quantity = int(item.get('quantity', 1))
                    
                    if not variant_id or quantity <= 0:
                        continue
                        
                    if isinstance(variant_id, str) and variant_id.isdigit():
                        variant_id = int(variant_id)
                    
                    try:
                        variant = ProductVariant.objects.select_for_update().get(id=variant_id)
                        
                        # Check if there's enough available stock
                        if variant.count_in_stock < quantity:
                            raise Exception(f'Not enough stock for {variant.product.name}')
                            
                        # Create reservation
                        reservation = InventoryReservation.objects.create(
                            variant=variant,
                            quantity=quantity,
                            session_id=checkout_session.id,
                            expires_at=timezone.now() + timedelta(minutes=3)  # 10 min reservation
                        )
                        
                        # Update reserved stock
                        variant.reserved_stock += quantity
                        variant.save()
                        
                        logger.info(f"Reserved {quantity} units of variant {variant.id} for session {checkout_session.id}")
                        
                    except ProductVariant.DoesNotExist:
                        raise Exception(f'Variant with ID {variant_id} not found')
                        
        except Exception as e:
            # If we can't reserve inventory, cancel the checkout session
            try:
                stripe.checkout.Session.expire(checkout_session.id)
            except Exception:
                pass
            raise e
        
        logger.info(f"Created checkout session: {checkout_session.id}")
        
        return JsonResponse({
            'id': checkout_session.id,
            'url': checkout_session.url
        })
   
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return JsonResponse(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_session_details(request):
    """
    Get details of a Stripe checkout session
    """
    try:
        session_id = request.GET.get('session_id')
       
        if not session_id:
            return JsonResponse(
                {'error': 'Session ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['line_items', 'payment_intent']
        )
       
        return JsonResponse({
            'id': session.id,
            'status': session.status,
            'payment_status': session.payment_status,
            'amount_total': session.amount_total,
            'currency': session.currency,
            'customer_email': session.customer_details.email if session.customer_details else None,
            'line_items': [
                {
                    'price_id': item.price.id,
                    'quantity': item.quantity,
                    'amount_total': item.amount_total,
                    'description': item.description
                }
                for item in session.line_items.data
            ] if session.line_items else []
        })
   
    except Exception as e:
        logger.error(f"Error getting session details: {str(e)}")
        return JsonResponse(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_buy_now_session(request):
    """
    Create a Stripe checkout session for a single item (Buy Now)
    """
    try:
        # Ensure Stripe API key is set
        if not stripe.api_key:
            stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv('STRIPE_SECRET_KEY')
            logger.info("Setting Stripe API key from configuration")
            
        data = json.loads(request.body)
        logger.info(f"Buy Now request data: {data}")
        
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        success_url = data.get('success_url', settings.STRIPE_SUCCESS_URL)
        cancel_url = data.get('cancel_url', settings.STRIPE_CANCEL_URL)
        
        # Ensure the cancel_url includes the session_id parameter
        if '?' not in cancel_url:
            cancel_url = f"{cancel_url}?session_id={{CHECKOUT_SESSION_ID}}"
        elif 'session_id=' not in cancel_url:
            cancel_url = f"{cancel_url}&session_id={{CHECKOUT_SESSION_ID}}"
        
        logger.info(f"Parsed data - variant_id: {variant_id}, quantity: {quantity}")
        
        if not variant_id:
            logger.error("Missing variant_id in request")
            return JsonResponse(
                {'error': 'Variant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        # Get the variant
        try:
            logger.info(f"Looking up variant with ID: {variant_id}")
            variant = ProductVariant.objects.get(id=variant_id)
            logger.info(f"Found variant: {variant.id} - {variant.product.name} - {variant.color} - {variant.storage}")
        except ProductVariant.DoesNotExist:
            logger.error(f"Variant with ID {variant_id} not found")
            return JsonResponse(
                {'error': f'Variant with ID {variant_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
       
        # Check if there's enough available stock (total - reserved)
        available_stock = variant.count_in_stock - variant.reserved_stock
        if available_stock < quantity:
            return JsonResponse(
                {
                    'error': f'Not enough stock for {variant.product.name}. Only {available_stock} available',
                    'available': available_stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )
       
        # Create a checkout session
        try:
            line_items = []
            
            # Always create price data on the fly
            logger.info(f"Creating price data for variant {variant.id}")
            price_in_cents = int(float(variant.price) * 100)
            
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{variant.product.name} - {variant.color} {variant.storage}",
                        'description': f"{variant.product.name} with {variant.color} color and {variant.storage} storage",
                        'metadata': {
                            'variant_id': str(variant.id),
                            'product_id': str(variant.product.id),
                            'color': variant.color,
                            'storage': variant.storage
                        }
                    },
                    'unit_amount': price_in_cents,
                    'recurring': None,  # Make it a one-time payment
                },
                'quantity': quantity,
            })
            
            logger.info(f"Creating checkout session with line items: {line_items}")
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'variant_id': str(variant_id),
                    'quantity': str(quantity)
                }
            )
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            return JsonResponse(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
       
        # Create a reservation
        with transaction.atomic():
            session_id = checkout_session.id
            expires_at = timezone.now() + timedelta(minutes=3)  # 5-minute reservation
           
            # Create a reservation record but don't actually reduce available inventory
            # This is just to track the intent to purchase
            reservation = InventoryReservation.objects.create(
                variant=variant,
                quantity=quantity,
                session_id=session_id,
                expires_at=expires_at,
                is_active=True
            )
           
            # Update reserved_stock to reflect the new reservation
            # count_in_stock remains the same until payment is confirmed
            variant.reserved_stock += quantity
            variant.save()
            
            # Log the reservation
            logger.info(f"Created reservation for session {session_id}, variant {variant.id}, quantity {quantity}")
        
        return JsonResponse({
            'id': checkout_session.id,
            'url': checkout_session.url
        })
   
    except Exception as e:
        logger.error(f"Error creating buy now session: {str(e)}")
        return JsonResponse(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def test_stripe_config(request):
    """
    Test endpoint to verify Stripe configuration
    """
    try:
        # Ensure Stripe API key is set
        if not stripe.api_key:
            stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv('STRIPE_SECRET_KEY')
        
        # Log the Stripe API key status (without exposing the actual key)
        logger.info(f"Stripe API key set: {bool(stripe.api_key)}")
        
        # Try to make a simple Stripe API call to verify configuration
        balance = stripe.Balance.retrieve()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Stripe configuration is valid',
            'stripe_key_configured': bool(stripe.api_key),
            'available_balance': balance.available[0].amount if balance.available else 0
        })
    except Exception as e:
        logger.error(f"Error testing Stripe configuration: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Stripe configuration error: {str(e)}',
            'stripe_key_configured': bool(stripe.api_key)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        # Check if this is a test request
        if sig_header == 'test_signature':
            # For testing, parse the JSON directly
            event = json.loads(payload)
            logger.info(f"Received test webhook event: {event['type']}")
        else:
            # Verify webhook signature for real events
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get the session ID and metadata
        session_id = session.id
        
        logger.info(f"Processing successful payment for session: {session_id}")
        
        # Get the items from the session metadata
        try:
            items_json = session.get('metadata', {}).get('items', '[]')
            items = json.loads(items_json)
            logger.info(f"Items from metadata: {items}")
            
            # If no items in metadata, try to get them from the line items
            if not items and hasattr(session, 'line_items'):
                items = []
                for item in session.line_items.data:
                    if 'price' in item and 'product' in item.price:
                        variant_id = item.price.product.metadata.get('variant_id')
                        if variant_id:
                            items.append({
                                'variant_id': variant_id,
                                'quantity': item.quantity
                            })
            
            # Update inventory in a transaction
            with transaction.atomic():
                for item in items:
                    variant_id = item.get('variant_id')
                    quantity = int(item.get('quantity', 1))
                    
                    # Skip if variant_id or quantity is invalid
                    if not variant_id or quantity <= 0:
                        continue
                    
                    # Convert variant_id to int if it's a string
                    if isinstance(variant_id, str) and variant_id.isdigit():
                        variant_id = int(variant_id)
                    
                    try:
                        # Get the variant and update inventory
                        variant = ProductVariant.objects.select_for_update().get(id=variant_id)
                        
                        # Only reduce inventory if there's enough stock
                        if variant.count_in_stock >= quantity:
                            # Update inventory count - ONLY on successful payment
                            variant.count_in_stock -= quantity
                            variant.save()
                            
                            logger.info(f"Updated inventory for variant {variant.id}: "
                                      f"count_in_stock={variant.count_in_stock}")
                        else:
                            logger.warning(f"Not enough stock for variant {variant.id}: "
                                         f"requested={quantity}, available={variant.count_in_stock}")
                    except ProductVariant.DoesNotExist:
                        logger.error(f"Variant with ID {variant_id} not found")
                
                return JsonResponse({'status': 'payment_processed'})
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # Handle the checkout.session.expired and checkout.session.canceled events
    elif event['type'] in ['checkout.session.expired', 'checkout.session.canceled']:
        session = event['data']['object']
        session_id = session.id
        
        logger.info(f"Processing {event['type']} event for session: {session_id}")
        
        try:
            with transaction.atomic():
                # Get all active reservations for this session
                reservations = InventoryReservation.objects.filter(
                    session_id=session_id,
                    is_active=True
                ).select_for_update()
                
                if not reservations.exists():
                    logger.info(f"No active reservations to release for session {session_id}")
                    return JsonResponse({'status': 'no_reservations_found'})
                
                # Process each reservation
                for reservation in reservations:
                    variant = reservation.variant
                    
                    # Mark reservation as canceled
                    reservation.is_active = False
                    reservation.canceled_at = timezone.now()
                    reservation.save()
                    
                    # Release the reserved stock
                    variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
                    variant.save()
                    
                    logger.info(f"Released {reservation.quantity} units of variant {variant.id} "
                               f"from canceled/expired session {session_id}")
                
                return JsonResponse({'status': 'reservations_released'})
                
        except Exception as e:
            logger.error(f"Error processing {event['type']} event: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # Return a 200 response to acknowledge receipt of the event
    return JsonResponse({'status': 'received'})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def release_checkout_reservation(request):
    """
    Release inventory reservations for a canceled checkout session.
    This is called when a user cancels the checkout or the session expires.
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse(
                {'error': 'Session ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Releasing reservations for session: {session_id}")
        
        # Release reserved inventory in a transaction
        with transaction.atomic():
            # Get all active reservations for this session
            reservations = InventoryReservation.objects.filter(
                session_id=session_id,
                is_active=True
            ).select_for_update()
            
            if not reservations.exists():
                logger.info(f"No active reservations found for session {session_id}")
                return JsonResponse({'status': 'no_reservations_found'})
            
            # Release each reservation
            for reservation in reservations:
                variant = reservation.variant
                
                # Log before state
                logger.info(f"Before release - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                          f"reserved_stock={variant.reserved_stock}")
                
                # Mark reservation as canceled
                reservation.is_active = False
                reservation.canceled_at = timezone.now()
                reservation.save()
                
                # Release the reserved stock
                variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
                variant.save()
                
                # Log after state
                logger.info(f"After release - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                          f"reserved_stock={variant.reserved_stock}")
            
            logger.info(f"Successfully released {reservations.count()} reservations for session {session_id}")
            return JsonResponse({
                'status': 'success',
                'message': f'Released {reservations.count()} reservations',
                'reservations_released': reservations.count()
            })
            
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error releasing reservation: {str(e)}", exc_info=True)
        return JsonResponse(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def debug_inventory_reservation(request):
    """
    Debug endpoint to check the status of inventory reservations for a session
    """
    try:
        session_id = request.GET.get('session_id')
        variant_id = request.GET.get('variant_id')
        
        if not session_id and not variant_id:
            return JsonResponse(
                {'error': 'Either session_id or variant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Query parameters for reservations
        query_params = {}
        if session_id:
            query_params['session_id'] = session_id
        if variant_id:
            query_params['variant_id'] = variant_id
        
        # Get all reservations matching the query
        reservations = InventoryReservation.objects.filter(**query_params)
        
        # Prepare response data
        reservations_data = []
        for res in reservations:
            variant = res.variant
            reservations_data.append({
                'id': res.id,
                'variant_id': variant.id,
                'product_name': variant.product.name,
                'color': variant.color,
                'storage': variant.storage,
                'quantity': res.quantity,
                'session_id': res.session_id,
                'is_active': res.is_active,
                'created_at': res.created_at.isoformat(),
                'expires_at': res.expires_at.isoformat(),
                'fulfilled_at': res.fulfilled_at.isoformat() if res.fulfilled_at else None,
                'canceled_at': res.canceled_at.isoformat() if res.canceled_at else None,
                'variant_data': {
                    'count_in_stock': variant.count_in_stock,
                    'reserved_stock': variant.reserved_stock,
                    'available_stock': variant.available_stock,
                    'is_in_stock': variant.is_in_stock
                }
            })
        
        return JsonResponse({
            'count': len(reservations_data),
            'reservations': reservations_data
        })
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return JsonResponse(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
