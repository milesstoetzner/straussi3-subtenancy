from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from tenants.models import MainTenant, SubTenant, ResidentialHome


class Contract(models.Model):
    main_tenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, verbose_name='Hauptmieter')
    sub_tenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, verbose_name='Untermieter')
    begin = models.DateField('Beginn des Untermietvertrages')
    end = models.DateField('Ende des Untermietvertrages')
    caution = models.FloatField('Höhe der Kaution in Euro')
    caution_comment = models.CharField('Anmerkungen zur Kaution', max_length=500, blank=True)
    is_identified = models.BooleanField('Lichtbildausweis kontrolliert?')
    is_matriculated = models.BooleanField('Immatrikulationsbescheinigung kontrolliert?')
    donation = models.FloatField('Freiwillige Spende in Euro', blank=True)
    is_active = models.BooleanField('Ist dieser Vertrag gültig?', default=True)

    # TODO: Zimmer Checkliste

    def get_absolute_url(self):
        return reverse('contracts:ContractView', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('contracts:ContractUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return str(
            self.pk) + ': ' + self.main_tenant.user.first_name + ' ' + self.main_tenant.user.last_name + ' (' + str(
            self.main_tenant.pk) + ')' + ' & ' + self.sub_tenant.user.first_name + ' ' + self.sub_tenant.user.last_name + ' (' + str(
            self.sub_tenant.pk) + ')'

    class Meta:
        verbose_name = 'Vertrag'
        verbose_name_plural = 'Vertäge'