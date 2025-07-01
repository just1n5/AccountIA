"""
Serializadores para la aplicación de declaraciones.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Declaration, IncomeRecord
from decimal import Decimal

User = get_user_model()


class IncomeRecordSerializer(serializers.ModelSerializer):
    """
    Serializador para registros de ingresos.
    """
    net_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = IncomeRecord
        fields = [
            'id',
            'third_party_nit',
            'third_party_name',
            'concept_code',
            'concept_description',
            'income_type',
            'gross_amount',
            'withholding_amount',
            'net_amount',
            'tax_schedule',
            'period',
            'is_deductible',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'net_amount']


class DeclarationSummarySerializer(serializers.ModelSerializer):
    """
    Serializador resumido para listados de declaraciones.
    """
    user_email = serializers.SerializerMethodField()
    balance = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    documents_count = serializers.IntegerField(
        read_only=True
    )
    progress_percentage = serializers.IntegerField(
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    def get_user_email(self, obj):
        """Obtiene el email del usuario, manejando casos nulos."""
        return obj.user.email if obj.user else 'test@accountia.co'
    
    class Meta:
        model = Declaration
        fields = [
            'id',
            'title',
            'fiscal_year',
            'status',
            'status_display',
            'total_income',
            'total_withholdings',
            'preliminary_tax',
            'balance',
            'user_email',
            'documents_count',
            'progress_percentage',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'balance',
            'documents_count',
            'progress_percentage',
            'status_display'
        ]


class DeclarationDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detallado para una declaración completa.
    """
    income_records = IncomeRecordSerializer(many=True, read_only=True)
    balance = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    is_editable = serializers.BooleanField(read_only=True)
    has_documents = serializers.BooleanField(read_only=True)
    documents_count = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Estadísticas agregadas
    income_summary = serializers.SerializerMethodField()
    
    # Campos de auditoría
    user_email = serializers.SerializerMethodField()
    
    def get_user_email(self, obj):
        """Obtiene el email del usuario, manejando casos nulos."""
        return obj.user.email if obj.user else 'test@accountia.co'
    
    class Meta:
        model = Declaration
        fields = [
            'id',
            'title',
            'fiscal_year',
            'status',
            'status_display',
            'total_income',
            'total_withholdings',
            'preliminary_tax',
            'balance',
            'declaration_data',
            'income_records',
            'is_editable',
            'has_documents',
            'documents_count',
            'progress_percentage',
            'income_summary',
            'processing_errors',
            'processing_warnings',
            'user_email',
            'is_active',
            'created_at',
            'updated_at',
            'deleted_at',
            'completed_at',
            'paid_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'deleted_at',
            'completed_at',
            'paid_at',
            'balance',
            'is_editable',
            'has_documents',
            'documents_count',
            'progress_percentage',
            'status_display',
            'user_email'
        ]
    
    def get_income_summary(self, obj):
        """
        Genera un resumen de ingresos por tipo y cédula.
        """
        income_by_type = {}
        income_by_schedule = {}
        
        for record in obj.income_records.all():
            # Por tipo
            if record.income_type not in income_by_type:
                income_by_type[record.income_type] = {
                    'count': 0,
                    'gross_amount': 0,
                    'withholding_amount': 0
                }
            
            income_by_type[record.income_type]['count'] += 1
            income_by_type[record.income_type]['gross_amount'] += float(record.gross_amount)
            income_by_type[record.income_type]['withholding_amount'] += float(record.withholding_amount)
            
            # Por cédula
            if record.tax_schedule:
                if record.tax_schedule not in income_by_schedule:
                    income_by_schedule[record.tax_schedule] = {
                        'count': 0,
                        'gross_amount': 0,
                        'withholding_amount': 0
                    }
                
                income_by_schedule[record.tax_schedule]['count'] += 1
                income_by_schedule[record.tax_schedule]['gross_amount'] += float(record.gross_amount)
                income_by_schedule[record.tax_schedule]['withholding_amount'] += float(record.withholding_amount)
        
        return {
            'by_type': income_by_type,
            'by_schedule': income_by_schedule
        }


class CreateDeclarationSerializer(serializers.ModelSerializer):
    """
    Serializador para crear una nueva declaración.
    """
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Título personalizado (opcional)'
    )
    
    class Meta:
        model = Declaration
        fields = ['title', 'fiscal_year']
        extra_kwargs = {
            'title': {'required': False}
        }
    
    def validate_fiscal_year(self, value):
        """
        Valida que el año fiscal sea razonable.
        """
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 2020 or value > current_year:
            raise serializers.ValidationError(
                f"El año fiscal debe estar entre 2020 y {current_year}"
            )
        
        return value
    
    def validate_title(self, value):
        """
        Valida y normaliza el título de la declaración.
        """
        if value:
            # Normalizar espacios y longitud
            value = ' '.join(value.split())
            if len(value) > 255:
                raise serializers.ValidationError(
                    "El título no puede tener más de 255 caracteres"
                )
        return value
    
    def create(self, validated_data):
        """
        Crea una nueva declaración - SIMPLIFICADO PARA DESARROLLO.
        """
        print(f"[DEBUG] CreateDeclarationSerializer.create()")
        
        # SIMPLIFICADO: Crear o usar usuario demo
        from apps.users.models import User
        
        user, created = User.objects.get_or_create(
            email='demo@accountia.co',
            defaults={
                'username': 'demo_user',
                'first_name': 'Demo',
                'last_name': 'User', 
                'is_active': True
            }
        )
        print(f"[DEBUG] Usuario {'creado' if created else 'obtenido'}: {user.email}")
        
        declaration = Declaration.objects.create(
            user=user,
            **validated_data
        )
        print(f"[DEBUG] Declaración creada: {declaration.id} - {declaration.title}")
        return declaration


class UpdateDeclarationStatusSerializer(serializers.Serializer):
    """
    Serializador para actualizar el estado de una declaración.
    """
    status = serializers.ChoiceField(choices=Declaration.STATUS_CHOICES)
    
    def validate_status(self, value):
        """
        Valida las transiciones de estado permitidas.
        """
        instance = self.context.get('instance')
        if not instance:
            return value
        
        current_status = instance.status
        
        # Definir transiciones permitidas
        allowed_transitions = {
            'draft': ['processing', 'completed'],
            'processing': ['completed', 'error', 'draft'],
            'completed': ['paid'],
            'error': ['draft', 'processing'],
            'paid': []  # Estado final
        }
        
        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"No se puede cambiar de '{current_status}' a '{value}'"
            )
        
        return value


class DuplicateDeclarationSerializer(serializers.Serializer):
    """
    Serializador para duplicar una declaración.
    """
    new_title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text='Título para la declaración duplicada (opcional)'
    )
    copy_income_records = serializers.BooleanField(
        default=True,
        help_text='Si se deben copiar los registros de ingresos'
    )
    
    def validate_new_title(self, value):
        """Valida el nuevo título."""
        if value:
            value = ' '.join(value.split())
        return value


class BulkDeclarationActionSerializer(serializers.Serializer):
    """
    Serializador para acciones en lote sobre declaraciones.
    """
    ACTION_CHOICES = [
        ('delete', 'Eliminar'),
        ('restore', 'Restaurar'),
        ('archive', 'Archivar'),
    ]
    
    declaration_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text='Lista de IDs de declaraciones'
    )
    action = serializers.ChoiceField(
        choices=ACTION_CHOICES,
        help_text='Acción a realizar'
    )
    
    def validate_declaration_ids(self, value):
        """Valida que las declaraciones existan y pertenezcan al usuario."""
        user = self.context['request'].user
        
        # Verificar que todas las declaraciones existen y pertenecen al usuario
        existing_declarations = Declaration.objects.filter(
            id__in=value,
            user=user
        ).values_list('id', flat=True)
        
        missing_ids = set(value) - set(existing_declarations)
        if missing_ids:
            raise serializers.ValidationError(
                f"Declaraciones no encontradas: {list(missing_ids)}"
            )
        
        return value


class DeclarationStatsSerializer(serializers.Serializer):
    """
    Serializador para estadísticas de declaraciones del usuario.
    """
    total_declarations = serializers.IntegerField()
    active_declarations = serializers.IntegerField()
    completed_declarations = serializers.IntegerField()
    draft_declarations = serializers.IntegerField()
    
    declarations_by_year = serializers.DictField(
        child=serializers.IntegerField()
    )
    declarations_by_status = serializers.DictField(
        child=serializers.IntegerField()
    )
    
    total_income_all = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2
    )
    total_withholdings_all = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2
    )
    
    last_declaration = DeclarationSummarySerializer(allow_null=True)
    

class UpdateDeclarationSerializer(serializers.ModelSerializer):
    """
    Serializador para actualizar campos básicos de una declaración.
    """
    class Meta:
        model = Declaration
        fields = ['title', 'fiscal_year']
        
    def validate_title(self, value):
        """Valida el título."""
        if value:
            value = ' '.join(value.split())
            if len(value) > 255:
                raise serializers.ValidationError(
                    "El título no puede tener más de 255 caracteres"
                )
        return value
    
    def validate_fiscal_year(self, value):
        """Valida el año fiscal."""
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 2020 or value > current_year:
            raise serializers.ValidationError(
                f"El año fiscal debe estar entre 2020 y {current_year}"
            )
        
        return value
