from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import process_file
from .models import ImportFile


@receiver(post_save, sender=ImportFile)
def process_file_when_created(sender, instance, created, **kwargs):
 
    if created and instance.status == ImportFile.STATUS_OPEN:
        # Atualiza o status para 'Iniciado' (STATUS_PROGRESS)
        ImportFile.objects.filter(id=instance.id).update(status=ImportFile.STATUS_PROGRESS)

        # Chama a tarefa Celery para processar o arquivo
        process_file.delay(instance.id)
