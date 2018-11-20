from django.views.generic import CreateView, ListView
from tenants.models import User, MainTenant, SubTenant
from tenants.forms import UserForm, UserUpdateForm, MainTenantForm, MainTenantUpdateForm, SubTenantForm, \
    SubTenantUpdateForm
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import ProtectedError
from django.contrib import messages
from django.core.mail import EmailMessage
from smtplib import SMTPException
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin

import datetime


def is_assistant(user):
    return user.is_assistant

# TODO: authorization using permissions or user flags?


@csrf_protect
@require_http_methods(["GET", "POST"])
def create_tenant(request, is_maintenant):
    context = {}

    if request.method == 'POST':
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
            messages.success(request, 'Bei Kommunikation mit unserer Sprechstunde gebe bitte immer deine ID an. Deine ID lautet: ' + str(user.pk))
            return redirect(reverse('login'))

    else:
        user_form = UserForm()
        tenant_form = MainTenantForm() if is_maintenant else SubTenantForm()
        context['get'] = True

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
            instance=request.user.maintenant) if request.user.is_maintenant else SubTenantUpdateForm(instance=request.user.subtenant)

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

    if tenant.is_maintenant or tenant.is_subtenant:
        context['tenant_form'] = MainTenantUpdateForm(
            instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(instance=tenant.subtenant)

    return render(request, 'tenants/view.html', context)


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

    if request.method == 'POST':

        # validate and save tenant
        user_form = UserUpdateForm(request.POST, instance=tenant)
        tenant_form = MainTenantUpdateForm(request.POST,
                                           instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            request.POST, instance=tenant.subtenant)

        if user_form.is_valid() and tenant_form.is_valid():
            user_form.save()
            tenant_form.save()

            messages.success(request, 'Änderungen wurden erfoglreich übernommen!')
            return redirect(reverse('tenants:TenantView', kwargs={'pk': tenant.pk}))

    else:

        # display update form
        user_form = UserUpdateForm(instance=tenant)
        tenant_form = MainTenantUpdateForm(instance=tenant.maintenant) if tenant.is_maintenant else SubTenantUpdateForm(
            instance=tenant.subtenant)
        context['get'] = True

    context['title'] = str(tenant) + ' aktualisieren'
    context['user_form'] = user_form
    context['tenant_form'] = tenant_form
    context['tenant'] = tenant

    return render(request, 'tenants/update.html', context)


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def delete_tenant(request, pk):

    # only tenant can delete his account
    if not (request.user.is_maintenant or request.user.is_subtenant) and request.user.id != pk:
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        try:
            user.delete()
        except ProtectedError:
            messages.error(request, 'Der Account kann nicht gelöscht werden. Das ist beispielsweise der Fall, wenn mindestens ein Vertrag mit diesem Account abgeschlossen wurde!')
            return redirect(reverse('tenants:TenantView', kwargs={'pk': user.pk}))

        messages.success(request, 'Der Account wurde erfolgreich gelöscht!')
        return redirect('Index')

    else:
        context = {}
        context['tenant'] = user
        context['title'] = str(user) + ' löschen'
        return render(request, 'tenants/delete.html', context)


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def contact_tenant(request, pk):

    tenant = get_object_or_404(User, pk=pk)

    # only tenants can be contacted
    if not (tenant.is_maintenant or tenant.is_subtenant):
        return HttpResponseForbidden()

    # only searching maintenants can be contacted
    if tenant.is_maintenant and not tenant.maintenant.is_searching:
        return HttpResponseForbidden()

    # only searching subtenants can be contacted
    if tenant.is_subtenant and not tenant.subtenant.is_searching:
        return HttpResponseForbidden()

    # only tenants can contact each other
    if not (request.user.is_maintenant or request.user.is_subtenant):
        messages.error(request, 'Nur Mieter können sich kontaktieren!')
        if tenant.is_subtenant:
            return redirect('Requests')
        else:
            return redirect('Offers')

    # only maintenants can contact subtenants
    if tenant.is_maintenant and request.user.is_maintenant:
        messages.error(request, 'Als Hauptmieter kannst du keine Hautpmieter kontaktieren')
        return redirect('Offers')

    # only subtenants can contact maintenants
    if tenant.is_subtenant and request.user.is_subtenant:
        messages.error(request, 'Als Untermieter kannst du keine Untermieter kontaktieren')
        return redirect('Requests')

    # email content
    msg = 'Hey,<br><br>'
    if tenant.is_maintenant:
        msg += 'ich interessiere mich für dein Angebot in dem Zeitraum ' + str(
            tenant.maintenant.begin_subtenancy) + ' bis ' + str(tenant.maintenant.end_subtenancy) + '.'
    else:
        msg += 'ich interessiere mich für dein Angebot in dem Zeitraum ' + str(
            tenant.subtenant.begin_subtenancy) + ' bis ' + str(tenant.subtenant.end_subtenancy) + '.'
    msg += '<br>Du kannst mich über folgende Email kontaktieren: ' + tenant.email
    msg += '<br><br>Grüße,<br>' + str(tenant)

    if request.method == 'POST':

        try:
            mail = EmailMessage('Ferienmiete Straußäcker 3 Kontaktaufnahme',
                msg,
                'HmjyGTxWRP1vtcLT@web.de',
                [tenant.email])
            mail.content_subtype = "html"
            mail.send()

        except SMTPException as e:
            if tenant.is_subtenant:
                messages.error(request, 'Untermieter konnte nicht kontaktiert werden!')
                return redirect('Requests')
            else:
                messages.error(request, 'Hauptmieter konnte nicht kontaktiert werden!')
                return redirect('Offers')

        if tenant.is_subtenant:
            messages.success(request, 'Untermieter wurde erfolgreich kontaktiert!')
            return redirect('Requests')
        else:
            messages.success(request, 'Hauptmieter wurde erfolgreich kontaktiert!')
            return redirect('Offers')

    else:

        # ask for consent
        context = {}
        context['tenant'] = tenant
        context['title'] = 'Kontaktaufnahme'
        context['msg'] = msg
        return render(request, 'tenants/contact.html', context)


class PasswordChange(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_message = 'Passwort wurde erfolgreich geändert!'

    def get_success_url(self):
        return redirect(self.request.user.get_absolute_url())


class PasswordReset(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    success_message = 'Wir haben eine E-Mail zum Zurücksetzen des Passwortes an die angegebene E-Mail-Adresse gesendet, sofern ein entsprechendes Konto existiert. Sie sollte in Kürze ankommen. Falls die E-Mail nicht angekommen sein sollte, bitte die E-Mail-Adresse auf Richtigkeit und gegebenenfalls den Spam-Ordner überprüfen.'
    success_url = '/'


class Offers(ListView):
    title = 'Angebote von Hauptmietern'
    template_name = 'tenants/requests.html'

    def get_queryset(self):
        return MainTenant.objects.filter(is_searching=True, end_subtenancy__gt=datetime.datetime.now()).order_by(
            'begin_subtenancy', 'end_subtenancy')


class Requests(ListView):
    title = 'Anfragen von Untermietern'
    template_name = 'tenants/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(is_searching=True, end_subtenancy__gt=datetime.datetime.now()).order_by(
            'begin_subtenancy', 'end_subtenancy')


def index(request):
    return render(request, 'tenants/index.html', {'title': 'Startseite'})


def legal_notice(request):
    return render(request, 'tenants/legal_notice.html', {'title': 'Impressum'})
