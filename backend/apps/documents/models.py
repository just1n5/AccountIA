"""
Modelos para la gestión de documentos y declaraciones en AccountIA
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone


class Declaration(models.Model):
    """
    Modelo para representar una declaración de renta
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('paid', 'Pagada'),
        ('error', 'Error')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='declarations')
    fiscal_year = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2030)],
        help_text="Año gravable de la declaración"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Datos resumen de la declaración
    summary_data = models.JSONField(
        null=True, 
        blank=True,
        help_text="Resumen de ingresos, retenciones e impuestos calculados"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Campos adicionales
    notes = models.TextField(blank=True, help_text="Notas adicionales")
    
    class Meta:
        unique_together = ['user', 'fiscal_year']
        ordering = ['-created_at']
        verbose_name = "Declaración de Renta"
        verbose_name_plural = "Declaraciones de Renta"
    
    def __str__(self):
        return f"Declaración {self.fiscal_year} - {self.user.get_full_name() or self.user.username}"
    
    def mark_as_completed(self):
        """Marcar declaración como completada"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def get_total_income(self):
        """Obtener total de ingresos"""
        if self.summary_data:
            return self.summary_data.get('total_ingresos', 0)
        return 0
    
    def get_total_withholdings(self):
        """Obtener total de retenciones"""
        if self.summary_data:
            return self.summary_data.get('total_retenciones', 0)
        return 0
    
    def get_estimated_tax(self):
        """Obtener impuesto estimado"""
        if self.summary_data:
            return self.summary_data.get('impuesto_estimado', 0)
        return 0


class Document(models.Model):
    """
    Modelo para representar documentos subidos por los usuarios
    """
    
    UPLOAD_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('uploaded', 'Subido'),
        ('processing', 'Procesando'),
        ('processed', 'Procesado'),
        ('error', 'Error')
    ]
    
    FILE_TYPE_CHOICES = [
        ('exogena_report', 'Información Exógena'),
        ('income_certificate', 'Certificado de Ingresos'),
        ('deduction_invoice', 'Soporte de Deducción'),
        ('bank_certificate', 'Certificado Bancario'),
        ('medical_invoice', 'Factura Médica'),
        ('education_invoice', 'Factura Educación'),
        ('mortgage_certificate', 'Certificado Hipotecario'),
        ('pension_certificate', 'Certificado Pensiones'),
        ('other', 'Otro')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    declaration = models.ForeignKey(Declaration, on_delete=models.CASCADE, related_name='documents')
    
    # Información del archivo
    file_name = models.CharField(max_length=255, help_text="Nombre del archivo")
    original_filename = models.CharField(max_length=255, help_text="Nombre original del archivo")
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    storage_path = models.CharField(max_length=500, help_text="Ruta en Google Cloud Storage")
    file_size = models.BigIntegerField(null=True, blank=True, help_text="Tamaño en bytes")
    content_type = models.CharField(max_length=100, blank=True)
    
    # Estado del procesamiento
    upload_status = models.CharField(max_length=20, choices=UPLOAD_STATUS_CHOICES, default='pending')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Datos procesados
    processed_data = models.JSONField(
        null=True, 
        blank=True,
        help_text="Datos extraídos del documento"
    )
    
    # Manejo de errores
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
    
    def __str__(self):
        return f"{self.original_filename} - {self.get_file_type_display()}"
    
    def mark_as_processing(self):
        """Marcar documento como en procesamiento"""
        self.upload_status = 'processing'
        self.processing_started_at = timezone.now()
        self.save()
    
    def mark_as_processed(self, processed_data=None):
        """Marcar documento como procesado"""
        self.upload_status = 'processed'
        self.processing_completed_at = timezone.now()
        if processed_data:
            self.processed_data = processed_data
        self.save()
    
    def mark_as_error(self, error_message):
        """Marcar documento con error"""
        self.upload_status = 'error'
        self.error_message = error_message
        self.retry_count += 1
        self.save()
    
    def can_retry(self):
        """Verificar si se puede reintentar el procesamiento"""
        return self.retry_count < 3 and self.upload_status == 'error'
    
    def get_processing_duration(self):
        """Obtener duración del procesamiento"""
        if self.processing_started_at and self.processing_completed_at:
            return self.processing_completed_at - self.processing_started_at
        return None
    
    def is_exogena_file(self):
        """Verificar si es un archivo de información exógena"""
        return self.file_type == 'exogena_report'


class ProcessingLog(models.Model):
    """
    Modelo para registrar logs del procesamiento de documentos
    """
    
    LOG_LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='processing_logs')
    
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES)
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log de Procesamiento"
        verbose_name_plural = "Logs de Procesamiento"
    
    def __str__(self):
        return f"{self.level.upper()}: {self.message[:50]}"


class TaxConcept(models.Model):
    """
    Modelo para almacenar conceptos fiscales y su clasificación
    """
    
    CATEGORY_CHOICES = [
        ('rentas_trabajo', 'Rentas de Trabajo'),
        ('rentas_capital', 'Rentas de Capital'),
        ('rentas_no_laborales', 'Rentas No Laborales'),
        ('retenciones', 'Retenciones'),
        ('otros', 'Otros')
    ]
    
    code = models.CharField(max_length=10, unique=True, help_text="Código del concepto")
    name = models.CharField(max_length=200, help_text="Nombre del concepto")
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "Concepto Fiscal"
        verbose_name_plural = "Conceptos Fiscales"
    
    def __str__(self):
        return f"{self.code} - {self.name}"
