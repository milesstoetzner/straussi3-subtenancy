import os
import datetime
import base64

from django.db.transaction import atomic
from django.urls import reverse
from .models import Contract, Roster
from tenants.models import MainTenant, SubTenant
from .forms import ContractForm
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from .utils import html_to_pdf
from subtenancy.views import handler404, handler400





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
    context['title'] = 'Vertrag erstellen'

    if request.method == 'GET':
        form = ContractForm()
        context['get'] = True
    else:
        form = ContractForm(request.POST)

        if form.is_valid():

            if 'step' not in request.POST:
                return handler400(request)

            step = request.POST['step']

            if step == 'preview':
                contract = form.save(commit=False)
                pdf = contract.preview_contract_pdf()
                context['form'] = form
                context['pdf'] = base64.b64encode(pdf).decode('utf-8')

                return render(request, 'contracts/create.html', context)

            elif step == 'save':
                contract = form.save()
                form.instance.subtenant.is_searching = False
                form.instance.subtenant.save()

                contract.save_contract_pdf()
                messages.success(request, 'Vertrag wurde erfolgreich erstellt!')
                return redirect(contract.get_absolute_url())

            else:
                return handler400(request)

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
    context['form'] = ContractForm(instance=contract)
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
        context['get'] = True
        context['form'] = ContractForm(instance=contract)
    else:
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            if form.has_changed():

                form.instance.is_changed = True
                form.save()

                messages.success(request, 'Änderungen erfolgreich übernommen!')

            else:
                messages.info(request, 'Es gab keine Änderungen!')
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

    messages.success(request, 'PDF wurde erfolgreich erstellt!')

    return redirect(reverse('contracts:ContractView', args=(contract.id,)))


@login_required
@permission_required('contracts.view_contract')
@require_GET
def view_contract_pdf(request, pk, v):
    filename = 'contract_' + str(pk) + '_version_' + str(v) + '.pdf'
    path = '/contracts/contracts/' + filename

    if os.path.isfile(os.getcwd() + path):
        response = HttpResponse()
        response['Content-Type'] = 'application/pdf'
        response["Content-Disposition"] = 'inline; filename=' + filename
        response['X-Accel-Redirect'] = path
        return response

    return handler404(request)


@login_required
@permission_required('contracts.view_short_contract')
@require_GET
def print_active_contracts(request, file):
    """
    Displays a list of all contracts that are active and still running as PDF for the SWS
    """
    queryset = Contract.objects.filter(is_active=True, end__gte=datetime.datetime.now()) \
        .order_by('maintenant__residential_home', 'maintenant__house_number', 'maintenant__room_number', 'begin', 'end')

    template_name = 'contracts/' + file
    pdf = html_to_pdf(template_name, {'contracts': queryset, 'today': datetime.datetime.now()})
    filename = 'ferienmiete_str3_' + str(datetime.datetime.now().strftime("%Y-%m-%d")) + '.pdf'

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=' + filename
        return response
    else:
        return handler404(request)


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
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(user_id=query_int) | Q(
            tenant_id=query_int) | Q(birthday=query_date))
    subtenants = SubTenant.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(user_id=int(query_int)) | Q(birthday=query_date))
    contracts = Contract.objects.filter(Q(id=query_int) | Q(begin=query_date) | Q(end=query_date))

    context = {
        'maintenants': maintenants,
        'subtenants': subtenants,
        'contracts': contracts,
        'query': query
    }

    return render(request, 'contracts/search_result.html', context)


@login_required
@permission_required('contracts.add_contract')
@require_http_methods(['GET'])
def view_help(request):
    """
    General information for assistants about tenants, contracts and the usage of this website.
    """
    context = {}
    context['title'] = 'Hilfe'
    messages.info(request, 'Falls ihr Fragen zur Bedienung der Website bzw. zur Untermiete habt, dann zögert nicht und ruft mich an bzw. schreibt mir: +49 1777 580061.')
    return render(request, 'contracts/help.html', context)


@login_required
@permission_required('contracts.view_roster')
@require_http_methods(['GET'])
def view_roster(request):
    """
    Displays the roster.
    """

    query = Roster.objects.filter(date__gte=datetime.datetime.now()).order_by('date')
    query_personal = Roster.objects.filter(date__gte=datetime.datetime.now(), assistant=request.user).order_by('date')

    context = {}
    context['title'] = 'Dienstplan'
    context['roster'] = query
    context['roster_personal'] = query_personal

    if not query:
        messages.info(request, 'Der Dienstplan enthält keine Einträge!')

    if not query_personal:
        messages.info(request, 'Du wirst im aktuellen Dienstplan nicht erwähnt!')

    return render(request, 'contracts/roster.html', context)
