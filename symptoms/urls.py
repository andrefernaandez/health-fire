from django.urls import path
from . import views



urlpatterns = [
    path('symptoms/', views.symptoms_data, name='symptoms_data'),  # Exemplo de URL
]

