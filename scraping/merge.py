import sys
import json
import copy
from datetime import datetime
import re

DEFAULT_TIME = "00:00"

# Remove seconds from the time
def format_time(time):
    if time == "":
        return DEFAULT_TIME
    else:
        return datetime.strptime(time, "%I:%M:%S %p").strftime("%H:%M")

# Format time range and remove 0 padding of hours
def format_range(start, end):
    timerange = start[0:5]+start[8:]+"-"+end[0:5]+end[8:]
    times = timerange.split("-")
    for i in range(0, 2):
        tokens = times[i].split(":")
        tokens[0] = str(int(tokens[0]))
        times[i] = ":".join(tokens)
    return "-".join(times)

# Make a separate entry for each precept, lecture, class, etc.
def expand(raw):
    lines = 0
    entries = []
    for entry in raw:
        info = {}
        if len(entry['listings']) > 0:
            depts = [e['dept'] for e in entry['listings']]
            nums =  [e['number'] for e in entry['listings']]
            info['listings'] = ""
            for i in range(0, len(depts)):
                info['listings'] += "/"+depts[i]+" "+nums[i]
        else:
            info['listings'] = ""
        info['area'] = entry['area']
        info['title'] = entry['title']
        if len(entry['classes']) == 0:
            info['course_id'] = entry['courseid']
            info['section'] = ""
            info['day'] = ""
            info['time'] = ""
            info['building'] = ""
            info['building_name'] = ""
            info['room'] = ""
            info['enroll'] = ""
            info['capacity'] = ""
            entries.append(info)
            continue
        for c in entry['classes']:
            section = c['section']
            entry_info = copy.deepcopy(info)
            entry_info['course_id'] = c['classnum']
            entry_info['section'] = section
            entry_info['day'] = c['days']
            entry_info['starttime'] = format_time(c['starttime'])
            entry_info['endtime'] = format_time(c['endtime'])
            entry_info['time'] = format_range(c['starttime'], c['endtime'])
            entry_info['building'] = c['bldg_id']
            entry_info['building_name'] = c['bldg']
            entry_info['room'] = c['roomnum']
            entry_info['enroll'] = c['enroll']
            entry_info['capacity'] = c['limit']
            entries.append(entry_info)
    return entries

# Test if the query and result are the same (+/- some formatting)
def near_match(query, result):
    # Remove punctuation
    query_terms = re.sub("[^0-9a-zA-Z]+", " ", query)
    query_terms = query_terms.split()
    result_terms = re.sub("[^0-9a-zA-Z]+", " ", result)
    result_terms = result_terms.split()

    # Check all permuations of words
    q_matches = r_matches = 0
    for i in range(0,len(query_terms)):
        q = query_terms[i]
        for r in result_terms:
            # Last query terms might be cut off
            if r == q or (i == len(query_terms)-1 and r.startswith(q)):
                q_matches += 1
                break
    for r in result_terms:
        for i in range(0,len(query_terms)):
            q = query_terms[i]
            if r == q or (i == len(query_terms)-1 and r.startswith(q)):
                r_matches += 1
                break
    return q_matches == len(query_terms) or r_matches == len(result_terms)

# Find a building match by name
def find_building(b, bldgs):
    if b == None or bldgs == None or len(b) == 0:
        return (None, None)

    # Search for exact match
    for key in bldgs:
        for alias in bldgs[key]['names'].split("/"):
            if b == alias:
                return (key, alias)

    # In the rare failure, look for a near match
    for key in bldgs:
        for alias in bldgs[key]['names'].split("/"):
            if near_match(b, alias):
                return (key, alias)

    return (None, None)

# Remove buildings with no classes
def restrict_bldg(sections, bldgs):
    buildings = []
    missing = []
    for section in sections:
        bldg_id = section['building']
        bldg = section['building_name']
        # Matching by id's is most reliable
        if bldg_id in bldgs:
            # Names on course offering get cut off
            section['building'] = [bldg_id]
            section['building_name'] = bldgs[bldg_id]['names'].split("/")[0]
            buildings.append(bldg_id)
        else:
            # If this fails, try matching by name
            bldg_id, name = find_building(bldg, bldgs)
            if bldg_id:
                section['building'] = [bldg_id]
                section['building_name'] = name
                buildings.append(bldg_id)
            elif section['building'] != "":
                section['building'] = [-1]
                missing.append(section['building'])
            else:
                section['building'] = [-1]

    # Remove buildings with no classes
    restricted = {}
    for b in buildings:
        restricted[b] = bldgs[b]

    # Print missing buildings to stderr
    missing = set(missing)   # Remove duplicates
    for m in missing:
        print(m, file=sys.stderr)

    return restricted

# Convert into a form that can be put into the database
def convert_db(data, project, model):
    pk=1
    ret = []
    for ent in data:
        temp = {}
        temp['pk'] = pk
        temp['model'] = project+"."+model
        temp['fields'] = ent
        ret.append(temp)
        pk+=1
    return ret


with open('buildids.json') as handle:
    building_info = json.load(handle)

with open('courses.json') as handle:
    course_info = json.load(handle)

# Add a default location for courses with no building
no_location = {}
no_location['building_id'] = '-1'
no_location['names'] = 'NO BUILDING'
no_location['lat'] = '40.346699'
no_location['lon'] = '-74.656509'
building_info['-1'] = no_location


processed = expand(course_info)
buildings = restrict_bldg(processed, building_info)
converted = convert_db(processed, "classes", "section")

buildings_data = convert_db(building_info.values(), "classes", "building")
buildings_restricted = convert_db(buildings.values(), "classes", "building")

with open('course_data.json', 'w') as handle:
    json.dump(converted, handle)

with open('building_data.json', 'w') as handle:
    json.dump(buildings_data, handle)

with open('buildings_restricted.json', 'w') as handle:
    json.dump(buildings, handle)
