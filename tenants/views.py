import datetime

from django.db.transaction import atomic

from tenants.models import User, SubTenant, SubtenancyRequest, Blacklist
from tenants.forms import UserUpdateForm, MainTenantCreateForm, MainTenantUpdateForm, SubTenantCreateForm, \
    SubTenantUpdateForm, SubtenancyRequestForm, RequestQueryForm, ResendConfirmationForm
from tenants.emails import send_registration_mail, send_confirmation_mail
from tenants.tokens import email_confirmation_token
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.mail import EmailMessage
from subtenancy.mail import send_email
from smtplib import SMTPException
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template
from django_ratelimit.decorators import ratelimit
from subtenancy.views import handler400
import logging

logger = logging.getLogger(__name__)


@atomic
@csrf_protect
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
@require_http_methods(['GET', 'POST'])
def create_tenant(request, is_maintenant):
    """
    Creates a new user and a corresponding maintenant/subtenant.
    This method is atomic. Registration is rate limited per client IP.
    """

    context = {}

    if request.method == 'GET':
        # Displays the maintenant/subtenant creation form (and the request form for subtenants)

        tenant_form = MainTenantCreateForm() if is_maintenant else SubTenantCreateForm()
        request_form = None if is_maintenant else SubtenancyRequestForm()
        context['get'] = True

    else:
        # Validates the received form data.
        # If the data is valid a new maintenant/subtenant (and the subtenant's request) is created.

        tenant_form = MainTenantCreateForm(request.POST) if is_maintenant else SubTenantCreateForm(request.POST)
        request_form = None if is_maintenant else SubtenancyRequestForm(request.POST)

        # evaluate both forms so that both show their errors
        tenant_valid = tenant_form.is_valid()
        request_valid = request_form is None or request_form.is_valid()

        if tenant_valid and request_valid:
            tenant = tenant_form.save()
            group_verbose = 'Maintenant' if is_maintenant else 'Subtenant'
            group = Group.objects.get(name=group_verbose)
            tenant.user.groups.add(group)
            tenant.type = 'HM' if is_maintenant else 'UM'
            tenant.save()

            if request_form is not None:
                subtenancy_request = request_form.save(commit=False)
                subtenancy_request.subtenant = tenant
                subtenancy_request.save()

            messages.success(request, _('Registrierung war erfolgreich. Wir haben dir eine E-Mail mit einem Bestätigungslink geschickt. Bitte bestätige deine E-Mail-Adresse, bevor du dich einloggst.'))

            logger.info('registration: %s "%s" (id %s)', tenant.type, tenant.username, tenant.pk)
            send_registration_mail(request, tenant)

            # mail_admins(subject='ANALYSE create_tenant', message='Es gab eine Registrierung!', fail_silently=True)

            return redirect(reverse('login'))

    context['title'] = _('Hauptmieter Registrierung') if is_maintenant else _('Untermieter Registrierung')
    context['tenant_form'] = tenant_form
    context['request_form'] = request_form
    context['is_maintenant'] = is_maintenant

    return render(request, 'tenants/create.html', context)


@require_GET
def confirm_email(request, uidb64, token):
    """
    Confirms the e-mail address behind a link from the registration or confirmation mail.
    """

    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not email_confirmation_token.check_token(user, token):
        logger.warning('invalid email confirmation link (uid %r)', uidb64)
        return render(request, 'tenants/confirm_email_failed.html', {'title': _('E-Mail-Adresse bestätigen')},
                      status=400)

    user.confirm_email()
    logger.info('email confirmed: user %s', user.pk)
    messages.success(request, _('Deine E-Mail-Adresse ist bestätigt. Du kannst dich nun einloggen.'))
    return redirect(reverse('login'))


@csrf_protect
@ratelimit(key='ip', rate='5/h', method='POST', block=True)
@require_http_methods(['GET', 'POST'])
def resend_confirmation(request):
    """
    Sends a new confirmation link to an unconfirmed account. Answers the same way whether or not the address exists,
    so the form cannot be used to look up accounts. Rate limited per client IP like the password reset.
    """

    context = {'title': _('Bestätigungslink erneut senden')}

    if request.method == 'GET':
        form = ResendConfirmationForm()
        context['get'] = True
    else:
        form = ResendConfirmationForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email__iexact=form.cleaned_data['email']).first()
            if user is not None and not user.is_email_confirmed():
                send_confirmation_mail(request, user)
            messages.success(request, _('Falls zu dieser E-Mail-Adresse ein noch nicht bestätigter Account existiert, haben wir einen neuen Bestätigungslink geschickt. Bitte prüfe auch den Spam-Ordner.'))
            return redirect(reverse('login'))

    context['form'] = form
    return render(request, 'tenants/resend_confirmation.html', context)


@login_required
@require_GET
def view_profile(request):
    """
    Displays the details about the authenticated user and his corresponding maintenant/subtenant.
    """

    context = {}
    context['get'] = True
    context['tenant'] = request.user
    context['title'] = _('Profil von') + ' ' + str(request.user)

    if request.user.is_tenant():
        if request.user.is_subtenant():
            messages.info(request, _('Als Untermieter kannst du nicht aktiv nach einem Zimmer suchen. Du musst warten, bis dich ein Hauptmieter über die Anfragenliste kontaktiert!'))

        if request.user.is_maintenant():
            context['tenant_form'] = MainTenantUpdateForm(instance=request.user.maintenant)
        else:
            context['tenant_form'] = SubTenantUpdateForm(instance=request.user.subtenant)
            subtenancy_request = request.user.subtenant.get_request()
            if subtenancy_request is not None:
                context['request_form'] = SubtenancyRequestForm(instance=subtenancy_request)
    else:
        context['tenant_form'] = UserUpdateForm(instance=request.user)

    return render(request, 'tenants/view.html', context)


def reset_email_confirmation(request, tenant):
    """
    A changed e-mail address is unverified again: clear the confirmation and send a fresh link. The caller decides what
    else happens (the owner is logged out, the Sprechstunde is not).
    """
    tenant.email_confirmed_at = None
    tenant.save(update_fields=['email_confirmed_at'])
    send_confirmation_mail(request, tenant)
    logger.info('email changed, confirmation reset: user %s', tenant.pk)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.change_own'])
@require_http_methods(['GET', 'POST'])
def update_profile(request):
    """
    Updates the details about a user and his corresponding maintenant/subtenant.
    """

    context = {}

    user = request.user

    # only tenants can be updated (accessing user.maintenant/user.subtenant on other users raises)
    if not user.is_tenant():
        return handler400(request)

    tenant = user.maintenant if user.is_maintenant() else user.subtenant
    form = MainTenantUpdateForm if user.is_maintenant() else SubTenantUpdateForm

    if request.method == 'GET':
        tenant_form = form(instance=tenant)
        context['get'] = True
    else:
        tenant_form = form(request.POST, instance=tenant)
        if tenant_form.is_valid():
            if tenant_form.has_changed():
                email_changed = 'email' in tenant_form.changed_data
                tenant_form.save()
                if email_changed:
                    # the owner changed their own address: un-confirm it, log them out and make them confirm it first
                    reset_email_confirmation(request, tenant)
                    messages.success(request, _('Deine E-Mail-Adresse wurde geändert. Wir haben dir einen Bestätigungslink an die neue Adresse geschickt. Bitte bestätige sie und logge dich anschließend wieder ein.'))
                    logout(request)
                    return redirect(reverse('login'))
                logger.info('profile updated: user %s', user.pk)
                messages.success(request, _('Änderungen wurden erfolgreich übernommen!'))
            else:
                messages.info(request, _('Es gab keine Änderungen!'))
            return redirect(reverse('Profile'))

    context['title'] = _('Profil aktualisieren')
    context['tenant_form'] = tenant_form
    context['tenant'] = tenant

    return render(request, 'tenants/update_profile.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.change_own'])
@require_http_methods(['GET', 'POST'])
def update_request(request):
    """
    Creates or updates the authenticated subtenant's request (a subtenant has at most one).
    """

    tenant = request.user

    # only subtenants have a request
    if not tenant.is_subtenant():
        return handler400(request)

    subtenancy_request = tenant.subtenant.get_request()
    has_request = subtenancy_request is not None
    if not has_request:
        subtenancy_request = SubtenancyRequest(subtenant=tenant.subtenant)

    context = {}

    if request.method == 'GET':
        form = SubtenancyRequestForm(instance=subtenancy_request)
        context['get'] = True
    else:
        form = SubtenancyRequestForm(request.POST, instance=subtenancy_request)
        if form.is_valid():
            if not has_request:
                form.save()
                logger.info('request created: user %s', tenant.pk)
                messages.success(request, _('Deine Anfrage wurde erstellt.'))
            elif form.has_changed():
                form.save()
                logger.info('request updated: user %s', tenant.pk)
                messages.success(request, _('Änderungen wurden erfolgreich übernommen!'))
            else:
                messages.info(request, _('Es gab keine Änderungen!'))
            return redirect(reverse('Profile'))

    context['has_request'] = has_request
    context['title'] = _('Anfrage aktualisieren') if has_request else _('Anfrage erstellen')
    context['form'] = form

    return render(request, 'tenants/request.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.change_own'])
@require_POST
def delete_request(request):
    """
    Deletes the authenticated subtenant's request, i.e. the subtenant stops searching for a room.
    """

    tenant = request.user

    # only subtenants have a request
    if not tenant.is_subtenant():
        return handler400(request)

    subtenancy_request = tenant.subtenant.get_request()
    if subtenancy_request is None:
        return handler400(request)

    subtenancy_request.delete()
    logger.info('request deleted: user %s', tenant.pk)
    messages.success(request, _('Deine Anfrage wurde gelöscht.'))

    return redirect(reverse('Profile'))


@login_required
@permission_required(['tenants.view_user', 'tenants.view_maintenant', 'tenants.view_subtenant'])
@require_GET
def view_tenant(request, pk):
    """
    Displays the details about a maintenant/subtenant.
    """

    user = get_object_or_404(User, pk=pk)

    # only tenants can be updated
    if not user.is_tenant():
        return handler400(request)

    tenant = user.maintenant if user.is_maintenant() else user.subtenant
    form = MainTenantUpdateForm if user.is_maintenant() else SubTenantUpdateForm

    context = {}
    context['get'] = True
    context['tenant'] = user
    context['title'] = str(user)
    context['tenant_form'] = form(instance=tenant)
    if user.is_subtenant() and tenant.get_request() is not None:
        context['request_form'] = SubtenancyRequestForm(instance=tenant.get_request())

    if user.is_maintenant():
        messages.info(request, 'Der Zeitraum der Verträge mit diesem Hauptmieter beträgt ' + str(
            tenant.get_amount_of_days()) + ' Tage!')

    return render(request, 'tenants/view.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.change_user', 'tenants.change_maintenant', 'tenants.change_subtenant'])
@require_http_methods(['GET', 'POST'])
def update_tenant(request, pk):
    """
    Updates the details about a maintenant/subtenant.
    """

    context = {}

    user = get_object_or_404(User, pk=pk)

    # only tenants can be updated (accessing user.maintenant/user.subtenant on other users raises)
    if not user.is_tenant():
        return handler400(request)

    tenant = user.maintenant if user.is_maintenant() else user.subtenant
    form = MainTenantUpdateForm if user.is_maintenant() else SubTenantUpdateForm

    if request.method == 'GET':
        tenant_form = form(instance=tenant)
        context['get'] = True
    else:
        tenant_form = form(request.POST, instance=tenant)
        if tenant_form.is_valid():
            if tenant_form.has_changed():
                email_changed = 'email' in tenant_form.changed_data
                tenant_form.save()
                if email_changed:
                    # the Sprechstunde changed the tenant's address: un-confirm it so the tenant must confirm the new one
                    reset_email_confirmation(request, tenant)
                    messages.info(request, 'Die E-Mail-Adresse wurde geändert. Der Account muss sie über den zugeschickten Link bestätigen, bevor er sich wieder einloggen kann.')
                logger.info('tenant updated by staff: user %s (by %s)', tenant.pk, request.user.pk)
                messages.success(request, 'Änderungen wurden erfolgreich übernommen!')
            else:
                messages.info(request, 'Es gab keine Änderungen!')

            return redirect(reverse('tenants:TenantView', kwargs={'pk': tenant.pk}))

    context['title'] = str(tenant.user) + 'aktualisieren'
    context['tenant_form'] = tenant_form
    context['tenant'] = tenant

    return render(request, 'tenants/update.html', context)


@csrf_protect
@login_required
@permission_required('tenants.contact_subtenant')
@require_http_methods(['GET', 'POST'])
def contact_subtenant(request, pk):
    """
    A maintenant can send an active searching subtenant an email containing his contact details.
    """

    subtenant = get_object_or_404(SubTenant, pk=pk)

    # only searching subtenants (with a request whose period has not ended) can be contacted
    if not subtenant.is_searching():
        return handler400(request)

    # a contact mail to an unconfirmed address would go nowhere
    if not subtenant.is_email_confirmed():
        return handler400(request)
    subtenancy_request = subtenant.get_request()

    # only active subtenants can be contacted
    if not subtenant.is_active:
        return handler400(request)

    # email content (the "don't reply" disclaimer and the footer come from the shared email/base.html)
    mail_context = {'user': request.user, 'subtenant': subtenant, 'subtenancy_request': subtenancy_request,
                    'site_name': get_current_site(request).name}
    content = get_template('tenants/contact_email.txt').render(mail_context)

    if request.method == 'GET':
        # Asks for consent

        context = {}
        context['subtenant'] = subtenant
        context['site_name'] = get_current_site(request).name
        context['title'] = _('Kontaktaufnahme')
        context['msg'] = content
        return render(request, 'tenants/contact.html', context)

    else:
        # Sends email with maintenant's contact details to the subtenant

        try:
            mail = EmailMessage('Untermiete Straußäcker 3 Kontaktaufnahme',
                                content,
                                '',
                                [subtenant.email])
            send_email(mail, receiver_id=subtenant.pk, sender_id=request.user.pk)

            confirmation = get_template('tenants/contact_email.txt').render({**mail_context, 'confirmation': True})
            mail = EmailMessage(
                'Bestätigung Untermiete Straußäcker 3 Kontaktaufnahme',
                confirmation,
                '',
                [request.user.email])
            send_email(mail, receiver_id=request.user.pk, fail_silently=True)
            logger.info('contact: maintenant %s contacted subtenant %s', request.user.pk, subtenant.pk)

            # mail_admins(subject='ANALYSE contact_subtenant', message='Es gab eine Kontaktaufnahme!', fail_silently=True)

        except SMTPException:
            logger.exception('contact mail failed: maintenant %s -> subtenant %s', request.user.pk, subtenant.pk)
            messages.error(request, _('Untermieter konnte nicht kontaktiert werden!'))
            return redirect('Requests')

        messages.success(request,
                         _(
                             'Untermieter wurde erfolgreich kontaktiert! Wir haben dir als Bestätigung der Kontaktaufnahme eine Email gesendet.'))
        return redirect('Requests')


@login_required()
@permission_required(['tenants.view_blacklist'])
@require_GET
def blacklist(request):
    """
    Displays the blacklist containing all blocked tenant ids and student ids.
    """

    query = Blacklist.objects.all()

    context = {}
    context['title'] = 'Schwarze Liste'
    context['blacklist'] = query

    if not query:
        messages.info(request, 'Die schwarze Liste ist leer!')

    return render(request, 'tenants/blacklist.html', context)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def query_requests(request):
    """
    Maintenant querys requests
    """

    context = {}
    # listed are requests of active subtenants whose address is confirmed, i.e. who can be contacted
    requests = SubtenancyRequest.objects.active().filter(subtenant__is_active=True,
                                                         subtenant__email_confirmed_at__isnull=False)

    if requests.exists():
        default = {
            'begin': requests.earliest('begin').begin,
            'end': requests.latest('end').end
        }
    else:
        default = {
            'begin': datetime.datetime.now(),
            'end': datetime.datetime.now(),
        }

    if request.method == 'GET':
        if not request.user.is_anonymous and request.user.is_subtenant():
            messages.error(request, _("In dieser Liste werden keine Zimmer angeboten, sondern Zimmer gesucht! Daher ist diese Liste nur für Hauptmieter bei der Suche nach einem Untermieter nützlich!"))
            messages.error(request, _("Untermieter können hier keine angebotenen Zimmer finden. Als Untermieter kannst du nicht aktiv nach einem Zimmer suchen. Du musst warten, bis dich ein Hauptmieter über diese Liste kontaktiert!"))

        form = RequestQueryForm(initial=default)
        context['get'] = True
    else:
        form = RequestQueryForm(request.POST)
        if form.is_valid():
            messages.success(request, _('Anfrageliste erfolgreich gefiltert'))
            order_first = request.POST['order_first']
            order_second = request.POST['order_second']
            context['object_list'] = requests.filter(begin__gte=form.cleaned_data.get('begin'),
                                                     end__lte=form.cleaned_data.get('end')).order_by(order_first, order_second)

    # if GET or form is not valid return whole list
    if request.method == 'GET' or not form.is_valid():
        context['object_list'] = requests.order_by('begin', 'end')

    context['title'] = _('Anfragenliste')
    context['form'] = form

    return render(request, 'tenants/requests.html', context)
