from django.shortcuts import render
from .models import Section, Building, User
from django.db.models import Q
from itertools import chain
from datetime import datetime
from datetime import time
import re
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.core import serializers
import json

@login_required
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
        course_json['label'] = str(course)+" "+course.title+" "+course.section+" "+course.time
        course_json['value'] = str(course)+" "+course.section
        course_json['type'] = "course"
        course_json['id'] = course.id
        results.append(course_json)
    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required
def enroll(request):
    query, time, dayString, courses, buildings, names = parse_terms(request)
    builds = {}
    for course in courses:
        if course.enroll:
            name = course.building_name
            if name in builds:
                builds[name]['courses'] += 1
                builds[name]['students'] += int(course.enroll)
            else:
                builds[name] = {}
                builds[name]['courses'] = 1
                builds[name]['students'] = int(course.enroll)
    data = json.dumps(builds)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def saved_locations(request):
    netid = request.user.username
    user = User.objects.get(netid=netid)

    courses = Section.objects.filter(id__in=user.courses)
    saved_courses = []
    for c in courses:
        courses_json = {}
        courses_json['id'] = c.pk #c.course_id
        courses_json['listing'] = str(c)
        courses_json['building_name'] = c.building_name
        courses_json['room'] = c.room
        courses_json['time'] = c.time
        courses_json['lon'] = c.building.lon
        courses_json['lat'] = c.building.lat
        saved_courses.append(courses_json)

    buildings = Building.objects.filter(id__in=user.buildings)
    saved_buildings = []
    for b in buildings:
        buildings_json = {}
        buildings_json['id'] = b.pk #b.building_id
        buildings_json['name'] = str(b)
        buildings_json['lon'] = b.lon
        buildings_json['lat'] = b.lat
        saved_buildings.append(buildings_json)

    data = {
        'courses': saved_courses,
        'buildings': saved_buildings
    }
    return JsonResponse(data)

def update_result(netid, isSave, isCourse, id):
    user = User.objects.get(netid=netid)

    if isCourse and id.isdigit() and Section.objects.filter(id=int(id)).exists():
        match = Section.objects.get(id=int(id))
        key = str(match.pk)
        if isSave and not key in user.courses:
            user.courses.append(key)
            match.searched += 1
            match.save()
        elif not isSave and key in user.courses:
            user.courses.remove(key)
    elif id.isdigit() and Section.objects.filter(id=int(id)).exists():
        match = Building.objects.get(id=int(id))
        key = str(match.pk)
        if isSave and not key in user.buildings:
            user.buildings.append(key)
            match.searched += 1
            match.save()
        elif not isSave and key in user.buildings:
            user.buildings.remove(key)

    user.save()

# Create user if not present already
def create_user(netid):
    if not User.objects.filter(netid=netid).exists():
        User.objects.create(netid=netid)

@login_required
def remove(request):
    remove_id = request.POST.get('r')
    if remove_id:
        netid = request.user.username
        update_result(netid, False, (remove_id[-1] == 'c'), remove_id[:-1])
    return HttpResponseRedirect(reverse('classes:saved_locations'))

@login_required
def save(request):
    save_id = request.POST.get('s')
    if save_id:
        netid = request.user.username
        update_result(netid, True, (save_id[-1] == 'c'), save_id[:-1])
    return HttpResponseRedirect(reverse('classes:saved_locations'))

@login_required
def index(request):
    netid = request.user.username
    create_user(netid)
    user = User.objects.get(netid=netid)
    context = {
        'saved_courses': Section.objects.filter(id__in=user.courses),
        'saved_buildings': Building.objects.filter(id__in=user.buildings),
        'netid': netid,
    }

    return render(request, 'classes/index.html', context)

def details(request, id, isCourse):
    netid = request.user.username
    create_user(netid)
    user = User.objects.get(netid=netid)
    context = {
        'saved_courses': Section.objects.filter(id__in=user.courses),
        'saved_buildings': Building.objects.filter(id__in=user.buildings),
        'netid': netid
    }
    if isCourse and id.isdigit() and Section.objects.filter(id=int(id)).exists():
        context['course'] = Section.objects.get(id=int(id))
    elif id.isdigit() and Building.objects.filter(id=int(id)).exists():
        context['building'] = Building.objects.get(id=int(id))

    return render(request, 'classes/index.html', context)


@login_required
def course_details(request, id):
    return details(request, id, isCourse=True)

@login_required
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
        for i in range(0, len(query)):
            # Handle invalid regex
            try:
                re.compile(query[i])
            except re.error:
                return (Section.objects.none(), Building.objects.none(), {})

            # Last search term might be incomplete
            if i == len(query)-1:
                q = query[i]
            else:
                q = query[i]+"($| |/)"

            # Always try to match query for building results
            builds = builds.filter(names__iregex = "(^| |/)"+q)

            # Display the canonical name and the name that matched to prevent confusion
            for b in builds:
                aliases = b.names.split("/")
                for j in range(0, len(aliases)):
                    name = aliases[j]
                    if re.search(query[i], name, re.IGNORECASE):
                        if j != 0:
                            names[aliases[0]] = " ("+name.strip()+")"
                        else:
                            names[aliases[0]] = ""
                        break

            # Match courses by listings and building
            matches = Q(listings__iregex = "(^| |/)"+q) | Q(building__names__iregex = "(^| |/)"+q)

            # Handle concat dept/number (e.g. cos333)
            if len(query[i]) >= 4:
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

@login_required
def search(request):
    template = 'classes/index.html'
    query, time, dayString, resultsFiltered, buildings, names = parse_terms(request)
    print(names)
    print(buildings)

    netid = request.user.username
    create_user(netid)
    user = User.objects.get(netid=netid)

    context = {
        'q': query,
        't': time,
        'd': dayString,
        'saved_courses': Section.objects.filter(id__in=user.courses),
        'saved_buildings': Building.objects.filter(id__in=user.buildings),
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

@login_required
def about(request):
    context = {

    }
    return render(request, 'classes/about.html', context)
