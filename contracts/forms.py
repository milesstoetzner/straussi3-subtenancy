from django.forms import ModelForm, TextInput, Textarea, DateInput, Select, NumberInput
from .models import Contract
from tenants.forms import BOOLEAN_CHOICES


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
        rent = cleaned_data.get('rent')
        condition = cleaned_data.get('condition')
        caution = cleaned_data.get('caution')
        is_maintenant_identified = cleaned_data.get('is_maintenant_identified')
        is_subtenant_identified = cleaned_data.get('is_subtenant_identified')
        is_subtenant_matriculated = cleaned_data.get('is_subtenant_matriculated')
        is_subtenant_allowed_in_DE = cleaned_data.get('is_subtenant_allowed_in_DE')
        donation = cleaned_data.get('donation')
        has_special_permission = cleaned_data.get('has_special_permission')

        # begin < end
        if begin and end:
            if begin >= end:
                self.add_error('end', 'Das Ende der Untermiete muss nach dem Beginn sein!')

        # positive rent
        if rent:
            if rent < 0:
                self.add_error('rent', 'Die Monatsmiete muss positiv sein!')

        # maintenant account is not blocked
        if maintenant:
            if not maintenant.user.is_active:
                self.add_error('maintenant', 'Der Account des Hauptmieters ist gesperrt!')

        # subtenant account is not blocked
        if subtenant:
            if not subtenant.user.is_active:
                self.add_error('subtenant', 'Der Account des Untermieters ist gesperrt!')

        # maintenant.begin_rent_agreement <= begin
        if maintenant and begin:
            if maintenant.begin_rent_agreement:
                if maintenant.begin_rent_agreement > begin:
                    self.add_error('begin', 'Der Begin der Untermiete ist vor dem Beginn des Hauptmietvertrages!')

        # maintenant.end_rent_agreement >= end
        if maintenant and end:
            if maintenant.end_rent_agreement:
                if maintenant.end_rent_agreement < end:
                    self.add_error('end', 'Das Ende der Untermiete ist nach dem Ende des Hauptmietvertrages!')

        # check for intersection with other contracts regarding maintenant
        if maintenant and begin and end:
            contracts = maintenant.contract_set.filter(is_active=True)
            for contract in contracts:
                if contract.id == self.instance.id:
                    continue
                if contract.begin <= begin <= contract.end:
                    self.add_error('begin',
                                   'Der Begin des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Hauptmieter!')
                if contract.begin <= end <= contract.end:
                    self.add_error('end',
                                   'Das Ende des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Hauptmieter!')
                if begin <= contract.begin <= end:
                    self.add_error('begin',
                                   'Es existriert bereits ein Vertrag mit dem Hauptmieter innerhalb des angegebene Zeitraums!')

        # check for intersection with other contracts regarding subtenant
        if subtenant and begin and end:
            contracts = subtenant.contract_set.filter(is_active=True)
            for contract in contracts:
                if contract.id == self.instance.id:
                    continue
                if contract.begin <= begin <= contract.end:
                    self.add_error('begin',
                                   'Der Begin des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Untermieter!')
                if contract.begin <= end <= contract.end:
                    self.add_error('end',
                                   'Das Ende des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Untermieter!')
                if begin <= contract.begin <= end:
                    self.add_error('begin',
                                   'Es existriert bereits ein Vertrag mit dem Untermieter innerhalb des angegebene Zeitraums!')

        # check maintenant amount day
        if maintenant and begin and end:
            if not has_special_permission:
                d = end - begin
                if maintenant.get_amount_of_days(self.instance.id) + d.days + 1 > 93:
                    self.add_error('end',
                                   'Der Hauptmieter überschreitet die 3 Monate Grenze! Falls er eine Sondergenehmigung besitzt, kann dies unten angegeben werden.')

        # condition is false
        if not condition:
            self.add_error('condition', 'Deine Wohnung muss in einem ordnungsgemäßen Zustand sein!')

        # positive caution
        if caution:
            if caution < 0:
                self.add_error('caution', 'Die Kaution muss positiv sein!')

        # is_maintenant_identified
        if not is_maintenant_identified:
            self.add_error('is_maintenant_identified', 'Lichtbildausweis des Hauptmieters muss kontrolliert werden!')

        # is_subtenant_identified
        if not is_subtenant_identified:
            self.add_error('is_subtenant_identified',
                           'Lichtbildausweis des Untermieters muss kontrolliert werden!')

        # is_subtenant_matriculated
        if not is_subtenant_matriculated:
            self.add_error('is_subtenant_matriculated', 'Immatrikulationsbescheinigung des Untermieters muss kontrolliert werden!')

        # is_subtenant_allowed_in_DE
        if not is_subtenant_allowed_in_DE:
            self.add_error('is_subtenant_allowed_in_DE', 'Der Untermieter muss berechtigt sein, sich in Deutschland aufzuhalten!')

        # positive donation
        if donation:
            if donation < 0:
                self.add_error('donation', 'Die Spende darf nicht negativ sein!')

    class Meta:
        model = Contract
        exclude = ['version', 'is_changed']
        help_texts = {
            'condition': 'Ein ordnungsgemäßer Zustand schließt die Vollständigkeit des Inventars entsprechend des Hauptmietvertrages ein.',
            'donation': 'Eine freiwillige Spende in Höhe von 2.50€ pro Woche ist angemessen.',
            'is_active': 'Wenn der Vertrag nicht gültig ist, dann wird er nicht in der Liste für das SWS augeführt. Ein Vertrag ist beispielsweise nicht gültig, wenn noch nicht alle Parteien unterschrieben haben.'
        }
        widgets = {
            'begin': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'condition': Select(choices=BOOLEAN_CHOICES),
            'condition_comment': Textarea(attrs={'rows': 1}),
            'caution_comment': Textarea(attrs={'rows': 1}),
            'is_maintenant_identified': Select(choices=BOOLEAN_CHOICES),
            'is_subtenant_identified': Select(choices=BOOLEAN_CHOICES),
            'is_subtenant_matriculated': Select(choices=BOOLEAN_CHOICES),
            'is_subtenant_allowed_in_DE': Select(choices=BOOLEAN_CHOICES),
            'is_active': Select(choices=BOOLEAN_CHOICES),
            'has_special_permission': Select(choices=BOOLEAN_CHOICES)
        }
