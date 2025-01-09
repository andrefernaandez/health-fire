from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import process_file_health
from .models import ImportFile

@receiver(post_save, sender=ImportFile)
def process_file_when_created(sender, instance, created, **kwargs):
    if created and instance.status == ImportFile.STATUS_OPEN:
        # Atualiza o status para 'Iniciado' (STATUS_PROGRESS)
        instance.status = ImportFile.STATUS_PROGRESS
        instance.save()  # Salva o status atualizado

        # Verifica se o tipo de arquivo é de saúde (TYPE_HEALTH)
        if instance.type == ImportFile.TYPE_HEALTH:

            process_file_health(instance.id)

        elif instance.type == ImportFile.TYPE_FIRE:

            pass
