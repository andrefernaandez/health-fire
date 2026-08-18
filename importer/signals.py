from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import process_file_health, process_file_burned, process_file_sivep_srag
from .models import ImportFile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ImportFile)
def process_file_when_created(sender, instance, created, **kwargs):
    if created and instance.status == ImportFile.STATUS_OPEN:
        instance.status = ImportFile.STATUS_PROGRESS
        instance.save()

        if instance.type == ImportFile.TYPE_HEALTH:
            process_file_health.delay(instance.id) 
        elif instance.type == ImportFile.TYPE_BURNED:
            process_file_burned.delay(instance.id)
        elif instance.type == ImportFile.TYPE_SIVEP_SRAG:
            process_file_sivep_srag.delay(instance.id)
