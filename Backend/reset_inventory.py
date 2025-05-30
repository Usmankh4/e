#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import ProductVariant, InventoryReservation
from django.utils import timezone
from django.db import transaction

def reset_variant_inventory(variant_id):
    """Reset the inventory for a specific variant"""
    try:
        with transaction.atomic():
            # Get the variant
            variant = ProductVariant.objects.get(id=variant_id)
            
            # Get all active reservations for this variant
            active_reservations = InventoryReservation.objects.filter(
                variant=variant,
                is_active=True
            )
            
            print(f"Found {active_reservations.count()} active reservations for variant {variant_id}")
            
            # Cancel all active reservations
            for reservation in active_reservations:
                print(f"Canceling reservation {reservation.id} for session {reservation.session_id}")
                reservation.is_active = False
                reservation.canceled_at = timezone.now()
                reservation.save()
            
            # Reset the reserved_stock to 0
            print(f"Resetting reserved_stock for variant {variant_id} from {variant.reserved_stock} to 0")
            variant.reserved_stock = 0
            variant.save()
            
            # Refresh from database
            variant.refresh_from_db()
            
            print(f"Inventory reset complete. Current state: count_in_stock={variant.count_in_stock}, "
                  f"reserved_stock={variant.reserved_stock}, available_stock={variant.available_stock}")
            
            return True
    except ProductVariant.DoesNotExist:
        print(f"Variant with ID {variant_id} not found")
        return False
    except Exception as e:
        print(f"Error resetting inventory: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python reset_inventory.py <variant_id>")
        sys.exit(1)
    
    variant_id = int(sys.argv[1])
    success = reset_variant_inventory(variant_id)
    
    if success:
        print(f"Successfully reset inventory for variant {variant_id}")
    else:
        print(f"Failed to reset inventory for variant {variant_id}")
        sys.exit(1)
