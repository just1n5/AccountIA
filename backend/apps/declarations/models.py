"""
Modelos de declaraciones fiscales.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Declaration(models.Model):
    """
    Representa una declaración de renta para un año fiscal específico.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('paid', 'Pagada'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='declarations',
        verbose_name='Usuario'
    )
    fiscal_year = models.IntegerField(
        verbose_name='Año fiscal',
        help_text='Año gravable de la declaración'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Datos del resumen
    total_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Ingresos totales'
    )
    total_withholdings = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Retenciones totales'
    )
    preliminary_tax = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Impuesto preliminar'
    )
    
    # Datos de la declaración procesada
    declaration_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos de la declaración',
        help_text='Datos estructurados de la declaración procesada'
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de completado'
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de pago'
    )
    
    # Información de procesamiento
    processing_errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Errores de procesamiento'
    )
    processing_warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Advertencias de procesamiento'
    )
    
    class Meta:
        verbose_name = 'Declaración'
        verbose_name_plural = 'Declaraciones'
        ordering = ['-fiscal_year', '-created_at']
        unique_together = [['user', 'fiscal_year']]
        indexes = [
            models.Index(fields=['user', '-fiscal_year']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Declaración {self.fiscal_year} - {self.user.email}"
    
    def mark_as_completed(self):
        """Marca la declaración como completada."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    def mark_as_paid(self):
        """Marca la declaración como pagada."""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'updated_at'])
    
    @property
    def is_editable(self):
        """Verifica si la declaración se puede editar."""
        return self.status in ['draft', 'processing', 'error']
    
    @property
    def has_documents(self):
        """Verifica si la declaración tiene documentos asociados."""
        return self.documents.exists()
    
    @property
    def balance(self):
        """Calcula el saldo (a pagar o a favor)."""
        if self.preliminary_tax is not None:
            return self.preliminary_tax - self.total_withholdings
        return None


class IncomeRecord(models.Model):
    """
    Representa un registro de ingreso individual extraído de la información exógena.
    """
    INCOME_TYPE_CHOICES = [
        ('salary', 'Salarios'),
        ('honorarios', 'Honorarios'),
        ('services', 'Servicios'),
        ('dividends', 'Dividendos'),
        ('interests', 'Intereses'),
        ('rental', 'Arrendamientos'),
        ('other', 'Otros'),
    ]
    
    SCHEDULE_CHOICES = [
        ('labor', 'Rentas de Trabajo'),
        ('capital', 'Rentas de Capital'),
        ('non_labor', 'Rentas No Laborales'),
        ('pensions', 'Pensiones'),
        ('dividends', 'Dividendos y Participaciones'),
    ]
    
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.CASCADE,
        related_name='income_records',
        verbose_name='Declaración'
    )
    
    # Información del tercero
    third_party_nit = models.CharField(
        max_length=20,
        verbose_name='NIT del tercero'
    )
    third_party_name = models.CharField(
        max_length=255,
        verbose_name='Nombre del tercero'
    )
    
    # Información del ingreso
    concept_code = models.CharField(
        max_length=10,
        verbose_name='Código del concepto',
        help_text='Código del concepto según la DIAN'
    )
    concept_description = models.CharField(
        max_length=255,
        verbose_name='Descripción del concepto'
    )
    income_type = models.CharField(
        max_length=20,
        choices=INCOME_TYPE_CHOICES,
        default='other',
        verbose_name='Tipo de ingreso'
    )
    
    # Valores
    gross_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor bruto'
    )
    withholding_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Retención practicada'
    )
    
    # Clasificación fiscal
    tax_schedule = models.CharField(
        max_length=20,
        choices=SCHEDULE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Cédula tributaria',
        help_text='Clasificación según cédulas del Estatuto Tributario'
    )
    
    # Información adicional
    period = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Período',
        help_text='Período del ingreso (ej: 2024-01)'
    )
    is_deductible = models.BooleanField(
        default=False,
        verbose_name='Es deducible'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas adicionales'
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Registro de Ingreso'
        verbose_name_plural = 'Registros de Ingresos'
        ordering = ['third_party_name', 'concept_code']
        indexes = [
            models.Index(fields=['declaration', 'income_type']),
            models.Index(fields=['tax_schedule']),
            models.Index(fields=['concept_code']),
        ]
    
    def __str__(self):
        return f"{self.third_party_name} - {self.concept_description}: ${self.gross_amount:,.0f}"
    
    @property
    def net_amount(self):
        """Calcula el valor neto (bruto - retenciones)."""
        return self.gross_amount - self.withholding_amount
