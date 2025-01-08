from celery import shared_task
from importer.utils import process_health_file
from health.models import TypeContent, CID
from symptoms.models import Symptoms
from importer.models import ImportFile
from django.utils import timezone

@shared_task
def process_file_health(import_file_id):
    try:
        # Recupera o objeto ImportFile pelo ID
        import_file = ImportFile.objects.get(id=import_file_id)

        import_file.status = ImportFile.STATUS_PROGRESS
        import_file.start_at = timezone.now()
        import_file.save()

        # Processa o arquivo CSV associado
        file_path = import_file.file.path
        processed_data = process_health_file(file_path)

        header_info = processed_data["header_info"]
        data_list = processed_data["data"]

        # Criar ou recuperar os objetos TypeContent e CID
        type_health, _ = TypeContent.objects.get_or_create(name=header_info["tipo_dado"])
        cid, _ = CID.objects.get_or_create(name=header_info["cid_capitulo"])

        # Salvar os dados no banco
        for line in data_list:
            try:
                federative_unit = line.get("unidade_federacao")

                if not federative_unit:
                    print(f"Linha ignorada: 'Unidade da Federação' ausente. Dados: {line}")
                    continue  # Ignorar linha se o valor estiver ausente

                # Criar instância de Symptoms no banco
                symtom=Symptoms.objects.filter(
                    type_health=type_health,
                    cid=cid,
                    federative_unit=federative_unit,
                    month_year__month=line["data"].month,
                      month_year__year=line["data"].year,  # Usando a data completa
                    value=line["valor"],
                ).first()
                if not symtom:
                    Symptoms.objects.create(
                    type_health=type_health,
                    cid=cid,
                    federative_unit=federative_unit,
                    month_year=line["data"],  # Usando a data completa
                    value=line["valor"],
                    file=import_file,
                )

            except Exception as e:
                print(f"Erro ao processar a linha: {e}. Dados: {line}")
                continue  # Continua processando as próximas linhas

        import_file.status = ImportFile.STATUS_FINALLY
        import_file.end_at = timezone.now()
        import_file.save()

        return f"Arquivo {import_file.file.name} processado com sucesso!"

    except ImportFile.DoesNotExist:
        raise Exception(f"ImportFile com ID {import_file_id} não encontrado.")
    except Exception as e:
        if 'import_file' in locals():
            # Atualiza o status para "aberto" em caso de falha
            import_file.status = ImportFile.STATUS_OPEN
            import_file.save()
        raise Exception(f"Erro ao processar o arquivo: {e}")