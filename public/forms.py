from django.forms import ModelForm, TextInput, DateInput, EmailInput, Select, NumberInput, CheckboxInput
from .models import MainTenant, SubTenant


class MainTenantForm(ModelForm):
    class Meta:
        model = MainTenant
        exclude = ['active']
        help_texts = {
            'comeback': 'Sofern kein Wiedereinzug geplant ist und der Hauptmieter somit vollständig auszieht, wird die Kaution über den Hausmeister zurückerstattet.'
        }
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'tenant_id': NumberInput(attrs={'class': 'form-control'}),
            'begin_rent_agreement':  DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_rent_agreement': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'phone_number': TextInput(attrs={'class': 'form-control'}),
            'residential_home': Select(attrs={'class': 'custom-select'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'room_number': NumberInput(attrs={'class': 'form-control'}),
            'begin_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comeback': Select(attrs={'class': 'form-control'}),
            'rent': NumberInput(attrs={'class': 'form-control'}),
            'room_condition': Select(attrs={'class': 'form-control'})
        }


class SubTenantForm(ModelForm):
    class Meta:
        model = SubTenant
        exclude = ['active']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'birthday': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': TextInput(attrs={'class': 'form-control'}),
            'eu': Select(attrs={'class': 'form-control'}),
            'student_id': NumberInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'phone_number': TextInput(attrs={'class': 'form-control'}),
            'begin_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'name': TextInput(attrs={'class': 'form-control'}),
            'street': TextInput(attrs={'class': 'form-control'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'postcode': NumberInput(attrs={'class': 'form-control'}),
            'city': TextInput(attrs={'class': 'form-control'}),
            'country': TextInput(attrs={'class': 'form-control'})
        }