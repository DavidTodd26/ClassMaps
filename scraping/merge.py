import sys
import json
import copy
from datetime import datetime

DEFAULT_TIME = "00:00" # No classes should start or end here

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
            info['course'] = [e['dept'] for e in entry['listings']]
            info['number'] = [e['number'] for e in entry['listings']]
        else:
            info['course'] = []
            info['number'] = []
        info['area'] = entry['area']
        if len(entry['profs']) > 0:
            info['profs'] = [e['name'] for e in entry['profs']]
        else:
            info['course'] = []
        info['title'] = entry['title']
        #if len(entry['classes']) == 0:
        #    info['section'] = ""
        #    info['day'] = ""
        #    info['starttime'] = DEFAULT_TIME
        #    info['endtime'] = DEFAULT_TIME
        #    info['building'] = ""
        #    info['room'] = ""
        #    info['enroll'] = ""
        #    info['capacity'] = ""
        #    entries.append(info)
        #    continue
        for c in entry['classes']:
            section = c['section']
            entry_info = copy.deepcopy(info)
            entry_info['section'] = section
            entry_info['day'] = c['days']
            entry_info['starttime'] = format_time(c['starttime'])
            entry_info['endtime'] = format_time(c['endtime'])
            entry_info['time'] = format_range(c['starttime'], c['endtime'])
            entry_info['building'] = c['bldg']
            entry_info['building_id'] = c['bldg_id']
            entry_info['room'] = c['roomnum']
            entry_info['enroll'] = c['enroll']
            entry_info['capacity'] = c['limit']
            entries.append(entry_info)
    return entries

# Add building lon and lat for each course section
def add_bldg(sections, bldgs):
    missing = []
    for section in sections:
        try:
            bldg = section['building_id']
            section['building_lat'] = bldgs[bldg]['lat']
            section['building_lon'] = bldgs[bldg]['lon']
        except KeyError:
            section['building_lat'] = ''
            section['building_lon'] = ''
            if section['building'] != "":
                missing.append(section['building'])

    # Print missing to stderr
    missing = set(missing)   # Remove duplicates
    for m in missing:
        print(m, file=sys.stderr)

    return sections

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

with open('test.json') as handle:
    course_info = json.load(handle)

processed = expand(course_info)
combined = add_bldg(processed, building_info)
converted = convert_db(combined, "classes", "section")

with open('data.json', 'w') as fp:
    json.dump(converted, fp)
