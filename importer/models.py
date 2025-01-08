from django.db import models


class ImportFile(models.Model):
    TYPE_HEALTH="health"
    TYPE_FIRE="fire"
    FILE_TYPE_CHOICES = [
        (TYPE_HEALTH, 'Saúde'),
        (TYPE_FIRE, 'Queimadas'),
    ]
    STATUS_OPEN = 1
    STATUS_PROGRESS = 2
    STATUS_FINALLY = 3
    FILE_STATUS_CHOICES = [
        (STATUS_OPEN, 'Aberto'),
        (STATUS_PROGRESS, 'Iniciado'),
        (STATUS_FINALLY, 'Finalizado'),
    ]
    type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=FILE_STATUS_CHOICES, default=1)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} - {self.file.name}"
