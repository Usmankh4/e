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
       
        logger.info(f"Processing cart items: {cart_items}")
        logger.info(f"Success URL: {success_url}, Cancel URL: {cancel_url}")
       
        if not cart_items:
            return JsonResponse(
                {'error': 'No items in cart'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        # Validate and reserve inventory
        line_items = []
        session_id = None
        reservations = []
       
        with transaction.atomic():
            # Generate a unique session ID
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[],  # Empty for now
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            session_id = checkout_session.id
           
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
                    # Release any reservations made so far
                    for reservation in reservations:
                        variant = reservation.variant
                        variant.reserved_stock -= reservation.quantity
                        variant.save()
                        reservation.delete()
                   
                    return JsonResponse(
                        {'error': f'Variant with ID {variant_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
               
                # Check if there's enough stock
                if variant.available_stock < quantity:
                    # Release any reservations made so far
                    for reservation in reservations:
                        variant = reservation.variant
                        variant.reserved_stock -= reservation.quantity
                        variant.save()
                        reservation.delete()
                   
                    return JsonResponse(
                        {'error': f'Not enough stock for {variant.product.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
               
                # Create a reservation
                expires_at = timezone.now() + timedelta(minutes=15)
                reservation = InventoryReservation.objects.create(
                    variant=variant,
                    quantity=quantity,
                    session_id=session_id,
                    expires_at=expires_at,
                    is_active=True
                )
                reservations.append(reservation)
               
                # Update reserved stock
                variant.reserved_stock += quantity
                variant.save()
               
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
           
            # Update the session with line items
            checkout_session = stripe.checkout.Session.modify(
                session_id,
                line_items=line_items,
                metadata={
                    'session_id': session_id,
                }
            )
           
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
       
        # Check if there's enough stock
        if variant.available_stock < quantity:
            return JsonResponse(
                {
                    'error': f'Not enough stock for {variant.product.name}',
                    'available': variant.available_stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )
       
        # Create a checkout session
        try:
            line_items = []
            
            # Check if we have a valid Stripe price ID
            if variant.stripe_price_id:
                logger.info(f"Using existing Stripe price ID: {variant.stripe_price_id}")
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
            expires_at = timezone.now() + timedelta(minutes=15)
           
            reservation = InventoryReservation.objects.create(
                variant=variant,
                quantity=quantity,
                session_id=session_id,
                expires_at=expires_at,
                is_active=True
            )
           
            # Update reserved stock
            variant.reserved_stock += quantity
            variant.save()
       
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
