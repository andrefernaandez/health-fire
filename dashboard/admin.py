from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Sum, Count
from symptoms.models import Symptoms
from burned.models import Burned
import json

class DashboardAdmin(admin.AdminSite):
    site_header = "Dashboard de Saúde e Queimadas"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        health_data = Symptoms.objects.values('month_year').annotate(total=Count('id'))
        burned_data = Burned.objects.values('register_at__year', 'register_at__month').annotate(total=Count('id'))
        
        health_labels = [f"{item['month_year'].year}-{item['month_year'].month}" for item in health_data]
        health_values = [item['total'] for item in health_data]
        burned_labels = [f"{item['register_at__year']}-{item['register_at__month']}" for item in burned_data]
        burned_values = [item['total'] for item in burned_data]
        
        burned_states = Burned.objects.values('city__federative_unit').annotate(total=Count('id'))
        state_labels = [item['city__federative_unit'] for item in burned_states]
        state_values = [item['total'] for item in burned_states]
        
        context = {
            'health_labels': json.dumps(health_labels),
            'health_values': json.dumps(health_values),
            'burned_labels': json.dumps(burned_labels),
            'burned_values': json.dumps(burned_values),
            'state_labels': json.dumps(state_labels),
            'state_values': json.dumps(state_values),
        }
        
        return TemplateResponse(request, "admin/dashboard.html", context)

admin_site = DashboardAdmin(name='dashboard_admin')
