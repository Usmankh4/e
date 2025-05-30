import os
import django
import sys
from django.db import connection

# Set up Django environment
sys.path.append('/Users/usmankhan/stack/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def check_column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table}' AND column_name = '{column}'
    """)
    return bool(cursor.fetchone())

def add_missing_columns():
    """Add missing columns to the InventoryReservation table"""
    with connection.cursor() as cursor:
        # Check if fulfilled_at column exists
        if not check_column_exists(cursor, 'myapp_inventoryreservation', 'fulfilled_at'):
            print("Adding fulfilled_at column...")
            cursor.execute("""
                ALTER TABLE myapp_inventoryreservation 
                ADD COLUMN fulfilled_at timestamp with time zone NULL
            """)
            print("fulfilled_at column added successfully")
        else:
            print("fulfilled_at column already exists")
        
        # Check if canceled_at column exists
        if not check_column_exists(cursor, 'myapp_inventoryreservation', 'canceled_at'):
            print("Adding canceled_at column...")
            cursor.execute("""
                ALTER TABLE myapp_inventoryreservation 
                ADD COLUMN canceled_at timestamp with time zone NULL
            """)
            print("canceled_at column added successfully")
        else:
            print("canceled_at column already exists")

if __name__ == "__main__":
    print("Checking and adding missing columns to InventoryReservation table...")
    add_missing_columns()
    print("Database schema update complete")
