from django.forms import ModelForm, TextInput, Textarea, DateInput, Select, NumberInput
from .models import Contract


class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'main_tenant': Select(attrs={'class': 'form-control'}),
            'sub_tenant': Select(attrs={'class': 'form-control'}),
            'caution': NumberInput(attrs={'class': 'form-control'}),
            'caution_comment': Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'photo_identification': Select(attrs={'class': 'form-control'}),
            'matriculation': Select(attrs={'class': 'form-control'}),
            'donation': NumberInput(attrs={'class': 'form-control'})
        }
