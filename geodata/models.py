from django.db import models


class Biome(models.Model):
    name = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Satellite(models.Model):
    name = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.name
