from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect


class PasswordChange(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_message = 'Passwort wurde erfolgreich geändert!'

    def get_success_url(self):
        return redirect(self.request.user.get_absolute_url())


class PasswordReset(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    success_message = 'Wir haben eine E-Mail zum Zurücksetzen des Passwortes an die angegebene E-Mail-Adresse gesendet, sofern ein entsprechendes Konto existiert. Sie sollte in Kürze ankommen. Falls die E-Mail nicht angekommen sein sollte, bitte die E-Mail-Adresse auf Richtigkeit und gegebenenfalls den Spam-Ordner überprüfen.'
    success_url = '/'
