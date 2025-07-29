from django.db import models

class FederativeUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)  

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255)
    federative_unit = models.ForeignKey(FederativeUnit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"     

class Biome(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Satellite(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name