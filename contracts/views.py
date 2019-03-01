import datetime
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
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from .utils import html_to_pdf
from django.utils.translation import gettext_lazy as _


@atomic
@csrf_protect
@login_required
@permission_required('contracts.add_contract')
@require_http_methods(['GET', 'POST'])
def create_contract(request):
    """
    Creates a new contract and saves a PDF, iff the received form data is valid. This method is atomic.
    """
    context = {}

    if request.method == 'GET':
        # Displays the contract form

        form = ContractForm()
        context['get'] = True

    else:
        # Validates the received form data. If data is valid a new contract is saved to the database and as PDF.

        form = ContractForm(request.POST)

        if form.is_valid():
            contract = form.save()
            form.instance.maintenant.is_searching = False
            form.instance.maintenant.save()
            form.instance.subtenant.is_searching = False
            form.instance.subtenant.save()

            contract.save_contract_pdf()

            messages.success(request, _('Vertrag wurde erfolgreich erstellt!'))

            return redirect(contract.get_absolute_url())

    context['title'] = _('Vertrag erstellen')
    context['form'] = form

    return render(request, 'contracts/create.html', context)


@login_required
@permission_required('contracts.view_contract')
@require_GET
def view_contract(request, pk):
    """
    Displays a contract identified by a given primary key (inside of an inactive form).
    If the contract is not the latest, the user has the ability to preview and save a new version as PDF.
    """
    contract = get_object_or_404(Contract, pk=pk)

    context = {}
    context['form'] = ContractUpdateForm(instance=contract)
    context['title'] = str(contract)
    context['is_latest'] = contract.is_latest()

    return render(request, 'contracts/view.html', context)


@atomic
@csrf_protect
@login_required
@permission_required('contracts.change_contract')
@require_http_methods(['GET', 'POST'])
def update_contract(request, pk):
    """
    Updates a contract identified by a given primary key, iff there had been changes. This method is atomic.
    """

    contract = get_object_or_404(Contract, pk=pk)
    context = {}
    context['title'] = 'Vertrag ' + str(contract.id) + ' ändern'

    if request.method == 'GET':
        # Displays the contract update form

        context['get'] = True
        context['form'] = ContractUpdateForm(instance=contract)

    else:
        # Validates the received form data.
        # Iff the data are valid and there had been changes, the changes will be saved to the database.

        form = ContractUpdateForm(request.POST, instance=contract)
        if form.is_valid():
            if form.has_changed():

                form.instance.is_changed = True
                form.save()

                messages.success(request, _('Änderungen erfolgreich übernommen!'))

            else:
                messages.info(request, _('Es gab keine Änderungen!'))
            return redirect(reverse('contracts:ContractView', args=(contract.id,)))
        else:
            context['form'] = form
    return render(request, 'contracts/update.html', context)


@login_required
@permission_required('contracts.view_contract')
@require_GET
def preview_contract_pdf(request, pk):
    """
    Previews the contract as PDF identified by a given primary key.
    """

    contract = get_object_or_404(Contract, pk=pk)
    pdf = contract.preview_contract_pdf()

    return HttpResponse(pdf, content_type='application/pdf')


@atomic
@csrf_protect
@login_required
@permission_required('contracts.change_contract')
@require_POST
def save_contract_pdf(request, pk):
    """
    Saves the newest version of the contract identified by a given primary key as PDF to the storage.
    """

    contract = get_object_or_404(Contract, pk=pk)

    contract.save_contract_pdf()

    messages.success(request, _('PDF wurde erfolgreich erstellt!'))

    return redirect(reverse('contracts:ContractView', args=(contract.id,)))


@login_required
@permission_required('contracts.view_contract')
@require_GET
def view_contract_pdf(request, pk, v):
    """
    Displays a contract as PDF identified by given primary key and a version number.
    """

    contract = get_object_or_404(Contract, pk=pk)
    pdf, filename = contract.view_contract_pdf(v)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=' + filename
        return response
    else:
        return HttpResponseNotFound()


@login_required
@permission_required('contracts.view_short_contract')
@require_GET
def print_active_contracts(request, file):
    """
    Displays a list of all contracts that are active and still running as PDF for the SWS
    """
    queryset = Contract.objects.filter(is_active=True, end__gte=datetime.datetime.now()) \
        .order_by('maintenant__residential_home', 'maintenant__house_number', 'maintenant__room_number', 'begin', 'end')

    path = os.path.join('contracts', 'contracts', file)
    pdf = html_to_pdf(path, {'contracts': queryset})
    filename = str(datetime.datetime.now())

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=' + filename
        return response
    else:
        return HttpResponseNotFound()


@csrf_protect
@login_required
@permission_required(['tenants.view_maintenant', 'tenants.view_subtenant', 'contracts.view_contract'])
@require_POST
def search(request):
    """
    Searches in all maintenants, subtenants and contracts for a user input.
    """

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

    maintenants = MainTenant.objects.filter(
        Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user_id=query_int) | Q(
            tenant_id=query_int) | Q(user__birthday=query_date))
    subtenants = SubTenant.objects.filter(
        Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user_id=int(query_int)) | Q(
            student_id=query_int) | Q(user__birthday=query_date))
    contracts = Contract.objects.filter(Q(id=query_int) | Q(begin=query_date) | Q(end=query_date))

    context = {
        'maintenants': maintenants,
        'subtenants': subtenants,
        'contracts': contracts,
        'query': query
    }

    return render(request, 'contracts/search_result.html', context)
