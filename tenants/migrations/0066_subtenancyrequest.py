import django.db.models.deletion
from django.db import migrations, models


def copy_requests_forward(apps, schema_editor):
    """
    Move the request of every searching subtenant into a SubtenancyRequest row.
    Subtenants that had switched their request off (is_searching=False) get no row: they were not searching.
    """
    SubTenant = apps.get_model('tenants', 'SubTenant')
    SubtenancyRequest = apps.get_model('tenants', 'SubtenancyRequest')
    for subtenant in SubTenant.objects.filter(is_searching=True).iterator():
        SubtenancyRequest.objects.create(
            subtenant=subtenant,
            begin=subtenant.begin_request,
            end=subtenant.end_request,
        )


def copy_requests_backward(apps, schema_editor):
    """
    Copy the requests back onto the subtenants.

    Runs while the re-added columns are still nullable. The reversed AlterField below then restores NOT NULL,
    which fails if any row is NULL, so subtenants without a request get is_searching=False and their registration
    date as period.
    """
    User = apps.get_model('tenants', 'User')
    SubTenant = apps.get_model('tenants', 'SubTenant')
    SubtenancyRequest = apps.get_model('tenants', 'SubtenancyRequest')
    requests = {r.subtenant_id: r for r in SubtenancyRequest.objects.all()}
    for subtenant in SubTenant.objects.all().iterator():
        subtenancy_request = requests.get(subtenant.pk)
        if subtenancy_request is not None:
            subtenant.begin_request = subtenancy_request.begin
            subtenant.end_request = subtenancy_request.end
            subtenant.is_searching = True
        else:
            # the subtenant's pk is the user's pk (multi-table inheritance)
            registered = User.objects.get(pk=subtenant.pk).created_at.date()
            subtenant.begin_request = registered
            subtenant.end_request = registered
            subtenant.is_searching = False
        subtenant.save(update_fields=['begin_request', 'end_request', 'is_searching'])


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0065_remove_historicalfeedback_history_user_and_more'),
    ]

    operations = [
        # make the old columns nullable first, so that reversing (re-adding them) works with existing rows
        migrations.AlterField(
            model_name='subtenant',
            name='begin_request',
            field=models.DateField(null=True, verbose_name='Beginn der angefragten Untermiete'),
        ),
        migrations.AlterField(
            model_name='subtenant',
            name='end_request',
            field=models.DateField(null=True, verbose_name='Ende der angefragten Untermiete'),
        ),
        migrations.CreateModel(
            name='SubtenancyRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.DateField(verbose_name='Beginn der angefragten Untermiete')),
                ('end', models.DateField(verbose_name='Ende der angefragten Untermiete')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subtenant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subtenancy_request', to='tenants.subtenant', verbose_name='Untermieter')),
            ],
            options={
                'verbose_name': 'Anfrage',
                'verbose_name_plural': 'Anfragen',
                'ordering': ['begin', 'end'],
            },
        ),
        migrations.RunPython(copy_requests_forward, copy_requests_backward),
        migrations.RemoveField(
            model_name='subtenant',
            name='begin_request',
        ),
        migrations.RemoveField(
            model_name='subtenant',
            name='end_request',
        ),
        migrations.RemoveField(
            model_name='subtenant',
            name='is_searching',
        ),
    ]
