from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from ratelimit.mixins import RatelimitMixin
from django.shortcuts import redirect, render
from .faq import faq_subtenant, faq_maintenant


class Login(RatelimitMixin, SuccessMessageMixin, LoginView):
    """
    Authenticates a user by username and password.
    This view is protected by a simple rate limiter.
    """

    title = 'Login'

    ratelimit_key = 'ip'
    ratelimit_rate = '3/3m'
    ratelimit_block = True
    ratelimit_method = 'POST'

    def get_success_message(self, cleaned_data):
        return 'Willkommen zurück, ' + self.request.user.get_full_name() + '!'


@csrf_protect
@login_required
@require_POST
def logout_view(request):
    """
    Logs user out.
    """

    logout(request)
    messages.success(request, 'Du hast dich erfolgreich ausgeloggt!')

    return redirect(reverse('Index'))


class PasswordChange(SuccessMessageMixin, PasswordChangeView):
    """
    Changes the password of a authenticated user.
    """

    template_name = 'registration/password_change.html'
    success_message = 'Passwort wurde erfolgreich geändert!'

    def get_success_url(self):
        return redirect(self.request.user.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context


class PasswordReset(SuccessMessageMixin, PasswordResetView):
    """
    Sends an OTP to a given email in order to reset the user's password identified by the given email.
    """

    template_name = 'registration/password_reset.html'
    success_message = 'Wir haben eine E-Mail zum Zurücksetzen des Passwortes an die angegebene E-Mail-Adresse gesendet, sofern ein entsprechendes Konto existiert. Sie sollte in Kürze ankommen. Falls die E-Mail nicht angekommen sein sollte, bitte die E-Mail-Adresse auf Richtigkeit und gegebenenfalls den Spam-Ordner überprüfen.'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context


# DEP: set up email and test
class PasswordResetConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Resets the password of a user authenticated by an OTP send to the user's email.
    """

    template_name = 'registration/password_confirm.html'
    success_message = 'Dein Passwort wurder erfolgreich zurückgesetzt!'

    def get_success_url(self):
        return redirect(reverse('login'))

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
                  {'title': 'Ferienmiete Straußäcker 3', 'faq_maintenant': faq_maintenant,
                   'faq_subtenant': faq_subtenant})


def legal_notice(request):
    """
    Displays legal notice, disclaimer, data protection declaration and some acknowledgments.
    """

    return render(request, 'subtenancy/legal_notice.html', {'title': 'Impressum'})
