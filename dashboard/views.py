from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
from disease_cases.models import DiseaseCase
from burned.models import Burned
from django.shortcuts import render
from django.db.models.functions import TruncMonth


@api_view(['GET'])
def evolucao_temporal(request):
    data = Burned.objects.values('register_at__year', 'register_at__month')\
        .annotate(total_queimadas=Count('id'))\
        .order_by('register_at__year', 'register_at__month')
    
    disease_data = DiseaseCase.objects.values('month_year__year', 'month_year__month')\
        .annotate(total_casos=Count('id'))\
        .order_by('month_year__year', 'month_year__month')
    
    return Response({
        'queimadas': [{'year': d['register_at__year'], 'month': d['register_at__month'], 'total': d['total_queimadas']} for d in data],
        'saude': [{'year': s['month_year__year'], 'month': s['month_year__month'], 'total': s['total_casos']} for s in disease_data]
    })


@api_view(['GET'])
def distribuicao_geografica(request):
    queimadas_por_estado = Burned.objects.values('federative_unit__name')\
        .annotate(total_queimadas=Count('id'))\
        .order_by('federative_unit__name')

    saude_por_estado = DiseaseCase.objects.values('federative_unit_name')\
        .annotate(total_casos=Count('id'))\
        .order_by('federative_unit_name')

    return Response({
        'queimadas': [{'estado': q['federative_unit__name'], 'total_queimadas': q['total_queimadas']} for q in queimadas_por_estado],
        'saude': [{'estado': s['federative_unit_name'], 'total_casos': s['total_casos']} for s in saude_por_estado]
    })


@api_view(['GET'])
def correlacao_queimadas_saude(request):
    # Agrupar queimadas por mês e ano
    dados = Burned.objects.values('register_at__year', 'register_at__month')\
        .annotate(total_queimadas=Count('id'))\
        .order_by('register_at__year', 'register_at__month')

    # Dados de saúde com conversão de 'value'
    saude = DiseaseCase.objects.values('month_year__year', 'month_year__month', 'value')\
        .order_by('month_year__year', 'month_year__month')

    # Conversão de valor textual para número
    saude_corrigido = []
    for s in saude:
        try:
            valor_convertido = float(s['value'].replace(',', '.'))  # caso venha com vírgula
        except (ValueError, AttributeError):
            valor_convertido = 0  # ou continue para ignorar

        saude_corrigido.append({
            'year': s['month_year__year'],
            'month': s['month_year__month'],
            'total_casos': valor_convertido
        })

    return Response({
        'queimadas': [
            {
                'year': d['register_at__year'],
                'month': d['register_at__month'],
                'total_queimadas': d['total_queimadas']
            } for d in dados
        ],
        'saude': saude_corrigido
    })




@api_view(['GET'])
def impacto_clima_queimadas(request):
    clima_queimadas = Burned.objects.values('no_rain_days', 'precipitation', 'fire_risk')\
        .annotate(total_queimadas=Count('id'))

    for cq in clima_queimadas:
        cq['no_rain_days'] = cq.get('no_rain_days', 0) or 0
        cq['fire_risk'] = cq.get('fire_risk', 0) or 0

    return Response({'impacto': list(clima_queimadas)})


def relatorios(request):
    return render(request, "dashboard/relatorios.html")
