from django.forms import ModelForm, DateInput, Select, Textarea
from .models import User, MainTenant, SubTenant, ResidentialHome, BlockedTenantID, BlockedStudentID
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

BOOLEAN_CHOICES = ((False, 'Nein'), (True, 'Ja'))


class ResidentialHomeForm(ModelForm):
    """
    Creates or updates a residential home.
    """

    class Meta:
        model = ResidentialHome
        fields = '__all__'
        help_texts = {
            'house_numbers': "Liste der Form: 'a', 'b', 'c'",
            'room_numbers': "Liste der Form:  1, 2, 3"
        }


class UserForm(UserCreationForm):
    """
    Creates a user extended by birthday and phone number.
    """

    class Meta:
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birthday', 'phone_number']
        model = User
        widgets = {
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class UserUpdateForm(ModelForm):
    """
    Updates a user.
    """

    class Meta(UserForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number']


class MainTenantForm(ModelForm):
    """
    Creates an maintenant with additional validation.
    """

    def clean(self):
        cleaned_date = super().clean()
        begin_rent_agreement = cleaned_date.get('begin_rent_agreement')
        end_rent_agreement = cleaned_date.get('end_rent_agreement')
        residential_home = cleaned_date.get('residential_home')
        house_number = cleaned_date.get('house_number')
        room_number = cleaned_date.get('room_number')
        rent = cleaned_date.get('rent')
        tenant_id = cleaned_date.get('tenant_id')

        # check black list
        if tenant_id:
            try:
                blocked = BlockedTenantID.objects.get(pk=tenant_id)
                self.add_error('tenant_id', 'Deine Mieternummer steht auf der Schwarzen Liste!')
            except BlockedTenantID.DoesNotExist:
                pass

        # begin_rent_agreement < end_rent_agreement
        if begin_rent_agreement and end_rent_agreement:
            if begin_rent_agreement >= end_rent_agreement:
                self.add_error('end_rent_agreement', 'Das Ende des Mietvertrages muss nach dem Beginn sein!')

        # house_number of residential_home
        if residential_home and house_number:
            if house_number not in residential_home.get_house_numbers_as_list():
                self.add_error('house_number',
                               'Diese Hausnummer existiert nicht. Erlaubt sind: ' + residential_home.house_numbers)

        # room_number of residential_home
        if residential_home and room_number:
            if room_number not in residential_home.get_room_numbers_as_list():
                self.add_error('room_number',
                               'Diese Zimmernummer existiert nicht. Erlaubt sind: ' + residential_home.room_numbers)

        # positive rent
        if rent:
            if rent < 0:
                self.add_error('rent', 'Die Tagesmiete muss positiv sein!')

    class Meta:
        model = MainTenant
        exclude = ['user']
        help_texts = {
            'is_returning': 'Sofern kein Wiedereinzug geplant ist und der Hauptmieter somit vollständig auszieht, wird die Kaution über den Hausmeister zurückerstattet.',
        }
        widgets = {
            'begin_rent_agreement': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_rent_agreement': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'begin_subtenancy': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_subtenancy': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'is_returning': Select(choices=BOOLEAN_CHOICES),
            'is_searching': Select(choices=BOOLEAN_CHOICES)
        }


class MainTenantUpdateForm(MainTenantForm):
    """
    Updates a maintenant. The difference to creating a maintenant is the now available field is_searching.
    """


class SubTenantForm(ModelForm):
    """
    Creates a subtenant with additional validation.
    """

    def clean(self):
        cleaned_date = super().clean()
        student_id = cleaned_date.get('student_id')
        begin_subtenancy = cleaned_date.get('begin_subtenancy')
        end_subtenancy = cleaned_date.get('end_subtenancy')

        # check black list
        if student_id:
            try:
                blocked = BlockedStudentID.objects.get(pk=student_id)
                self.add_error('student_id', 'Deine Matrikelnummer steht auf der Schwarzen Liste!')
            except BlockedStudentID.DoesNotExist:
                pass

        # begin_subtenancy < end_subtenancy
        if begin_subtenancy and end_subtenancy:
            if begin_subtenancy >= end_subtenancy:
                self.add_error('end_subtenancy', 'Das Ende des Untermietvertrages muss nach dem Beginn sein!')

    class Meta:
        model = SubTenant
        exclude = ['user', 'is_searching']
        widgets = {
            'is_eu': Select(choices=BOOLEAN_CHOICES),
            'begin_subtenancy': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_subtenancy': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'is_searching': Select(choices=BOOLEAN_CHOICES)
        }


class SubTenantUpdateForm(SubTenantForm):
    """
    Updates a subtenant. The difference to creating a subtenant is the now available field is_searching.
    """
    class Meta(SubTenantForm.Meta):
        exclude = ['user']
