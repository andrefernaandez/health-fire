from django.urls import path
from .views import (
    evolucao_temporal,
    distribuicao_geografica,
    correlacao_queimadas_saude,
    impacto_clima_queimadas,
    relatorios
)
from django.shortcuts import render

urlpatterns = [
    path('dashboard/', lambda request: render(request, 'dashboard.html'), name='dashboard'),
    path('evolucao-temporal/', evolucao_temporal, name='evolucao_temporal'),
    path('distribuicao-geografica/', distribuicao_geografica, name='distribuicao_geografica'),
    path('correlacao-queimadas-saude/', correlacao_queimadas_saude, name='correlacao_queimadas_saude'),
    path('impacto-clima-queimadas/', impacto_clima_queimadas, name='impacto_clima_queimadas'),
    path("relatorios/", relatorios, name="relatorios"),
]

