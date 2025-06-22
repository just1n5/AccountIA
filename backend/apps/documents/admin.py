"""
Configuración del admin para documentos.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Document, DocumentTemplate


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin para documentos.
    """
    list_display = [
        'id_short',
        'declaration_link',
        'original_file_name',
        'file_type_badge',
        'upload_status_badge',
        'file_size_formatted',
        'uploaded_by_link',
        'created_at'
    ]
    list_filter = [
        'upload_status',
        'file_type',
        'encrypted',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'id',
        'original_file_name',
        'file_name',
        'declaration__user__email',
        'uploaded_by__email'
    ]
    readonly_fields = [
        'id',
        'file_name',
        'storage_path',
        'storage_url',
        'file_extension',
        'checksum',
        'is_processed',
        'has_errors',
        'get_storage_key',
        'processing_started_at',
        'processing_completed_at',
        'created_at',
        'updated_at',
        'processed_data_display',
        'processing_errors_display'
    ]
    fieldsets = (
        ('Información General', {
            'fields': (
                'id',
                'declaration',
                'file_type',
                'description'
            )
        }),
        ('Archivo', {
            'fields': (
                'original_file_name',
                'file_name',
                'file_size',
                'mime_type',
                'file_extension'
            )
        }),
        ('Almacenamiento', {
            'fields': (
                'storage_path',
                'storage_url',
                'get_storage_key',
                'encrypted',
                'checksum'
            )
        }),
        ('Estado de Procesamiento', {
            'fields': (
                'upload_status',
                'is_processed',
                'has_errors',
                'processing_started_at',
                'processing_completed_at',
                'processing_errors_display'
            )
        }),
        ('Datos Procesados', {
            'fields': ('processed_data_display',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': (
                'uploaded_by',
                'version',
                'is_active',
                'tags',
                'created_at',
                'updated_at'
            )
        })
    )
    
    def get_queryset(self, request):
        """
        Optimiza las consultas del admin.
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'declaration',
            'declaration__user',
            'uploaded_by'
        )
    
    def id_short(self, obj):
        """Muestra una versión corta del UUID."""
        return str(obj.id)[:8] + '...'
    id_short.short_description = 'ID'
    
    def declaration_link(self, obj):
        """Link a la declaración."""
        url = reverse('admin:declarations_declaration_change', args=[obj.declaration.id])
        return format_html(
            '<a href="{}">{} - {}</a>',
            url,
            obj.declaration.fiscal_year,
            obj.declaration.user.email
        )
    declaration_link.short_description = 'Declaración'
    
    def file_type_badge(self, obj):
        """Badge para el tipo de archivo."""
        colors = {
            'exogena_report': '#007bff',
            'income_certificate': '#28a745',
            'withholding_certificate': '#17a2b8',
            'bank_certificate': '#6f42c1',
            'health_invoice': '#e83e8c',
            'education_invoice': '#fd7e14',
            'mortgage_certificate': '#20c997',
            'pension_certificate': '#ffc107',
            'dependents_proof': '#6c757d',
            'other': '#6c757d'
        }
        color = colors.get(obj.file_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_file_type_display()
        )
    file_type_badge.short_description = 'Tipo'
    file_type_badge.admin_order_field = 'file_type'
    
    def upload_status_badge(self, obj):
        """Badge para el estado de carga."""
        colors = {
            'pending': '#6c757d',
            'uploading': '#ffc107',
            'uploaded': '#17a2b8',
            'processing': '#fd7e14',
            'processed': '#28a745',
            'error': '#dc3545'
        }
        color = colors.get(obj.upload_status, '#6c757d')
        
        # Agregar icono si está procesado o tiene error
        icon = ''
        if obj.upload_status == 'processed':
            icon = '✓ '
        elif obj.upload_status == 'error':
            icon = '✗ '
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}{}</span>',
            color,
            icon,
            obj.get_upload_status_display()
        )
    upload_status_badge.short_description = 'Estado'
    upload_status_badge.admin_order_field = 'upload_status'
    
    def file_size_formatted(self, obj):
        """Formatea el tamaño del archivo."""
        if not obj.file_size:
            return '-'
        
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_formatted.short_description = 'Tamaño'
    file_size_formatted.admin_order_field = 'file_size'
    
    def uploaded_by_link(self, obj):
        """Link al usuario que subió el archivo."""
        if not obj.uploaded_by:
            return '-'
        
        url = reverse('admin:auth_user_change', args=[obj.uploaded_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.email)
    uploaded_by_link.short_description = 'Subido por'
    
    def processed_data_display(self, obj):
        """Muestra los datos procesados de forma legible."""
        if not obj.processed_data:
            return 'Sin datos procesados'
        
        # Para archivos de exógena, mostrar resumen
        if obj.file_type == 'exogena_report' and 'stats' in obj.processed_data:
            stats = obj.processed_data['stats']
            return format_html(
                '<div>'
                '<strong>Registros:</strong> {} procesados de {}<br>'
                '<strong>Ingresos totales:</strong> ${}<br>'
                '<strong>Retenciones totales:</strong> ${}<br>'
                '<strong>Errores:</strong> {}<br>'
                '<strong>Advertencias:</strong> {}'
                '</div>',
                stats.get('processed_records', 0),
                stats.get('total_records', 0),
                stats.get('total_income', '0'),
                stats.get('total_withholdings', '0'),
                len(obj.processed_data.get('errors', [])),
                len(obj.processed_data.get('warnings', []))
            )
        
        # Para otros tipos, mostrar JSON formateado
        import json
        return format_html(
            '<pre style="white-space: pre-wrap;">{}</pre>',
            json.dumps(obj.processed_data, indent=2, ensure_ascii=False)
        )
    processed_data_display.short_description = 'Datos procesados'
    
    def processing_errors_display(self, obj):
        """Muestra los errores de procesamiento."""
        if not obj.processing_errors:
            return 'Sin errores'
        
        errors_html = '<br>'.join(f'• {error}' for error in obj.processing_errors)
        return format_html('<div style="color: #dc3545;">{}</div>', errors_html)
    processing_errors_display.short_description = 'Errores de procesamiento'
    
    actions = ['mark_for_reprocessing', 'soft_delete_documents']
    
    def mark_for_reprocessing(self, request, queryset):
        """Acción para marcar documentos para reprocesamiento."""
        count = 0
        for doc in queryset:
            if doc.upload_status == 'error':
                doc.upload_status = 'uploaded'
                doc.processing_errors = []
                doc.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} documento(s) marcado(s) para reprocesamiento.'
        )
    mark_for_reprocessing.short_description = 'Marcar para reprocesamiento'
    
    def soft_delete_documents(self, request, queryset):
        """Acción para hacer soft delete de documentos."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{count} documento(s) marcado(s) como inactivo(s).'
        )
    soft_delete_documents.short_description = 'Marcar como inactivo'


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    """
    Admin para plantillas de documentos.
    """
    list_display = [
        'name',
        'template_type',
        'is_active',
        'variables_count',
        'created_at',
        'updated_at'
    ]
    list_filter = [
        'is_active',
        'template_type',
        'created_at'
    ]
    search_fields = [
        'name',
        'description'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'variables_display'
    ]
    fieldsets = (
        ('Información General', {
            'fields': (
                'name',
                'description',
                'template_type',
                'is_active'
            )
        }),
        ('Contenido', {
            'fields': (
                'template_content',
                'variables',
                'variables_display'
            )
        }),
        ('Metadatos', {
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )
    
    def variables_count(self, obj):
        """Cuenta el número de variables."""
        return len(obj.variables) if obj.variables else 0
    variables_count.short_description = 'Variables'
    
    def variables_display(self, obj):
        """Muestra las variables de forma legible."""
        if not obj.variables:
            return 'Sin variables'
        
        variables_html = '<ul>'
        for var in obj.variables:
            if isinstance(var, dict):
                variables_html += f'<li><strong>{var.get("name", "?")}:</strong> {var.get("description", "")}</li>'
            else:
                variables_html += f'<li>{var}</li>'
        variables_html += '</ul>'
        
        return format_html(variables_html)
    variables_display.short_description = 'Variables disponibles'
