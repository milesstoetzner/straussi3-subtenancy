from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, DateInput, Select, Textarea, DateField, ChoiceField, EmailField
from .models import User, MainTenant, SubTenant, SubtenancyRequest, Blacklist
from .utils import REQUEST_ORDERING
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

BOOLEAN_CHOICES = ((False, _('Nein')), (True, _('Ja')))


class LoginForm(AuthenticationForm):
    """
    Login that additionally requires a confirmed e-mail address. The template shows a hint with the resend link when
    email_unconfirmed is set.
    """

    email_unconfirmed = False

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_email_confirmed():
            self.email_unconfirmed = True
            raise ValidationError(_('Deine E-Mail-Adresse ist noch nicht bestätigt.'), code='email_unconfirmed')


class ResendConfirmationForm(Form):
    """
    Asks for the address of the account that should get a new confirmation link.
    """

    email = EmailField(label=_('Email Adresse'), max_length=150)


class UserUpdateForm(ModelForm):
    """
    Updates a user.
    """

    class Meta:
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number']
        model = User
        widgets = {
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


def validate_not_blacklisted(form, cleaned_data):
    """
    Adds errors to first_name and last_name if the full name is on the blacklist.
    """

    first_name = cleaned_data.get('first_name')
    last_name = cleaned_data.get('last_name')

    if first_name and last_name:
        blocked = Blacklist.objects.filter(name__icontains=first_name + ' ' + last_name)
        if blocked:
            form.add_error('first_name', _('Dein Name steht auf der schwarzen Liste!'))
            form.add_error('last_name', _('Dein Name steht auf der schwarzen Liste!'))


def validate_data_processing_consent(form, cleaned_data):
    """
    Adds an error if the consent to data processing was not given.
    """

    if not cleaned_data.get('accepted_data_processing'):
        form.add_error('accepted_data_processing', _('Du musst der Datenverarbeitung zustimmen.'))


def validate_request_period(form, cleaned_data):
    """
    Adds an error if the requested subtenancy does not end after it begins.
    """

    begin = cleaned_data.get('begin')
    end = cleaned_data.get('end')

    if begin and end:
        if begin >= end:
            form.add_error('end', _('Das Ende der angefragten Untermiete muss nach dem Beginn sein!'))


class MainTenantCreateForm(UserCreationForm):
    """
    Creates a maintenant with additional validation.
    """

    def clean(self):
        cleaned_data = super().clean()
        validate_not_blacklisted(self, cleaned_data)
        validate_data_processing_consent(self, cleaned_data)
        return cleaned_data

    class Meta:
        model = MainTenant
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'birthday', 'phone_number',
                  'tenant_id', 'accepted_data_processing']
        widgets = {
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'accepted_data_processing': Select(choices=BOOLEAN_CHOICES)
        }


class MainTenantUpdateForm(ModelForm):
    """
    Updates a maintenant. The difference to creating a maintenant is that username, password1 and password2 is not available.
    """

    def clean(self):
        cleaned_data = super().clean()
        validate_not_blacklisted(self, cleaned_data)
        return cleaned_data

    class Meta(MainTenantCreateForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number', 'tenant_id']


class SubTenantCreateForm(UserCreationForm):
    """
    Creates a subtenant with additional validation. The request itself is created with SubtenancyRequestForm.
    """

    def clean(self):
        cleaned_data = super().clean()
        validate_not_blacklisted(self, cleaned_data)
        validate_data_processing_consent(self, cleaned_data)
        return cleaned_data

    class Meta:
        model = SubTenant
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'birthday', 'phone_number',
                  'nationality', 'name', 'street', 'house_number', 'postcode', 'city', 'country',
                  'accepted_data_processing']
        help_texts = {
            'name': _('Vollständiger Name für die Korrespondenzadresse'),
            'accepted_data_processing': _('Mehr Informationen unter https://untermiete.straussi3.de/impressum'),
        }
        widgets = {
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'accepted_data_processing': Select(choices=BOOLEAN_CHOICES)
        }


class SubTenantUpdateForm(ModelForm):
    """
    Updates a subtenant. The difference to creating a subtenant is that username, password1 and password2 is not available.
    """

    def clean(self):
        cleaned_data = super().clean()
        validate_not_blacklisted(self, cleaned_data)
        return cleaned_data

    class Meta(SubTenantCreateForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number',
                  'nationality', 'name', 'street', 'house_number', 'postcode', 'city', 'country']


class SubtenancyRequestForm(ModelForm):
    """
    Creates or updates a subtenant's request. Used during registration and when the subtenant updates the request.
    """

    def clean(self):
        cleaned_data = super().clean()
        validate_request_period(self, cleaned_data)
        return cleaned_data

    class Meta:
        model = SubtenancyRequest
        fields = ['begin', 'end']
        help_texts = {
            'end': _('Solange die Anfrage existiert und ihr Zeitraum noch nicht vorbei ist, erscheint sie in der Anfragenliste. Sobald ein Vertrag abgeschlossen wird, wird sie automatisch gelöscht. Du kannst sie jederzeit in deinem Profil löschen.'),
        }
        widgets = {
            'begin': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class RequestQueryForm(Form):
    """
    Maintennat can query database.
    """

    begin = DateField(label=_('Beginn der Anfrage'), widget=DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    end = DateField(label=_('Ende der Anfrage'), widget=DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    order_first = ChoiceField(label=_('Zunächst ordnen nach'), choices=REQUEST_ORDERING)
    order_second = ChoiceField(label=_('Dann ordnen nach'), choices=REQUEST_ORDERING)

    def clean(self):
        cleaned_data = super().clean()
        begin = cleaned_data.get('begin')
        end = cleaned_data.get('end')

        # begin < end
        if begin and end:
            if begin >= end:
                self.add_error('end', _('Das Ende der angefragten Untermiete muss nach dem Beginn sein!'))
