from django.shortcuts import render


def Assistant(request):
    return render(request, 'private/assistent.html')
