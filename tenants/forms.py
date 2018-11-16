from django.forms import ModelForm, TextInput, DateInput, EmailInput, Select, NumberInput, CheckboxInput, PasswordInput
from .models import User, MainTenant, SubTenant, ResidentialHome
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

BOOLEAN_CHOICES = ((False, 'Nein'), (True, 'Ja'))


class ResidentialHomeForm(ModelForm):
    class Meta:
        model = ResidentialHome
        fields = '__all__'
        help_texts = {
            'house_numbers': "Liste der Form: 'a', 'b', 'c'",
            'room_numbers': "Liste der Form:  1, 2, 3"
        }


class UserForm(UserCreationForm):

    class Meta:
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birthday', 'phone_number']
        model = User
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'password1': PasswordInput(attrs={'class': 'form-control'}),  # TODO: funktioniert nicht
            'password2': PasswordInput(attrs={'class': 'form-control'}),  # TODO: funktioniert nicht
            'birthday': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'phone_number': TextInput(attrs={'class': 'form-control'})
        }


class UserUpdateForm(ModelForm):

    class Meta(UserForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number']


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
        is_room_appropriate = cleaned_date.get('is_room_appropriate')

        # begin_rent_agreement < end_rent_agreement
        if begin_rent_agreement and end_rent_agreement:
            if begin_rent_agreement >= end_rent_agreement:
                self.add_error('end_rent_agreement', 'Das Ende des Mietvertrages muss nach dem Beginn sein!')

        # house_number of residential_home
        if residential_home and house_number:
            if house_number not in residential_home.get_house_numbers_as_list():
                self.add_error('house_number', 'Diese Hausnummer existiert nicht. Erlaubt sind: ' + residential_home.house_numbers)

        # room_number of residential_home
        if residential_home and room_number:
            if room_number not in residential_home.get_room_numbers_as_list():
                self.add_error('room_number', 'Diese Zimmernummer existiert nicht. Erlaubt sind: ' + residential_home.room_numbers)

        # begin_subtenancy < end_subtenancy
        if begin_subtenancy and end_subtenancy:
            if begin_subtenancy >= end_subtenancy:
                self.add_error('end_subtenancy', 'Das Ende des Untermietvertrages muss nach dem Beginn sein!')

        # positive rent
        if rent:
            if rent < 0:
                self.add_error('rent', 'Die Tagesmiete muss positiv sein!')

        # is_room_appropriate is false
        if not is_room_appropriate:
                self.add_error('is_room_appropriate', 'Dein Zimmer muss in einem ordnungsgemäßen Zustand sein!')

    class Meta:
        model = MainTenant
        exclude = ['user', 'is_searching']
        help_texts = {
            'is_returning': 'Sofern kein Wiedereinzug geplant ist und der Hauptmieter somit vollständig auszieht, wird die Kaution über den Hausmeister zurückerstattet.',
        }
        widgets = {
            'tenant_id': NumberInput(attrs={'class': 'form-control'}),
            'begin_rent_agreement': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end_rent_agreement': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'residential_home': Select(attrs={'class': 'form-control'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'room_number': NumberInput(attrs={'class': 'form-control'}),
            'begin_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'is_returning': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES),
            'rent': NumberInput(attrs={'class': 'form-control'}),
            'is_room_appropriate': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES),
            'is_searching': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES)
        }


class MainTenantUpdateForm(MainTenantForm):
    class Meta(MainTenantForm.Meta):
        exclude = ['user']


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
        exclude = ['user', 'is_searching']
        widgets = {
            'nationality': TextInput(attrs={'class': 'form-control'}),
            'is_eu': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES),
            'student_id': NumberInput(attrs={'class': 'form-control'}),
            'begin_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'end_subtenancy': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'name': TextInput(attrs={'class': 'form-control'}),
            'street': TextInput(attrs={'class': 'form-control'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'postcode': NumberInput(attrs={'class': 'form-control'}),
            'city': TextInput(attrs={'class': 'form-control'}),
            'country': TextInput(attrs={'class': 'form-control'}),
            'is_searching': Select(attrs={'class': 'form-control'}, choices=BOOLEAN_CHOICES)
        }


class SubTenantUpdateForm(SubTenantForm):
    class Meta(SubTenantForm.Meta):
        exclude = ['user']
