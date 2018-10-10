from django.views.generic import CreateView, ListView, UpdateView, DetailView
from .models import Contract
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, MainTenantUpdateForm, SubTenantForm, SubTenantUpdateForm
from .forms import ContractForm, ContractUpdateForm
from django.contrib.messages.views import SuccessMessageMixin


# TODO: authenticated and residential home scope! view, create, update, delete of contracts and main-/subtenants

# TODO: display rent?!
# TODO: display donation?!
class ContractCreate(SuccessMessageMixin, CreateView):
    model = Contract
    form_class = ContractForm
    form_class.use_required_attribute = False

    # TODO: success url zur pdf
    # TODO: message ändern
    success_url = '/'
    success_message = 'Vertrag erfolgreich erstellt!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractList(ListView):
    template_name = 'private/contract_list.html'

    def get_queryset(self):
        return Contract.objects.all().order_by('-id')


class ContractUpdate(SuccessMessageMixin, UpdateView):
    model = Contract
    form_class = ContractUpdateForm
    template_name = 'private/contract_update_form.html'

    success_message = 'Änderungen erfolgreich übernommen!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


def ContractPreview(request):
    pass


class Assistant(ListView):
    template_name = 'private/assistent.html'

    def get_queryset(self):
        return SubTenant.objects.all()


# OPTIMIZATION: not hardcoded view
class MainTenantList(ListView):
    template_name = 'private/maintenant_list.html'

    def get_queryset(self):
        return MainTenant.objects.all().order_by('-id')


class MainTenantUpdate(SuccessMessageMixin, UpdateView):
    model = MainTenant
    form_class = MainTenantUpdateForm
    template_name = 'private/maintenant_update_form.html'

    success_message = 'Änderungen erfolgreich übernommen!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


# OPTIMIZATION: not hardcoded view
class SubTenantList(ListView):
    template_name = 'private/subtenant_list.html'

    def get_queryset(self):
        return SubTenant.objects.all().order_by('-id')


class SubTenantUpdate(SuccessMessageMixin, UpdateView):
    model = SubTenant
    form_class = SubTenantUpdateForm
    template_name = 'private/subtenant_update_form.html'

    success_message = 'Änderungen erfolgreich übernommen!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context
