from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tenants.tokens import email_confirmation_token
from django.conf import settings

from subtenancy.mail import send_email


def _site_name(request):
    return get_current_site(request).name if request is not None else settings.ORIGIN


def confirmation_url(request, user):
    """
    Absolute URL of the confirmation link. Built from the request for a web view, or from ORIGIN when there is no
    request (a management command).
    """
    path = reverse('ConfirmEmail', kwargs={
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': email_confirmation_token.make_token(user),
    })
    if request is not None:
        return request.build_absolute_uri(path)
    return settings.ORIGIN.rstrip('/') + path


def send_text_mail(subject, template_name, context, to, receiver_id=None):
    content = get_template(template_name).render(context)
    mail = EmailMessage(subject, content, '', [to])
    send_email(mail, receiver_id=receiver_id, fail_silently=True)


def send_registration_mail(request, user):
    """
    Welcome mail after the registration, with the confirmation link.
    """
    send_text_mail('Untermiete Straußäcker 3 Registrierung',
                   'tenants/register_email.txt',
                   {'user': user, 'site_name': _site_name(request),
                    'confirm_url': confirmation_url(request, user)},
                   user.email, receiver_id=user.pk)


def send_confirmation_mail(request, user):
    """
    Short mail with a fresh confirmation link, after a resend or a change of the address. Until it is confirmed the
    account cannot log in.
    """
    send_text_mail('Untermiete Straußäcker 3 E-Mail-Adresse bestätigen',
                   'tenants/confirm_email.txt',
                   {'user': user, 'site_name': _site_name(request),
                    'confirm_url': confirmation_url(request, user)},
                   user.email, receiver_id=user.pk)
