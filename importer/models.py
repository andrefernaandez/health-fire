from django.db import models

class ImportFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('health', 'Saúde'),
        ('fire', 'Queimadas'),
    ]
    type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.file.name}"
