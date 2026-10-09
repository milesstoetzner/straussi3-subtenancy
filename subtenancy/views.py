from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

@method_decorator(
    ratelimit(key='ip', rate='10/5m', method='POST', block=True),
    name='dispatch'
)
class Login(SuccessMessageMixin, LoginView):
    """
    Authenticates a user by username and password.
    This view is protected by a simple rate limiter keyed on the client IP (see RATELIMIT_IP_META_KEY in settings).
    """

    title = 'Login'

    def get_success_message(self, cleaned_data):
        return _('Willkommen zurück') + ', ' + self.request.user.get_full_name() + '!'


@csrf_protect
@login_required
@require_POST
def logout_view(request):
    """
    Logs user out.
    """

    logout(request)
    messages.success(request, _('Du hast dich erfolgreich ausgeloggt!'))

    return redirect(reverse('Index'))


class PasswordChange(SuccessMessageMixin, PasswordChangeView):
    """
    Changes the password of a authenticated user.
    """

    template_name = 'registration/password_change.html'
    success_message = _('Passwort wurde erfolgreich geändert!')

    def get_success_url(self):
        return reverse('Profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context


@method_decorator(
    ratelimit(key='subtenancy.ratelimit.client_ip', rate='5/h', method='POST', block=True),
    name='dispatch'
)
class PasswordReset(SuccessMessageMixin, PasswordResetView):
    """
    Sends an OTP to a given email in order to reset the user's password identified by the given email.
    Rate limited per client IP so the form cannot be used to flood a mailbox.
    """

    template_name = 'registration/password_reset.html'
    success_message = _(
        'Wir haben eine E-Mail zum Zurücksetzen des Passwortes an die angegebene E-Mail-Adresse gesendet, sofern ein entsprechendes Konto existiert. Sie sollte in Kürze ankommen. Falls die E-Mail nicht angekommen sein sollte, bitte die E-Mail-Adresse auf Richtigkeit und gegebenenfalls den Spam-Ordner überprüfen.')
    success_url = '/'
    html_email_template_name = 'registration/password_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context


class PasswordResetCallback(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Resets the password of a user authenticated by an OTP send to the user's email.
    """

    template_name = 'registration/password_confirm.html'
    success_message = _('Dein Passwort wurde erfolgreich zurückgesetzt!')

    def get_success_url(self):
        return reverse('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context


def index(request):
    """
    Displays the landing page with FAQ for maintenants and subtenants.
    """
    return render(request, 'subtenancy/index.html',
                  {'title': _('Ferienmiete') + ' Straußäcker 3'})


def legal_notice(request):
    """
    Displays legal notice, disclaimer, data protection declaration and some acknowledgments.
    """

    return render(request, 'subtenancy/legal_notice.html', {'title': _('Impressum')})


def handler400(request, exception=None):
    messages.error(request, _('Es tut uns Leid, aber deine Anfrage konnte nicht verarbeitet werden!'))
    return redirect_to_error(request, 400)


def handler403(request, exception=None):
    messages.error(request, _('Es tut uns Leid, aber auf diese Seite hast du keinen Zugriff!'))
    return redirect_to_error(request, 403)


def handler404(request, exception=None):
    messages.error(request, _('Es tut uns Leid, aber die angefragte URL %(path)s wurde nicht gefunden!') % {
        'path': str(request.path)})
    return redirect_to_error(request, 404)


def handler500(request, exception=None):
    messages.error(request, _('Es tut uns Leid, aber ein unerwarteter Fehler ist aufgetreten!'))
    return redirect_to_error(request, 500)


def handlerCSRF(request, reason=""):
    messages.error(request, _('Es tut uns Leid, aber die CSRF Überprüfung ist fehlgeschlagen!'))
    return redirect_to_error(request, 403)


def redirect_to_error(request, status):
    """
    Render for each error the error page.
    """

    context = {}
    context['get'] = True
    context['title'] = _('Error')

    return render(request, 'tenants/error.html', status=status, context=context)