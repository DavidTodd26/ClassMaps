from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import datetime


# A section of a course
class Section(models.Model):
    building = models.CharField(max_length=200, blank=True, null=True)
    building_id = models.CharField(max_length=200, blank=True, null=True)
    building_lat = models.CharField(max_length=200, blank=True, null=True)
    building_lon = models.CharField(max_length=200, blank=True, null=True)
    profs = ArrayField(models.CharField(max_length=100, blank=True, null=True), blank=True, null=True)
    room = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200, blank=True, null=True)
    section = models.CharField(max_length=200, blank=True, null=True)
    course = ArrayField(models.CharField(max_length=100, blank=True, null=True), blank=True, null=True)
    day = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    starttime = models.TimeField(blank=True, null=True)
    endtime = models.TimeField(blank=True, null=True)
    time = models.CharField(max_length=200, blank=True, null=True)
    number = ArrayField(models.CharField(max_length=100, blank=True, null=True), blank=True, null=True)
    enroll = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        courses = []
        for i in range(0, len(self.course)):
            courses.append(self.course[i]+" "+self.number[i])
        ret = "/".join(courses)
        return "/".join(courses)+" "+self.title+" "+self.section
