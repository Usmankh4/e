import os
import django
import sys
from datetime import timedelta

# Set up Django environment
sys.path.append('/Users/usmankhan/stack/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from myapp.models import InventoryReservation, ProductVariant
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def cleanup_expired_reservations():
    """Clean up expired reservations and verify inventory consistency"""
    now = timezone.now()
    
    # Find all expired but still active reservations
    expired_reservations = InventoryReservation.objects.filter(
        expires_at__lt=now,
        is_active=True
    )
    
    logger.info(f"Found {expired_reservations.count()} expired but still active reservations")
    
    # Process each expired reservation
    for reservation in expired_reservations:
        with transaction.atomic():
            try:
                variant = reservation.variant
                
                # Log before state
                logger.info(f"Before cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                           f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
                
                # Release the reserved stock
                variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
                variant.save()
                
                # Mark reservation as canceled
                reservation.is_active = False
                reservation.canceled_at = now
                reservation.save()
                
                # Refresh from database to ensure we have the latest values
                variant.refresh_from_db()
                
                # Log after state
                logger.info(f"After cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                           f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
                
                logger.info(f"Released {reservation.quantity} units of variant {variant.id} "
                           f"from reservation {reservation.id}. New reserved_stock: {variant.reserved_stock}")
            
            except Exception as e:
                logger.error(f"Error cleaning up reservation {reservation.id}: {str(e)}")

def verify_inventory_consistency():
    """Verify that reserved_stock matches the sum of active reservations"""
    variants = ProductVariant.objects.all()
    
    for variant in variants:
        # Calculate the sum of quantities in active reservations
        active_reservations_sum = InventoryReservation.objects.filter(
            variant=variant,
            is_active=True
        ).values_list('quantity', flat=True)
        
        actual_reserved = sum(active_reservations_sum)
        
        # Check if there's a discrepancy
        if variant.reserved_stock != actual_reserved:
            logger.info(f"Fixing discrepancy for variant {variant.id}: "
                       f"reserved_stock={variant.reserved_stock}, actual_reserved={actual_reserved}")
            
            # Update the reserved_stock to match the actual sum
            variant.reserved_stock = actual_reserved
            variant.save()
            
            logger.info(f"Fixed variant {variant.id}: new reserved_stock={variant.reserved_stock}")

def cleanup_stale_reservations():
    """Clean up reservations that are older than 24 hours"""
    one_day_ago = timezone.now() - timedelta(hours=24)
    
    # Find all active reservations older than 24 hours
    stale_reservations = InventoryReservation.objects.filter(
        created_at__lt=one_day_ago,
        is_active=True
    )
    
    logger.info(f"Found {stale_reservations.count()} stale reservations (older than 24 hours)")
    
    # Process each stale reservation
    for reservation in stale_reservations:
        with transaction.atomic():
            try:
                variant = reservation.variant
                
                # Log before state
                logger.info(f"Before stale cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                           f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
                
                # Release the reserved stock
                variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
                variant.save()
                
                # Mark reservation as canceled
                reservation.is_active = False
                reservation.canceled_at = timezone.now()
                reservation.save()
                
                # Refresh from database to ensure we have the latest values
                variant.refresh_from_db()
                
                # Log after state
                logger.info(f"After stale cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                           f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
                
                logger.info(f"Released {reservation.quantity} units of variant {variant.id} "
                           f"from stale reservation {reservation.id}. New reserved_stock: {variant.reserved_stock}")
            
            except Exception as e:
                logger.error(f"Error cleaning up stale reservation {reservation.id}: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting reservation cleanup process...")
    
    # Clean up expired reservations
    cleanup_expired_reservations()
    
    # Clean up stale reservations
    cleanup_stale_reservations()
    
    # Verify inventory consistency
    verify_inventory_consistency()
    
    logger.info("Reservation cleanup process completed")
