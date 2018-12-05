from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords


class ResidentialHome(models.Model):
    """
    Model for a residential home. Every change to a record is logged.
    """

    name = models.CharField('Name', max_length=250)
    short = models.CharField('Abkürzung', max_length=4)
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


class BlockedTenantID(models.Model):
    """
    Model for a blocked tenant id. A maintenant with this id can not register an account.
    Every change to a record is logged.
    """

    id = models.PositiveIntegerField('Mieterummer', unique=True, primary_key=True)
    description = models.CharField('Beschreibung', max_length=500, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Blockierte Mieternummer'
        verbose_name_plural = 'Blockierte Mieternummern'


class BlockedStudentID(models.Model):
    """
    Model for a blocked student id. A subtenant with this id can not register an account.
    Every change to a record is logged.
    """

    id = models.PositiveIntegerField('Matrikelnummer', unique=True, primary_key=True)
    description = models.CharField('Beschreibung', max_length=500, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Blockierte Matrikelnummer'
        verbose_name_plural = 'Blockierte Matrikelnummern'


class User(AbstractUser):
    """
    Model for user. A user can be an assistant, maintenant, subtenant or external.
    Every change to a record is logged.
    """

    first_name = models.CharField('Vorname', max_length=150)
    last_name = models.CharField('Nachname', max_length=150)
    email = models.EmailField('Email Adresse', max_length=150)
    birthday = models.DateField('Geburtstag')
    phone_number = models.CharField('Telefonnummer', max_length=15)
    is_maintenant = models.BooleanField('Hauptmieter', default=False)
    is_subtenant = models.BooleanField('Untermieter', default=False)
    is_external = models.BooleanField('SWS oder Hausmeister', default=False)
    is_assistant = models.BooleanField('Sprechstunde', default=False)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('tenants:TenantView', kwargs={'pk': self.pk})

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + str(self.pk) + ')'

    class Meta:
        permissions = (
            ("change_own", "Can change his own user and corresponding maintenant/subtenant"),
            ("delete_own", "Can delete his own user and corresponding maintenant/subtenant")
        )


class MainTenant(models.Model):
    """
    Model for a maintenant. Each maintenant record belongs to a user.
    Every change to a record is logged.
    """

    # Information about main tenant
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tenant_id = models.PositiveIntegerField('Mieternummer', unique=True)
    begin_rent_agreement = models.DateField('Beginn des Mietvertrages')
    end_rent_agreement = models.DateField('Ende des Mietvertrages')

    # Information about subtenancy
    residential_home = models.ForeignKey(ResidentialHome, on_delete=models.PROTECT, verbose_name='Wohnheim')
    house_number = models.CharField('Hausnummer', max_length=10)
    room_number = models.CharField('Zimmernummer', max_length=10)
    rent = models.DecimalField('Monatsmiete in Euro', max_digits=5, decimal_places=2)
    is_returning = models.BooleanField('Ist ein Wiedereinzug ins Zimmer geplant?')

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_amount_of_days(self):
        """
        Returns the amount of days a maintenant has subleased his room.
        """

        amount = 0
        contracts = self.contract_set.filter(is_active=True)
        for contract in contracts:
            delta = contract.end - contract.begin
            amount += delta.days + 1
        return amount

    def __str__(self):
        return str(self.pk) + ': ' + self.user.first_name + ' ' + self.user.last_name + ' (' + str(self.user.birthday) + ')' + ' (' + str(self.tenant_id) + ')'

    class Meta:
        verbose_name = 'Hauptmieter'
        verbose_name_plural = 'Haupmieter'
        permissions = (
            ("contact_subtenant", "Can contact subtenant"),
        )


class SubTenant(models.Model):
    """
    Model for a subtenant. Each subtenant record belongs to a user.
    Every change to a record is logged.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Information about sub tenant
    nationality = models.CharField('Nationalität', max_length=100)
    is_eu = models.BooleanField('Ist dein Herkunftsland in der EU?')
    student_id = models.PositiveIntegerField('Matrikelnummer', unique=True)

    # Information about subtenancy
    begin_subtenancy = models.DateField('Beginn der Untermiete')
    end_subtenancy = models.DateField('Ende der Untermiete')
    is_searching = models.BooleanField('Ich suche für den oben genannten Zeitraum ein Zimmer', default=True)

    # Correspondence address
    name = models.CharField('Name', max_length=250)
    street = models.CharField('Straße', max_length=250)
    house_number = models.CharField('Hausnummer', max_length=10)
    postcode = models.PositiveIntegerField('Postleitzahl')
    city = models.CharField('Ort', max_length=250)
    country = models.CharField('Land', max_length=250)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk) + ': ' + self.user.first_name + ' ' + self.user.last_name + ' (' + str(self.user.birthday) + ')' + ' (' + str(self.student_id) + ')'

    class Meta:
        verbose_name = 'Untermieter'
        verbose_name_plural = 'Untermieter'