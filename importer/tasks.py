from importer.utils import process_health_file
from importer.models import ImportFile
from celery import shared_task

@shared_task
def process_file(file_id):
    try:
        import_file = ImportFile.objects.get(id=file_id)
        file_path = import_file.file.path  

        if import_file.type == 'health':
            result = process_health_file(file_path)
            print(f"Dados de saúde processados: {result['header_info']}")

            for line in result['data']:
                imprimir_linha_do_arquivo.delay(line)

        elif import_file.type == 'fire':
            print("Processar dados de queimadas")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_id}: {e}")

@shared_task
def imprimir_linha_do_arquivo(line):
    print(f"Linha do arquivo: {line}")
