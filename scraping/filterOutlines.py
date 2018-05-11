import json
from merge import find_building

with open('buildings_restricted.json') as handle:
    buildings = json.load(handle)

with open('outlines.geojson') as handle:
    outlines = json.load(handle)

filtered = []
for outline in outlines["features"]:
    name = outline["properties"]["name"]
    bldg_id, name = find_building(name, buildings)
    if bldg_id or outline["properties"]["building"] == "dormitory":
        filtered.append(outline)

outlines["features"] = filtered
with open('outlines_filtered.geojson', 'w') as handle:
    json.dump(outlines, handle)
