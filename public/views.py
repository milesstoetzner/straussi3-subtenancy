from django.shortcuts import render
from django.views.generic import CreateView, ListView
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, SubTenantForm
from django.contrib.messages.views import SuccessMessageMixin

import datetime


class MainTenantCreate(SuccessMessageMixin, CreateView):
    model = MainTenant
    form_class = MainTenantForm
    form_class.use_required_attribute = False

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


class SubTenantCreate(SuccessMessageMixin, CreateView):
    model = SubTenant
    form_class = SubTenantForm
    form_class.use_required_attribute = False

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
    template_name = 'public/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(active='Ja', end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


def Index(request):
    return render(request, 'public/index.html')


def Impressum(request):
    return render(request, 'public/impressum.html')