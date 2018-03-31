import requests
import json
import re
import math
import sys

buildids = json.load(open('buildids.json'))

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

for id in buildids:
    d = buildids[id]
    target_url = 'http://m.princeton.edu/map/campus?feed=91eda3cbe8&group=princeton&featureindex=' + id
    try:
        r = requests.get(target_url)
        coord_string = re.search('esri\.geometry\.Polygon\(\{"rings":(\[.*\]\]\])', r.text).group(1)
        coords = json.loads(coord_string)
        d['coords'] = map(lambda x: map(xyToLatLong, x), coords)
    except Exception as e:
        print "Error loading coordinates:", d['name'], id, target_url

features = map(toGeoJsonEntry, buildids.values())
geo_json = {
    'type': 'FeatureCollection',
    'features': features
}

with open('shapes.json', 'w') as fp:
    json.dump(geo_json, fp)
