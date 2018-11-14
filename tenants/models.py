from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class ResidentialHome(models.Model):
    name = models.CharField('Name', max_length=250)
    short = models.CharField('Abkürzung', max_length=4)
    street = models.CharField('Straße', max_length=250)
    house_numbers = models.CharField('Hausnummern', max_length=1000)
    room_numbers = models.CharField('Zimmernummern', max_length=1000)
    postcode = models.CharField('Postleitzahl', max_length=25)
    city = models.CharField('Ort', max_length=250)
    country = models.CharField('Land', max_length=250)

    def get_house_numbers_as_list(self):
        return self.house_numbers.replace(' ', '').split(",")

    def get_room_numbers_as_list(self):
        return self.room_numbers.replace(' ', '').split(",")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Wohnheim'
        verbose_name_plural = 'Wohnheime'


class User(AbstractUser):
    birthday = models.DateField('Geburtstag', default='1111-11-11')
    phone_number = models.CharField('Telefonnummer', max_length=15, default='')
    residential_home = models.ForeignKey(ResidentialHome, on_delete=models.PROTECT, verbose_name='Wohnheim', null=True, blank=True)
    is_maintenant = models.BooleanField('Hauptmieter', default=False)
    is_subtenant = models.BooleanField('Untermieter', default=False)
    # TODO: exclusive is_maintenant, is_subtenant, is_staff, is_superuser


class MainTenant(models.Model):
    # Information about main tenant
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tenant_id = models.PositiveIntegerField('Mieternummer', unique=True)
    begin_rent_agreement = models.DateField('Beginn des Mietvertrages')
    end_rent_agreement = models.DateField('Ende des Mietvertrages')

    # Information about subtenancy
    house_number = models.CharField('Hausnummer', max_length=10)
    room_number = models.CharField('Zimmernummer', max_length=10)
    begin_subtenancy = models.DateField('Beginn der Untermiete')
    end_subtenancy = models.DateField('Ende der Untermiete')
    rent = models.PositiveIntegerField('Monatsmiete in Euro')
    is_returning = models.BooleanField('Ist ein Wiedereinzug ins Zimmer geplant?')
    is_room_appropriate = models.BooleanField('Ist das Zimmer in einem ordnungsgemäßen Zustand?')

    # TODO: add created, last_updated fields?!

    def get_absolute_url(self):
        return reverse('contracts:MainTenantView', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('contracts:MainTenantUpdate', kwargs={'pk': self.pk})

    def get_all_contracts(self):
        return self.contract_set.all()

    # TODO: implement comments
    def get_all_comments(self):
        return []

    def __str__(self):
        return str(self.pk) + ': ' + self.user.first_name + ' ' + self.user.last_name + ' (' + str(self.user.birthday) + ')' + ' (' + str(self.tenant_id) + ')'

    class Meta:
        verbose_name = 'Hauptmieter'
        verbose_name_plural = 'Haupmieter'


class SubTenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Information about sub tenant
    nationality = models.CharField('Nationalität', max_length=100)
    is_eu = models.BooleanField('Ist dein Herkunftsland in der EU?')
    student_id = models.PositiveIntegerField('Matrikelnummer', unique=True)

    # Information about subtenancy
    begin_subtenancy = models.DateField('Beginn der Untermiete')
    end_subtenancy = models.DateField('Ende der Untermiete')

    # Correspondence address
    name = models.CharField('Name', max_length=250)
    street = models.CharField('Straße', max_length=250)
    house_number = models.CharField('Hausnummer', max_length=10)
    postcode = models.PositiveIntegerField('Postleitzahl')
    city = models.CharField('Ort', max_length=250)
    country = models.CharField('Land', max_length=250)

    # TODO: add created, last_updated fields?!

    def get_absolute_url(self):
        return reverse('contracts:SubTenantView', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('contracts:SubTenantUpdate', kwargs={'pk': self.pk})

    def get_all_contracts(self):
        return self.contract_set.all()

    # TODO: implement comments
    def get_all_comments(self):
        return []

    def __str__(self):
        return str(self.pk) + ': ' + self.user.first_name + ' ' + self.user.last_name + ' (' + str(self.user.birthday) + ')' + ' (' + str(self.student_id) + ')'

    class Meta:
        verbose_name = 'Untermieter'
        verbose_name_plural = 'Untermieter'