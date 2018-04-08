from django.shortcuts import render
from .models import Section
from django.db.models import Q
from enum import Enum

# Create your views here.
class Term(Enum):
    INVALID = 0
    COURSE = 1
    NUMBER = 2


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

def classify_term(query):
    if len(query) == 3 and query.isalpha():
        return COURSE
    elif len(query) == 3 and query.isdigit():
        return NUMBER
    else:
        return INVALID

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q')
    tokens = query.split()
    for t in tokens:
        category = classify_term(t)
        if category == COURSE:
            results = Section.objects.filter(Q(course__icontains=query))
        elif category == NUMBER:
            results = Section.objects.filter(Q(number__icontains=query))
        else:
            results = None
    context = {
        'classes': results
    }

    return render(request, template, context)
