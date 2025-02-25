from django.contrib import admin
from .models import ImportFile
from .tasks import process_file_health, process_file_burned

@admin.register(ImportFile)
class ImportFileAdmin(admin.ModelAdmin):
    list_display = ('type', 'file', 'uploaded_at')
    list_filter = ('type', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Verifica o tipo do arquivo e chama a tarefa correspondente
        if obj.type == ImportFile.TYPE_HEALTH:
            process_file_health.delay(obj.id)
        elif obj.type == ImportFile.TYPE_FIRE:
            process_file_burned.delay(obj.id)
