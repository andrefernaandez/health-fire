from django.contrib import admin
from .models import DiseaseCase, SivepSrag


@admin.register(DiseaseCase)
class DiseaseCaseAdmin(admin.ModelAdmin):
    pass


@admin.register(SivepSrag)
class SivepSragAdmin(admin.ModelAdmin):
    list_display = ("nu_notific", "sg_uf", "dt_interna")
    search_fields = ("nu_notific",)