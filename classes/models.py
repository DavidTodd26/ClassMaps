from django.db import models

# Create your models here.
class Section(models.Model):
    building = models.CharField(max_length=200, default="")
    building_id = models.CharField(max_length=200, default="")
    building_lat = models.CharField(max_length=200, default="")
    building_lon = models.CharField(max_length=200, default="")
    profs = models.CharField(max_length=400, default="")
    room = models.CharField(max_length=200, default="")
    area = models.CharField(max_length=200, default="")
    section = models.CharField(max_length=200, default="")
    course = models.CharField(max_length=200, default="")
    day = models.CharField(max_length=200, default="")
    section = models.CharField(max_length=200, default="")
    title = models.CharField(max_length=200, default="")
    time = models.CharField(max_length=200, default="")
    number = models.CharField(max_length=200, default="")
