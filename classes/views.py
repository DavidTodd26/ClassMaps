from django.shortcuts import render
from .models import Section
from django.db.models import Q
from enum import Enum

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

def classify_terms(query):
    ret = [""] * 2
    for q in query:
        if len(q) == 3 and q.isalpha():
            ret[0] = q
        elif len(q) == 3 and q.isdigit():
            ret[1] = q

    # If nothing matches
    if not any(ret):
        return ["zzzzz"] * 2
    return ret

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q').split()
    tokens = classify_terms(query)
    results = Section.objects.filter(course__icontains=tokens[0]).filter(number__icontains=tokens[1])
    print(query)
    print(tokens)
    print(results)
    context = {
        'classes': results
    }

    return render(request, template, context)
