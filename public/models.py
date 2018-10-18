from django.db import models
from django.urls import reverse

BOOLEAN_CHOICES = (('Nein', 'Nein'), ('Ja', 'Ja')) #TODO: bad practice?!
# TODO: rename 'active' to 'is_active' in MainTenant, SubTenant and Contract


class ResidentialHome(models.Model):
    name = models.CharField('Name', max_length=250)
    short = models.CharField('Abkürzung', max_length=4)
    street = models.CharField('Straße', max_length=250)
    house_numbers = models.CharField('Hausnummern', max_length=1000)
    room_numbers = models.CharField('Zimmernummern', max_length=1000)
    postcode = models.CharField('Postleitzahl', max_length=25)
    city = models.CharField('Ort', max_length=250)
    country = models.CharField('Land', max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Wohnheim'
        verbose_name_plural = 'Wohnheime'


class MainTenant(models.Model):
    # Information about main tenant
    first_name = models.CharField('Vorname', max_length=250)
    last_name = models.CharField('Nachname', max_length=250)
    tenant_id = models.PositiveIntegerField('Mieternummer')
    begin_rent_agreement = models.DateField('Beginn des Mietvertrages')
    end_rent_agreement = models.DateField('Ende des Mietvertrages')
    email = models.EmailField('Email')
    phone_number = models.CharField('Telefonnummer', max_length=15)

    # Information about subtenancy
    residential_home = models.ForeignKey(ResidentialHome, on_delete=models.PROTECT, verbose_name='Wohnheim')
    house_number = models.CharField('Hausnummer', max_length=10)
    room_number = models.CharField('Zimmernummer', max_length=10)
    begin_subtenancy = models.DateField('Beginn der Untermiete')
    end_subtenancy = models.DateField('Ende der Untermiete')
    comeback = models.CharField('Ist ein Wiedereinzug ins Zimmer geplant?', max_length=10, choices=BOOLEAN_CHOICES)
    rent = models.FloatField('Monatsmiete in Euro')
    room_condition = models.CharField('Ist das Zimmer in einem ordnungsgemäßen Zustand?', max_length=10, choices=BOOLEAN_CHOICES)

    active = models.CharField('Ist dieser Account aktiv?', max_length=10, choices=BOOLEAN_CHOICES, default='Ja')

    # TODO: add created, last_updated fields?!

    def get_absolute_url(self):
        return reverse('private:MainTenantUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.pk) + ': '+ self.first_name + ' ' + self.last_name + ' (' + str(self.tenant_id) + ')'

    class Meta:
        verbose_name = 'Hauptmieter'
        verbose_name_plural = 'Haupmieter'


class SubTenant(models.Model):
    # Information about sub tenant
    first_name = models.CharField('Vorname', max_length=250)
    last_name = models.CharField('Nachname', max_length=250)
    birthday = models.DateField('Geburtstag')
    nationality = models.CharField('Nationalität', max_length=100)
    eu = models.CharField('Ist dein Herkunftsland in der EU?', max_length=10, choices=BOOLEAN_CHOICES)
    student_id = models.PositiveIntegerField('Matrikelnummer')
    email = models.EmailField('Email')
    phone_number = models.CharField('Telefonnummer', max_length=15)

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

    active = models.CharField('Ist dieser Account aktiv?', max_length=10, choices=BOOLEAN_CHOICES, default='Ja')
    residential_home = models.ForeignKey(ResidentialHome, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Wohnheim')

    # TODO: add created, last_updated fields?!

    def get_absolute_url(self):
        return reverse('private:SubTenantUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.pk) + ': ' + self.first_name + ' ' + self.last_name + ' (' + str(self.birthday) + ')'

    class Meta:
        verbose_name = 'Untermieter'
        verbose_name_plural = 'Untermieter'