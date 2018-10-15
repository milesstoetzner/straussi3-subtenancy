from django.forms import ModelForm, TextInput, DateInput, EmailInput, Select, NumberInput
from .models import MainTenant, SubTenant
from .residential_homes import RESIDENTIAL_HOMES


class MainTenantForm(ModelForm):

    def clean(self):
        cleaned_date = super().clean()
        begin_rent_agreement = cleaned_date.get('begin_rent_agreement')
        end_rent_agreement = cleaned_date.get('end_rent_agreement')
        residential_home = cleaned_date.get('residential_home')
        house_number = cleaned_date.get('house_number')
        room_number = cleaned_date.get('room_number')
        begin_subtenancy = cleaned_date.get('begin_subtenancy')
        end_subtenancy = cleaned_date.get('end_subtenancy')
        rent = cleaned_date.get('rent')
        room_condition = cleaned_date.get('room_condition')

        # begin_rent_agreement < end_rent_agreement
        if begin_rent_agreement and end_rent_agreement:
            if begin_rent_agreement >= end_rent_agreement:
                self.add_error('end_rent_agreement', 'Das Ende des Mietvertrages muss nach dem Beginn sein!')

        # TODO: validate phone_number

        # house_number of residential_home
        if residential_home and house_number:
            if house_number not in RESIDENTIAL_HOMES[residential_home].get('house_numbers'):
                self.add_error('house_number', 'Diese Hausnummer existiert nicht. Erlaubt sind: ' + str(
                    RESIDENTIAL_HOMES[residential_home].get('house_numbers')))

        # room_number of residential_home
        if residential_home and room_number:
            if int(room_number) not in RESIDENTIAL_HOMES[residential_home].get('room_numbers'):
                self.add_error('room_number', 'Diese Zimmernummer existiert nicht. Erlaubt sind: ' + str(
                    RESIDENTIAL_HOMES[residential_home].get('room_numbers')))

        # begin_subtenancy < end_subtenancy
        if begin_subtenancy and end_subtenancy:
            if begin_subtenancy >= end_subtenancy:
                self.add_error('end_subtenancy', 'Das Ende des Untermietvertrages muss nach dem Beginn sein!')

        # positive rent
        if rent:
            if rent < 0:
                self.add_error('rent', 'Die Tagesmiete muss positiv sein!')

        # room_condition is true
        if room_condition:
            if room_condition != 'Ja':
                self.add_error('room_condition', 'Dein Zimmer muss in einem ordnungsgemäßen Zustand sein!')

    class Meta:
        model = MainTenant
        exclude = ['active']
        labels = {
            'test': 'ich bin ein label'
        }
        help_texts = {
            'comeback': 'Sofern kein Wiedereinzug geplant ist und der Hauptmieter somit vollständig auszieht, wird die Kaution über den Hausmeister zurückerstattet.',
            'rent': 'Die Tagesmiete entspricht der Monatsmiete geteilt durch 30. Beispiel: Die Monatsmiete beträgt 300€, daher beträgt die Tagesmiete 300€/30 = 10€'
        }
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'tenant_id': NumberInput(attrs={'class': 'form-control'}),
            'begin_rent_agreement': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end_rent_agreement': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'phone_number': TextInput(attrs={'class': 'form-control'}),
            'residential_home': Select(attrs={'class': 'custom-select'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'room_number': NumberInput(attrs={'class': 'form-control'}),
            'begin_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'comeback': Select(attrs={'class': 'form-control'}),
            'rent': NumberInput(attrs={'class': 'form-control'}),
            'room_condition': Select(attrs={'class': 'form-control'}),
            'active': Select(attrs={'class': 'form-control'}),
        }


class MainTenantUpdateForm(MainTenantForm):
    class Meta(MainTenantForm.Meta):
        exclude = []


class SubTenantForm(ModelForm):

    def clean(self):
        cleaned_date = super().clean()
        begin_subtenancy = cleaned_date.get('begin_subtenancy')
        end_subtenancy = cleaned_date.get('end_subtenancy')

        # begin_subtenancy < end_subtenancy
        if begin_subtenancy and end_subtenancy:
            if begin_subtenancy >= end_subtenancy:
                self.add_error('end_subtenancy', 'Das Ende des Untermietvertrages muss nach dem Beginn sein!')

    class Meta:
        model = SubTenant
        exclude = ['active', 'residential_home']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'birthday': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'nationality': TextInput(attrs={'class': 'form-control'}),
            'eu': Select(attrs={'class': 'form-control'}),
            'student_id': NumberInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'phone_number': TextInput(attrs={'class': 'form-control'}),
            'begin_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'name': TextInput(attrs={'class': 'form-control'}),
            'street': TextInput(attrs={'class': 'form-control'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'postcode': NumberInput(attrs={'class': 'form-control'}),
            'city': TextInput(attrs={'class': 'form-control'}),
            'country': TextInput(attrs={'class': 'form-control'}),
            'active': Select(attrs={'class': 'form-control'}),
            'residential_home': Select(attrs={'class': 'form-control'}),
        }


class SubTenantUpdateForm(SubTenantForm):
    class Meta(SubTenantForm.Meta):
        exclude = []