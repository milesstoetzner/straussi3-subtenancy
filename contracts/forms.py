from django.forms import ModelForm, TextInput, Textarea, DateInput, Select, NumberInput
from .models import Contract
from tenants.forms import BOOLEAN_CHOICES


class ContractForm(ModelForm):
    def clean(self):
        cleaned_date = super().clean()
        maintenant = cleaned_date.get('maintenant')
        subtenant = cleaned_date.get('subtenant')
        begin = cleaned_date.get('begin')
        end = cleaned_date.get('end')
        caution = cleaned_date.get('caution')
        is_identified = cleaned_date.get('is_identified')
        is_matriculated = cleaned_date.get('is_matriculated')
        donation = cleaned_date.get('donation')

        # begin < end
        if begin and end:
            if begin >= end:
                self.add_error('end', 'Das Ende des Untermietvertrages muss nach dem Beginn sein!')

        # maintenant.begin_rent_agreement <= begin
        if maintenant and begin:
            if maintenant.begin_rent_agreement:
                if maintenant.begin_rent_agreement > begin:
                    self.add_error('begin',
                                   'Der Begin des Untermietvertrages ist vor dem Beginn des Hauptmietvertrages!')

        # maintenant.end_rent_agreement >= end
        if maintenant and end:
            if maintenant.end_rent_agreement:
                if maintenant.end_rent_agreement < end:
                    self.add_error('end', 'Das Ende des Untermietvertrages ist nach dem Ende des Hauptmietvertrages!')

        # check for intersection with other contracts regarding maintenant
        if maintenant:
            contracts = Contract.objects.filter(maintenant=maintenant, is_active=True)
            for contract in contracts:
                if contract.id == self.instance.id:
                    continue
                if contract.begin <= begin <= contract.end:
                    self.add_error('begin', 'Der Begin des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Hauptmieter!')
                if contract.begin <= end <= contract.end:
                    self.add_error('end', 'Das Ende des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Hauptmieter!')
                if begin <= contract.begin <= end:
                    self.add_error('begin', 'Es existriert bereits ein Vertrag mit dem Hauptmieter innerhalb des angegebene Zeitraums!')

        # check for intersection with other contracts regarding subtenant
        if subtenant:
            contracts = Contract.objects.filter(subtenant=subtenant, is_active=True)
            for contract in contracts:
                if contract.id == self.instance.id:
                    continue
                if contract.begin <= begin <= contract.end:
                    self.add_error('begin', 'Der Begin des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Untermieter!')
                if contract.begin <= end <= contract.end:
                    self.add_error('end', 'Das Ende des Vertrages liegt innerhalb des Zeitraums eines bereits existierenden Vertrages mit dem Untermieter!')
                if begin <= contract.begin <= end:
                    self.add_error('begin', 'Es existriert bereits ein Vertrag mit dem Untermieter innerhalb des angegebene Zeitraums!')

        # positive caution
        if caution:
            if caution < 0:
                self.add_error('caution', 'Die Kaution muss positiv sein!')

        # is_identified
        if not is_identified:
                self.add_error('is_identified', 'Lichtbildausweis muss kontrolliert werden!')

        # is_matriculated
        if not is_matriculated:
                self.add_error('is_matriculated', 'Immatrikulationsbescheinigung muss kontrolliert werden!')

        # positive donation
        if donation:
            if donation < 0:
                self.add_error('donation', 'Die Spende darf nicht negativ sein!')

    class Meta:
        model = Contract
        exclude = ['is_active', 'version', 'is_changed']
        widgets = {
            'maintenant': Select(attrs={'class': 'form-control'}),
            'subtenant': Select(attrs={'class': 'form-control'}),
            'begin': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'caution': NumberInput(attrs={'class': 'form-control'}),
            'caution_comment': Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'is_identified': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES),
            'is_matriculated': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES),
            'donation': NumberInput(attrs={'class': 'form-control'}),
            'is_active': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES),
        }


class ContractUpdateForm(ContractForm):
    class Meta(ContractForm.Meta):
        exclude = ['version', 'is_changed']
