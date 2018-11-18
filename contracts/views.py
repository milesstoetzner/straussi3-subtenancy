import contracts, os
from django.apps import apps
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import View, CreateView, ListView, UpdateView, DetailView
from .models import Contract
from tenants.models import MainTenant, SubTenant
from .forms import ContractForm, ContractUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

import json
import datetime

from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required

from django.http import HttpResponse
from .utils import render_to_pdf

# TODO: permissions einführen - nicht über flags


# TODO: display maintenant details und subtenant details
class ContractCreate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Contract
    title = 'Vertrag erstellen'
    template_name = 'contracts/create.html'
    form_class = ContractForm
    form_class.use_required_attribute = False
    permission_required = 'contracts.add_contract'
    max_width = '600px'

    # TODO: save contracts as pdf?

    def test_func(self):
        return self.request.user.is_assistant

    def form_valid(self, form):
        self.object = form.save()
        self.object.maintenant.is_searching = False
        self.object.maintenant.save()
        self.object.subtenant.is_searching = False
        self.object.subtenant.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('contracts:ContractRender', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Contract
    context_object_name = 'object'
    form_class = ContractUpdateForm
    template_name = 'contracts/view.html'
    http_method_names = 'get'
    max_width = '600px'

    def test_func(self):
        return self.request.user.is_assistant

    def get_success_url(self):
        return reverse_lazy('contracts:SubTenantView', args=(self.object.id,)) # TODO was?!

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(self.get_object())
        context['is_latest'] = self.object.is_latest()
        return context


class ContractUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Contract
    title = 'Vertrag ändern'
    form_class = ContractUpdateForm
    template_name = 'contracts/update.html'
    success_message = 'Änderungen erfolgreich übernommen!'
    max_width = '600px'

    def test_func(self):
        return self.request.user.is_assistant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractPreviewPDF(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Contract

    def test_func(self):
        return self.request.user.is_assistant

    def get(self, request, *args, **kwargs):
        data = {
            'contract': self.get_object()
        }
        pdf = render_to_pdf('contracts/contracts/' + self.get_object().maintenant.residential_home.short + '.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


# TODO: create contract templates
class ContractRenderPDF(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Contract

    def test_func(self):
        return self.request.user.is_assistant

    def post(self, request, *args, **kwargs):
        # TODO render new version of pdf
        # TODO set newest version in contract.version

        self.get_object().version += 1
        self.get_object().save()

        data = {
            'contract': self.get_object()
        }
        pdf = render_to_pdf('contracts/contracts/' + self.get_object().maintenant.residential_home.short + '.html', data)

        print('nach pdf')

        # filename = self.get_object().get_filename()
        # path = os.path.join(apps.get_app_config('contracts').path, 'contracts', filename)

        print('nach path')

        fs = FileSystemStorage()
        # fs.save('test.pdf', pdf)

        print('nach save')

        messages.success(request, 'PDF wurde erfolgreich erstellt!')
        return redirect(reverse('contracts:ContractView', args=(self.get_object().id,)))


class ContractViewPDF(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Contract

    def test_func(self):
        return self.request.user.is_assistant

    def get(self, request, *args, **kwargs):
        fs = FileSystemStorage()
        filename = self.get_object().get_filename(self.kwargs['v'])
        path = os.path.join(apps.get_app_config('contracts').path, 'contracts', filename)
        if fs.exists(path):
            with fs.open(path) as pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename=' + filename
                return response
        else:
            return HttpResponseNotFound()


class ContractsActive(LoginRequiredMixin, UserPassesTestMixin, ListView):
    title = 'Aktive Verträge'
    template_name = 'contracts/list.html'
    paginate_by = 50
    max_width = '100%'

    def test_func(self):
        return self.request.user.is_assistant or self.request.user.is_external or self.request.user.is_staff

    def get_queryset(self):
        return Contract.objects.filter(is_active=True, end__gte=datetime.datetime.now()) \
            .order_by('maintenant__residential_home', 'maintenant__house_number', 'maintenant__room_number')


class ContractsArchive(LoginRequiredMixin, UserPassesTestMixin, ListView):
    title = 'Archiv'
    template_name = 'contracts/list.html'
    paginate_by = 50
    max_width = '100%'

    def test_func(self):
        return self.request.user.is_assistant or self.request.user.is_external or self.request.user.is_staff

    def get_queryset(self):
        return Contract.objects.filter(is_active=True, end__lt=datetime.datetime.now()) \
            .order_by('maintenant__residential_home', 'maintenant__house_number', 'maintenant__room_number')


@csrf_protect
@login_required
@permission_required(['tenants.view_maintenant', 'tenants.view_subtenant', 'contracts.view_contract'])
@require_POST
def search(request):
    query = request.POST['query']

    # TODO: complex query! full name, birthday, tenant_id
    maintenants = MainTenant.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
    subtenants = SubTenant.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))

    # TODO: vertrag query hinzufügen

    context = {
        'maintenants': maintenants,
        'subtenants': subtenants,
        'contracts': {},
        'query': query
    }

    return render(request, 'contracts/search_result.html', context)


@login_required
@permission_required('tenants.view_maintenant')
def main_tenant_json(request, pk):
    obj = MainTenant.objects.get(pk=pk)
    data = serializers.serialize('json', [obj, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return HttpResponse(data, content_type='application/json')


@login_required
@permission_required('tenants.view_subtenant')
def sub_tenant_json(request, pk):
    obj = SubTenant.objects.get(pk=pk)
    data = serializers.serialize('json', [obj, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return HttpResponse(data, content_type='application/json')
