from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0035_fix_nullable_fields_final'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryreservation',
            name='fulfilled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
