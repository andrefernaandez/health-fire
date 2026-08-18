from django.contrib import admin
from .models import ImportFile

@admin.register(ImportFile)
class ImportFileAdmin(admin.ModelAdmin):
    list_display = ('type', 'file', 'uploaded_at')
    list_filter = ('type', 'uploaded_at')
