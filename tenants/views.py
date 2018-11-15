from django.views.generic import CreateView, ListView
from tenants.models import User, MainTenant, SubTenant
from tenants.forms import UserForm, UserUpdateForm, MainTenantForm, MainTenantUpdateForm, SubTenantForm, \
    SubTenantUpdateForm
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import ProtectedError
from django.contrib import messages

import datetime

# TODO: permission using flags is shit


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

            # TODO: send email with id etc
            # TODO: need confirmation?

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
@require_http_methods(["GET"])
def view_tenant(request, pk):

    if not request.user.is_assistant and request.user.id != pk:
        return HttpResponseForbidden()

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
    if not request.user.is_staff and request.user.id != pk:
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=pk)

    if not (user.is_maintenant or user.is_subtenant):
        return HttpResponseForbidden()

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
        return HttpResponseForbidden()

    # only maintenants can contact subtenants
    if tenant.is_maintenant and request.user.is_maintenant:
        messages.error(request, 'Als Hauptmieter kannst du keine Hautpmieter kontaktieren')
        return redirect('Offers')

    # only subtenants can contact maintenants
    if tenant.is_subtenant and request.user.is_subtenant:
        messages.error(request, 'Als Untermieter kannst du keine Untermieter kontaktieren')
        return redirect('Requests')

    if request.method == 'POST':

        # send email
        # TODO: send contact email
        if request.user.is_maintenant:
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
        return render(request, 'tenants/contact.html', context)


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
