from django.forms import Form, ModelForm, DateInput, Select, Textarea, DateField, ChoiceField
from .models import User, MainTenant, SubTenant, Blacklist
from .utils import REQUEST_ORDERING
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

BOOLEAN_CHOICES = ((False, _('Nein')), (True, _('Ja')))


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


def clean_tenant(self, cleaned_data):
    first_name = cleaned_data.get('first_name')
    last_name = cleaned_data.get('last_name')
    accepted_data_processing = cleaned_data.get('accepted_data_processing')

    # check blacklist
    if first_name and last_name:
        blocked = Blacklist.objects.filter(name__icontains=first_name + ' ' + last_name)
        if blocked:
            self.add_error('first_name', _('Dein Name steht auf der schwarzen Liste!'))
            self.add_error('last_name', _('Dein Name steht auf der schwarzen Liste!'))

    # accepted_data_processing is true
    if not accepted_data_processing:
        self.add_error('accepted_data_processing', _('Du musst der Datenverarbeitung zustimmen.'))


class MainTenantCreateForm(UserCreationForm):
    """
    Creates a maintenant with additional validation.
    """

    def clean(self):
        cleaned_data = super().clean()
        return clean_tenant(self, cleaned_data)

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
        return clean_tenant(self, cleaned_data)

    class Meta(MainTenantCreateForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number', 'tenant_id']


def clean_subtenant(self, cleaned_data):
    begin_request = cleaned_data.get('begin_request')
    end_request = cleaned_data.get('end_request')
    accepted_data_processing = cleaned_data.get('accepted_data_processing')

    # begin_request < end_request
    if begin_request and end_request:
        if begin_request >= end_request:
            self.add_error('end_request', _('Das Ende der angefragten Untermiete muss nach dem Beginn sein!'))

    # accepted_data_processing is true
    if not accepted_data_processing:
        self.add_error('accepted_data_processing', _('Du musst der Datenverarbeitung zustimmen.'))


class SubTenantCreateForm(UserCreationForm):
    """
    Creates a subtenant with additional validation.
    """

    def clean(self):
        cleaned_data = super().clean()
        return clean_subtenant(self, cleaned_data)

    class Meta:
        model = SubTenant
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'birthday', 'phone_number',
                  'nationality', 'begin_request', 'end_request', 'is_searching',
                  'name', 'street', 'house_number', 'postcode', 'city', 'country', 'accepted_data_processing']
        help_texts = {
            'is_searching': _(
                'Wenn dieser Wert auf "Nein" gesetzt ist, taucht deine Anfrage mit dem oben genannten Zeitraum NICHT in der Anfragenliste auf. Sobald ein Vertrag abgeschlossen wird, wird dieser Wert automatisch auf "Nein" gesetzt. Das beudetet: Wenn deine Anfrage mit dem oben angegebenen Zeitraum in die Anfragenliste wieder aufgenommen werden soll, muss dieser Wert "Ja" lauten.'),
            'name': _('Vollständiger Name für die Korrespondenzadresse'),
            'accepted_data_processing': _('Mehr Informationen unter https://untermiete.straussi3.de/impressum'),
        }
        widgets = {
            'is_eu': Select(choices=BOOLEAN_CHOICES),
            'begin_request': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_request': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'is_searching': Select(choices=BOOLEAN_CHOICES),
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'accepted_data_processing': Select(choices=BOOLEAN_CHOICES)
        }


class SubTenantUpdateForm(ModelForm):
    """
    Updates a subtenant. The difference to creating a subtenant is the now available field is_searching.
    """

    def clean(self):
        cleaned_data = super().clean()
        return clean_subtenant(self, cleaned_data)

    class Meta(SubTenantCreateForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'birthday', 'phone_number',
                  'nationality', 'begin_request', 'end_request', 'is_searching',
                  'name', 'street', 'house_number', 'postcode', 'city', 'country']


class RequestUpdateForm(SubTenantCreateForm):
    """
    Subtenant can update only his request.
    """

    class Meta(SubTenantUpdateForm.Meta):
        fields = ['begin_request', 'end_request', 'is_searching']


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
        begin = cleaned_data.get('begin_request')
        end = cleaned_data.get('end_request')

        # begin_request < end_request
        if begin and end:
            if begin >= end:
                self.add_error('end', _('Das Ende der angefragten Untermiete muss nach dem Beginn sein!'))
