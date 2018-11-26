from django.db.transaction import atomic
from subtenancy.utils import is_assistant, is_maintenant, is_tenant, get_verbose_changed_data
from django.views.generic import ListView
from tenants.models import User, MainTenant, SubTenant, BlockedTenantID, BlockedStudentID
from tenants.forms import UserForm, UserUpdateForm, MainTenantForm, MainTenantUpdateForm, SubTenantForm, \
    SubTenantUpdateForm
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.db.models import ProtectedError
from django.contrib import messages
from django.core.mail import EmailMessage
from smtplib import SMTPException
from .faq import faq_subtenant, faq_maintenant

import datetime


@atomic
@csrf_protect
@require_http_methods(["GET", "POST"])
def create_tenant(request, is_maintenant):
    context = {}

    if request.method == 'GET':

        user_form = UserForm()
        tenant_form = MainTenantForm() if is_maintenant else SubTenantForm()
        context['get'] = True

    else:

        user_form = UserForm(request.POST)
        tenant_form = MainTenantForm(request.POST) if is_maintenant else SubTenantForm(request.POST)

        if user_form.is_valid() and tenant_form.is_valid():
            user = user_form.save(False)
            user.is_maintenant = is_maintenant
            user.is_subtenant = not is_maintenant
            user.save()

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
@user_passes_test(is_assistant)
@require_GET
def view_tenant(request, pk):
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
@require_http_methods(["GET", "POST"])
def update_tenant(request, pk):
    context = {}

    # only assistants or the owner can update tenant
    if not request.user.is_assistant and request.user.id != pk:
        return HttpResponseForbidden()

    tenant = get_object_or_404(User, pk=pk)

    # only tenants can be updated
    if not (tenant.is_maintenant or tenant.is_subtenant):
        return HttpResponseForbidden()

    if request.method == 'GET':

        # display update form
        user_form = UserUpdateForm(instance=tenant)
        tenant_form = MainTenantUpdateForm(instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            instance=tenant.subtenant)
        context['get'] = True

    else:

        # validate and save tenant
        user_form = UserUpdateForm(request.POST, instance=tenant)
        tenant_form = MainTenantUpdateForm(request.POST,
                                           instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            request.POST, instance=tenant.subtenant)

        if user_form.is_valid() and tenant_form.is_valid():

            if user_form.has_changed() or tenant_form.has_changed():

                changes_user = get_verbose_changed_data(user_form.changed_data, User)
                changes_tenant = get_verbose_changed_data(tenant_form.changed_data, MainTenant if tenant.is_maintenant else SubTenant)

                user_form.save()
                tenant_form.save()

                messages.success(request, 'Änderungen wurden erfolgreich übernommen!')
                messages.success(request, "Folgende Felder wurden geändert: %s." % ", ".join(changes_user + changes_tenant))

            else:
                messages.info(request, 'Es gab keine Änderungen!')

            if request.user.is_assistant:
                return redirect(reverse('tenants:TenantView', kwargs={'pk': tenant.pk}))
            else:
                return redirect(reverse('Profile'))

    context['title'] = str(tenant) + ' aktualisieren'
    context['user_form'] = user_form
    context['tenant_form'] = tenant_form
    context['tenant'] = tenant

    return render(request, 'tenants/update.html', context)


@atomic
@csrf_protect
@login_required
@user_passes_test(is_tenant)
@require_http_methods(["GET", "POST"])
def delete_tenant(request, pk):

    # tenant can only delete his account
    if request.user.id != pk:
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=pk)

    if request.method == 'GET':

        context = {}
        context['tenant'] = user
        context['title'] = str(user) + ' löschen'
        return render(request, 'tenants/delete.html', context)

    else:

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
@user_passes_test(is_maintenant)
@require_http_methods(["GET", "POST"])
def contact_tenant(request, pk):
    tenant = get_object_or_404(User, pk=pk)

    # only subtenants can be contacted
    if not tenant.is_subtenant:
        return HttpResponseForbidden()

    # only searching subtenants can be contacted
    if not tenant.subtenant.is_searching:
        return HttpResponseForbidden()

    # email content
    msg = 'Hey,<br><br>'
    msg += 'ich interessiere mich für dein Angebot in dem Zeitraum ' + str(
        tenant.subtenant.begin_subtenancy) + ' bis ' + str(tenant.subtenant.end_subtenancy) + '.'
    msg += '<br>Du kannst mich über folgende Email kontaktieren: ' + tenant.email
    msg += '<br><br>Grüße,<br>' + str(tenant)

    if request.method == 'GET':

        # ask for consent
        context = {}
        context['tenant'] = tenant
        context['title'] = 'Kontaktaufnahme'
        context['msg'] = msg
        return render(request, 'tenants/contact.html', context)

    else:
        try:
            mail = EmailMessage('Ferienmiete Straußäcker 3 Kontaktaufnahme',
                                msg,
                                'HmjyGTxWRP1vtcLT@web.de',
                                [tenant.email])
            mail.content_subtype = "html"
            mail.send()

        except SMTPException as e:
            messages.error(request, 'Untermieter konnte nicht kontaktiert werden!')
            return redirect('Requests')

        messages.success(request, 'Untermieter wurde erfolgreich kontaktiert!')
        return redirect('Requests')


class Requests(ListView):
    title = 'Anfragen von Untermietern'
    template_name = 'tenants/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(is_searching=True, end_subtenancy__gt=datetime.datetime.now()).order_by(
            'begin_subtenancy', 'end_subtenancy')


@login_required()
@user_passes_test(is_assistant)
@require_GET
def blacklist(request):
    context = {}
    context['title'] = 'Schwarze Liste'
    context['tenant_ids'] = BlockedTenantID.objects.all()
    context['student_ids'] = BlockedStudentID.objects.all()

    return render(request, 'tenants/blacklist.html', context)


def index(request):
    return render(request, 'tenants/index.html',
                  {'title': 'Ferienmiete Straußäcker 3', 'faq_maintenant': faq_maintenant,
                   'faq_subtenant': faq_subtenant})


def legal_notice(request):
    return render(request, 'tenants/legal_notice.html', {'title': 'Impressum'})
