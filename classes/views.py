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
        # Course
        if len(q) == 3 and q.isalpha():
            results = results.filter(course__icontains = q)
        # Number
        elif len(q) == 3 and q.isdigit():
            results = results.filter(number__icontains = q)
        # Section
        elif re.match("^[A-Z]\d\d[A-Z]?$", q):
            results = results.filter(section__icontains = q)
        # Building
        elif len(q) > 0:
            results = results.filter(building__icontains = q)
        else:
            results = Section.objects.none()

        # Always try to match query for building results
        buildings = buildings.filter(names__icontains = q)
        names = []
        # Display the primary name and the name that matched to prevent confusion
        for b in buildings:
            for i in range(0, len(b.names)):
                name = b.names[i]
                if q.upper() in name.upper():
                    if i != 0:
                        b.names.append(" ("+name.strip()+")")
                    else:
                        b.names.append("")
                    break
    return (results, buildings)

def searchDay(results, query, mon, tues, wed, thurs, fri):
    results2 = Section.objects.none()
    if (mon != None):
        results2 = results2 | results.filter(Q(day__icontains="M"))
    if (tues != None):
        results2 = results2 | results.filter(Q(day__iregex=r'T(?!h)'))
    if (wed != None):
        results2 = results2 | results.filter(Q(day__icontains="W"))
    if (thurs != None):
        results2 = results2 | results.filter(Q(day__icontains="Th"))
    if (fri != None):
        results2 = results2 | results.filter(Q(day__icontains="F"))
    if (mon == None and tues == None and wed == None and thurs == None and fri == None):
        results2 = results
    if (not query):
        if (mon != None):
            results2 = results2 | Section.objects.filter(Q(day__icontains="M"))
        if (tues != None):
            results2 = results2 | Section.objects.filter(Q(day__iregex=r'T(?!h)'))
        if (wed != None):
            results2 = results2 | Section.objects.filter(Q(day__icontains="W"))
        if (thurs != None):
            results2 = results2 | Section.objects.filter(Q(day__icontains="Th"))
        if (fri != None):
            results2 = results2 | Section.objects.filter(Q(day__icontains="F"))
    return results2

def searchTime(inputTime, results):
    resultsWithTime = Section.objects.none()
    resultFilter = Section.objects.none()
    convertedTime = datetime.strptime(inputTime, '%I:%M%p').time()
    resultsWithTime = results.filter(starttime__lte = convertedTime, endtime__gte = convertedTime)
    return resultsWithTime

def getDayString(mon, tues, wed, thurs, fri):
    days = ""
    if (mon != None):
        days += " Monday"
    if (tues != None):
        days += " Tuesday"
    if (wed != None):
        days += " Wednesday"
    if (thurs != None):
        days += " Thursday"
    if (fri != None):
        days += " Friday"
    if (days):
        days = "," + days
    return days

@login_required
def search(request):
    template = 'classes/searches.html'
    query = request.GET.get('q', None)
    mon = request.GET.get('M', None)
    tues = request.GET.get('T', None)
    wed = request.GET.get('W', None)
    thurs = request.GET.get('Th', None)
    fri = request.GET.get('F', None)
    time = request.GET.get('t', None)
    results, buildings = search_terms(query)
    results2 = searchDay(results, query, mon, tues, wed, thurs, fri)
    if (time):
        results2 = searchTime(time, results2)
        if (not query and mon == None and tues == None and wed == None and thurs == None and fri == None):
            results2 = searchTime(time, Section.objects.all())
        time = "," + time
    dayString = getDayString(mon, tues, wed, thurs, fri)
    context = {
        'q': query,
        't': time,
        'd': dayString,
        'classes': results2,
        'buildings': buildings,
        'netid': request.user.username
    }
    return render(request, template, context)
