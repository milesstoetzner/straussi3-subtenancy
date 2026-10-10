from django.db import migrations, models
from django.db.models import F


def confirm_existing_accounts(apps, schema_editor):
    """
    Accounts registered before e-mail confirmation existed count as confirmed; they have been reachable so far.
    """
    User = apps.get_model('tenants', 'User')
    User.objects.filter(email_confirmed_at__isnull=True).update(email_confirmed_at=F('created_at'))


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0066_subtenancyrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_confirmed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='E-Mail bestätigt am'),
        ),
        migrations.RunPython(confirm_existing_accounts, migrations.RunPython.noop),
    ]
