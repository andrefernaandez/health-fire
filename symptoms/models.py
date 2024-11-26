from django.db import models
from health.models import TypeContent, CID

class Symptoms(models.Model):
    type_health = models.ForeignKey(TypeContent, on_delete=models.CASCADE)
    cid = models.ForeignKey(CID, on_delete=models.CASCADE)
    federative_unit = models.CharField(max_length=100)
    month_year = models.DateField()
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type_health.name} - {self.cid.name} ({self.month_year})"
