from django.forms import ModelForm, TextInput, Textarea, DateInput, Select, NumberInput
from django.db import models
from .models import Contract
from public.models import MainTenant, SubTenant


class ContractForm(ModelForm):
    def clean(self):
        cleaned_date = super().clean()
        main_tenant = cleaned_date.get('main_tenant')
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

        # main_tenant.begin_rent_agreement <= begin
        if main_tenant and begin:
            if main_tenant.begin_rent_agreement:
                if main_tenant.begin_rent_agreement > begin:
                    self.add_error('begin',
                                   'Der Begin des Untermietvertrages ist vor dem Beginn des Hauptmietvertrages!')

        # main_tenant.end_rent_agreement >= end
        if main_tenant and end:
            if main_tenant.end_rent_agreement:
                if main_tenant.end_rent_agreement < end:
                    self.add_error('end', 'Das Ende des Untermietvertrages ist nach dem Ende des Hauptmietvertrages!')

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
        exclude = ['active']
        widgets = {
            'main_tenant': Select(attrs={'class': 'form-control'}),
            'sub_tenant': Select(attrs={'class': 'form-control'}),
            'begin': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'caution': NumberInput(attrs={'class': 'form-control'}),
            'caution_comment': Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'is_identified': Select(attrs={'class': 'form-control'}),
            'is_matriculated': Select(attrs={'class': 'form-control'}),
            'donation': NumberInput(attrs={'class': 'form-control'}),
            'is_active': Select(attrs={'class': 'form-control'}),
        }


class ContractUpdateForm(ContractForm):
    class Meta(ContractForm.Meta):
        exclude = []
