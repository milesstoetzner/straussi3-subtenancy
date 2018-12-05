from django.db.transaction import atomic
from subtenancy.utils import get_verbose_changed_data
from django.views.generic import ListView
from tenants.models import User, MainTenant, SubTenant, BlockedTenantID, BlockedStudentID
from tenants.forms import UserForm, UserUpdateForm, MainTenantForm, MainTenantUpdateForm, SubTenantForm, \
    SubTenantUpdateForm
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.db.models import ProtectedError
from django.contrib import messages
from django.core.mail import EmailMessage
from smtplib import SMTPException
from .faq import faq_subtenant, faq_maintenant

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

            # TODO: add to groupe

            tenant = tenant_form.save(False)
            tenant.user = user
            tenant.save()

            messages.success(request, 'Registrierung war erfolgreich. Du kannst dich nun einloggen')
            messages.success(request,
                             'Bei Kommunikation mit unserer Sprechstunde gebe bitte immer deine ID an. Deine ID lautet: ' + str(
                                 user.pk))
            return redirect(reverse('login'))

    context['title'] = 'Hauptmieter Registrierung' if is_maintenant else 'Untermieter Registrierung'
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
    context['title'] = str(request.user)

    if request.user.is_maintenant or request.user.is_subtenant:
        context['tenant_form'] = MainTenantUpdateForm(
            instance=request.user.maintenant) if request.user.is_maintenant else SubTenantUpdateForm(
            instance=request.user.subtenant)

    return render(request, 'tenants/view.html', context)


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

    # TODO: update own profile

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

                changes_user = get_verbose_changed_data(user_form.changed_data, User)
                changes_tenant = get_verbose_changed_data(tenant_form.changed_data,
                                                          MainTenant if tenant.is_maintenant else SubTenant)

                user_form.save()
                tenant_form.save()

                messages.success(request, 'Änderungen wurden erfolgreich übernommen!')
                messages.success(request,
                                 "Folgende Felder wurden geändert: %s." % ", ".join(changes_user + changes_tenant))

            else:
                messages.info(request, 'Es gab keine Änderungen!')

            return redirect(reverse('tenants:TenantView', kwargs={'pk': tenant.pk}))

    context['title'] = str(tenant) + ' aktualisieren'
    context['user_form'] = user_form
    context['tenant_form'] = tenant_form
    context['tenant'] = tenant

    return render(request, 'tenants/update.html', context)


@atomic
@csrf_protect
@login_required
@permission_required(['tenants.delete_own'])
@require_http_methods(['GET', 'POST'])
def delete_tenant(request, pk):
    """
    Deletes a user and his corresponding maintenant/subtenant iff no contracts exist.
    """

    # tenant can only delete his account
    if request.user.id != pk:
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=pk)

    if request.method == 'GET':
        # Asks for consent

        context = {}
        context['tenant'] = user
        context['title'] = str(user) + ' löschen'
        return render(request, 'tenants/delete.html', context)

    else:
        # Deletes the user and his correspoding maintenant/subtenant iff no contracts exist.

        try:
            user.delete()
        except ProtectedError:
            messages.error(request,
                           'Der Account kann nicht gelöscht werden. Das ist beispielsweise der Fall, wenn mindestens ein Vertrag mit diesem Account abgeschlossen wurde!')
            return redirect(reverse('Profile'))

        messages.success(request, 'Der Account wurde erfolgreich gelöscht!')
        return redirect('Index')


@csrf_protect
@login_required
@permission_required('tenants.contact_subtenant')
@require_http_methods(['GET', 'POST'])
def contact_tenant(request, pk):
    """
    A maintenant can send an active searching subtenant an email containing his contact details.
    """

    tenant = get_object_or_404(User, pk=pk)

    # only subtenants can be contacted
    if not tenant.is_subtenant:
        return HttpResponseForbidden()

    # only searching subtenants can be contacted
    if not tenant.subtenant.is_searching:
        return HttpResponseForbidden()

    # only active subtenants can be contacted
    if not tenant.is_active:
        return HttpResponseForbidden()

    # email content
    msg = '<b>Nicht auf diese Email antworten!</b><br><br>' + 'Hey,<br><br>ich interessiere mich für deine Anfrage in dem Zeitraum ' + str(
        tenant.subtenant.begin_subtenancy) + ' bis ' + str(
        tenant.subtenant.end_subtenancy) + '.<br>Du kannst mich über folgende Email kontaktieren: ' + tenant.email + '<br><br>Grüße,<br>' + str(
        tenant)

    if request.method == 'GET':
        # Asks for consent

        context = {}
        context['tenant'] = tenant
        context['title'] = 'Kontaktaufnahme'
        context['msg'] = msg
        return render(request, 'tenants/contact.html', context)

    else:
        # Sends email with maintenant's contact details to the subtenant

        try:
            mail = EmailMessage('Ferienmiete Straußäcker 3 Kontaktaufnahme',
                                msg,
                                'HmjyGTxWRP1vtcLT@web.de',  # DEP: change email
                                [tenant.email])
            mail.content_subtype = "html"
            mail.send()

            mail = EmailMessage('Bestätigung Ferienmiete Straußäcker 3 Kontaktaufnahme',
                                '<b>Bestätigung folgender Kontaktaufnahme:</b><br><br>' + msg,
                                'HmjyGTxWRP1vtcLT@web.de',  # DEP: change email
                                [request.user.email])
            mail.content_subtype = "html"
            mail.send()

        except SMTPException as e:
            messages.error(request, 'Untermieter konnte nicht kontaktiert werden!')
            return redirect('Requests')

        messages.success(request, 'Untermieter wurde erfolgreich kontaktiert! Wir haben dir als Bestätigung der Kontaktaufnahme eine Email gesendet.')
        return redirect('Requests')


@login_required()
@permission_required(['tenants.view_blockedtenantid', 'tenants.view_blockedstudentid'])
@require_GET
def blacklist(request):
    """
    Displays the blacklist containing all blocked tenant ids and student ids.
    """

    context = {}
    context['title'] = 'Schwarze Liste'
    context['tenant_ids'] = BlockedTenantID.objects.all()
    context['student_ids'] = BlockedStudentID.objects.all()

    return render(request, 'tenants/blacklist.html', context)


class Requests(ListView):
    """
    Displays a list of all subtenants' requests.
    """

    title = 'Anfragen von Untermietern'
    template_name = 'tenants/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(user__is_active=True, is_searching=True,
                                        end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy',
                                                                                             'end_subtenancy')


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
