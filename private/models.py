from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from public.models import MainTenant, SubTenant, ResidentialHome
from public.models import BOOLEAN_CHOICES


class Contract(models.Model):
    main_tenant = models.ForeignKey(MainTenant, on_delete=models.PROTECT, verbose_name='Hauptmieter')  # TODO: on_delete!?  # TODO: OneToOne?! # TODO: limit to: residential_home, active
    sub_tenant = models.ForeignKey(SubTenant, on_delete=models.PROTECT, verbose_name='Untermieter')  # TODO: on_delete!?  # TODO: OneToOne?! # TODO: limit to: residential_home='', residential_home, active
    begin = models.DateField('Beginn des Untermietvertrages')
    end = models.DateField('Ende des Untermietvertrages')
    caution = models.FloatField('Höhe der Kaution in Euro')
    caution_comment = models.CharField('Anmerkungen zur Kaution', max_length=500, blank=True, null=True)
    photo_identification = models.CharField('Lichtbildausweis kontrolliert?', max_length=10, choices=BOOLEAN_CHOICES)
    matriculation = models.CharField('Immatrikulationsbescheinigung kontrolliert?', max_length=10, choices=BOOLEAN_CHOICES)
    donation = models.FloatField('Freiwillige Spende in Euro')
    # TODO: Zimmer Checkliste

    active = models.CharField('Ist dieser Vertrag aktiv?', max_length=10, choices=BOOLEAN_CHOICES, default='Ja')

    def get_absolute_url(self):
        return reverse('private:ContractUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.pk) + ': ' + self.main_tenant.first_name + ' ' + self.main_tenant.last_name + ' (' + str(self.main_tenant.pk) + ')' + ' & ' + self.sub_tenant.first_name + ' ' + self.sub_tenant.last_name + ' (' + str(self.sub_tenant.pk) + ')'

    class Meta:
        verbose_name = 'Vertrag'
        verbose_name_plural = 'Vertäge'


# TODO: bad practice?!
class Administrative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    residential_home = models.ForeignKey(ResidentialHome, on_delete=models.PROTECT, verbose_name='Wohnheim')

    def __str__(self):
        return str(self.residential_home)
