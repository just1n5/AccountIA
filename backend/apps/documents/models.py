"""
Modelos de documentos y archivos de soporte.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from apps.declarations.models import Declaration
import uuid
import os

User = get_user_model()


class Document(models.Model):
    """
    Representa un documento o archivo de soporte subido por el usuario.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('exogena_report', 'Información Exógena'),
        ('income_certificate', 'Certificado de Ingresos'),
        ('withholding_certificate', 'Certificado de Retenciones'),
        ('bank_certificate', 'Certificado Bancario'),
        ('health_invoice', 'Factura de Salud'),
        ('education_invoice', 'Factura de Educación'),
        ('mortgage_certificate', 'Certificado de Crédito Hipotecario'),
        ('pension_certificate', 'Certificado de Pensiones'),
        ('dependents_proof', 'Prueba de Dependientes'),
        ('other', 'Otro'),
    ]
    
    UPLOAD_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('uploading', 'Subiendo'),
        ('uploaded', 'Subido'),
        ('processing', 'Procesando'),
        ('processed', 'Procesado'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Declaración'
    )
    
    # Información del archivo
    file_name = models.CharField(
        max_length=255,
        verbose_name='Nombre del archivo'
    )
    original_file_name = models.CharField(
        max_length=255,
        verbose_name='Nombre original del archivo'
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Tamaño del archivo (bytes)'
    )
    file_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Tipo de documento'
    )
    mime_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Tipo MIME'
    )
    
    # Almacenamiento
    storage_path = models.CharField(
        max_length=500,
        verbose_name='Ruta de almacenamiento',
        help_text='Ruta en Google Cloud Storage'
    )
    storage_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='URL de descarga'
    )
    
    # Estado del procesamiento
    upload_status = models.CharField(
        max_length=20,
        choices=UPLOAD_STATUS_CHOICES,
        default='pending',
        verbose_name='Estado de carga'
    )
    
    # Datos procesados
    processed_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos procesados',
        help_text='Datos extraídos del documento'
    )
    
    # Metadatos de procesamiento
    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Inicio de procesamiento'
    )
    processing_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fin de procesamiento'
    )
    processing_errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Errores de procesamiento'
    )
    
    # Control de versiones
    version = models.IntegerField(
        default=1,
        verbose_name='Versión'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Seguridad
    checksum = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name='Checksum SHA256'
    )
    encrypted = models.BooleanField(
        default=True,
        verbose_name='Encriptado'
    )
    
    # Metadatos
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Subido por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    # Información adicional
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Etiquetas'
    )
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['declaration', 'file_type']),
            models.Index(fields=['upload_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_file_type_display()} - {self.original_file_name}"
    
    def get_storage_key(self):
        """Genera la clave de almacenamiento en GCS."""
        user_id = self.declaration.user.id
        declaration_id = self.declaration.id
        return f"users/{user_id}/declarations/{declaration_id}/documents/{self.id}/{self.file_name}"
    
    @property
    def is_processed(self):
        """Verifica si el documento ha sido procesado."""
        return self.upload_status == 'processed'
    
    @property
    def has_errors(self):
        """Verifica si el documento tiene errores de procesamiento."""
        return self.upload_status == 'error' or bool(self.processing_errors)
    
    @property
    def file_extension(self):
        """Obtiene la extensión del archivo."""
        return os.path.splitext(self.file_name)[1].lower()
    
    def mark_as_processing(self):
        """Marca el documento como en procesamiento."""
        from django.utils import timezone
        self.upload_status = 'processing'
        self.processing_started_at = timezone.now()
        self.save(update_fields=['upload_status', 'processing_started_at', 'updated_at'])
    
    def mark_as_processed(self, data=None):
        """Marca el documento como procesado."""
        from django.utils import timezone
        self.upload_status = 'processed'
        self.processing_completed_at = timezone.now()
        if data:
            self.processed_data = data
        self.save(update_fields=['upload_status', 'processing_completed_at', 'processed_data', 'updated_at'])
    
    def mark_as_error(self, errors):
        """Marca el documento con error."""
        from django.utils import timezone
        self.upload_status = 'error'
        self.processing_completed_at = timezone.now()
        if isinstance(errors, str):
            errors = [errors]
        self.processing_errors = errors
        self.save(update_fields=['upload_status', 'processing_completed_at', 'processing_errors', 'updated_at'])


class DocumentTemplate(models.Model):
    """
    Plantillas de documentos que el sistema puede generar.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    template_type = models.CharField(
        max_length=50,
        verbose_name='Tipo de plantilla'
    )
    template_content = models.TextField(
        verbose_name='Contenido de la plantilla'
    )
    variables = models.JSONField(
        default=list,
        verbose_name='Variables disponibles'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Plantilla de Documento'
        verbose_name_plural = 'Plantillas de Documentos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
