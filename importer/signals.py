from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import process_file_health
from .models import ImportFile


@receiver(post_save, sender=ImportFile)
def process_file_when_created(sender, instance, created, **kwargs):
 
    if created and instance.status == ImportFile.STATUS_OPEN:
        # Atualiza o status para 'Iniciado' (STATUS_PROGRESS)
        import_file=ImportFile.objects.filter(id=instance.id)

        import_file.status=ImportFile.STATUS_PROGRESS
        import_file.save()
        if import_file.type==ImportFile.TYPE_HEALTH:

        # Chama a tarefa Celery para processar o arquivo 
            process_file_health(instance.id)

        elif import_file.type==ImportFile.TYPE_FIRE:
            pass
        #process file fire
