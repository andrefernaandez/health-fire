from celery import shared_task
from importer.utils import process_health_file, process_burned_file
from health.models import TypeContent, CID
from disease_cases.models import DiseaseCase
from importer.models import ImportFile
from burned.models import Burned
from geo_data.models import Biome, City, Satellite, FederativeUnit
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
                federative_unit_name = line.get("unidade_federacao")

                if not federative_unit_name:
                    print(f"Linha ignorada: 'Unidade da Federação' ausente. Dados: {line}")
                    continue  # Ignorar linha se o valor estiver ausente

                # Criar instância de disease_cases no banco
                disease=DiseaseCase.objects.filter(
                    type_health=type_health,
                    cid=cid,
                    federative_unit_name=federative_unit_name,
                    month_year__month=line["data"].month,
                      month_year__year=line["data"].year,  # Usando a data completa
                    value=line["valor"],
                ).first()
                if not disease:
                    DiseaseCase.objects.create(
                    type_health=type_health,
                    cid=cid,
                    federative_unit_name=federative_unit_name,
                    register_at=line["data"],  # Usando a data completa
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
    
    # Coleta os nomes únicos
    city_keys = set((line["city"].strip(), line["federative_unit"].strip()) for line in data_list if line["city"].strip())
    biome_names = set(line["biome"].strip() for line in data_list if line["biome"].strip())
    satellite_names = set(line["satellite"].strip() for line in data_list if line["satellite"].strip())
    federative_names = set(line["federative_unit"].strip() for line in data_list if line["federative_unit"].strip())

    # Busca os objetos existentes
    federatives = {fu.name: fu for fu in FederativeUnit.objects.filter(name__in=federative_names)}
    cities = {(city.name, city.federative_unit.name): city for city in City.objects.select_related("federative_unit").all()}
    biomes = {b.name: b for b in Biome.objects.filter(name__in=biome_names)}
    satellites = {s.name: s for s in Satellite.objects.filter(name__in=satellite_names)}

    # Cria FederativeUnit ausentes
    new_federatives = [FederativeUnit(name=name) for name in federative_names if name not in federatives]
    FederativeUnit.objects.bulk_create(new_federatives)
    federatives.update({fu.name: fu for fu in FederativeUnit.objects.filter(name__in=federative_names)})

    # Cria City ausentes
    new_cities = []
    for name, state in city_keys:
        if (name, state) not in cities:
            fu = federatives.get(state)
            if fu:
                new_cities.append(City(name=name, federative_unit=fu))
    City.objects.bulk_create(new_cities)
    cities.update({(c.name, c.federative_unit.name): c for c in City.objects.select_related("federative_unit").all()})

    # Cria Biome e Satellite ausentes
    Biome.objects.bulk_create([Biome(name=name) for name in biome_names if name not in biomes])
    Satellite.objects.bulk_create([Satellite(name=name) for name in satellite_names if name not in satellites])
    biomes.update({b.name: b for b in Biome.objects.filter(name__in=biome_names)})
    satellites.update({s.name: s for s in Satellite.objects.filter(name__in=satellite_names)})

    # Processa as instâncias de Burned
    burned_instances = []

    for line in data_list:
        try:
            register_at = datetime.strptime(line["register_at"].strip(), "%d/%m/%Y %H:%M")
            city_key = (line["city"].strip(), line["federative_unit"].strip())
            city = cities.get(city_key)

            if not city:
                logger.warning(f"Cidade não encontrada: {city_key}")
                continue

            burned_instance = Burned(
                register_at=register_at,
                city=city,
                biome=biomes.get(line["biome"].strip()),
                satellite=satellites.get(line["satellite"].strip()),
                latitude=line["latitude"],
                longitude=line["longitude"],
                no_rain_days=0 if math.isnan(line["no_rain_days"]) else line["no_rain_days"],
                precipitation=0 if math.isnan(line["precipitation"]) else line["precipitation"],
                fire_risk=0 if math.isnan(line["fire_risk"]) else line["fire_risk"],
                frp=0 if math.isnan(line["frp"]) else line["frp"],
                federative_unit=city.federative_unit,
                file=import_file,
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
