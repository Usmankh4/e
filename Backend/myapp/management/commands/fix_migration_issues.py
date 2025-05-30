from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes migration issues by directly modifying the database schema'

    def handle(self, *args, **options):
        # Check if created_at column exists in inventorychange table
        with connection.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='myapp_inventorychange' AND column_name='created_at'")
            column_exists = cursor.fetchone() is not None
            
            if column_exists:
                self.stdout.write(self.style.SUCCESS('created_at column already exists in inventorychange table'))
            else:
                # Add created_at column if it doesn't exist
                cursor.execute("ALTER TABLE myapp_inventorychange ADD COLUMN created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP")
                self.stdout.write(self.style.SUCCESS('Successfully added created_at column to inventorychange table'))
            
            # Fix the migration record in django_migrations
            cursor.execute("SELECT id FROM django_migrations WHERE app='myapp' AND name='0033_add_reservation_timestamps'")
            migration_exists = cursor.fetchone() is not None
            
            if migration_exists:
                self.stdout.write(self.style.SUCCESS('Migration 0033_add_reservation_timestamps already exists'))
            else:
                # Find the latest applied migration
                cursor.execute("SELECT id, app, name FROM django_migrations WHERE app='myapp' ORDER BY id DESC LIMIT 1")
                last_migration = cursor.fetchone()
                
                if last_migration:
                    self.stdout.write(self.style.SUCCESS(f'Last applied migration: {last_migration[2]}'))
                    
                    # Insert the 0033_add_reservation_timestamps migration record
                    cursor.execute(
                        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, CURRENT_TIMESTAMP)",
                        ['myapp', '0033_add_reservation_timestamps']
                    )
                    self.stdout.write(self.style.SUCCESS('Successfully added migration record for 0033_add_reservation_timestamps'))
                else:
                    self.stdout.write(self.style.ERROR('No previous migrations found'))
            
            # Also add the 0034_fix_created_at migration record
            cursor.execute("SELECT id FROM django_migrations WHERE app='myapp' AND name='0034_fix_created_at'")
            fix_migration_exists = cursor.fetchone() is not None
            
            if fix_migration_exists:
                self.stdout.write(self.style.SUCCESS('Migration 0034_fix_created_at already exists'))
            else:
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, CURRENT_TIMESTAMP)",
                    ['myapp', '0034_fix_created_at']
                )
                self.stdout.write(self.style.SUCCESS('Successfully added migration record for 0034_fix_created_at'))
