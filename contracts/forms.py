from django.forms import ModelForm, TextInput, Textarea, DateInput, Select, NumberInput
from .models import Contract
from tenants.forms import BOOLEAN_CHOICES
from django.utils.translation import gettext_lazy as _


class ContractForm(ModelForm):
    """
    Creates a new contract. Before creation there are a few validations - e.g. the begin and end is validated against
    already existing contracts with the maintenant resp. subtenant
    """

    def clean(self):
        cleaned_data = super().clean()
        maintenant = cleaned_data.get('maintenant')
        subtenant = cleaned_data.get('subtenant')
        begin = cleaned_data.get('begin')
        end = cleaned_data.get('end')
        condition_room = cleaned_data.get('condition_room')
        condition_flat = cleaned_data.get('condition_flat')
        caution = cleaned_data.get('caution')
        is_identified = cleaned_data.get('is_identified')
        is_matriculated = cleaned_data.get('is_matriculated')
        donation = cleaned_data.get('donation')
        has_special_permission = cleaned_data.get('has_special_permission')

        # begin < end
        if begin and end:
            if begin >= end:
                self.add_error('end', _('Das Ende des Untermietvertrages muss nach dem Beginn sein!'))

        # maintenant account is not blocked
        if maintenant:
            if not maintenant.user.is_active:
                self.add_error('maintenant', _('Der Account des Hauptmieters ist gesperrt!'))

        # subtenant account is not blocked
        if subtenant:
            if not subtenant.user.is_active:
                self.add_error('subtenant', _('Der Account des Untermieters ist gesperrt!'))

        # maintenant.begin_rent_agreement <= begin
        if maintenant and begin:
            if maintenant.begin_rent_agreement:
                if maintenant.begin_rent_agreement > begin:
                    self.add_error('begin',
                                   _('Der Begin des Untermietvertrages ist vor dem Beginn des Hauptmietvertrages!'))

        # maintenant.end_rent_agreement >= end
        if maintenant and end:
            if maintenant.end_rent_agreement:
                if maintenant.end_rent_agreement < end:
                    self.add_error('end', _('Das Ende des Untermietvertrages ist nach dem Ende des Hauptmietvertrages!'))

        # check for intersection with other contracts regarding maintenant
        if maintenant and begin and end:
            contracts = maintenant.contract_set.filter(is_active=True)
            for contract in contracts:
                if contract.id == self.instance.id:
                    continue
                if contract.begin <= begin <= contract.end:
                    self.add_error('begin',
                                   _('Der Begin des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Hauptmieter!'))
                if contract.begin <= end <= contract.end:
                    self.add_error('end',
                                   _('Das Ende des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Hauptmieter!'))
                if begin <= contract.begin <= end:
                    self.add_error('begin',
                                   _('Es existriert bereits ein Vertrag mit dem Hauptmieter innerhalb des angegebene Zeitraums!'))

        # check for intersection with other contracts regarding subtenant
        if subtenant and begin and end:
            contracts = subtenant.contract_set.filter(is_active=True)
            for contract in contracts:
                if contract.id == self.instance.id:
                    continue
                if contract.begin <= begin <= contract.end:
                    self.add_error('begin',
                                   _('Der Begin des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Untermieter!'))
                if contract.begin <= end <= contract.end:
                    self.add_error('end',
                                   _('Das Ende des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Untermieter!'))
                if begin <= contract.begin <= end:
                    self.add_error('begin',
                                   _('Es existriert bereits ein Vertrag mit dem Untermieter innerhalb des angegebene Zeitraums!'))

        # check maintenant amount day
        if maintenant and begin and end:
            if not has_special_permission:
                d = end - begin
                if maintenant.get_amount_of_days(self.instance.id) + d.days + 1 > 93:
                    self.add_error('end',
                                   _('Der Hauptmieter überschreitet die 3 Monate Grenze! Falls er eine Sondergenehmigung besitzt, kann dies unten angegeben werden.'))

        # condition_room is false
        if not condition_room:
            self.add_error('condition_room', _('Dein Zimmer muss in einem ordnungsgemäßen Zustand sein!'))

        # flat_condition is false
        if not condition_flat:
            self.add_error('condition_flat', _('Deine Wohnung muss in einem ordnungsgemäßen Zustand sein!'))

        # positive caution
        if caution:
            if caution < 0:
                self.add_error('caution', _('Die Kaution muss positiv sein!'))

        # is_identified
        if not is_identified:
            self.add_error('is_identified', _('Lichtbildausweis muss kontrolliert werden!'))

        # is_matriculated
        if not is_matriculated:
            self.add_error('is_matriculated', _('Immatrikulationsbescheinigung muss kontrolliert werden!'))

        # positive donation
        if donation:
            if donation < 0:
                self.add_error('donation', _('Die Spende darf nicht negativ sein!'))

    class Meta:
        model = Contract
        exclude = ['is_active', 'version', 'is_changed']
        help_texts = {
            'condition_room': _('Ein ordnungsgemäßer Zustand schließt die Vollständigkeit des Inventars entsprechend des Hauptmietvertrages ein.')
        }
        widgets = {
            'begin': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'condition_room': Select(choices=BOOLEAN_CHOICES),
            'condition_flat': Select(choices=BOOLEAN_CHOICES),
            'condition_comment': Textarea(attrs={'rows': 1}),
            'caution_comment': Textarea(attrs={'rows': 1}),
            'is_identified': Select(choices=BOOLEAN_CHOICES),
            'is_matriculated': Select(choices=BOOLEAN_CHOICES),
            'is_active': Select(choices=BOOLEAN_CHOICES),
            'has_special_permission': Select(choices=BOOLEAN_CHOICES)
        }


class ContractUpdateForm(ContractForm):
    """
    Updates an existing contract. The only difference to the creation is that the field 'is_active' is available.
    """

    class Meta(ContractForm.Meta):
        exclude = ['version', 'is_changed']
