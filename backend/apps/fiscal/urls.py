"""
URLs para la API de análisis fiscal
"""
from django.urls import path
from . import views

app_name = 'fiscal'

urlpatterns = [
    # Endpoint principal de análisis
    path('analyze/', views.analyze_fiscal_data, name='analyze'),
    
    # Testing y debugging
    path('test-parser/', views.test_parser_only, name='test_parser'),
    
    # Información fiscal
    path('limits/', views.get_fiscal_limits, name='fiscal_limits'),
    
    # Simulaciones
    path('simulate-deductions/', views.simulate_deductions, name='simulate_deductions'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
