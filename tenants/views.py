import datetime

from django.db.transaction import atomic
from tenants.models import User, SubTenant, Blacklist, HallOfFame
from tenants.forms import UserUpdateForm, MainTenantCreateForm, MainTenantUpdateForm, SubTenantCreateForm, \
    SubTenantUpdateForm, FeedbackForm, RequestUpdateForm, RequestQueryForm
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.contrib import messages
from django.core.mail import EmailMessage, mail_admins
from smtplib import SMTPException
from django.views.generic import ListView
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template
from subtenancy.views import handler400


@atomic
@csrf_protect
@require_http_methods(['GET', 'POST'])
def create_tenant(request, is_maintenant):
    """
    Creates a new user and a corresponding maintenant/subtenant.
    This method is atomic.
    """

    context = {}

    if request.method == 'GET':
        # Displays the two forms: user creation form and maintenant/subtenant creation form

        tenant_form = MainTenantCreateForm() if is_maintenant else SubTenantCreateForm()
        context['get'] = True

    else:
        # Validates the received form data.
        # If data of both forms are valid a new user and his corresponding maintenant/subtenant is created.

        tenant_form = MainTenantCreateForm(request.POST) if is_maintenant else SubTenantCreateForm(request.POST)

        if tenant_form.is_valid():
            tenant = tenant_form.save()
            group_verbose = 'Maintenant' if is_maintenant else 'Subtenant'
            group = Group.objects.get(name=group_verbose)
            tenant.user.groups.add(group)
            tenant.type = 'HM' if is_maintenant else 'UM'
            tenant.save()

            messages.success(request, _('Registrierung war erfolgreich. Du kannst dich nun einloggen.'))

            content = get_template('tenants/register_email.html').render(
                {'user': tenant, 'site_name': get_current_site(request).name})
            mail = EmailMessage('Ferienmiete Straußäcker 3 Registrierung/ Subtenancy Straußäcker 3 Registration',
                                content,
                                '', [tenant.email])
            mail.content_subtype = "html"
            mail.send(fail_silently=True)

            mail_admins(subject='ANALYSE create_tenant', message='Es gab eine Registrierung!', fail_silently=True)

            return redirect(reverse('login'))

    context['title'] = _('Hauptmieter Registrierung') if is_maintenant else _('Untermieter Registrierung')
    context['tenant_form'] = tenant_form
    context['is_maintenant'] = is_maintenant

    return render(request, 'tenants/create.html', context)


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
        context['tenant_form'] = MainTenantUpdateForm(
            instance=request.user.maintenant) if request.user.is_maintenant() else SubTenantUpdateForm(
            instance=request.user.subtenant)
    else:
        context['tenant_form'] = UserUpdateForm(instance=request.user)

    return render(request, 'tenants/view.html', context)


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

    tenant = user.maintenant if user.is_maintenant() else user.subtenant
    form = MainTenantUpdateForm if user.is_maintenant() else SubTenantUpdateForm

    # only tenants can be updated
    if not tenant.is_tenant():
        return handler400(request)

    if request.method == 'GET':
        tenant_form = form(instance=tenant)
        context['get'] = True
    else:
        tenant_form = form(request.POST, instance=tenant)
        if tenant_form.is_valid():
            if tenant_form.has_changed():
                tenant_form.save()
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
    Updates a subtenant's request details.
    """

    context = {}

    tenant = request.user

    # only subtenants can update request
    if not tenant.is_subtenant():
        return handler400(request)

    if request.method == 'GET':
        form = RequestUpdateForm(instance=tenant.subtenant)
        context['get'] = True
    else:
        form = RequestUpdateForm(request.POST, instance=tenant.subtenant)
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, _('Änderungen wurden erfolgreich übernommen!'))
            else:
                messages.info(request, _('Es gab keine Änderungen!'))

            return redirect(reverse('Profile'))

    context['title'] = _('Anfrage aktualisieren')
    context['form'] = form

    return render(request, 'tenants/update_request.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.delete_own'])
@require_http_methods(['GET', 'POST'])
def delete_profile(request):
    """
    Deletes the authenticated user and his corresponding maintenant/subtenant iff no contracts exist.
    """

    user = request.user

    if request.method == 'GET':
        context = {}
        context['tenant'] = user
        context['title'] = _('Account löschen')
        return render(request, 'tenants/delete.html', context)
    else:
        try:
            user.delete()
        except ProtectedError:
            messages.error(request,
                           _(
                               'Der Account kann nicht gelöscht werden, da mindestens ein Vertrag mit diesem Account abgeschlossen wurde!'))
            return redirect(reverse('Profile'))

        messages.success(request, _('Der Account wurde erfolgreich gelöscht!'))
        return redirect('Index')


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
    tenant = user.maintenant if user.is_maintenant() else user.subtenant
    form = MainTenantUpdateForm if user.is_maintenant() else SubTenantUpdateForm

    # only tenants can be updated
    if not tenant.is_tenant():
        return handler400(request)

    if request.method == 'GET':
        tenant_form = form(instance=tenant)
        context['get'] = True
    else:
        tenant_form = form(request.POST, instance=tenant)
        if tenant_form.is_valid():
            if tenant_form.has_changed():
                tenant_form.save()
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

    # only searching subtenants can be contacted
    if not subtenant.is_searching:
        return handler400(request)

    # only active subtenants can be contacted
    if not subtenant.is_active:
        return handler400(request)

    # email content
    content = get_template('tenants/contact_email.html').render(
        {'user': request.user, 'subtenant': subtenant, 'site_name': get_current_site(request).name})

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
            mail = EmailMessage('Ferienmiete Straußäcker 3 Kontaktaufnahme/ Subtenancy Straußäcker 3 First Contact',
                                '<b>Do not answer directly to this Email!' +
                                '<br>Für eine Kontaktaufnahme bitte nicht auf diese Email direkt antworten, sondern auf die unten angegebene!</b><br><br>' + content,
                                '',
                                [subtenant.email])
            mail.content_subtype = "html"
            mail.send()

            mail = EmailMessage(
                'Bestätigung Ferienmiete Straußäcker 3 Kontaktaufnahme/ Subtenancy Straußäcker 3 First Contact Confirmation',
                '<b>Confirmation of the following first contact.' +
                '<br>Bestätigung folgender Kontaktaufnahme.</b><br><br>' + content,
                '',
                [request.user.email])
            mail.content_subtype = "html"
            mail.send()

            mail_admins(subject='ANALYSE contact_subtenant', message='Es gab eine Kontaktaufnahme!', fail_silently=True)

        except SMTPException as e:
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
    Maintennat querys requests
    """

    context = {}
    subtenants = SubTenant.objects.filter(user__is_active=True, is_searching=True)

    default = {
        'begin': subtenants.earliest('begin_request').begin_request,
        'end': subtenants.latest('end_request').end_request
    }

    if request.method == 'GET':
        form = RequestQueryForm(initial=default)
        context['get'] = True
    else:
        form = RequestQueryForm(request.POST)
        if form.is_valid():
            messages.success(request, _('Anfrageliste erfolgreich gefiltert'))
            context['object_list'] = subtenants.filter(begin_request__gte=form.cleaned_data.get('begin'),
                                                       end_request__lte=form.cleaned_data.get('end')).order_by(
                'begin_request',
                'end_request')

    # if GET or form is not valid return whole list
    if request.method == 'GET' or not form.is_valid():
        context['object_list'] = subtenants.filter(end_request__gt=datetime.datetime.now()).order_by(
            'begin_request',
            'end_request')

    context['title'] = _('Anfragenliste')
    context['form'] = form

    return render(request, 'tenants/requests.html', context)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def create_feedback(request):
    """
    User sends feedback that is stored in the database and send as Email to the admins.
    """

    context = {}

    if request.method == 'GET':
        form = FeedbackForm()
        context['get'] = True
    else:
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()
            content = get_template('tenants/feedback_email.html').render({'feedback': feedback})
            mail_admins(subject='Ferienmiete Straußäcker 3 Neues Feedback', message=content, fail_silently=True,
                        html_message=content)

            messages.success(request, _('Danke für dein Feedback!'))
            return redirect('Index')

    context['title'] = _('Feedback senden')
    context['form'] = form

    return render(request, 'tenants/feedback.html', context)


@login_required()
@permission_required(['tenants.view_halloffame'])
@require_GET
def hall_of_fame(request):
    """
    Displays the blacklist containing all blocked tenant ids and student ids.
    """

    query = HallOfFame.objects.all()

    context = {}
    context['title'] = 'Hall of Fame'
    context['hall'] = query

    if not query:
        messages.info(request, 'Die Hall of Fame ist leider leer!')

    return render(request, 'tenants/hall_of_fame.html', context)
