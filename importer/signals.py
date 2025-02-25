from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import process_file_health, process_file_burned
from .models import ImportFile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ImportFile)
def process_file_when_created(sender, instance, created, **kwargs):
    if created and instance.status == ImportFile.STATUS_OPEN:
        # Adiciona log para garantir que o ImportFile foi salvo corretamente
        logger.info(f"ImportFile com ID {instance.id} criado. Tipo: {instance.type}, Status: {instance.status}")

        instance.status = ImportFile.STATUS_PROGRESS
        instance.save()  # Salva o status atualizado

        if instance.type == ImportFile.TYPE_HEALTH:
            process_file_health(instance.id)
        elif instance.type == ImportFile.TYPE_FIRE:
            process_file_burned(instance.id)
