from celery import shared_task
from importer.utils import process_health_file, process_burned_file
from health.models import TypeContent, CID
from symptoms.models import Symptoms
from importer.models import ImportFile
from burned.models import Burned
from geodata.models import Biome, City, Satellite
from django.utils import timezone
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


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






@shared_task
def process_file_burned(import_file_id):
    logger.info(f"Iniciando processamento do ImportFile ID: {import_file_id}")
    
    try:
        import_file = ImportFile.objects.get(id=import_file_id)
    except ImportFile.DoesNotExist:
        logger.error(f"ImportFile com ID {import_file_id} não encontrado.")
        return f"ImportFile com ID {import_file_id} não encontrado."
    
    import_file.status = ImportFile.STATUS_PROGRESS
    import_file.start_at = timezone.now()
    import_file.save()
    
    file_path = import_file.file.path
    processed_data = process_burned_file(file_path)
    data_list = processed_data["data"]

    logger.info(f"Total de registros processados: {len(data_list)}")
    
    city_names = set(line["city"].strip() for line in data_list if line["city"].strip())
    biome_names = set(line["biome"].strip() for line in data_list if line["biome"].strip())
    satellite_names = set(line["satellite"].strip() for line in data_list if line["satellite"].strip())
    
    cities = {city.name: city for city in City.objects.filter(name__in=city_names)}
    biomes = {biome.name: biome for biome in Biome.objects.filter(name__in=biome_names)}
    satellites = {sat.name: sat for sat in Satellite.objects.filter(name__in=satellite_names)}
    
    new_cities = [City(name=name) for name in city_names if name not in cities]
    new_biomes = [Biome(name=name) for name in biome_names if name not in biomes]
    new_satellites = [Satellite(name=name) for name in satellite_names if name not in satellites]
    
    City.objects.bulk_create(new_cities)
    Biome.objects.bulk_create(new_biomes)
    Satellite.objects.bulk_create(new_satellites)
    
    cities.update({city.name: city for city in City.objects.filter(name__in=city_names)})
    biomes.update({biome.name: biome for biome in Biome.objects.filter(name__in=biome_names)})
    satellites.update({sat.name: sat for sat in Satellite.objects.filter(name__in=satellite_names)})
    
    burned_instances = []

    for line in data_list:
        try:
            register_at = datetime.strptime(line["register_at"].strip(), "%d/%m/%Y %H:%M")
            city = cities.get(line["city"].strip())
            biome = biomes.get(line["biome"].strip(), None)
            satellite = satellites.get(line["satellite"].strip(), None)
            
            burned_instance = Burned(
                register_at=register_at,
                city=city,
                biome=biome,
                satellite=satellite,
                latitude=line["latitude"],
                longitude=line["longitude"],
                no_rain_days=0 if math.isnan(line["no_rain_days"]) else line["no_rain_days"],
                precipitation=0 if math.isnan(line["precipitation"]) else line["precipitation"],
                fire_risk=0 if math.isnan(line["fire_risk"]) else line["fire_risk"],
                frp=0 if math.isnan(line["frp"]) else line["frp"],
            )
            burned_instances.append(burned_instance)
        
        except Exception as e:
            logger.error(f"Erro ao processar a linha: {e}. Dados: {line}")
    
    Burned.objects.bulk_create(burned_instances)
    
    import_file.status = ImportFile.STATUS_FINALLY
    import_file.end_at = timezone.now()
    import_file.save()
    
    logger.info(f"Processamento do ImportFile ID {import_file_id} concluído.")
    return f"Arquivo {import_file.file.name} processado com sucesso!"
