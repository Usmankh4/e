import os
import django
import sys

# Set up Django environment
sys.path.append('/Users/usmankhan/stack/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.management import call_command

def apply_migrations():
    print("Applying pending migrations...")
    call_command('migrate')
    print("Migrations applied successfully!")

if __name__ == "__main__":
    apply_migrations()
