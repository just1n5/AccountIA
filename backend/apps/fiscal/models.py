"""
Modelos para el módulo fiscal
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone


class FiscalAnalysisSession(models.Model):
    """
    Sesión de análisis fiscal para un usuario
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fiscal_sessions')
    session_id = models.UUIDField(unique=True)
    
    # Datos de entrada
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Resultados del análisis
    analysis_results = models.JSONField(default=dict)
    processing_time = models.FloatField(null=True, blank=True)
    
    # Estados
    status = models.CharField(max_length=20, choices=[
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('error', 'Error'),
    ], default='processing')
    
    # Metadatos
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sesión de Análisis Fiscal'
        verbose_name_plural = 'Sesiones de Análisis Fiscal'
    
    def __str__(self):
        return f"Análisis {self.session_id} - {self.user.username}"


class UserFiscalProfile(models.Model):
    """
    Perfil fiscal del usuario para personalizar análisis
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fiscal_profile')
    
    # Información personal
    has_dependents = models.BooleanField(default=False)
    dependents_count = models.PositiveIntegerField(default=0)
    
    # Preferencias de deducciones
    has_health_insurance = models.BooleanField(default=False)
    has_mortgage = models.BooleanField(default=False)
    has_afc_account = models.BooleanField(default=False)
    
    # Configuraciones
    prefers_conservative_analysis = models.BooleanField(default=True)
    wants_optimization_suggestions = models.BooleanField(default=True)
    
    # Metadatos
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil Fiscal de Usuario'
        verbose_name_plural = 'Perfiles Fiscales de Usuarios'
    
    def __str__(self):
        return f"Perfil fiscal - {self.user.username}"


class FiscalOptimizationRecommendation(models.Model):
    """
    Recomendaciones de optimización fiscal generadas
    """
    session = models.ForeignKey(FiscalAnalysisSession, on_delete=models.CASCADE, 
                               related_name='recommendations')
    
    # Detalles de la recomendación
    recommendation_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Impacto financiero
    potential_saving = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    effort_level = models.CharField(max_length=20, choices=[
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ], default='medium')
    
    # Estado
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ], default='medium')
    
    is_implemented = models.BooleanField(default=False)
    implemented_at = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-priority', '-potential_saving']
        verbose_name = 'Recomendación de Optimización'
        verbose_name_plural = 'Recomendaciones de Optimización'
    
    def __str__(self):
        return f"{self.title} - ${self.potential_saving or 0:,.0f}"
