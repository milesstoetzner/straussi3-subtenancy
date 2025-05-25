from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0063_auto_20240714_0136'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Feedback',
        ),
    ]