from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from tenants.models import MainTenant, SubTenant, ResidentialHome


class Contract(models.Model):
    maintenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, verbose_name='Hauptmieter')
    subtenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, verbose_name='Untermieter')
    begin = models.DateField('Beginn des Untermietvertrages')
    end = models.DateField('Ende des Untermietvertrages')
    caution = models.FloatField('Höhe der Kaution in Euro')
    caution_comment = models.CharField('Anmerkungen zur Kaution', max_length=500, blank=True)
    is_identified = models.BooleanField('Lichtbildausweis kontrolliert?')
    is_matriculated = models.BooleanField('Immatrikulationsbescheinigung kontrolliert?')
    donation = models.FloatField('Freiwillige Spende in Euro', blank=True)
    is_active = models.BooleanField('Ist dieser Vertrag gültig?', default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_changed = models.BooleanField(default=True)

    version = models.IntegerField(default=0)

    # TODO: Zimmer Checkliste

    # TODO: implement comments

    def get_absolute_url(self):
        return reverse('contracts:ContractView', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('contracts:ContractUpdate', kwargs={'pk': self.pk})

    def is_latest(self):
        return not self.is_changed and self.updated_at >= self.maintenant.updated_at and self.updated_at >= self.subtenant.updated_at

    def __str__(self):
        return str(
            self.pk) + ': ' + self.maintenant.user.first_name + ' ' + self.maintenant.user.last_name + ' (' + str(
            self.maintenant.pk) + ')' + ' & ' + self.subtenant.user.first_name + ' ' + self.subtenant.user.last_name + ' (' + str(
            self.subtenant.pk) + ')'

    class Meta:
        verbose_name = 'Vertrag'
        verbose_name_plural = 'Vertäge'