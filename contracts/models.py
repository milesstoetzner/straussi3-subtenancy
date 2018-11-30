from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from tenants.models import MainTenant, SubTenant, ResidentialHome
from .utils import add_one_month, is_end_of_month
from simple_history.models import HistoricalRecords


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

    has_special_permission = models.BooleanField('Hat der Hauptmieter eine Sondergenehmigung, um den Zeitraum von 3 Monaten zu überschreiten?', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_changed = models.BooleanField(default=True)

    version = models.IntegerField(default=0)

    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('contracts:ContractView', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('contracts:ContractUpdate', kwargs={'pk': self.pk})

    def is_latest(self):
        return not self.is_changed and self.updated_at >= self.maintenant.updated_at and self.updated_at >= self.subtenant.updated_at

    def get_rents(contract):
        months = []
        rents = []
        current = contract.begin.replace(day=1)
        end = contract.end.replace(day=1)
        daily_rent = contract.maintenant.rent / 30

        # first month
        months.append(current)
        current = add_one_month(current)

        # rent first month
        delta = current - contract.begin
        rents.append(round(delta.days * daily_rent, 2))

        while current < end:
            # add month between first and last month
            months.append(current)

            # add rents between first and last rent
            rents.append(contract.maintenant.rent)

            current = add_one_month(current)

        # add last month
        months.append(end)

        # add last rent
        if is_end_of_month(contract.end):
            rents.append(contract.maintenant.rent)
        else:
            rents.append(round(contract.end.day * daily_rent, 2))

        # fill array until 6 entries (for displaying contract details)
        while len(months) < 6:
            months.append("")

        # fill array until 6 entries (for displaying contract details)
        while len(rents) < 6:
            rents.append("")

        return {'months': months, 'rents': rents}

    def __str__(self):
        return str(
            self.pk) + ': ' + self.maintenant.user.first_name + ' ' + self.maintenant.user.last_name + ' (' + str(
            self.maintenant.pk) + ')' + ' & ' + self.subtenant.user.first_name + ' ' + self.subtenant.user.last_name + ' (' + str(
            self.subtenant.pk) + ')'

    class Meta:
        verbose_name = 'Vertrag'
        verbose_name_plural = 'Vertäge'
