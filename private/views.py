from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from .models import Contract
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, SubTenantForm
from .forms import ContractForm

# TODO: authenticated and residential home scope! view, create, update, delete of contracts and main-/subtenants


class ContractCreate(CreateView):
    model = Contract
    form_class = ContractForm
    form_class.use_required_attribute = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


def Assistant(request):
    return render(request, 'private/assistent.html')


class MainTenantList(ListView):
    template_name = 'private/maintenant_list.html'

    def get_queryset(self):
        return MainTenant.objects.all()


class MainTenantUpdate(UpdateView):
    model = MainTenant
    form_class = MainTenantForm
    template_name = 'private/maintenant_update_form.html'

    # add success url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context