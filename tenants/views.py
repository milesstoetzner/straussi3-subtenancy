from django.shortcuts import render
from django.views.generic import CreateView, ListView
from tenants.models import User, MainTenant, SubTenant
from tenants.forms import UserForm, MainTenantForm, SubTenantForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

import datetime


@csrf_protect
@require_http_methods(["GET", "POST"])
def create_maintenant(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        maintenant_form = MainTenantForm(request.POST)

        if user_form.is_valid() and maintenant_form.is_valid():
            user = user_form.save(False)
            user.is_maintenant = True
            user.save()

            maintenant = maintenant_form.save(False)
            maintenant.user = user
            maintenant.save()

            return redirect(reverse('Index'))

    else:
        user_form = UserForm()
        maintenant_form = MainTenantForm()

    return render(request, 'tenants/tenant_form.html', {'user_form': user_form, 'maintenant_form': maintenant_form})


# OPTIMIZE: send email with id to main tenant
class MainTenantCreate(SuccessMessageMixin, CreateView):
    model = MainTenant
    title = 'Hauptmieter Registrierung'
    template_name = 'tenants/tenant_form.html'
    form_class = MainTenantForm
    form_class.use_required_attribute = False
    max_width = '600px'

    success_url = '/'
    success_message = 'Du hast dich erfolgreich als Hauptmieter registriert. Deine ID lautet: %(pk)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            pk=self.object.pk,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True
        return context


# OPTIMIZE: send email with id to sub tenant
class SubTenantCreate(SuccessMessageMixin, CreateView):
    model = SubTenant
    title = 'Untemieter Registrierung'
    template_name = 'tenants/tenant_form.html'
    form_class = SubTenantForm
    form_class.use_required_attribute = False
    max_width = '600px'

    success_url = '/'
    success_message = 'Du hast dich erfolgreich als Untermieter registriert. Deine ID lautet: %(pk)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            pk=self.object.pk,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True
        return context


class Offers(ListView):
    title = 'Angebote von Hauptmietern'
    template_name = 'tenants/requests.html'
    max_width = '600px'

    def get_queryset(self):
        return MainTenant.objects.filter(user__is_active=True, end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


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