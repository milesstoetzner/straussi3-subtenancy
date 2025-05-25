from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0031_auto_20190412_1405'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Roster',
        ),
    ]