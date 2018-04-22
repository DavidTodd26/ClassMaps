from django.shortcuts import render
from .models import Section, Building
from django.db.models import Q
from itertools import chain
from datetime import datetime
from datetime import time
import re
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    netid = request.user.username
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
        if match == 'c':
            match = Section.objects.get(id=int(id))
        else:
            match = Building.objects.get(id=int(id))
        if func == 's' and not netid in match.saved:
            match.saved.append(netid)
            match.searched += 1
            match.save()
        elif func == 'r' and netid in match.saved:
            match.saved.remove(netid)
            match.save()
    context = {
        'saved_courses': Section.objects.filter(saved__contains=[netid]),
        'saved_buildings': Building.objects.filter(saved__contains=[netid]),
        'netid': netid
    }
    return render(request, 'classes/index.html', context)

@login_required
def details(request, id):
    netid = request.user.username
    if id.isdigit():
        course = Section.objects.get(id=int(id))
        context = {
            'c': course,
            'saved_courses': Section.objects.filter(saved__contains=[netid]),
            'saved_buildings': Building.objects.filter(saved__contains=[netid]),
            'netid': netid
        }
    else:
        building = Building.objects.get(names__contains=[id])
        context = {
            'building': building,
            'saved_courses': Section.objects.filter(saved__contains=[netid]),
            'saved_buildings': Building.objects.filter(saved__contains=[netid]),
            'netid': netid
        }

    return render(request, 'classes/index.html', context)

# Filter by course, number, section, day, and time
def search_terms(query):
    if query == None or len(query) == 0:
        return (Section.objects.none(), Building.objects.none())

    query = query.split()
    results = Section.objects.all()
    buildings = Building.objects.all()

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
            results = results.filter(building__icontains = q)
        else:
            results = Section.objects.none()

        # Always try to match query for building results
        buildings = buildings.filter(names__icontains = q)
        names = []
        for b in buildings:
            for name in b.names:
                if q.upper() in name.upper():
                    b.names[0] = name
                    break
    return (results, buildings)

def searchTime(inputTime, results):
    resultsWithTime = Section.objects.none()
    resultFilter = Section.objects.none()
    convertedTime = datetime.strptime(inputTime, '%I:%M%p').time()
    resultsWithTime = results.filter(starttime__lte = convertedTime, endtime__gte = convertedTime)
    return resultsWithTime

@login_required
def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q')
    query2 = request.GET.get('q2', None)
    query3 = request.GET.get('q3', None)
    query4 = request.GET.get('q4', None)
    query5 = request.GET.get('q5', None)
    query6 = request.GET.get('q6', None)
    time = request.GET.get('t', None)
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
    if (query2 == None and query3 == None and query4 == None and query5 == None and query6 == None):
        results2 = results
        buildings2 = buildings
    if (time):
        results2 = searchTime(time, results2)
        buildings2 = searchTime(time, buildings2)
    context = {
        'q': query,
        't': time,
        'classes': results2,
        'buildings': buildings2,
        'netid': request.user.username
    }
    return render(request, template, context)
