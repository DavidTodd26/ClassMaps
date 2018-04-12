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
    if id.isdigit():
        course = Section.objects.get(id=int(id))
        context = {
            'classe': course
        }
    else:
        building = Section.objects.filter(building__icontains = id).first()
        context = {
            'building': building
        }

    return render(request, 'classes/details.html', context)

# Filter by course, number, section, day, and time
def search_terms(query):
    query = query.split()
    results = Section.objects.all()
    buildings = Section.objects.none()

    for q in query:
        # Day
        if re.match("^[MTWThF]+$", q):
            results = results.filter(day__icontains = q)
        # Course
        if len(q) == 3 and q.isalpha():
            results = results.filter(course__icontains = q)
        # Number
        elif len(q) == 3 and q.isdigit():
            results = results.filter(number__icontains = q)
        # Section
        elif re.match("^[A-Z]\d\d[A-Z]?$", q):
            results = results.filter(section__icontains = q)
        # Time
        elif re.match("^\d\d:\d\d$", q):
            t = q.split(":")
            t = time(hour = int(t[0]), minute = int(t[1]))
            results = results.filter(starttime__lte = t, endtime__gte = t)
        # Building
        elif len(q) > 0:
            buildings = Section.objects.filter(building__icontains = q).first()
            results = Section.objects.none()
        else:
            results = Section.objects.none()

    return (results, buildings)

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q')
    results, building = search_terms(query)
    context = {
        'classes': results,
        'building': building
    }

    return render(request, template, context)
