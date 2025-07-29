from django.http import HttpResponse

def disease_cases_data(request):
    return HttpResponse("Dados de casos de doenças")
