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


class Login(RatelimitMixin, SuccessMessageMixin, LoginView):
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
    logout(request)
    messages.success(request, 'Du hast dich erfolgreich ausgeloggt!')
    return redirect(reverse('Index'))


class PasswordChange(SuccessMessageMixin, PasswordChangeView):
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
    template_name = 'registration/password_reset.html'
    success_message = 'Wir haben eine E-Mail zum Zurücksetzen des Passwortes an die angegebene E-Mail-Adresse gesendet, sofern ein entsprechendes Konto existiert. Sie sollte in Kürze ankommen. Falls die E-Mail nicht angekommen sein sollte, bitte die E-Mail-Adresse auf Richtigkeit und gegebenenfalls den Spam-Ordner überprüfen.'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context


# DEP: set up email
class PasswordResetConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'registration/password_confirm.html'
    success_message = 'Dein Passwort wurder erfolgreich zurückgesetzt!'

    def get_success_url(self):
        return redirect(reverse('login'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True
        return context
