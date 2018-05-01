from django.shortcuts import render
from .models import Section, Building
from django.db.models import Q
from itertools import chain
from datetime import datetime
from datetime import time
import re
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Test
from django.http import HttpResponse
import json

@login_required
def query(request):
    q = request.GET.get('term', '')
    courses, buildings = search_terms(q[:20])
    results = []
    for building in buildings:
        building_json = {}
        building_json['label'] = str(building)+building.names[-1]
        building_json['value'] = str(building)
        results.append(building_json)
    for course in courses:
        course_json = {}
        course_json['label'] = str(course)+" "+course.title+" "+course.section
        course_json['value'] = str(course)+" "+course.section
        results.append(course_json)
    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

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
    zoom = 0
    lon = 0
    lat = 0
    if id != None:
        if match == 'c':
            match = Section.objects.get(id=int(id))
            lon = match.building_lon
            lat = match.building_lat
        else:
            match = Building.objects.get(id=int(id))
            lon = match.lon
            lat = match.lat
        if func == 's' and not netid in match.saved:
            match.saved.append(netid)
            match.searched += 1
            match.save()
            zoom = 1
        elif func == 'r' and netid in match.saved:
            match.saved.remove(netid)
            match.save()
    context = {
        'saved_courses': Section.objects.filter(saved__contains=[netid]),
        'saved_buildings': Building.objects.filter(saved__contains=[netid]),
        'netid': netid,
        'zoom': zoom,
        'last_lon': lon,
        'last_lat': lat
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

# Filter by course, number, building, and section
def search_terms(query):
    if query == None or len(query) == 0:
        return (Section.objects.none(), Building.objects.none())

    queryset = query.split(",")           # Fields separated by ',' are OR'ed

    courses = Section.objects.none()
    buildings = Building.objects.none()

    for query in queryset:
        query = query.split()
        query = "/".join(query).split("/")    # For cross-listed

        results = Section.objects.all()
        builds = Building.objects.all()
        for q in query:
            matches = results.filter(listings__icontains = "/"+q) | \
                      results.filter(listings__icontains = " "+q) | \
                      results.filter(section__istartswith = q) | \
                      results.filter(building__istartswith = q) | \
                      results.filter(building__icontains = " "+q)

            # Handle concat dept/number (e.g. cos333)
            if len(q) >= 4:
                matches = matches | \
                          results.filter(listings__icontains = "/"+q[0:3]) & \
                          results.filter(listings__icontains = " "+q[3:])

            results = matches

            # Always try to match query for building results
            builds = builds.filter(names__icontains = q)
            names = []
            # Display the primary name and the name that matched to prevent confusion
            for b in builds:
                for i in range(0, len(b.names)):
                    name = b.names[i]
                    if q.upper() in name.upper():
                        if i != 0:
                            b.names.append(" ("+name.strip()+")")
                        else:
                            b.names.append("")
                        break
        courses = set(chain(courses, results))
        buildings = set(chain(buildings, builds))
    return (courses, buildings)

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
    try:
        datetime.strptime(inputTime, '%I:%M%p').time()
    except ValueError:
        return resultsWithTime
    convertedTime = datetime.strptime(inputTime, '%I:%M%p').time()
    resultsWithTime = results.filter(starttime__lte = convertedTime, endtime__gte = convertedTime)
    return resultsWithTime

def getDayString(mon, tues, wed, thurs, fri):
    days = ""
    if (mon != None):
        days += " Monday,"
    if (tues != None):
        days += " Tuesday,"
    if (wed != None):
        days += " Wednesday,"
    if (thurs != None):
        days += " Thursday,"
    if (fri != None):
        days += " Friday,"
    if (days):
        days = "on" + days
    return days[:-1]

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
    resultsFiltered = searchDay(results, query, mon, tues, wed, thurs, fri)
    if (time):
        resultsFiltered = searchTime(time, resultsFiltered)
        if (not query and mon == None and tues == None and wed == None and thurs == None and fri == None):
            resultsFiltered = searchTime(time, Section.objects.all())
        time = "at " + time
    if (time == None):
        time = ""
    dayString = getDayString(mon, tues, wed, thurs, fri)
    context = {
        'q': query,
        't': time,
        'd': dayString,
        'classes': resultsFiltered,
        'buildings': buildings,
        'netid': request.user.username
    }
    return render(request, template, context)
