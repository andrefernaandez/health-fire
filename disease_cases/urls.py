from django.urls import path
from . import views


urlpatterns = [
    path('disease_cases/', views.disease_cases_data, name='disease_cases_data'),
]
