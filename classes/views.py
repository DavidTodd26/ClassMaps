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

def classify_terms(query):
    ret = [""] * 2
    for q in query.split():
        if len(query) == 3 and query.isalpha():
            ret[0] = q
        elif len(query) == 3 and query.isdigit():
            ret[1] = q
    return ret

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q')
    tokens = classify_terms(query)
    results = Section.objects.filter(Q(course__icontains=tokens[0], number__icontains=tokens[1]))
    context = {
        'classes': results
    }

    return render(request, template, context)
