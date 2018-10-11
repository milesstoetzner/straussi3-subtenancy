from django.db import models
from django.urls import reverse
from public.models import MainTenant, SubTenant
from public.models import BOOLEAN_CHOICES


# TODO: nullabel - why does this model need null=True while MainTenant does not?!
class Contract(models.Model):
    main_tenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, null=True, verbose_name='Hauptmieter', limit_choices_to={'active': 'Ja'})  # TODO: on_delete!?
    sub_tenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, null=True, verbose_name='Untermieter', limit_choices_to={'active': 'Ja'})  # TODO: on_delete!?
    begin = models.DateField('Beginn des Untermietvertrages', null=True)
    end = models.DateField('Ende des Untermietvertrages', null=True)
    caution = models.FloatField('Höhe der Kaution in Euro', null=True)
    caution_comment = models.CharField('Anmerkungen zur Kaution', max_length=500, blank=True, null=True)
    photo_identification = models.CharField('Lichtbildausweis kontrolliert?', max_length=10, choices=BOOLEAN_CHOICES, null=True)
    matriculation = models.CharField('Immatrikulationsbescheinigung kontrolliert?', max_length=10, choices=BOOLEAN_CHOICES, null=True)
    donation = models.FloatField('Freiwillige Spende in Euro', null=True)
    # TODO: Zimmer Checkliste

    active = models.CharField('Ist dieser Vertrag aktiv?', max_length=10, choices=BOOLEAN_CHOICES, default='Ja')

    def get_absolute_url(self):
        return reverse('private:ContractUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.pk) + ': ' + self.main_tenant.first_name + ' ' + self.main_tenant.last_name + ' (' + str(self.main_tenant.pk) + ')' + ' & ' + self.sub_tenant.first_name + ' ' + self.sub_tenant.last_name + ' (' + str(self.sub_tenant.pk) + ')'
