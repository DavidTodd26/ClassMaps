from django.shortcuts import render
from .models import Section
from django.db.models import Q
from datetime import time
import re

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
    ret = [""] * 5
    for q in query:
        if len(q) == 3 and q.isalpha():
            ret[0] = q
        elif len(q) == 3 and q.isdigit():
            ret[1] = q
        elif re.match("[A-Z]\d\d[A-Z]?", q):
            ret[2] = q
        elif re.match("[MTWThF]+", q):
            ret[3] = q
        elif re.match("\d\d:\d\d", q):
            ret[4] = q

    # If nothing matches
    if not any(ret):
        return ["zzzzz"]*4 + [""]
    return ret

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q').split()
    tokens = classify_terms(query)

    # Filter by course, number, section, and day
    results = Section.objects.filter(course__icontains = tokens[0],
                                     number__icontains = tokens[1],
                                     section__icontains = tokens[2],
                                     day__icontains = tokens[3])
    # Filter by time
    if tokens[4] != "":
        t = tokens[4].split(":")
        t = time(hour = int(t[0]), minute = int(t[1]))
        results = results.filter(starttime__lte = t, endtime__gte = t)

    context = {
        'classes': results
    }

    return render(request, template, context)
