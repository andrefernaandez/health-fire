from django.contrib import admin
from .models import Burned

@admin.register(Burned)
class BurnedAdmin(admin.ModelAdmin):
    list_display = ("register_at", "satellite", "city", "biome", "fire_risk", "latitude", "longitude")
    search_fields = ("city__name", "biome__name", "satellite__name")
    list_filter = ("biome", "satellite")