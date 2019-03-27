from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
from tenants.utils import COUNTRIES, TYPES


class ResidentialHome(models.Model):
    """
    Model for a residential home. Every change to a record is logged.
    """

    id = models.IntegerField(unique=True, primary_key=True)
    short = models.CharField('Abkürzung', max_length=4)
    name = models.CharField('Name', max_length=250)
    street = models.CharField('Straße', max_length=250)
    house_numbers = models.CharField('Hausnummern', max_length=1000)
    room_numbers = models.CharField('Zimmernummern', max_length=1000)
    postcode = models.CharField('Postleitzahl', max_length=25)
    city = models.CharField('Ort', max_length=250)
    country = models.CharField('Land', max_length=250)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_house_numbers_as_list(self):
        """
        Returns the house numbers as list. The house numbers are stored concatenated as string.
        """

        return self.house_numbers.replace(' ', '').split(",")

    def get_room_numbers_as_list(self):
        """
        Returns the room numbers as list. The room numbers are stored concatenated as string.
        """

        return self.room_numbers.replace(' ', '').split(",")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Wohnheim'
        verbose_name_plural = 'Wohnheime'


class Blacklist(models.Model):
    """
    Main/Subtenant with the listed name can not register.
    """

    name = models.CharField('Vollständiger Name', max_length=500, unique=True)
    reason = models.CharField('Beschreibung', max_length=500)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('tenants:Blacklist')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Blockierter Mieter'
        verbose_name_plural = 'Blockierte Mieter'


class User(AbstractUser):
    """
    Model for user. A user can be an assistant, maintenant, subtenant or external.
    Every change to a record is logged.
    """

    first_name = models.CharField(_('Vorname'), max_length=150)
    last_name = models.CharField(_('Nachname'), max_length=150)
    email = models.EmailField(_('Email Adresse'), max_length=150, unique=True)
    birthday = models.DateField(_('Geburtstag'))
    phone_number = models.CharField(_('Telefonnummer'), max_length=15)
    type = models.CharField(_('Typ'), max_length=3, choices=TYPES)

    history = HistoricalRecords(inherit=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_tenant(self):
        return self.type == 'HM' or self.type == 'UM'

    def is_maintenant(self):
        return self.type == 'HM'

    def is_subtenant(self):
        return self.type == 'UM'

    def is_sws(self):
        return self.type == 'SWS'

    def is_assistant(self):
        return self.type == 'SS'

    def get_absolute_url(self):
        return reverse('tenants:TenantView', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name) + ' (' + str(self.pk) + ')'

    class Meta:
        permissions = (
            ("change_own", "Can change his own user and corresponding maintenant/subtenant"),
            ("delete_own", "Can delete his own user and corresponding maintenant/subtenant")
        )


class MainTenant(User):
    """
    Model for a maintenant. Each maintenant record belongs to a user.
    Every change to a record is logged.
    """

    # Information about main tenant
    # NOTE: user still exists because of migrations problems while the change to multi table inherit from user
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tenant_id = models.PositiveIntegerField(_('Mieternummer'), unique=True)
    begin_rent_agreement = models.DateField(_('Beginn des Mietvertrages'))
    end_rent_agreement = models.DateField(_('Ende des Mietvertrages'))

    # Information about subtenancy
    residential_home = models.ForeignKey(ResidentialHome, on_delete=models.PROTECT, verbose_name=_('Wohnheim'), default=1)
    house_number = models.CharField(_('Hausnummer'), max_length=10)
    room_number = models.CharField(_('Zimmernummer'), max_length=10)

    def get_room(self):
        return str(self.house_number) + ' ' + str(self.room_number)

    def get_amount_of_days(self, exclude=None):
        """
        Returns the amount of days a maintenant has subleased his room.
        """

        amount = 0

        if exclude:
            contracts = self.contract_set.filter(is_active=True).exclude(id=exclude)
        else:
            contracts = self.contract_set.filter(is_active=True)

        for contract in contracts:
            delta = contract.end - contract.begin
            amount += delta.days + 1
        return amount

    def __str__(self):
        return '[' + str(self.pk) + '] ' + self.first_name + ' ' + self.last_name + ' (' + self.birthday.strftime('%d.%m.%Y') + ')' + ' (' + str(self.tenant_id) + ')'

    class Meta:
        verbose_name = _('Hauptmieter')
        verbose_name_plural = _('Hauptmieter')
        ordering = ['-user__id']
        permissions = (
            ("contact_subtenant", _("Can contact subtenant")),
        )


class SubTenant(User):
    """
    Model for a subtenant. Each subtenant record belongs to a user.
    Every change to a record is logged.
    """

    # NOTE: user still exists because of migrations problems while the change to multi table inherit from user
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Information about sub tenant
    nationality = models.CharField(_('Nationalität'), choices=COUNTRIES, max_length=2)
    student_id = models.PositiveIntegerField(_('Matrikelnummer'), unique=True)

    # Information about subtenancy
    begin_request = models.DateField(_('Beginn der angefragten Untermiete'))
    end_request = models.DateField(_('Ende der angefragten Untermiete'))
    is_searching = models.BooleanField(_('Ich suche für den oben genannten Zeitraum ein Zimmer'), default=True)

    # Correspondence address
    name = models.CharField(_('Name'), max_length=250)
    street = models.CharField(_('Straße'), max_length=250)
    house_number = models.CharField(_('Hausnummer'), max_length=10)
    postcode = models.CharField(_('Postleitzahl'), max_length=50)
    city = models.CharField(_('Ort'), max_length=250)
    country = models.CharField(_('Land'), choices=COUNTRIES, max_length=2)

    def __str__(self):
        return '[' + str(self.pk) + '] ' + self.first_name + ' ' + self.last_name + ' (' + self.birthday.strftime('%d.%m.%Y') + ')' + ' (' + str(self.student_id) + ')'

    class Meta:
        verbose_name = _('Untermieter')
        verbose_name_plural = _('Untermieter')
        ordering = ['-user__id']


class Feedback(models.Model):
    """
    User can send some feedback.
    """

    title = models.CharField('Titel', max_length=250)
    description = models.CharField('Beschreibung', max_length=1000)
    is_done = models.BooleanField('Bearbeitet?', default=False)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '[' + str(self.pk) + ']   ' + str(self.title)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'


class HallOfFame(models.Model):
    """
    Some legendary requests.
    """

    message = models.CharField('Nachricht', max_length=10000)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
