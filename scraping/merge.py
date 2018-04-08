import sys
import json
import copy

# Make a separate entry for each precept, lecture, or class
def expand(raw):
    lines = 0
    entries = []
    for entry in raw:
        info = {}
        if len(entry['listings']) > 0:
            info['course'] = "_".join([e['dept'] for e in entry['listings']])
            info['number'] = "_".join([e['number'] for e in entry['listings']])
        else:
            info['course'] = []
            info['number'] = []
        info['area'] = entry['area']
        if len(entry['profs']) > 0:
            info['profs'] = "_".join([e['name'] for e in entry['profs']])
        else:
            info['course'] = []
        info['title'] = entry['title']
        if len(entry['classes']) == 0:
            info['section'] = ""
            info['day'] = ""
            info['time'] = ""
            info['building'] = ""
            info['room'] = ""
            entries.append(info)
            continue
        for c in entry['classes']:
            section = c['section']
            entry_info = copy.deepcopy(info)
            entry_info['section'] = section
            entry_info['day'] = c['days']
            entry_info['time'] = c['starttime'].split(" ")[0][0:5]+"-"+ \
                                 c['endtime'].split(" ")[0][0:5]
            entry_info['building'] = c['bldg']
            entry_info['building_id'] = c['bldg_id']
            entry_info['room'] = c['roomnum']
            entries.append(entry_info)
    return entries

# Add building lon and lat for each course section
def add_bldg(sections, bldgs):
    for section in sections:
        try:
            bldg = section['building_id']
            section['building_lat'] = bldgs[bldg]['lat']
            section['building_lon'] = bldgs[bldg]['lon']
        except KeyError:
            section['building_lat'] = ''
            section['building_lon'] = ''
            #sys.stderr.write("No building data for room: "+section['building']+
            #                 section['course'][0]+" "+section['number'][0]+section['section']+"\n")
    return sections

# Convert into a form that can be put into the database
def convert_db(data):
    pk=1
    ret = []
    for ent in data:
        temp = {}
        temp['pk'] = pk
        temp['model'] = "classes.section"
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
converted = convert_db(combined)

with open('data.json', 'w') as fp:
    json.dump(converted, fp)
