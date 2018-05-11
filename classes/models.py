from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
import re

# Natural keys for buildings
class BuildingManager(models.Manager):
    def get_by_natural_key(self, building_id):
        return self.get(building_id=building_id)

class Building(models.Model):
    objects = BuildingManager()

    names = models.CharField(max_length=1000, blank=True, null=True)
    building_id = models.IntegerField(default=-1)
    lat = models.CharField(max_length=200, blank=True, null=True)
    lon = models.CharField(max_length=200, blank=True, null=True)
    searched = models.IntegerField(default=0)

    def natural_key(self):
        return self.building_id

    def __str__(self):
        return self.names.split("/")[0]

# A section of a course, such as a precept or lecture
class Section(models.Model):
    course_id = models.CharField(max_length=10, blank=True, null=True)
    building = models.ForeignKey(Building, blank=True, null=True, on_delete=models.CASCADE)
    # Storing the name here speeds up the search in the heatmap
    building_name = models.CharField(max_length=100, blank=True, null=True)
    room = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200, blank=True, null=True)
    section = models.CharField(max_length=200, blank=True, null=True)
    listings = models.CharField(max_length=200, blank=True, null=True)
    day = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    starttime = models.TimeField(blank=True, null=True)
    endtime = models.TimeField(blank=True, null=True)
    time = models.CharField(max_length=200, blank=True, null=True)
    enroll = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.CharField(max_length=200, blank=True, null=True)
    searched = models.IntegerField(default=0)

    def __str__(self):
        return self.listings[1:]

class User(models.Model):
    netid = models.CharField(max_length=20, blank=True, null=True)
    courses = ArrayField(models.CharField(max_length=10, blank=True, null=True), default=list())
    buildings = ArrayField(models.CharField(max_length=10, blank=True, null=True), default=list())
