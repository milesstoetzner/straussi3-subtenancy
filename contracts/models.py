import os
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from tenants.models import MainTenant, SubTenant, ResidentialHome
from .utils import add_one_month, is_end_of_month, html_to_pdf, save_html_as_pdf
from simple_history.models import HistoricalRecords
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _


class Contract(models.Model):
    """
    Model for a subtenancy contract between a maintenant and a subtenant. Every change to a record is logged.
    """

    maintenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, verbose_name=_('Hauptmieter'))
    subtenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, verbose_name=_('Untermieter'))
    begin = models.DateField(_('Beginn der Untermiete'))
    end = models.DateField(_('Ende der Untermiete'))
    condition = models.BooleanField(_('Ist das Zimmer und die Wohnung gereinigt und in einem ordnungsgemäßen Zustand?'), default=False)
    condition_comment = models.CharField(_('Sonstige Anmerkungen zum Zimmer oder zur Wohnung'), max_length=75, blank=True)
    caution = models.DecimalField(_('Höhe der Kaution in Euro'), max_digits=5, decimal_places=2, default=0)
    caution_comment = models.CharField(_('Anmerkungen zur Kaution'), max_length=150, blank=True)
    is_maintenant_identified = models.BooleanField(_('Wurde der Lichtbildausweis des Hauptmieters kontrolliert?'), default=False)
    is_subtenant_identified = models.BooleanField(_('Wurde der Lichtbildausweis des Untermieters kontrolliert?'), default=False)
    is_subtenant_matriculated = models.BooleanField(_('Wurde die Immatrikulationsbescheinigung des Untermieters kontrolliert?'), default=False)
    is_subtenant_allowed_in_DE = models.BooleanField(_('Darf der Untermieter sich für den Zeitraum in Deutschland aufhalten?'), default=False)
    donation = models.DecimalField(_('Freiwillige Spende in Euro'), max_digits=5, decimal_places=2, default=0)
    has_special_permission = models.BooleanField(_('Hat der Hauptmieter eine Sondergenehmigung, um den Zeitraum von 3 Monaten zu überschreiten?'), default=False)
    is_active = models.BooleanField(_('Ist dieser Vertrag gültig?'), default=True)

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

        months = []
        rents = []
        current = self.begin.replace(day=1)
        end = self.end.replace(day=1)
        daily_rent = self.maintenant.rent / 30

        # first month
        months.append(current)
        current = add_one_month(current)

        # rent first month
        delta = current - self.begin
        rents.append(round(delta.days * daily_rent, 2))

        while current < end:
            # add month between first and last month
            months.append(current)

            # add rents between first and last rent
            rents.append(self.maintenant.rent)

            current = add_one_month(current)

        # add last month
        months.append(end)

        # add last rent
        if is_end_of_month(self.end):
            rents.append(self.maintenant.rent)
        else:
            rents.append(round(self.end.day * daily_rent, 2))

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

        source = os.path.join('contracts', 'contracts', 'str3.html')
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

        source = os.path.join('contracts', 'contracts', 'str3.html')
        destination = os.path.join('contracts', 'contracts',
                                   'contract_' + str(self.pk) + '_version_' + str(self.version) + '.pdf')

        save_html_as_pdf(source, {'contract': self}, destination)

        self.is_changed = False
        self.save()

    def __str__(self):
        return '[' + str(
            self.pk) + '] ' + self.maintenant.user.last_name + ' (' + str(
            self.maintenant.pk) + ')' + ' & ' + self.subtenant.user.last_name + ' (' + str(
            self.subtenant.pk) + ')'

    class Meta:
        verbose_name = _('Vertrag')
        verbose_name_plural = _('Verträge')
        permissions = (
            ("view_short_contract", _("Can view short version of a contract")),
        )
