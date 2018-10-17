from django.shortcuts import render
from django.views.generic import CreateView, ListView
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, SubTenantForm
from django.contrib.messages.views import SuccessMessageMixin

import datetime


# OPTIMIZE: send email with id to main tenant
class MainTenantCreate(SuccessMessageMixin, CreateView):
    model = MainTenant
    title = 'Hauptmieter Registrierung'
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


class Requests(ListView):
    title = 'Anfragenliste'
    template_name = 'public/requests.html'
    max_width = '600px'

    def get_queryset(self):
        return SubTenant.objects.filter(active='Ja', end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


def Index(request):
    return render(request, 'public/index.html', {'title': 'Startseite', 'max_width': '600px'})


def Impressum(request):
    return render(request, 'public/impressum.html', {'title': 'Impressum', 'max_width': '600px'})