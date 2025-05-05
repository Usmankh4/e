import json
import logging
import uuid
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Product, ProductVariant
from .serializers import CartSerializer, CartItemSerializer
from .inventory_views import validate_inventory as check_inventory

logger = logging.getLogger('myapp')

def get_or_create_cart(request):
    """
    Helper function to get or create a cart based on user authentication status
    """
    user = request.user if request.user.is_authenticated else None
    
    if user:
        # Try to get the user's cart
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    # For anonymous users, use session ID
    session_id = request.COOKIES.get('cart_session_id')
    
    if not session_id:
        # Generate a new session ID if none exists
        session_id = str(uuid.uuid4())
    
    # Get or create cart for this session
    cart, created = Cart.objects.get_or_create(session_id=session_id)
    
    return cart, session_id if created else None


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request):
    """
    Get the current user's cart
    """
    try:
        result = get_or_create_cart(request)
        
        if isinstance(result, tuple):
            cart, session_id = result
        else:
            cart = result
            session_id = None
        
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        
        # Set session cookie if needed
        if session_id:
            response.set_cookie(
                'cart_session_id', 
                session_id, 
                max_age=60*60*24*30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        return Response(
            {"error": "Failed to retrieve cart"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """
    Add an item to the cart
    """
    try:
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the product
        product = get_object_or_404(Product, id=product_id)
        
        # Get the variant if specified
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
            
            # Check if there's enough stock
            if variant.available_stock < quantity:
                return Response(
                    {
                        "error": "Not enough stock available",
                        "available": variant.available_stock,
                        "requested": quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get or create the cart
        result = get_or_create_cart(request)
        
        if isinstance(result, tuple):
            cart, session_id = result
        else:
            cart = result
            session_id = None
        
        # Check if the item is already in the cart
        with transaction.atomic():
            if variant:
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    # Update quantity if item already exists
                    cart_item.quantity += quantity
                    cart_item.save()
            else:
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    variant=None,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    # Update quantity if item already exists
                    cart_item.quantity += quantity
                    cart_item.save()
        
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        
        # Set session cookie if needed
        if session_id:
            response.set_cookie(
                'cart_session_id', 
                session_id, 
                max_age=60*60*24*30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return Response(
            {"error": "Failed to add item to cart"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def update_cart_item(request, item_id):
    """
    Update the quantity of a cart item
    """
    try:
        quantity = int(request.data.get('quantity', 1))
        
        if quantity < 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the cart
        result = get_or_create_cart(request)
        
        if isinstance(result, tuple):
            cart, session_id = result
        else:
            cart = result
            session_id = None
        
        # Get the cart item
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock if there's a variant
        if cart_item.variant and cart_item.variant.available_stock < quantity:
            return Response(
                {
                    "error": "Not enough stock available",
                    "available": cart_item.variant.available_stock,
                    "requested": quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity == 0:
            # Remove the item if quantity is 0
            cart_item.delete()
        else:
            # Update the quantity
            cart_item.quantity = quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        
        # Set session cookie if needed
        if session_id:
            response.set_cookie(
                'cart_session_id', 
                session_id, 
                max_age=60*60*24*30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        return Response(
            {"error": "Failed to update cart item"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart
    """
    try:
        # Get the cart
        result = get_or_create_cart(request)
        
        if isinstance(result, tuple):
            cart, session_id = result
        else:
            cart = result
            session_id = None
        
        # Get the cart item
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete the cart item
        cart_item.delete()
        
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        
        # Set session cookie if needed
        if session_id:
            response.set_cookie(
                'cart_session_id', 
                session_id, 
                max_age=60*60*24*30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        return Response(
            {"error": "Failed to remove item from cart"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def merge_carts(request):
    """
    Merge an anonymous cart with the user's cart after login
    """
    try:
        session_id = request.COOKIES.get('cart_session_id')
        
        if not session_id:
            return Response(
                {"message": "No anonymous cart to merge"},
                status=status.HTTP_200_OK
            )
        
        # Get the anonymous cart
        try:
            anonymous_cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response(
                {"message": "No anonymous cart to merge"},
                status=status.HTTP_200_OK
            )
        
        # Get or create the user's cart
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Merge the carts
        with transaction.atomic():
            for anon_item in anonymous_cart.items.all():
                # Check if the item is already in the user's cart
                if anon_item.variant:
                    user_item, created = CartItem.objects.get_or_create(
                        cart=user_cart,
                        product=anon_item.product,
                        variant=anon_item.variant,
                        defaults={'quantity': anon_item.quantity}
                    )
                    
                    if not created:
                        # Update quantity if item already exists
                        user_item.quantity += anon_item.quantity
                        user_item.save()
                else:
                    user_item, created = CartItem.objects.get_or_create(
                        cart=user_cart,
                        product=anon_item.product,
                        variant=None,
                        defaults={'quantity': anon_item.quantity}
                    )
                    
                    if not created:
                        # Update quantity if item already exists
                        user_item.quantity += anon_item.quantity
                        user_item.save()
            
            # Delete the anonymous cart
            anonymous_cart.delete()
        
        serializer = CartSerializer(user_cart)
        response = Response(serializer.data)
        
        # Clear the session cookie
        response.delete_cookie('cart_session_id')
        
        return response
    
    except Exception as e:
        logger.error(f"Error merging carts: {str(e)}")
        return Response(
            {"error": "Failed to merge carts"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_cart(request):
    """
    Clear all items from the cart
    """
    try:
        # Get the cart
        result = get_or_create_cart(request)
        
        if isinstance(result, tuple):
            cart, session_id = result
        else:
            cart = result
            session_id = None
        
        # Delete all cart items
        cart.items.all().delete()
        
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        
        # Set session cookie if needed
        if session_id:
            response.set_cookie(
                'cart_session_id', 
                session_id, 
                max_age=60*60*24*30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return Response(
            {"error": "Failed to clear cart"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_cart(request):
    """
    Validate the cart items against current inventory
    """
    try:
        # Get the cart
        result = get_or_create_cart(request)
        
        if isinstance(result, tuple):
            cart, session_id = result
        else:
            cart = result
            session_id = None
        
        # Check each item with a variant
        invalid_items = []
        for item in cart.items.all():
            if item.variant:
                if item.variant.available_stock < item.quantity:
                    invalid_items.append({
                        'id': item.id,
                        'product_name': item.product.name,
                        'variant_id': item.variant.id,
                        'requested': item.quantity,
                        'available': item.variant.available_stock
                    })
        
        response_data = {
            'is_valid': len(invalid_items) == 0,
            'invalid_items': invalid_items
        }
        
        response = Response(response_data)
        
        # Set session cookie if needed
        if session_id:
            response.set_cookie(
                'cart_session_id', 
                session_id, 
                max_age=60*60*24*30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Error validating cart: {str(e)}")
        return Response(
            {"error": "Failed to validate cart"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
