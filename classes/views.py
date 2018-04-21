from django.shortcuts import render
from .models import Section, Building
from django.db.models import Q
from itertools import chain
from datetime import time
import re
from django.shortcuts import redirect

def login(request):
    return redirect('/accounts/login')

# Create your views here.
def index(request):
    id = request.GET.get('s')
    if id != None:
        func = 's'
        match = id[-1]
        id = id[:-1]
    else:
        id = request.GET.get('r')
        if id != None:
            match = id[-1]
            id = id[:-1]
            func = 'r'

    if id != None:
        print(id)
        if match == 'c':
            match = Section.objects.get(id=int(id))
        else:
            match = Building.objects.get(id=int(id))
        if func == 's':
            match.saved.append("dtodd") #TODO: Replace netid
            match.save()
        elif func == 'r':
            match.saved.remove("dtodd") #TODO: Replace netid
            match.save()
    context = {
        #TODO: Replace netid
        'saved_courses': Section.objects.filter(saved__contains=["dtodd"]),
        'saved_buildings': Building.objects.filter(saved__contains=["dtodd"])
    }
    return render(request, 'classes/index.html', context)

def details(request, id):
    print(request)
    print("teSt",id.isdigit())
    if id.isdigit():
        course = Section.objects.get(id=int(id))
        context = {
            'c': course,
            'saved_courses': Section.objects.filter(saved__contains=["dtodd"]),
            'saved_buildings': Building.objects.filter(saved__contains=["dtodd"])
        }
    else:
        print("TEST")
        building = Building.objects.get(names__contains=[id])
        context = {
            'building': building,
            'saved_courses': Section.objects.filter(saved__contains=["dtodd"]),
            'saved_buildings': Building.objects.filter(saved__contains=["dtodd"])
        }

    return render(request, 'classes/index.html', context)

# Filter by course, number, section, day, and time
def search_terms(query):
    if query == None or len(query) == 0:
        return (Section.objects.none(), Section.objects.none())

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
            buildings = Section.objects.filter(building__icontains = q)
            buildings = buildings.values_list('building', flat=True).distinct()
            results = results.filter(building__icontains = q)
        else:
            results = Section.objects.none()

    return (results, buildings)

def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q')
    query2 = request.GET.get('q2', None)
    query3 = request.GET.get('q3', None)
    query4 = request.GET.get('q4', None)
    query5 = request.GET.get('q5', None)
    query6 = request.GET.get('q6', None)
    results, buildings = search_terms(query)
    results2 = Section.objects.none()
    buildings2 = Section.objects.none()
    if (query2 != None):
        results2 = results2 | results.filter(Q(day__icontains=query2))
        buildings2 = buildings2 | buildings.filter(Q(day__icontains=query2))
    if (query3 != None):
        results2 = results2 | results.filter(Q(day__iregex=r'T(?!h)'))
        buildings2 = buildings2 | buildings.filter(Q(day__iregex=r'T(?!h)'))
    if (query4 != None):
        results2 = results2 | results.filter(Q(day__icontains=query4))
        buildings2 = buildings2 | buildings.filter(Q(day__icontains=query4))
    if (query5 != None):
        results2 = results2 | results.filter(Q(day__icontains=query5))
        buildings2 = buildings2 | buildings.filter(Q(day__icontains=query5))
    if (query6 != None):
        results2 = results2 | results.filter(Q(day__icontains=query6))
        buildings2 = buildings2 | buildings.filter(Q(day__icontains=query6))
    context = {
        'classes': results2,
        'buildings': buildings2
    }
    return render(request, template, context)
