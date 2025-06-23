"""
Serializadores para la aplicación de declaraciones.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Declaration, IncomeRecord

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
    document_count = serializers.IntegerField(
        source='documents.count', 
        read_only=True
    )
    
    def get_user_email(self, obj):
        """Obtiene el email del usuario, manejando casos nulos."""
        return obj.user.email if obj.user else 'test@accountia.co'
    
    class Meta:
        model = Declaration
        fields = [
            'id',
            'fiscal_year',
            'status',
            'total_income',
            'total_withholdings',
            'preliminary_tax',
            'balance',
            'user_email',
            'document_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'balance',
            'document_count'
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
    
    # Estadísticas agregadas
    income_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Declaration
        fields = [
            'id',
            'fiscal_year',
            'status',
            'total_income',
            'total_withholdings',
            'preliminary_tax',
            'balance',
            'declaration_data',
            'income_records',
            'is_editable',
            'has_documents',
            'income_summary',
            'processing_errors',
            'processing_warnings',
            'created_at',
            'updated_at',
            'completed_at',
            'paid_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'completed_at',
            'paid_at',
            'balance',
            'is_editable',
            'has_documents'
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
    class Meta:
        model = Declaration
        fields = ['fiscal_year']
    
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
        
        # Para MVP: no validar duplicados por ahora
        # TODO: Restaurar validación de usuario cuando se implemente autenticación real
        
        return value
    
    def create(self, validated_data):
        """
        Crea una nueva declaración para el usuario autenticado.
        """
        request = self.context['request']
        
        # TESTING: Crear usuario dummy si no existe o es AnonymousUser
        from django.conf import settings
        from django.contrib.auth.models import AnonymousUser
        
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            from apps.users.models import User
            user, created = User.objects.get_or_create(
                email='test@accountia.co',
                defaults={
                    'first_name': 'Test',
                    'last_name': 'User',
                    'is_active': True
                }
            )
            print(f"🔧 TESTING: Usuario creado/obtenido: {user.email}")
        else:
            user = request.user
            print(f"🔧 TESTING: Usuario existente: {user}")
        
        declaration = Declaration.objects.create(
            user=user,
            **validated_data
        )
        print(f"🔧 TESTING: Declaración creada: {declaration.id}")
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
