from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import ProductVariant, InventoryReservation
import logging

logger = logging.getLogger('myapp')

@api_view(['GET'])
@permission_classes([AllowAny])
def get_variant_stock(request, variant_id=None):
    """
    Get stock information for a specific variant or filtered variants
    """
    try:
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
            return Response({
                'id': variant.id,
                'stock': variant.stock,
                'reserved': variant.reserved,
                'available': variant.available_stock
            })
        else:
            # Handle filtering by query params
            variant_ids = request.query_params.get('ids')
            if variant_ids:
                ids = [int(id) for id in variant_ids.split(',')]
                variants = ProductVariant.objects.filter(id__in=ids)
                result = {}
                for variant in variants:
                    result[variant.id] = {
                        'stock': variant.stock,
                        'reserved': variant.reserved,
                        'available': variant.available_stock
                    }
                return Response(result)
            return Response({"error": "No variant ID provided"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error getting variant stock: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_variant_stock(request):
    """
    Update stock for a variant
    """
    try:
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity')
        
        if not variant_id or quantity is None:
            return Response({"error": "variant_id and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        variant = get_object_or_404(ProductVariant, id=variant_id)
        variant.stock = quantity
        variant.save()
        
        return Response({
            'id': variant.id,
            'stock': variant.stock,
            'reserved': variant.reserved,
            'available': variant.available_stock
        })
    except Exception as e:
        logger.error(f"Error updating variant stock: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reserve_inventory(request):
    """
    Reserve inventory for a checkout session
    """
    try:
        session_id = request.data.get('session_id')
        items = request.data.get('items', [])
        
        if not session_id or not items:
            return Response({"error": "session_id and items are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete any existing reservations for this session
        InventoryReservation.objects.filter(session_id=session_id).delete()
        
        results = []
        for item in items:
            variant_id = item.get('variant_id')
            quantity = item.get('quantity', 1)
            
            variant = get_object_or_404(ProductVariant, id=variant_id)
            
            # Check if enough stock is available
            if variant.available_stock < quantity:
                # Rollback any reservations made so far
                InventoryReservation.objects.filter(session_id=session_id).delete()
                return Response({
                    "error": f"Not enough stock for variant {variant_id}",
                    "available": variant.available_stock,
                    "requested": quantity
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create reservation
            reservation = InventoryReservation.objects.create(
                variant=variant,
                session_id=session_id,
                quantity=quantity
            )
            
            # Update variant reserved count
            variant.reserved += quantity
            variant.save()
            
            results.append({
                'variant_id': variant_id,
                'quantity': quantity,
                'reservation_id': reservation.id
            })
        
        return Response({
            'session_id': session_id,
            'reservations': results
        })
    except Exception as e:
        logger.error(f"Error reserving inventory: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def release_reservation(request):
    """
    Release a reservation (e.g., when checkout is abandoned)
    """
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all reservations for this session
        reservations = InventoryReservation.objects.filter(session_id=session_id)
        
        if not reservations.exists():
            return Response({"message": "No reservations found for this session"})
        
        # Release each reservation
        for reservation in reservations:
            variant = reservation.variant
            variant.reserved_stock -= reservation.quantity
            variant.save()
        
        # Delete the reservations
        count = reservations.count()
        reservations.delete()
        
        return Response({
            "message": f"Released {count} reservations for session {session_id}"
        })
    except Exception as e:
        logger.error(f"Error releasing reservation: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def commit_reservation(request):
    """
    Commit a reservation (convert reserved to sold)
    """
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all reservations for this session
        reservations = InventoryReservation.objects.filter(session_id=session_id)
        
        if not reservations.exists():
            return Response({"message": "No reservations found for this session"})
        
        # Commit each reservation
        for reservation in reservations:
            variant = reservation.variant
            variant.stock -= reservation.quantity
            variant.reserved -= reservation.quantity
            variant.save()
        
        # Delete the reservations
        count = reservations.count()
        reservations.delete()
        
        return Response({
            "message": f"Committed {count} reservations for session {session_id}"
        })
    except Exception as e:
        logger.error(f"Error committing reservation: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_inventory(request):
    """
    Validate that requested inventory is available
    """
    try:
        items = request.data.get('items', [])
        
        if not items:
            return Response({"error": "items are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        all_available = True
        
        for item in items:
            variant_id = item.get('variant_id')
            quantity = item.get('quantity', 1)
            
            variant = get_object_or_404(ProductVariant, id=variant_id)
            
            available = variant.available_stock >= quantity
            if not available:
                all_available = False
            
            results.append({
                'variant_id': variant_id,
                'requested': quantity,
                'available': variant.available_stock,
                'is_available': available
            })
        
        return Response({
            'all_available': all_available,
            'items': results
        })
    except Exception as e:
        logger.error(f"Error validating inventory: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
