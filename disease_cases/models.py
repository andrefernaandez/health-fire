from django.db import models
from health.models import TypeContent, CID


class DiseaseCase(models.Model):
    type_health = models.ForeignKey(TypeContent, on_delete=models.CASCADE)
    cid = models.ForeignKey(CID, on_delete=models.CASCADE)
    federative_unit_name = models.CharField(max_length=100)
    register_at = models.DateField()
    value = models.CharField(max_length=100)
    file = models.ForeignKey('importer.ImportFile', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type_health.name} - {self.cid.name} ({self.month_year})"
