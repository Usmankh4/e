from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0036_add_fulfilled_at_to_inventoryreservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryreservation',
            name='canceled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
