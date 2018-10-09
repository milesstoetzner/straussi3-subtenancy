from django.db import models
from public.models import MainTenant, SubTenant
from public.models import BOOLEAN_CHOICES


# TODO nullabel?!
class Contract(models.Model):
    main_tenant = models.ForeignKey(MainTenant, on_delete=models.CASCADE, null=True, verbose_name='Hauptmieter')  # TODO: on_delete!?
    sub_tenant = models.ForeignKey(SubTenant, on_delete=models.CASCADE, null=True, verbose_name='Untermieter')  # TODO: on_delete!?
    # TODO: zeitraum mit Miete jeweils
    caution = models.PositiveIntegerField('Höhe der Kaution in Euro', null=True)
    caution_comment = models.CharField('Anmerkung zur Kaution', max_length=500, null=True)
    photo_identification = models.CharField('Lichtbildausweis kontrolliert', max_length=10, choices=BOOLEAN_CHOICES)
    matriculation = models.CharField('Immatrikulationsbescheinigung kontrolliert', max_length=10, choices=BOOLEAN_CHOICES)
    donation = models.PositiveIntegerField('Freiwillige Spende in Euro', null=True)
    # TODO: Zimmer Checkliste

    def __str__(self):
        return self.pk