import os
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from tenants.models import MainTenant, SubTenant, ResidentialHome
from .utils import add_one_month, is_end_of_month, html_to_pdf, save_html_as_pdf
from simple_history.models import HistoricalRecords
from django.db.transaction import atomic


class Contract(models.Model):
    """
    Model for a subtenancy contract between a maintenant and a subtenant. Every change to a record is logged.
    """

    maintenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, verbose_name='Hauptmieter')
    subtenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, verbose_name='Untermieter')
    begin = models.DateField('Beginn des Untermietvertrages')
    end = models.DateField('Ende des Untermietvertrages')
    condition_room = models.BooleanField('Ist das Zimmer gereinigt und in einem ordnungsgemäßen Zustand?',
                                         default=False)
    condition_flat = models.BooleanField(
        'Sind die Gemeinschaftsräume gereinigt und steht ein Staurum in Küche/Kühleschrank bereit?', default=False)
    condition_comment = models.CharField('Sonstige Anmerkungen zum Zimmer oder zur Wohnung', max_length=75, blank=True)
    caution = models.FloatField('Höhe der Kaution in Euro')
    caution_comment = models.CharField('Anmerkungen zur Kaution', max_length=150, blank=True)
    is_identified = models.BooleanField('Lichtbildausweis kontrolliert?')
    is_matriculated = models.BooleanField('Immatrikulationsbescheinigung kontrolliert?')
    donation = models.FloatField('Freiwillige Spende in Euro', blank=True)
    is_active = models.BooleanField('Ist dieser Vertrag gültig?', default=True)

    has_special_permission = models.BooleanField(
        'Hat der Hauptmieter eine Sondergenehmigung, um den Zeitraum von 3 Monaten zu überschreiten?', default=False)

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
        """
        Checks if there had been some update to the maintenant, subtenant or the contract itself.
        """

        return not self.is_changed \
               and self.updated_at >= self.maintenant.updated_at \
               and self.updated_at >= self.maintenant.user.updated_at \
               and self.updated_at >= self.subtenant.updated_at \
               and self.updated_at >= self.subtenant.user.updated_at

    def get_rents(contract):
        """
        Returns one list containing the rents and one containing the corresponding months.
        Each list has the length of 6.
        """

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

    def preview_contract_pdf(self):
        """
        Renders the contract as a PDF file and returns the PDF without saving.
        """

        source = os.path.join('contracts', 'contracts', str(self.maintenant.residential_home.short) + '.html')
        pdf = html_to_pdf(source, {'contract': self})
        return pdf

    @atomic
    def save_contract_pdf(self):
        """
        Renders the contract as a PDF file and saves the file to the storage.
        Each time a contract is saved as PDF the version attribute increments.
        This operation is atomic.
        """

        self.version += 1

        source = os.path.join('contracts', 'contracts', str(self.maintenant.residential_home.short) + '.html')
        destination = os.path.join('contracts', 'contracts',
                                   'contract_' + str(self.pk) + '_version_' + str(self.version) + '.pdf')

        status = save_html_as_pdf(source, {'contract': self}, destination)

        if status:
            self.is_changed = False
            self.save()

        return status

    def __str__(self):
        return str(
            self.pk) + ': ' + self.maintenant.user.first_name + ' ' + self.maintenant.user.last_name + ' (' + str(
            self.maintenant.pk) + ')' + ' & ' + self.subtenant.user.first_name + ' ' + self.subtenant.user.last_name + ' (' + str(
            self.subtenant.pk) + ')'

    class Meta:
        verbose_name = 'Vertrag'
        verbose_name_plural = 'Vertäge'
        permissions = (
            ("view_short_contract", "Can view short version of a contract"),
        )
