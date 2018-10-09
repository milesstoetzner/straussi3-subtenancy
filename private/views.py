from django.shortcuts import render
from django.views.generic import CreateView
from .models import Contract
from .forms import ContractForm


class ContractCreate(CreateView):
    model = Contract
    form_class = ContractForm
    form_class.use_required_attribute = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True
        return context


def Assistant(request):
    return render(request, 'private/assistent.html')
