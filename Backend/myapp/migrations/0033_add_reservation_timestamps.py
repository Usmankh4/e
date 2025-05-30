from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0032_productvariant_max_purchase_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryreservation',
            name='fulfilled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventoryreservation',
            name='canceled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
