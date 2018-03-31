import json
import re
import urllib2

# Parse strings of the form <...>info<...>
def strip_tags(str):
    return str.replace(">","<").split("<")[2]

# Return all cleaned matches for regexp in a list
def scrape_all(regexp):
    dat = []
    for match in regexp.findall(feed):
        dat.append(strip_tags(match))
    return dat

# Places data feed
feed = urllib2.urlopen("http://etcweb.princeton.edu/webfeeds/places/").read()

# RE expressions
get_id = re.compile("<building_id>.*?</building_id>")
get_name = re.compile("<building_name>.*?</building_name>")
get_lon = re.compile("<longitude>.*?</longitude>")
get_lat = re.compile("<latitude>.*?</latitude>")

# Extract data
ids = scrape_all(get_id)
names = scrape_all(get_name)
lons = scrape_all(get_lon)
lats = scrape_all(get_lat)

# Combine and save to json
comb = {}
for i in range(0,len(ids)):
    place = ids[i]
    # Some places are listed more than once; only include the first
    if not place in comb:
        comb[place] = {}
        comb[place]["id"] = place
        comb[place]["name"] = names[i]
        comb[place]["lon"] = lons[i]
        comb[place]["lat"] = lats[i]

with open('buildids.json', 'w') as fp:
    json.dump(comb, fp)
