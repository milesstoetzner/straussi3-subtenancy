from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from tenants.utils import COUNTRIES, TYPES


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
        return "/admin/tenants/user/" + str(self.pk)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, parent_link=True)
    tenant_id = models.PositiveIntegerField(_('Mieternummer'), unique=True)

    # Data processing
    accepted_data_processing = models.BooleanField(_('Ich stimme der Datenverarbeitung zu'), default=False)

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

    def get_absolute_url(self):
        return reverse('tenants:TenantView', kwargs={'pk': self.pk})

    def __str__(self):
        return '[' + str(self.pk) + '] ' + self.first_name + ' ' + self.last_name + ' (' + self.birthday.strftime(
            '%d.%m.%Y') + ')' + ' (' + str(self.tenant_id) + ')'

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, parent_link=True)

    # Information about sub tenant
    nationality = models.CharField(_('Nationalität'), choices=COUNTRIES, max_length=2)

    # Correspondence address
    name = models.CharField(_('Name'), max_length=250)
    street = models.CharField(_('Straße'), max_length=250)
    house_number = models.CharField(_('Hausnummer'), max_length=10)
    postcode = models.CharField(_('Postleitzahl'), max_length=50)
    city = models.CharField(_('Ort'), max_length=250)
    country = models.CharField(_('Land'), choices=COUNTRIES, max_length=2)

    # Data processing
    accepted_data_processing = models.BooleanField(_('Ich stimme der Datenverarbeitung zu'), default=False)

    def get_request(self):
        """
        Returns the subtenant's request or None if there is none.
        """
        return getattr(self, 'subtenancy_request', None)

    def is_searching(self):
        """
        A subtenant is searching for a room iff there is a request whose period has not ended yet.
        """
        subtenancy_request = self.get_request()
        return subtenancy_request is not None and subtenancy_request.is_active()

    def get_absolute_url(self):
        return reverse('tenants:TenantView', kwargs={'pk': self.pk})

    def __str__(self):
        return '[' + str(self.pk) + '] ' + self.first_name + ' ' + self.last_name + ' (' + self.birthday.strftime(
            '%d.%m.%Y') + ')'

    class Meta:
        verbose_name = _('Untermieter')
        verbose_name_plural = _('Untermieter')
        ordering = ['-user__id']


class SubtenancyRequestQuerySet(models.QuerySet):
    def active(self):
        """
        Requests whose period has not ended yet. Only these are listed publicly.
        """
        return self.filter(end__gte=timezone.localdate())


class SubtenancyRequest(models.Model):
    """
    A subtenant's request for a room, i.e. the requested period. A subtenant has at most one request.
    Its existence means the subtenant is searching: it is deleted when a contract is created or when the subtenant
    withdraws it, and it drops out of the public list once its period has ended.
    """

    subtenant = models.OneToOneField(SubTenant, on_delete=models.CASCADE, related_name='subtenancy_request',
                                     verbose_name=_('Untermieter'))
    begin = models.DateField(_('Beginn der angefragten Untermiete'))
    end = models.DateField(_('Ende der angefragten Untermiete'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SubtenancyRequestQuerySet.as_manager()

    def is_active(self):
        return self.end >= timezone.localdate()

    def __str__(self):
        return '[' + str(self.subtenant_id) + '] ' + self.begin.strftime('%d.%m.%Y') + ' - ' + self.end.strftime(
            '%d.%m.%Y')

    class Meta:
        verbose_name = _('Anfrage')
        verbose_name_plural = _('Anfragen')
        ordering = ['begin', 'end']


class Blacklist(models.Model):
    """
    Main/Subtenant with the listed name can not register.
    """

    name = models.CharField('Vollständiger Name', max_length=500, unique=True)
    reason = models.CharField('Beschreibung', max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('tenants:Blacklist')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Blockierter Mieter'
        verbose_name_plural = 'Blockierte Mieter'
