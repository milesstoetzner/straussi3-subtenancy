from django.forms import Form, ModelForm, DateInput, Select, Textarea, DateField, ChoiceField
from .models import User, MainTenant, SubTenant, Blacklist, Feedback
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

    # check blacklist
    if first_name and last_name:
        blocked = Blacklist.objects.filter(name__icontains=first_name + ' ' + last_name)
        if blocked:
            self.add_error('first_name', _('Dein Name steht auf der schwarzen Liste!'))
            self.add_error('last_name', _('Dein Name steht auf der schwarzen Liste!'))


class MainTenantCreateForm(UserCreationForm):
    """
    Creates an maintenant with additional validation.
    """

    def clean(self):
        cleaned_data = super().clean()
        return clean_tenant(self, cleaned_data)

    class Meta:
        model = MainTenant
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'birthday', 'phone_number',
                  'tenant_id']
        widgets = {
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
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

    # begin_request < end_request
    if begin_request and end_request:
        if begin_request >= end_request:
            self.add_error('end_request', _('Das Ende der angefragten Untermiete muss nach dem Beginn sein!'))


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
                  'name', 'street', 'house_number', 'postcode', 'city', 'country']
        help_texts = {
            'is_searching': _(
                'Wenn dieser Wert auf "Nein" gesetzt ist, taucht deine Anfrage mit dem oben genannten Zeitraum NICHT in der Anfragenliste auf. Sobald ein Vertrag abgeschlossen wird, wird dieser Wert automatisch auf "Nein" gesetzt. Das beudetet: Wenn deine Anfrage mit dem oben angegebenen Zeitraum in die Anfragenliste wieder aufgenommen werden soll, muss dieser Wert "Ja" lauten.'),
            'name': _('Vollständiger Name für die Korrespondenzadresse')
        }
        widgets = {
            'is_eu': Select(choices=BOOLEAN_CHOICES),
            'begin_request': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_request': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'is_searching': Select(choices=BOOLEAN_CHOICES),
            'birthday': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
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


class FeedbackForm(ModelForm):
    """
    User creates feedback.
    """

    class Meta:
        model = Feedback
        exclude = ["is_done"]
        widgets = {
            "description": Textarea(attrs={'rows': 10})
        }
