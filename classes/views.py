from django.shortcuts import render
from .models import Section
from django.db.models import Q

# Create your views here.

def index(request):
    context = {

    }
    return render(request, 'classes/index.html', context)

def details(request, id):
    classe = Section.objects.get(id=id)
    context = {
        'classe': classe
    }

    return render(request, 'classes/details.html', context)

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q')
    results = Section.objects.filter(Q(course__icontains=query)) | Section.objects.filter(Q(number__icontains=query)) 
    context = {
        'classes': results
    }

    return render(request, template, context)