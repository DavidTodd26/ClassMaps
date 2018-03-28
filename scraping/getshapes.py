import requests
import json
import re
import math
import sys

dormids = json.load(open('dormids.json'))

def xyToLatLong(p):
  x, y = p
  earth_radius = 6378137
  return [(x / earth_radius)/math.pi * 180,
          90 - (math.atan(math.exp(-y/earth_radius)))*360/math.pi]

def toGeoJsonEntry(d):
    try:
        return {
            'type': 'Feature',
            'properties': {
                'id': d['id']
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': d['coords']
            }
        }
    except:
        c = []
        return {
            'type': 'Feature',
            'properties': {
                'id': d['id']
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': c
            }
        }

for id in dormids:
    d = dormids[id]
    target_url = 'http://m.princeton.edu/map/campus?feed=91eda3cbe8&group=princeton&featureindex=' + d['id']
    try:
        r = requests.get(target_url)
        coord_string = re.search('esri\.geometry\.Polygon\(\{"rings":(\[.*\]\]\])', r.text).group(1)
        coords = json.loads(coord_string)
        d['coords'] = map(lambda x: map(xyToLatLong, x), coords)
    except Exception as e:
        print "Error loading coordinates:", d['name'], d['id'], target_url

features = map(toGeoJsonEntry, dormids.values())
geo_json = {
    'type': 'FeatureCollection',
    'features': features
}

print json.dumps(geo_json)
