from django.contrib import admin
from .models import ImportFile
from .tasks import process_file_health

@admin.register(ImportFile)
class ImportFileAdmin(admin.ModelAdmin):
    list_display = ('type', 'file', 'uploaded_at')
    list_filter = ('type', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        process_file_health.delay(obj.id) 
