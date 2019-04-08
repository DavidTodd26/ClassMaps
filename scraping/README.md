## Updating the Database and Building outlines

### Requirements

It is strongly recommended, though not strictly necessary, to create a new
environment with virtualenv or a similar tool.

#### Updating Database
1. Python 3.6
2. Django 2.0.4
3. PostgreSQL 10.3

Temporarily replace .../classmaps/settings.py with settings_offline.py.

Also create a new database by opening a terminal window and running:

  initdb /usr/local/var/postgres -E utf8
  
  createdb ps_classes

#### Updating Building Outlines
1. QGIS 3 (https://qgis.org/en/site/forusers/download.html)

### Introduction

Course data is scraped from the course registrar, and building data is scraped
from Princeton webfeeds using the scripts in the .../scraping/ directory. All
future filepaths will be relative to this folder. The data is then moved into a
Heroku hosted Postgres database with the following steps, each of which will be
explained in more detail:
1. Scrape the raw data and format as a json file
2. Process the raw data into another json file
3. Add this json to a local Postgres database
4. Move the elements from the local database to the Heroku database

Besides the courses and buildings, building outlines were also obtained from
OpenStreetMap's API and processed using QCIS 3.

### Scrape the Raw Data

Course data is saved to a courses.json file by running:

  python scraper.py > courses.json

Occasionally, a connection times out for one or more courses, which prints an
error with the corresponding course id number. These missed courses can then be
recovered by running the scrape_id() function. If all runs smoothly, nothing
should be printed. Expected runtime is ~15 minutes from a normal laptop.

For each course, the professors, sections, meetings times, building locations,
and other pertinent information is retrieved.

Note: The TERM_CODE variable must be updated to the appropriate semester.


Building data is saved to buildids.json obtained by running:

  python getbuildids.py

For each building, the longitude, latitude, name, and id number is retrieved.

Rerunning this script is not usually necessary since buildings do not change much.

### Process the Data

The raw data (courses.json and buildids.json) is cleaned by running:

  python merge.py

This script separated classes into their sections, resolves discrepancy between
building names, and prepares the data to be inputted into a database. The
merge.py script outputs 3 files:
1. course_data.json: courses ready to be added to a database
2. building_data.json: buildings ready to be added to a database
3. buildings_restricted.json: buildings that have at least one class, which is
needed to filter building outlines, which is discussed later.

### Add Data to a Local Database

The processed data was loaded to a local PostgreSQL database by navigating to the
root directory of the project and running the two commands:

python manage.py loaddata course_data.json
python manage.py loaddata building_data.json

### Add Data to the Heroku Database

With the course and building information in a local database, the Heroku
database can be updated by running the following:

heroku login
heroku pg:reset
heroku pg:push ps_classes DATABASE_URL --app classmaps

This resets the Heroku database and makes it appear exactly as the local
database.

### Updating Building Outlines

From https://www.openstreetmap.org/#map=18/40.34917/-74.65574, using the 'Export'
button to select the appropriate rectangle that contains all buildings of interest.
This downloads the needed information as a .osm file.

Open QGIS 3, create a new Project, and from the Layer menu, select
Add Layer > Add Vector Layer. Choose the .osm file as the source, and only check
multipolygons in the popup that appears. On the main screen, right click on
the multipolygons layer in the lower left, and select Save As to export as
outlines.geojson

With outlines.geojson and buildings_restricted.json from above, open a terminal
window and run:

  python filterOutlines.py

This restricts the outlines to dorms and buildings with classes. Because of some
flakiness with OpenStreetMap, manual adjustments had to be made, such as
retagging some buildings as dorms.

The outputted outlines_filtered.geojson is copy-pasted into
.../classes/static/classes/buildings.js
