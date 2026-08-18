from django.db import models
from health.models import TypeContent, CID


class DiseaseCase(models.Model):
    type_health = models.ForeignKey(TypeContent, on_delete=models.CASCADE)
    cid = models.ForeignKey(CID, on_delete=models.CASCADE)
    federative_unit_name = models.CharField(max_length=100)
    register_at = models.DateTimeField()
    value = models.CharField(max_length=100)
    file = models.ForeignKey('importer.ImportFile', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type_health.name} - {self.cid.name} {self.register_at}"


class SivepSrag(models.Model):
    id = models.AutoField(primary_key=True)
    nu_notific = models.CharField(max_length=30, null=True, blank=True)
    dt_interna = models.DateField(null=True, blank=True)
    sg_uf = models.CharField(max_length=2)
    co_mun_res = models.IntegerField(null=True, blank=True)
    classi_fin = models.SmallIntegerField(null=True, blank=True)
    evolucao = models.SmallIntegerField(null=True, blank=True)
    cs_sexo = models.CharField(max_length=1, null=True, blank=True)
    nu_idade_n = models.IntegerField(null=True, blank=True)

    file = models.ForeignKey('importer.ImportFile', on_delete=models.CASCADE)

    class Meta:
        db_table = "sivep_srag"

    def __str__(self):
        return f"SIVEP SRAG {self.nu_notific} - {self.sg_uf}"
    

    