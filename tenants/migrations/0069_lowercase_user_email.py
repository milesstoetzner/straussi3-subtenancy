from django.db import migrations
from django.db.models import F
from django.db.models.functions import Lower


def lowercase_emails(apps, schema_editor):
    """
    Stores every e-mail address in lowercase, as User.save() does from now on. Then the unique index on the address
    also holds for different spellings, and an address is found by comparing it with the lowercased input.

    If two accounts have the same address in different spellings, the unique index rejects the update and the
    migration fails without changing anything. One of the two has to get another address first.
    """

    User = apps.get_model('tenants', 'User')
    User.objects.update(email=Lower(F('email')))


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0068_alter_user_phone_number'),
    ]

    operations = [
        migrations.RunPython(lowercase_emails, migrations.RunPython.noop),
    ]
