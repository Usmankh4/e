from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import logging
from ...models import InventoryReservation, ProductVariant

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired inventory reservations and release reserved stock'

    def handle(self, *args, **options):
        # Get all active reservations that have expired
        expired_reservations = InventoryReservation.objects.filter(
            is_active=True,
            expires_at__lte=timezone.now()
        ).select_related('variant')
        
        if not expired_reservations.exists():
            self.stdout.write(self.style.SUCCESS('No expired reservations found.'))
            return
        
        self.stdout.write(f"Found {expired_reservations.count()} expired reservations to clean up...")
        
        # Process each expired reservation
        with transaction.atomic():
            for reservation in expired_reservations:
                variant = reservation.variant
                
                # Mark reservation as expired
                reservation.is_active = False
                reservation.canceled_at = timezone.now()
                reservation.save()
                
                # Update variant's reserved stock
                variant.reserved_stock = max(0, variant.reserved_stock - reservation.quantity)
                variant.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Released {reservation.quantity} units of variant {variant.id} "
                        f"from expired reservation {reservation.id}"
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up expired reservations.'))
