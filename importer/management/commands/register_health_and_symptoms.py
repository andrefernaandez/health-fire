from health.models import TypeContent, CID
from symptoms.models import Symptoms
from importer.models import ImportFile
from django.utils import timezone

def register_health_and_symptoms(import_file_id):
    try:
        # Recupera o objeto ImportFile pelo ID
        import_file = ImportFile.objects.get(id=import_file_id)

        # Verifica se o arquivo foi processado corretamente
        if import_file.status != ImportFile.STATUS_FINALLY:
            raise Exception("O arquivo não foi processado corretamente.")

        # Chama o process_health_file e retorna processed_data
        processed_data = process_health_file(import_file.file.path)

        header_info = processed_data["header_info"]
        data_list = processed_data["data"]

        # Criar ou recuperar os objetos TypeContent e CID
        type_health, _ = TypeContent.objects.get_or_create(name=header_info["tipo_dado"])
        cid, _ = CID.objects.get_or_create(name=header_info["cid_capitulo"])

        # Salvar os dados no banco
        for line in data_list:
            federative_unit = line.get("unidade_federacao")
            if federative_unit:
                Symptoms.objects.create(
                    type_health=type_health,
                    cid=cid,
                    federative_unit=federative_unit,
                    month_year=line["data"],  # Usando a data completa (mês e ano)
                    value=line["valor"],
                    file=import_file,
                )

        print("Dados registrados com sucesso!")

    except Exception as e:
        print(f"Erro ao registrar dados: {e}")
