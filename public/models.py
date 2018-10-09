from django.db import models
from django.urls import reverse

RESIDENTIAL_HOME_TYPE_CHOICES = (('str1', 'Straußäcker 1'), ('str2', 'Straußäcker 2'), ('str3', 'Straußäcker 3'),)
BOOLEAN_CHOICES = (('Nein', 'Nein'), ('Ja', 'Ja')) #TODO: bad practice?!


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
    residential_home = models.CharField('Wohnheim', max_length=10, choices=RESIDENTIAL_HOME_TYPE_CHOICES)
    house_number = models.CharField('Hausnummer', max_length=2)
    room_number = models.CharField('Zimmernummer', max_length=3)
    begin_subtenancy = models.DateField('Beginn der Untermiete')
    end_subtenancy = models.DateField('Ende der Untermiete')
    comeback = models.CharField('Ist ein Wiedereinzug ins Zimmer geplant?', max_length=10, choices=BOOLEAN_CHOICES)
    rent = models.PositiveIntegerField('Monatliche Miete in Euro')
    room_condition = models.CharField('Ist das Zimmer in einem ordnungsgemäßen Zustand?', max_length=10, choices=BOOLEAN_CHOICES)

    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('MainTenant', kwargs={'pk': self.pk})  # TODO: remove this

    # TODO: Main Tenant Validation

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + str(self.tenant_id) + ')'


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

    active = models.BooleanField(default=True) # TODO: exclude from Form

    # TODO: Sub Tenant Validation

    def __str__(self):
        return self.first_name + ' ' + self.last_name + '(' + str(self.birthday) + ')'