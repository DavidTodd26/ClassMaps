import json
import re
import requests
import sys

# Parse strings of the form "<...>info<...>"
def strip_tags(line):
    return line.replace(">","<").split("<")[2]

# Parse matches
def clean(match):
    id = strip_tags(re.search("<location_code>.*?</location_code>", match).group())
    id = str(int(id)) # Remove leading zeroes
    name = strip_tags(re.search("<name>.*?</name>", match).group())
    name = name.replace("amp;","") # Remove encoding
    lon = strip_tags(re.search("<longitude>.*?</longitude>", match).group())
    lat = strip_tags(re.search("<latitude>.*?</latitude>", match).group())
    aliases = [strip_tags(line) for line in re.findall("<alias>.*?</alias>", match)]

    ret = {}
    ret["building_id"] = id
    ret["names"] = name
    for alias in aliases:
        ret["names"] += "/" + alias
    ret["lat"] = lat
    ret["lon"] = lon
    return ret

# Return all cleaned matches for regexp in a list
def scrape_all(regexp, feed):
    dat = {}
    for match in regexp.findall(feed):
        ent = clean(match)
        dat[ent["building_id"]] = ent
    return dat

# Places data feed
feed = requests.get("http://etcweb.princeton.edu/webfeeds/map/").text

# RE expression
get_bldgs = re.compile("<location_code>\d+</location_code><group>Building</group>.*?(?:</aliases>|<aliases/>)")

# Extract data
bldgs = scrape_all(get_bldgs, feed)

with open('buildids.json', 'w') as fp:
    json.dump(bldgs, fp)
