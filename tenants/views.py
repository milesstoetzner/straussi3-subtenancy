from django.shortcuts import render
from django.views.generic import CreateView, ListView
from tenants.models import User, MainTenant, SubTenant
from tenants.forms import UserForm, UserUpdateForm, MainTenantForm, MainTenantUpdateForm, SubTenantForm, SubTenantUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound

import datetime


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

            # OPTIMIZE: send email with id to main tenant and email verification

            # add message with id
            return redirect(reverse('login'))

    else:
        user_form = UserForm()
        tenant_form = MainTenantForm() if is_maintenant else SubTenantForm()
        context['get'] = True

    context['title'] = 'Hauptmieter Registrierung' if is_maintenant else 'Untermieter Registrierung'
    context['max_width'] = '600px'
    context['user_form'] = user_form
    context['tenant_form'] = tenant_form
    context['main'] = is_maintenant

    return render(request, 'tenants/create.html', context)


@login_required
@require_http_methods(["GET"])
def view_tenant(request, pk):
    context = {}
    context['max_width'] = '600px'
    context['get'] = True

    if not request.user.is_staff and request.user.id != pk:
        return HttpResponseForbidden()

    user = User.objects.get(pk=pk)

    context['user_form'] = UserUpdateForm(instance=user)
    context['title'] = user.first_name + ' ' + user.last_name
    context['main'] = user.is_maintenant
    context['update_url'] = user.get_update_url()

    if not user.is_staff:
        context['tenant_form'] = MainTenantUpdateForm(instance=user.maintenant) if user.is_maintenant else SubTenantUpdateForm(instance=user.subtenant)

    return render(request, 'tenants/view.html', context)


# TODO: update_tenant route
@csrf_protect
@require_http_methods(["GET", "POST"])
def update_tenant(request, pk):

    context = {}

    if not request.user.is_staff and request.user.id != pk:
        return HttpResponseForbidden()

    user = User.objects.get(pk=pk)

    if not user.is_maintenant and not user.is_subtenant:
        return HttpResponseForbidden()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        tenant_form = MainTenantUpdateForm(request.POST, instance=user.maintenant) if user.is_maintenant else SubTenantUpdateForm(request.POST, instance=user.subtenant)

        if user_form.is_valid() and tenant_form.is_valid():
            user_form.save()
            tenant_form.save()

            # TODO: add message
            return redirect(reverse('tenants:TenantView', kwargs={'pk': user.pk}))

    else:
        user_form = UserUpdateForm(instance=user)
        tenant_form = MainTenantUpdateForm(instance=user.maintenant) if user.is_maintenant else SubTenantUpdateForm(instance=user.subtenant)
        context['get'] = True

    context['title'] = 'Informationen Aktualisieren'
    context['max_width'] = '600px'
    context['user_form'] = user_form
    context['tenant_form'] = tenant_form
    context['update_url'] = user.get_update_url()
    context['main'] = True

    return render(request, 'tenants/update.html', context)


# TODO: delete_tenant route
@csrf_protect
@require_http_methods(["POST"])
def delete_tenant(request, pk):

    if not request.user.is_staff and request.user.id != pk:
        return HttpResponseForbidden()

    User.objects.get(pk=pk).delete()
    # TODO: add message
    return redirect('Index')


class Offers(ListView):
    title = 'Angebote von Hauptmietern'
    template_name = 'tenants/requests.html'
    max_width = '600px'

    def get_queryset(self):
        return MainTenant.objects.filter(is_searching=True, end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


class Requests(ListView):
    title = 'Anfragen von Untermietern'
    template_name = 'tenants/requests.html'
    max_width = '600px'

    def get_queryset(self):
        return SubTenant.objects.filter(user__is_active=True, end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


def index(request):
    return render(request, 'tenants/index.html', {'title': 'Startseite', 'max_width': '600px'})


def legal_notice(request):
    return render(request, 'tenants/legal_notice.html', {'title': 'Impressum', 'max_width': '600px'})