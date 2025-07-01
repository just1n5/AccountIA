"""
Configuración del admin para el módulo fiscal
"""
from django.contrib import admin
from .models import FiscalAnalysisSession, UserFiscalProfile, FiscalOptimizationRecommendation


@admin.register(FiscalAnalysisSession)
class FiscalAnalysisSessionAdmin(admin.ModelAdmin):
    """Admin para sesiones de análisis fiscal"""
    list_display = ['session_id', 'user', 'status', 'processing_time', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'session_id', 'original_filename']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'session_id', 'status')
        }),
        ('Archivo de Entrada', {
            'fields': ('original_filename', 'file_size')
        }),
        ('Resultados', {
            'fields': ('processing_time', 'analysis_results'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserFiscalProfile)
class UserFiscalProfileAdmin(admin.ModelAdmin):
    """Admin para perfiles fiscales de usuarios"""
    list_display = ['user', 'has_dependents', 'dependents_count', 
                   'has_health_insurance', 'has_mortgage', 'updated_at']
    list_filter = ['has_dependents', 'has_health_insurance', 'has_mortgage', 'has_afc_account']
    search_fields = ['user__username', 'user__email']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Personal', {
            'fields': ('has_dependents', 'dependents_count')
        }),
        ('Deducciones', {
            'fields': ('has_health_insurance', 'has_mortgage', 'has_afc_account')
        }),
        ('Preferencias', {
            'fields': ('prefers_conservative_analysis', 'wants_optimization_suggestions')
        }),
    )


@admin.register(FiscalOptimizationRecommendation)
class FiscalOptimizationRecommendationAdmin(admin.ModelAdmin):
    """Admin para recomendaciones de optimización"""
    list_display = ['title', 'session', 'recommendation_type', 'priority', 
                   'potential_saving', 'effort_level', 'is_implemented']
    list_filter = ['recommendation_type', 'priority', 'effort_level', 'is_implemented']
    search_fields = ['title', 'description', 'session__user__username']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('session', 'recommendation_type', 'title', 'description')
        }),
        ('Impacto', {
            'fields': ('potential_saving', 'effort_level', 'priority')
        }),
        ('Estado', {
            'fields': ('is_implemented', 'implemented_at')
        }),
    )
    
    actions = ['mark_as_implemented']
    
    def mark_as_implemented(self, request, queryset):
        """Acción para marcar recomendaciones como implementadas"""
        from django.utils import timezone
        
        updated = queryset.update(
            is_implemented=True,
            implemented_at=timezone.now()
        )
        
        self.message_user(
            request,
            f'{updated} recomendaciones marcadas como implementadas.'
        )
    
    mark_as_implemented.short_description = "Marcar como implementadas"
