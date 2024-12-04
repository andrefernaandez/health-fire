from django.utils import timezone

from importer.utils import process_health_file, imprimir_linha_do_arquivo
from importer.models import ImportFile
from celery import shared_task


@shared_task
def process_file(file_id):
    try:
        import_file = ImportFile.objects.get(id=file_id)
        import_file.status = ImportFile.STATUS_PROGRESS
        import_file.start_at = timezone.now()
        import_file.save()
        file_path = import_file.file.path

        if import_file.type == 'health':
            result = process_health_file(file_path)
            print(f"Dados de saúde processados: {result['header_info']}")

            for line in result['data']:
                imprimir_linha_do_arquivo(line)
            return
        if import_file.type == 'fire':
            pass
            # result = process_health_file(file_path)
            # print(f"Dados de saúde processados: {result['header_info']}")
            #
            # for line in result['data']:
            #     imprimir_linha_do_arquivo(line)
        import_file.status = ImportFile.STATUS_FINALLY
        import_file.end_at = timezone.now()
        import_file.save()
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_id}: {e}")
