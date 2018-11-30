import os
from django.db.transaction import atomic
from django.urls import reverse
from django.views.generic import ListView
from .models import Contract
from tenants.models import MainTenant, SubTenant
from .forms import ContractForm, ContractUpdateForm
from django.http import HttpResponseNotFound
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from subtenancy.utils import is_assistant, is_assistant_or_external, get_verbose_changed_data

import datetime

from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test

from django.http import HttpResponse
from .utils import html_to_pdf, save_html_as_pdf


@atomic
@csrf_protect
@login_required
@user_passes_test(is_assistant)
@require_http_methods(["GET", "POST"])
def create_contract(request):
    context = {}

    if request.method == 'GET':

        form = ContractForm()
        context['get'] = True

    else:

        form = ContractForm(request.POST)

        if form.is_valid():
            contract = form.save()
            form.instance.maintenant.is_searching = False
            form.instance.maintenant.save()
            form.instance.subtenant.is_searching = False
            form.instance.subtenant.save()

            messages.success(request, 'Vertrag wurde erfolgreich erstellt!')
            return redirect(contract.get_absolute_url())

    context['title'] = 'Vertrag erstellen'
    context['form'] = form

    return render(request, 'contracts/create.html', context)


@login_required
@user_passes_test(is_assistant)
@require_GET
def view_contract(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    context = {}
    context['form'] = ContractUpdateForm(instance=contract)
    context['title'] = str(contract)
    context['is_latest'] = contract.is_latest()

    return render(request, 'contracts/view.html', context)


@atomic
@csrf_protect
@login_required
@user_passes_test(is_assistant)
@require_http_methods(["GET", "POST"])
def update_contract(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    context = {}
    context['title'] = 'Vertrag ändern'

    if request.method == 'GET':
        context['get'] = True
        context['form'] = ContractUpdateForm(instance=contract)
    else:
        form = ContractUpdateForm(request.POST, instance=contract)
        if form.is_valid():
            if form.has_changed():

                changes = get_verbose_changed_data(form.changed_data, Contract)

                form.instance.is_changed = True
                form.save()

                messages.success(request, 'Änderungen erfolgreich übernommen!')
                messages.success(request, "Folgende Felder wurden geändert: %s." % ", ".join(changes))

            else:
                messages.info(request, 'Es gab keine Änderungen!')
            return redirect(reverse('contracts:ContractView', args=(contract.id, )))
        else:
            context['form'] = form
    return render(request, 'contracts/update.html', context)


@login_required
@user_passes_test(is_assistant)
@require_GET
def view_contract_pdf(request, pk, v):
    fs = FileSystemStorage()
    filename = 'contract_' + str(pk) + '_version_' + str(v) + '.pdf'
    path = os.path.join('contracts', 'contracts', filename)
    if fs.exists(path):
        with fs.open(path) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename=' + filename
            return response
    else:
        return HttpResponseNotFound()


@login_required
@user_passes_test(is_assistant)
@require_GET
def preview_contract_pdf(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    source = os.path.join('contracts', 'contracts', str(contract.maintenant.residential_home.short) + '.html')
    pdf = html_to_pdf(source, {'contract': contract})

    return HttpResponse(pdf, content_type='application/pdf')


@atomic
@csrf_protect
@login_required
@user_passes_test(is_assistant)
@require_POST
def save_contract_pdf(request, pk):

    contract = get_object_or_404(Contract, pk=pk)
    contract.version += 1

    source = os.path.join('contracts', 'contracts', str(contract.maintenant.residential_home.short) + '.html')
    destination = os.path.join('contracts', 'contracts', 'contract_' + str(contract.pk) + '_version_' + str(contract.version) + '.pdf')

    status = save_html_as_pdf(source, {'contract': contract}, destination)

    if status:
        contract.is_changed = False
        contract.save()
        messages.success(request, 'PDF wurde erfolgreich erstellt!')
    else:
        messages.error(request, 'PDF konnte nicht erstellt werden!')

    return redirect(reverse('contracts:ContractView', args=(contract.id,)))


class ContractsActive(LoginRequiredMixin, UserPassesTestMixin, ListView):
    title = 'Aktive Verträge'
    template_name = 'contracts/list.html'
    paginate_by = 50
    max_width = '100%'
    queryset = Contract.objects.filter(is_active=True, end__gte=datetime.datetime.now()) \
            .order_by('maintenant__residential_home', 'maintenant__house_number', 'maintenant__room_number')

    def test_func(self):
        return is_assistant_or_external(self.request.user)


class ContractsArchive(LoginRequiredMixin, UserPassesTestMixin, ListView):
    title = 'Archiv'
    template_name = 'contracts/list.html'
    paginate_by = 50
    max_width = '100%'
    queryset = Contract.objects.filter(Q(is_active=False) | Q(end__lt=datetime.datetime.now())) \
            .order_by('maintenant__residential_home', 'maintenant__house_number', 'maintenant__room_number')

    def test_func(self):
        return is_assistant_or_external(self.request.user)


@csrf_protect
@login_required
@user_passes_test(is_assistant)
@require_POST
def search(request):
    query = request.POST['query']

    try:
        query_int = int(query)
    except ValueError:
        query_int = -1

    try:
        d = datetime.datetime.strptime(query, '%d.%m.%Y')
        query_date = d.strftime('%Y-%m-%d')
    except ValueError:
        query_date = "1111-11-11"

    maintenants = MainTenant.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user_id=query_int) | Q(tenant_id=query_int) | Q(user__birthday=query_date))
    subtenants = SubTenant.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user_id=int(query_int)) | Q(student_id=query_int) | Q(user__birthday=query_date))
    contracts = Contract.objects.filter(Q(id=query_int) | Q(begin=query_date) | Q(end=query_date))

    context = {
        'maintenants': maintenants,
        'subtenants': subtenants,
        'contracts': contracts,
        'query': query
    }

    return render(request, 'contracts/search_result.html', context)
