from django.db import migrations
from django.utils import timezone

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0033_add_reservation_timestamps'),
    ]

    operations = [
        # This is an empty migration that doesn't try to add the created_at field again
        # since it already exists in the database
    ]
