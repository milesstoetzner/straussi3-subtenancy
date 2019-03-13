from django.db.transaction import atomic
from tenants.models import User, SubTenant, Blacklist
from tenants.forms import UserForm, UserUpdateForm, MainTenantForm, MainTenantUpdateForm, SubTenantForm, \
    SubTenantUpdateForm, FeedbackForm, RequestUpdateForm
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.db.models import ProtectedError
from django.contrib import messages
from django.core.mail import EmailMessage, mail_admins
from smtplib import SMTPException
from django.views.generic import ListView
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template

import datetime


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

        user_form = UserForm()
        tenant_form = MainTenantForm() if is_maintenant else SubTenantForm()
        context['get'] = True

    else:
        # Validates the received form data.
        # If data of both forms are valid a new user and his corresponding maintenant/subtenant is created.

        user_form = UserForm(request.POST)
        tenant_form = MainTenantForm(request.POST) if is_maintenant else SubTenantForm(request.POST)

        if user_form.is_valid() and tenant_form.is_valid():
            user = user_form.save(False)
            user.is_maintenant = is_maintenant
            user.is_subtenant = not is_maintenant
            user.save()

            group_verbose = 'Maintenant' if is_maintenant else 'Subtenant'
            group = Group.objects.get(name=group_verbose)
            user.groups.add(group)

            tenant = tenant_form.save(False)
            tenant.user = user
            tenant.save()

            messages.success(request, _('Registrierung war erfolgreich. Du kannst dich nun einloggen.'))

            content = get_template('tenants/register_email.html').render({'user': user})
            mail = EmailMessage('Ferienmiete Straußäcker 3 Registrierung/ Subtenancy Straußäcker 3 Registration',
                                content,
                                '', [user.email])
            mail.content_subtype = "html"
            mail.send(fail_silently=True)

            return redirect(reverse('login'))

    context['title'] = _('Hauptmieter Registrierung') if is_maintenant else _('Untermieter Registrierung')
    context['user_form'] = user_form
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
    context['user_form'] = UserUpdateForm(instance=request.user)
    context['tenant'] = request.user
    context['title'] = _('Profil von') + ' ' + str(request.user)

    if request.user.is_maintenant or request.user.is_subtenant:
        context['tenant_form'] = MainTenantUpdateForm(
            instance=request.user.maintenant) if request.user.is_maintenant else SubTenantUpdateForm(
            instance=request.user.subtenant)

    return render(request, 'tenants/view.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.change_own'])
@require_http_methods(['GET', 'POST'])
def update_profile(request):
    """
    Updates the details about a user and his corresponding maintenant/subtenant.
    NOTE: this is copy and pasted (and adjusted) from update_tenant
    """

    context = {}

    tenant = request.user

    if request.method == 'GET':
        # Displays the two forms: user creation form and maintenant/subtenant creation form

        user_form = UserUpdateForm(instance=tenant)
        tenant_form = MainTenantUpdateForm(instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            instance=tenant.subtenant)
        context['get'] = True

    else:
        # Validates the received form data.
        # Iff the data of both forms are valid and there had been changes, the changes will be saved to the database.

        user_form = UserUpdateForm(request.POST, instance=tenant)
        tenant_form = MainTenantUpdateForm(request.POST,
                                           instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            request.POST, instance=tenant.subtenant)

        if user_form.is_valid() and tenant_form.is_valid():

            if user_form.has_changed() or tenant_form.has_changed():

                user_form.save()
                tenant_form.save()

                messages.success(request, _('Änderungen wurden erfolgreich übernommen!'))


            else:
                messages.info(request, _('Es gab keine Änderungen!'))

            return redirect(reverse('Profile'))

    context['title'] = _('Profil aktualisieren!')
    context['user_form'] = user_form
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
    Updates the details about a user and his corresponding maintenant/subtenant.
    NOTE: this is copy and pasted (and adjusted) from update_tenant
    """

    context = {}

    tenant = request.user

    # only tenants can be updated
    if not tenant.is_subtenant:
        return HttpResponseForbidden()

    subtenant = tenant.subtenant

    if request.method == 'GET':

        form = RequestUpdateForm(instance=subtenant)
        context['get'] = True

    else:

        form = RequestUpdateForm(request.POST, instance=subtenant)

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
        # Asks for consent

        context = {}
        context['tenant'] = user
        context['title'] = _('Account löschen')
        return render(request, 'tenants/delete.html', context)

    else:
        # Deletes the user and his corresponding maintenant/subtenant iff no contracts exist.

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
    Displays the details about a user and his corresponding maintenant/subtenant.
    """

    tenant = get_object_or_404(User, pk=pk)

    context = {}
    context['get'] = True
    context['user_form'] = UserUpdateForm(instance=tenant)
    context['tenant'] = tenant
    context['title'] = str(tenant)

    if tenant.is_maintenant:
        messages.info(request, 'Der Zeitraum der Verträge mit diesem Hauptmieter beträgt ' + str(
            tenant.maintenant.get_amount_of_days()) + ' Tage!')

    if tenant.is_maintenant or tenant.is_subtenant:
        context['tenant_form'] = MainTenantUpdateForm(
            instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(instance=tenant.subtenant)
        context['is_maintenant'] = tenant.is_maintenant

    return render(request, 'tenants/view.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.change_user', 'tenants.change_maintenant', 'tenants.change_subtenant'])
@require_http_methods(['GET', 'POST'])
def update_tenant(request, pk):
    """
    Updates the details about a user and his corresponding maintenant/subtenant.
    """

    context = {}

    tenant = get_object_or_404(User, pk=pk)

    # only tenants can be updated
    if not (tenant.is_maintenant or tenant.is_subtenant):
        return HttpResponseForbidden()

    if request.method == 'GET':
        # Displays the two forms: user creation form and maintenant/subtenant creation form

        user_form = UserUpdateForm(instance=tenant)
        tenant_form = MainTenantUpdateForm(instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            instance=tenant.subtenant)
        context['get'] = True

    else:
        # Validates the received form data.
        # Iff the data of both forms are valid and there had been changes, the changes will be saved to the database.

        user_form = UserUpdateForm(request.POST, instance=tenant)
        tenant_form = MainTenantUpdateForm(request.POST,
                                           instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            request.POST, instance=tenant.subtenant)

        if user_form.is_valid() and tenant_form.is_valid():

            if user_form.has_changed() or tenant_form.has_changed():

                user_form.save()
                tenant_form.save()

                messages.success(request, _('Änderungen wurden erfolgreich übernommen!'))

            else:
                messages.info(request, 'Es gab keine Änderungen!')

            return redirect(reverse('tenants:TenantView', kwargs={'pk': tenant.pk}))

    context['title'] = _('%(tenant)s aktualisieren!') % {'tenant': str(tenant)}
    context['user_form'] = user_form
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

    subtenant = get_object_or_404(User, pk=pk)

    # only subtenants can be contacted
    if not subtenant.is_subtenant:
        return HttpResponseForbidden()

    # only searching subtenants can be contacted
    if not subtenant.subtenant.is_searching:
        return HttpResponseForbidden()

    # only active subtenants can be contacted
    if not subtenant.is_active:
        return HttpResponseForbidden()

    # email content
    content = get_template('tenants/contact_email.html').render({'user': request.user, 'subtenant': subtenant})

    if request.method == 'GET':
        # Asks for consent

        context = {}
        context['subtenant'] = subtenant
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

        except SMTPException as e:
            print(e)
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

    context = {}
    context['title'] = _('Schwarze Liste')
    context['blacklist'] = Blacklist.objects.all()

    if not blacklist:
        messages.info(request, _('Die schwarze Liste ist leer!'))

    return render(request, 'tenants/blacklist.html', context)


class Requests(ListView):
    """
    Displays a list of all subtenants' requests.
    """

    title = _('Anfragen von Untermietern')
    template_name = 'tenants/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(user__is_active=True, is_searching=True,
                                        end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy',
                                                                                             'end_subtenancy')


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
