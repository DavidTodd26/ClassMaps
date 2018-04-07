import json
import re
import urllib2

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

    ret = {}
    ret["id"] = id
    ret["name"] = name
    ret["lat"] = lat
    ret["lon"] = lon
    return ret

# Return all cleaned matches for regexp in a list
def scrape_all(regexp, feed):
    dat = {}
    for match in regexp.findall(feed):
        ent = clean(match)
        dat[ent["id"]] = ent
    return dat

# Places data feed
feed = urllib2.urlopen("http://etcweb.princeton.edu/webfeeds/map/").read()
#feed = "".join(feed.split())

# RE expression
get_bldgs = re.compile("<location_code>\d+</location_code><group>Building</group>.*?</latitude>")

# Extract data
bldgs = scrape_all(get_bldgs, feed)

with open('buildids.json', 'w') as fp:
    json.dump(bldgs, fp)
