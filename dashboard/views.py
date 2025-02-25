from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
from symptoms.models import Symptoms
from burned.models import Burned
from django.shortcuts import render

@api_view(['GET'])
def evolucao_temporal(request):
    data = Burned.objects.values('register_at__year', 'register_at__month')\
        .annotate(total_queimadas=Count('id'))\
        .order_by('register_at__year', 'register_at__month')
    
    symptoms_data = Symptoms.objects.values('month_year__year', 'month_year__month')\
        .annotate(total_casos=Count('id'))\
        .order_by('month_year__year', 'month_year__month')
    
    return Response({
        'queimadas': [{'year': d['register_at__year'], 'month': d['register_at__month'], 'total': d['total_queimadas']} for d in data],
        'saude': [{'year': s['month_year__year'], 'month': s['month_year__month'], 'total': s['total_casos']} for s in symptoms_data]
    })

@api_view(['GET'])
def distribuicao_geografica(request):
    queimadas_por_estado = Burned.objects.values('city__name')\
        .annotate(total_queimadas=Count('id'))
    
    saude_por_estado = Symptoms.objects.values('federative_unit')\
        .annotate(total_casos=Count('id'))
    
    return Response({'queimadas': list(queimadas_por_estado), 'saude': list(saude_por_estado)})

@api_view(['GET'])
def correlacao_queimadas_saude(request):
    # Agrupar queimadas por mês e ano
    dados = Burned.objects.values('register_at__year', 'register_at__month')\
        .annotate(total_queimadas=Count('id'))\
        .order_by('register_at__year', 'register_at__month')


    saude = Symptoms.objects.values('month_year__year', 'month_year__month', 'value')\
        .order_by('month_year__year', 'month_year__month')

    # Substituir valores inválidos de fire_risk
    for d in dados:
        if 'fire_risk' in d and d['fire_risk'] == -999:
            d['fire_risk'] = 0

    return Response({
        'queimadas': [{'year': d['register_at__year'], 'month': d['register_at__month'], 'total_queimadas': d['total_queimadas']} for d in dados],
        'saude': [{'year': s['month_year__year'], 'month': s['month_year__month'], 'total_casos': s['value']} for s in saude]
    })


@api_view(['GET'])
def impacto_clima_queimadas(request):
    clima_queimadas = Burned.objects.values('no_rain_days', 'precipitation', 'fire_risk')\
        .annotate(total_queimadas=Count('id'))
    

    for cq in clima_queimadas:
        if cq['no_rain_days'] == -999:
            cq['no_rain_days'] = 0
        if cq['fire_risk'] == -999:
            cq['fire_risk'] = 0
    
    return Response({'impacto': list(clima_queimadas)})

def relatorios(request):
    return render(request, "dashboard/relatorios.html")
