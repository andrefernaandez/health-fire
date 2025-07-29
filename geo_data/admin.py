from django.contrib import admin
from .models import City, Biome, Satellite

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',)


@admin.register(Biome)
class BiomeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
