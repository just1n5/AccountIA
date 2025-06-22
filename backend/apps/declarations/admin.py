"""
Configuración del admin para declaraciones.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Declaration, IncomeRecord


@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    """
    Admin para declaraciones.
    """
    list_display = [
        'id',
        'user_email',
        'fiscal_year',
        'status_badge',
        'total_income_formatted',
        'total_withholdings_formatted',
        'balance_formatted',
        'document_count',
        'created_at'
    ]
    list_filter = [
        'status',
        'fiscal_year',
        'created_at',
        'completed_at'
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'id'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'completed_at',
        'paid_at',
        'balance',
        'is_editable',
        'has_documents',
        'processing_errors_display',
        'processing_warnings_display'
    ]
    fieldsets = (
        ('Información General', {
            'fields': ('id', 'user', 'fiscal_year', 'status')
        }),
        ('Datos Financieros', {
            'fields': (
                'total_income',
                'total_withholdings',
                'preliminary_tax',
                'balance'
            )
        }),
        ('Fechas', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
                'paid_at'
            )
        }),
        ('Procesamiento', {
            'fields': (
                'processing_errors_display',
                'processing_warnings_display',
                'declaration_data'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """
        Optimiza las consultas del admin.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user').annotate(
            doc_count=Count('documents')
        )
    
    def user_email(self, obj):
        """Muestra el email del usuario."""
        return obj.user.email
    user_email.short_description = 'Usuario'
    user_email.admin_order_field = 'user__email'
    
    def status_badge(self, obj):
        """Muestra el estado con un badge de color."""
        colors = {
            'draft': '#6c757d',
            'processing': '#ffc107',
            'completed': '#28a745',
            'paid': '#17a2b8',
            'error': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def total_income_formatted(self, obj):
        """Formatea el total de ingresos."""
        return f"${obj.total_income:,.0f}"
    total_income_formatted.short_description = 'Ingresos'
    total_income_formatted.admin_order_field = 'total_income'
    
    def total_withholdings_formatted(self, obj):
        """Formatea el total de retenciones."""
        return f"${obj.total_withholdings:,.0f}"
    total_withholdings_formatted.short_description = 'Retenciones'
    total_withholdings_formatted.admin_order_field = 'total_withholdings'
    
    def balance_formatted(self, obj):
        """Formatea el balance."""
        balance = obj.balance
        if balance is None:
            return '-'
        
        color = '#dc3545' if balance > 0 else '#28a745'
        label = 'A pagar' if balance > 0 else 'A favor'
        
        return format_html(
            '<span style="color: {};">${:,.0f} ({})</span>',
            color,
            abs(balance),
            label
        )
    balance_formatted.short_description = 'Balance'
    
    def document_count(self, obj):
        """Muestra el número de documentos."""
        count = obj.doc_count
        if count > 0:
            url = reverse('admin:documents_document_changelist') + f'?declaration__id__exact={obj.id}'
            return format_html('<a href="{}">{} documentos</a>', url, count)
        return '0 documentos'
    document_count.short_description = 'Documentos'
    
    def processing_errors_display(self, obj):
        """Muestra los errores de procesamiento."""
        if obj.processing_errors:
            errors_html = '<br>'.join(f'• {error}' for error in obj.processing_errors)
            return format_html('<div style="color: #dc3545;">{}</div>', errors_html)
        return 'Sin errores'
    processing_errors_display.short_description = 'Errores'
    
    def processing_warnings_display(self, obj):
        """Muestra las advertencias de procesamiento."""
        if obj.processing_warnings:
            warnings_html = '<br>'.join(f'• {warning}' for warning in obj.processing_warnings)
            return format_html('<div style="color: #ffc107;">{}</div>', warnings_html)
        return 'Sin advertencias'
    processing_warnings_display.short_description = 'Advertencias'


@admin.register(IncomeRecord)
class IncomeRecordAdmin(admin.ModelAdmin):
    """
    Admin para registros de ingresos.
    """
    list_display = [
        'id',
        'declaration_link',
        'third_party_name',
        'concept_code',
        'income_type_badge',
        'gross_amount_formatted',
        'withholding_amount_formatted',
        'tax_schedule_badge'
    ]
    list_filter = [
        'income_type',
        'tax_schedule',
        'is_deductible',
        'declaration__fiscal_year'
    ]
    search_fields = [
        'third_party_name',
        'third_party_nit',
        'concept_code',
        'concept_description'
    ]
    readonly_fields = [
        'id',
        'net_amount',
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Declaración', {
            'fields': ('declaration',)
        }),
        ('Información del Tercero', {
            'fields': (
                'third_party_nit',
                'third_party_name'
            )
        }),
        ('Información del Ingreso', {
            'fields': (
                'concept_code',
                'concept_description',
                'income_type',
                'gross_amount',
                'withholding_amount',
                'net_amount'
            )
        }),
        ('Clasificación Fiscal', {
            'fields': (
                'tax_schedule',
                'is_deductible',
                'period'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'notes',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """
        Optimiza las consultas del admin.
        """
        qs = super().get_queryset(request)
        return qs.select_related('declaration', 'declaration__user')
    
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
    
    def income_type_badge(self, obj):
        """Badge para el tipo de ingreso."""
        colors = {
            'salary': '#007bff',
            'honorarios': '#6f42c1',
            'services': '#e83e8c',
            'dividends': '#fd7e14',
            'interests': '#20c997',
            'rental': '#ffc107',
            'other': '#6c757d'
        }
        color = colors.get(obj.income_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_income_type_display()
        )
    income_type_badge.short_description = 'Tipo'
    income_type_badge.admin_order_field = 'income_type'
    
    def tax_schedule_badge(self, obj):
        """Badge para la cédula tributaria."""
        if not obj.tax_schedule:
            return '-'
        
        colors = {
            'labor': '#007bff',
            'capital': '#28a745',
            'non_labor': '#ffc107',
            'pensions': '#17a2b8',
            'dividends': '#e83e8c'
        }
        color = colors.get(obj.tax_schedule, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_tax_schedule_display()
        )
    tax_schedule_badge.short_description = 'Cédula'
    tax_schedule_badge.admin_order_field = 'tax_schedule'
    
    def gross_amount_formatted(self, obj):
        """Formatea el monto bruto."""
        return f"${obj.gross_amount:,.0f}"
    gross_amount_formatted.short_description = 'Valor Bruto'
    gross_amount_formatted.admin_order_field = 'gross_amount'
    
    def withholding_amount_formatted(self, obj):
        """Formatea el monto de retención."""
        return f"${obj.withholding_amount:,.0f}"
    withholding_amount_formatted.short_description = 'Retención'
    withholding_amount_formatted.admin_order_field = 'withholding_amount'
