"""
Serializadores para la aplicación de documentos.
"""
from rest_framework import serializers
from .models import Document, DocumentTemplate
from apps.declarations.models import Declaration


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializador para documentos.
    """
    file_extension = serializers.CharField(read_only=True)
    is_processed = serializers.BooleanField(read_only=True)
    has_errors = serializers.BooleanField(read_only=True)
    storage_key = serializers.CharField(source='get_storage_key', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id',
            'declaration',
            'file_name',
            'original_file_name',
            'file_size',
            'file_type',
            'mime_type',
            'storage_path',
            'storage_url',
            'upload_status',
            'file_extension',
            'is_processed',
            'has_errors',
            'storage_key',
            'description',
            'tags',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'storage_path',
            'storage_url',
            'upload_status',
            'file_extension',
            'is_processed',
            'has_errors',
            'storage_key',
            'created_at',
            'updated_at'
        ]


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializador para iniciar la carga de un documento.
    """
    file_name = serializers.CharField(max_length=255)
    file_type = serializers.ChoiceField(choices=Document.DOCUMENT_TYPE_CHOICES)
    file_size = serializers.IntegerField(min_value=1, required=False)
    mime_type = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_file_name(self, value):
        """
        Valida el nombre del archivo.
        """
        import os
        
        # Verificar extensión permitida
        ext = os.path.splitext(value)[1].lower()
        allowed_extensions = ['.xlsx', '.xls', '.pdf', '.jpg', '.jpeg', '.png']
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Extensión de archivo no permitida. Extensiones válidas: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def validate_file_size(self, value):
        """
        Valida el tamaño del archivo.
        """
        max_size = 10 * 1024 * 1024  # 10 MB
        
        if value > max_size:
            raise serializers.ValidationError(
                f"El archivo es demasiado grande. Tamaño máximo: {max_size / 1024 / 1024} MB"
            )
        
        return value


class DocumentStatusUpdateSerializer(serializers.Serializer):
    """
    Serializador para actualizar el estado de un documento.
    """
    upload_status = serializers.ChoiceField(choices=['uploaded', 'error'])
    error_message = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Valida que si el estado es error, debe incluir mensaje.
        """
        if data['upload_status'] == 'error' and not data.get('error_message'):
            raise serializers.ValidationError(
                "Se requiere un mensaje de error cuando el estado es 'error'"
            )
        
        return data


class DocumentProcessedDataSerializer(serializers.ModelSerializer):
    """
    Serializador para mostrar datos procesados de un documento.
    """
    processed_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'file_type',
            'original_file_name',
            'upload_status',
            'processed_data',
            'processed_summary',
            'processing_errors',
            'processing_started_at',
            'processing_completed_at'
        ]
    
    def get_processed_summary(self, obj):
        """
        Genera un resumen de los datos procesados.
        """
        if not obj.processed_data:
            return None
        
        # Para archivos de exógena
        if obj.file_type == 'exogena_report' and 'stats' in obj.processed_data:
            stats = obj.processed_data['stats']
            return {
                'total_records': stats.get('total_records', 0),
                'processed_records': stats.get('processed_records', 0),
                'total_income': stats.get('total_income', 0),
                'total_withholdings': stats.get('total_withholdings', 0),
                'has_errors': bool(obj.processed_data.get('errors', [])),
                'has_warnings': bool(obj.processed_data.get('warnings', []))
            }
        
        return None


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """
    Serializador para plantillas de documentos.
    """
    class Meta:
        model = DocumentTemplate
        fields = [
            'id',
            'name',
            'description',
            'template_type',
            'variables',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
