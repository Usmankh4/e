#!/usr/bin/env python
import os
import django
import logging
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from myapp.models import InventoryReservation, ProductVariant

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('cleanup_script')

def cleanup_expired_reservations():
    """Clean up expired inventory reservations and release reserved stock"""
    logger.info("Starting cleanup of expired reservations...")
    
    # Get current time
    now = timezone.now()
    
    # Get all active reservations that have expired
    expired_reservations = InventoryReservation.objects.filter(
        is_active=True,
        expires_at__lte=now
    ).select_related('variant')
    
    if not expired_reservations.exists():
        logger.info('No expired reservations found.')
        return
    
    logger.info(f"Found {expired_reservations.count()} expired reservations to clean up...")
    
    # Process each expired reservation
    with transaction.atomic():
        for reservation in expired_reservations:
            variant = reservation.variant
            
            # Log before state
            logger.info(f"Before cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                        f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
            
            # Release the reserved stock
            old_reserved_stock = variant.reserved_stock
            variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
            variant.save()
            
            # Mark reservation as expired
            reservation.is_active = False
            reservation.canceled_at = now
            reservation.save()
            
            # Refresh from database
            variant.refresh_from_db()
            
            # Log after state
            logger.info(f"After cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                        f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
            
            logger.info(
                f"Released {reservation.quantity} units of variant {variant.id} "
                f"from expired reservation {reservation.id}. "
                f"Reserved stock changed from {old_reserved_stock} to {variant.reserved_stock}"
            )
    
    logger.info('Successfully cleaned up expired reservations.')

def cleanup_stale_reservations():
    """Clean up stale reservations that are older than 24 hours"""
    logger.info("Starting cleanup of stale reservations...")
    
    # Get current time minus 24 hours
    cutoff_time = timezone.now() - timedelta(hours=24)
    
    # Get all reservations (active or not) that are older than the cutoff time
    stale_reservations = InventoryReservation.objects.filter(
        created_at__lte=cutoff_time
    ).select_related('variant')
    
    if not stale_reservations.exists():
        logger.info('No stale reservations found.')
        return
    
    logger.info(f"Found {stale_reservations.count()} stale reservations to clean up...")
    
    # Process each stale reservation
    with transaction.atomic():
        for reservation in stale_reservations:
            variant = reservation.variant
            
            # Only update if the reservation is still active
            if reservation.is_active:
                # Log before state
                logger.info(f"Before stale cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                            f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
                
                # Release the reserved stock
                old_reserved_stock = variant.reserved_stock
                variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
                variant.save()
                
                # Mark reservation as expired
                reservation.is_active = False
                reservation.canceled_at = timezone.now()
                reservation.save()
                
                # Refresh from database
                variant.refresh_from_db()
                
                # Log after state
                logger.info(f"After stale cleanup - Variant {variant.id}: count_in_stock={variant.count_in_stock}, "
                            f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
                
                logger.info(
                    f"Released {reservation.quantity} units of variant {variant.id} "
                    f"from stale reservation {reservation.id}. "
                    f"Reserved stock changed from {old_reserved_stock} to {variant.reserved_stock}"
                )
            else:
                # Just delete the reservation if it's already inactive
                logger.info(f"Deleting inactive stale reservation {reservation.id}")
                reservation.delete()
    
    logger.info('Successfully cleaned up stale reservations.')

def verify_inventory_consistency():
    """Verify that all variants have consistent inventory counts"""
    logger.info("Verifying inventory consistency...")
    
    # Get all variants
    variants = ProductVariant.objects.all()
    
    for variant in variants:
        # Calculate the total quantity in active reservations
        active_reservations = InventoryReservation.objects.filter(
            variant=variant,
            is_active=True
        )
        
        total_reserved = sum(res.quantity for res in active_reservations)
        
        # Check if the reserved_stock matches the sum of active reservations
        if variant.reserved_stock != total_reserved:
            logger.warning(
                f"Inconsistency found for variant {variant.id}: "
                f"reserved_stock={variant.reserved_stock}, "
                f"sum of active reservations={total_reserved}"
            )
            
            # Fix the inconsistency
            old_reserved_stock = variant.reserved_stock
            variant.reserved_stock = total_reserved
            variant.save()
            
            logger.info(
                f"Fixed inconsistency for variant {variant.id}: "
                f"reserved_stock changed from {old_reserved_stock} to {total_reserved}"
            )
    
    logger.info('Inventory consistency verification complete.')

if __name__ == "__main__":
    # Run all cleanup functions
    cleanup_expired_reservations()
    cleanup_stale_reservations()
    verify_inventory_consistency()
    
    logger.info("All cleanup tasks completed successfully.")
