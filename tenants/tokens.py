from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token for the e-mail confirmation link, built like the password reset token: signed, bound to the user and expiring
    after PASSWORD_RESET_TIMEOUT. The hash contains the address and the confirmation timestamp, so a link stops working
    once the address is confirmed or changed.
    """

    key_salt = 'tenants.tokens.EmailConfirmationTokenGenerator'

    def _make_hash_value(self, user, timestamp):
        confirmed = '' if user.email_confirmed_at is None else user.email_confirmed_at.isoformat()
        return f'{user.pk}{user.email}{confirmed}{timestamp}'


email_confirmation_token = EmailConfirmationTokenGenerator()
