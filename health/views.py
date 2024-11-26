from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadForm
import csv


def home(request):
    return HttpResponse("Página Inicial - Bem-vindo ao HealthFire!")


def upload_csv(request):
    if request.method == 'POST' and request.FILES['file']:
        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Não é um arquivo CSV.", status=400)

        if csv_file.multiple_chunks():
            return HttpResponse("O arquivo é muito grande.", status=400)

        # Processar o arquivo CSV
        csv_data = csv.reader(csv_file.read().decode('utf-8').splitlines())
        header = next(csv_data)

        for row in csv_data:
            # Lógica para processar cada linha
            print(row)

        return HttpResponse("Arquivo CSV enviado e processado com sucesso!")
    else:
        form = UploadForm()
    # Atualize o caminho do template aqui:
    return render(request, 'health/upload.html', {'form': form})
