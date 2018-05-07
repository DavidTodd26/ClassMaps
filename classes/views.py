from django.shortcuts import render
from .models import Section, Building
from django.db.models import Q
from itertools import chain
from datetime import datetime
from datetime import time
import re
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import json

#@login_required
def query(request):
    query, time, dayString, courses, buildings, names = parse_terms(request)
    results = []
    for building in buildings:
        building_json = {}
        building_json['label'] = str(building)+names[building.names.split("/")[0]]
        building_json['value'] = str(building)
        building_json['type'] = "building"
        building_json['id'] = building.id
        results.append(building_json)
    for course in courses:
        course_json = {}
        course_json['label'] = str(course)+" "+course.title+" "+course.section
        course_json['value'] = str(course)+" "+course.section
        course_json['type'] = "course"
        course_json['id'] = course.id
        results.append(course_json)
    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

#@login_required
def enroll(request):
    query, time, dayString, courses, buildings, names = parse_terms(request)
    builds = {}
    for course in courses:
        if course.enroll:
            if course.building in builds:
                builds[course.building]['courses'] += 1
                builds[course.building]['students'] += int(course.enroll)
            else:
                builds[course.building] = {}
                builds[course.building]['courses'] = 1
                builds[course.building]['students'] = int(course.enroll)
    data = json.dumps(builds)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def update_result(netid, isSave, isCourse, id):
    zoom = 0
    lon = 0
    lat = 0
    if isCourse and id.isdigit() and Section.objects.filter(id=int(id)).exists():
        match = Section.objects.get(id=int(id))
        lon = match.building_lon
        lat = match.building_lat
    elif id.isdigit() and Section.objects.filter(id=int(id)).exists():
        match = Building.objects.get(id=int(id))
        lon = match.lon
        lat = match.lat
    else:
        return (lon, lat, zoom)

    if isSave and not netid in match.saved:
        match.saved.append(netid)
        match.searched += 1
        match.save()
        zoom = 1
    elif not isSave and netid in match.saved:
        match.saved.remove(netid)
        match.save()

    return (lon, lat, zoom)

#@login_required
def index(request):
    netid = request.user.username
    save_id = request.GET.get('s')
    remove_id = request.GET.get('r')
    context = {}
    if save_id:
        lon, lat, zoom = update_result(netid, True, (save_id[-1] == 'c'), save_id[:-1])
    elif remove_id:
        lon, lat, zoom = update_result(netid, False, (remove_id[-1] == 'c'), remove_id[:-1])
    else:
        lon, lat, zoom = 0, 0, 0

    context = {
        'saved_courses': Section.objects.filter(saved__contains=[netid]),
        'saved_buildings': Building.objects.filter(saved__contains=[netid]),
        'netid': netid,
        'zoom': zoom,
        'last_lon': lon,
        'last_lat': lat
    }

    return render(request, 'classes/index.html', context)

def details(request, id, isCourse):
    netid = request.user.username
    context = {
        'saved_courses': Section.objects.filter(saved__contains=[netid]),
        'saved_buildings': Building.objects.filter(saved__contains=[netid]),
        'netid': netid
    }
    if isCourse and id.isdigit() and Section.objects.filter(id=int(id)).exists():
        context['course'] = Section.objects.get(id=int(id))
    elif id.isdigit() and Building.objects.filter(id=int(id)).exists():
        context['building'] = Building.objects.get(id=int(id))

    return render(request, 'classes/index.html', context)


#@login_required
def course_details(request, id):
    return details(request, id, isCourse=True)

#@login_required
def building_details(request, id):
    return details(request, id, isCourse=False)

# Filter by course, number, building, and section
def search_terms(query):
    if query == None:
        return (Section.objects.all(), Building.objects.all(), {})

    if query == "":
        return (Section.objects.all(), Building.objects.none(), {})

    queryset = query.split(",")           # Fields separated by ',' are OR'ed

    courses = Section.objects.none()
    buildings = Building.objects.none()
    names = {}  # Map canonical building name to name actually searched

    for query in queryset:
        query = query.split()
        query = "/".join(query).split("/")    # For cross-listed
        concat = Q()

        results = Section.objects.all()
        builds = Building.objects.all()
        for q in query:
            # Always try to match query for building results
            builds = builds.filter(names__icontains = " "+q) | \
                     builds.filter(names__icontains = "/"+q) | \
                     builds.filter(names__istartswith = q)

            # Display the canonical name and the name that matched to prevent confusion
            for b in builds:
                aliases = b.names.split("/")
                for i in range(0, len(aliases)):
                    name = aliases[i]
                    if q.upper() in name.upper():
                        if i != 0:
                            names[aliases[0]] = " ("+name.strip()+")"
                        else:
                            names[aliases[0]] = ""
                        break

            # Match courses
            matches = Q(listings__icontains = "/"+q) | \
                      Q(listings__icontains = " "+q) | \
                      Q(section__istartswith = q)

            # Handle building - look for match in canonical name and aliases
            for b in builds:
                matches = matches | \
                    Q(building__istartswith = b.names.split("/")[0]) | \
                    Q(building__icontains = " "+b.names.split("/")[0])

            # Handle concat dept/number (e.g. cos333)
            if len(q) >= 4:
                matches = matches | \
                          (Q(listings__icontains = "/"+q[0:3]) & \
                          Q(listings__icontains = " "+q[3:]))

            concat = concat & matches

        courses = courses | Section.objects.filter(concat)
        buildings = buildings | builds

    return (courses, buildings, names)

def searchDay(results, query, mon, tues, wed, thurs, fri):
    results2 = Section.objects.none()
    if mon:
        results2 = results2 | results.filter(Q(day__icontains="M"))
    if tues:
        results2 = results2 | results.filter(Q(day__iregex=r'T(?!h)'))
    if wed:
        results2 = results2 | results.filter(Q(day__icontains="W"))
    if thurs:
        results2 = results2 | results.filter(Q(day__icontains="Th"))
    if fri:
        results2 = results2 | results.filter(Q(day__icontains="F"))
    if not mon and not tues and not wed and not thurs and not fri:
        results2 = results
    if not query:
        if mon:
            results2 = results2 | Section.objects.filter(Q(day__icontains="M"))
        if tues:
            results2 = results2 | Section.objects.filter(Q(day__iregex=r'T(?!h)'))
        if wed:
            results2 = results2 | Section.objects.filter(Q(day__icontains="W"))
        if thurs:
            results2 = results2 | Section.objects.filter(Q(day__icontains="Th"))
        if fri:
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
    if mon:
        days += "M"
    if tues:
        days += "T"
    if wed:
        days += "W"
    if thurs:
        days += "Th"
    if fri:
        days += "F"
    return days

def parse_terms(request):
    query = request.GET.get('q', None)
    mon = request.GET.get('M', None)
    tues = request.GET.get('T', None)
    wed = request.GET.get('W', None)
    thurs = request.GET.get('Th', None)
    fri = request.GET.get('F', None)
    time = request.GET.get('t', None)
    results, buildings, names = search_terms(query)
    resultsFiltered = searchDay(results, query, mon, tues, wed, thurs, fri)
    if time:
        resultsFiltered = searchTime(time, resultsFiltered)
        if not query and not mon and not tues and not wed and not thurs and not fri:
            resultsFiltered = searchTime(time, Section.objects.all())
        time = "at " + time
    else:
        time = ""
    dayString = getDayString(mon, tues, wed, thurs, fri)

    return(query, time, dayString, resultsFiltered, buildings, names)

#@login_required
def search(request):
    template = 'classes/index.html'
    query, time, dayString, resultsFiltered, buildings, names = parse_terms(request)

    netid = request.user.username

    context = {
        'q': query,
        't': time,
        'd': dayString,
        'saved_courses': Section.objects.filter(saved__contains=[netid]),
        'saved_buildings': Building.objects.filter(saved__contains=[netid]),
        'netid': netid
    }
    context['num_matches'] = len(resultsFiltered) + len(buildings)
    # If one match, we can put it directly on the map
    if len(resultsFiltered) == 1 and len(buildings) == 0:
        context['course'] = resultsFiltered[0]
    elif len(resultsFiltered) == 0 and len(buildings) == 1:
        context['building'] = buildings[0]
    else:
        # Add queried names
        for b in buildings:
            name = b.names.split("/")[0]
            b.names = name + "/" + names[name]
        context['classes'] = resultsFiltered
        context['buildings'] = buildings

    return render(request, template, context)

#@login_required
def about(request):
    context = {

    }
    return render(request, 'classes/about.html', context)
