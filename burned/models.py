from django.db import models
from geodata.models import Biome, City, Satellite

class Burned(models.Model):
    register_at = models.DateTimeField()
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    biome = models.ForeignKey(Biome, on_delete=models.CASCADE)
    no_rain_days = models.IntegerField()
    precipitation = models.FloatField()
    fire_risk = models.FloatField()
    latitude = models.CharField(max_length=15)  
    longitude = models.CharField(max_length=15)

    frp = models.FloatField()

    def __str__(self):
        return f"Burned at {self.register_at} - {self.city}"