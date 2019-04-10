import os
import calendar
from datetime import datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from tenants.models import MainTenant, SubTenant, ResidentialHome
from .utils import html_to_pdf, save_html_as_pdf
from simple_history.models import HistoricalRecords
from django.db.transaction import atomic
from dateutil import relativedelta


class Contract(models.Model):
    """
    Model for a subtenancy contract between a maintenant and a subtenant. Every change to a record is logged.
    """

    maintenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, verbose_name='Hauptmieter')
    subtenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, verbose_name='Untermieter')
    begin = models.DateField('Beginn der Untermiete')
    end = models.DateField('Ende der Untermiete')
    rent = models.DecimalField('Monatsmiete in Euro', max_digits=5, decimal_places=2)
    condition = models.BooleanField('Ist das Zimmer und die Wohnung gereinigt und in einem ordnungsgemäßen Zustand?',
                                    default=False)
    condition_comment = models.CharField('Sonstige Anmerkungen zum Zimmer oder zur Wohnung', max_length=1000, blank=True)
    caution = models.DecimalField('Höhe der Kaution in Euro', max_digits=5, decimal_places=2, default=0)
    caution_comment = models.CharField('Anmerkungen zur Kaution', max_length=1000, blank=True)
    is_maintenant_returning = models.BooleanField('Plant der Hauptmieter ins Zimmer zurückzukehren?', default=True)
    is_maintenant_allowed = models.BooleanField('Liegt der Zeitraum der Untermiete innerhalb des Zeitraums des Hauptmietvertrages?', default=False)
    is_maintenant_identified = models.BooleanField('Wurde der Lichtbildausweis des Hauptmieters kontrolliert?',
                                                   default=False)
    is_subtenant_identified = models.BooleanField('Wurde der Lichtbildausweis des Untermieters kontrolliert?',
                                                  default=False)
    is_subtenant_matriculated = models.BooleanField(
        'Wurde die Immatrikulationsbescheinigung des Untermieters kontrolliert?', default=False)
    is_subtenant_allowed_in_DE = models.BooleanField(
        'Darf der Untermieter sich für den Zeitraum in Deutschland aufhalten?', default=False)
    donation = models.DecimalField('Freiwillige Spende in Euro', max_digits=5, decimal_places=2, default=0)
    has_special_permission = models.BooleanField(
        'Hat der Hauptmieter eine Sondergenehmigung, um den Zeitraum von 3 Monaten zu überschreiten?', default=False)
    is_active = models.BooleanField('Ist dieser Vertrag gültig?', default=True)

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
               and self.updated_at >= self.subtenant.updated_at

    def get_rents(self):
        """
        Returns one list containing the rents and one containing the corresponding months.
        Each list has the length of 6.
        """
        full_rent = self.rent
        daily_rent = round(full_rent / 30)

        start_date = self.begin
        end_date = self.end

        rents = []
        months = []

        should_continue = True
        current_date = start_date
        while should_continue:
            # default assume full month
            current_rent = full_rent

            # handle first month
            if current_date == start_date:
                last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                remaining_days = last_day - start_date.day + 1

                if not remaining_days == last_day:
                    # partial first month
                    current_rent = remaining_days * daily_rent

            # handle last month
            if current_date.month == end_date.month and current_date.year == end_date.year:
                last_day = calendar.monthrange(end_date.year, end_date.month)[1]

                if not end_date.day == last_day:
                    # partial last month
                    current_rent = end_date.day * daily_rent

                should_continue = False

            months.append(current_date)
            rents.append(current_rent)

            current_date += relativedelta.relativedelta(months=1)

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

        source = '/contracts/contract.tex'
        pdf = html_to_pdf(source, {'contract': self, 'today': datetime.now(), 'preview': True})
        return pdf

    @atomic
    def save_contract_pdf(self):
        """
        Renders the contract as a PDF file and saves the file to the storage.
        Each time a contract is saved as PDF the version attribute increments.
        This operation is atomic.
        """

        self.version += 1

        template_name = 'contracts/contract.tex'
        destination = os.path.join('contracts', 'contracts',
                                   'contract_' + str(self.pk) + '_version_' + str(self.version) + '.pdf')

        save_html_as_pdf(template_name, {'contract': self, 'today': datetime.now()}, destination)

        self.is_changed = False
        self.save()

    def __str__(self):
        return '[' + str(
            self.pk) + '] ' + self.maintenant.user.last_name + ' (' + str(
            self.maintenant.pk) + ')' + ' & ' + self.subtenant.user.last_name + ' (' + str(
            self.subtenant.pk) + ')'

    class Meta:
        verbose_name = 'Vertrag'
        verbose_name_plural = 'Verträge'
        permissions = (
            ("view_short_contract", "Can view short version of a contract"),
        )
