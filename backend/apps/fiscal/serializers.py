"""
Serializadores para la API fiscal
"""
from rest_framework import serializers
from .models import FiscalAnalysisSession, UserFiscalProfile, FiscalOptimizationRecommendation


class UserFiscalProfileSerializer(serializers.ModelSerializer):
    """Serializador para el perfil fiscal del usuario"""
    
    class Meta:
        model = UserFiscalProfile
        fields = [
            'has_dependents', 'dependents_count',
            'has_health_insurance', 'has_mortgage', 'has_afc_account',
            'prefers_conservative_analysis', 'wants_optimization_suggestions'
        ]


class FiscalOptimizationRecommendationSerializer(serializers.ModelSerializer):
    """Serializador para recomendaciones de optimización"""
    
    class Meta:
        model = FiscalOptimizationRecommendation
        fields = [
            'id', 'recommendation_type', 'title', 'description',
            'potential_saving', 'effort_level', 'priority',
            'is_implemented', 'implemented_at', 'created_at'
        ]


class FiscalAnalysisSessionSerializer(serializers.ModelSerializer):
    """Serializador para sesiones de análisis fiscal"""
    recommendations = FiscalOptimizationRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = FiscalAnalysisSession
        fields = [
            'session_id', 'original_filename', 'file_size',
            'status', 'processing_time', 'analysis_results',
            'recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['session_id', 'created_at', 'updated_at']


class FiscalAnalysisRequestSerializer(serializers.Serializer):
    """Serializador para solicitud de análisis fiscal"""
    exogena_file = serializers.FileField(required=False)
    use_demo = serializers.BooleanField(default=False)
    user_context = serializers.JSONField(required=False, default=dict)
    
    def validate(self, data):
        """Validación de datos de entrada"""
        if not data.get('exogena_file') and not data.get('use_demo', False):
            raise serializers.ValidationError(
                "Se requiere archivo de exógena o usar datos demo"
            )
        return data


class DeductionSimulationSerializer(serializers.Serializer):
    """Serializador para simulación de deducciones"""
    base_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    deductions = serializers.JSONField()
    
    def validate_base_income(self, value):
        """Validar que el ingreso base sea positivo"""
        if value < 0:
            raise serializers.ValidationError("El ingreso base debe ser positivo")
        return value
    
    def validate_deductions(self, value):
        """Validar estructura de deducciones"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Las deducciones deben ser un objeto")
        
        for key, amount in value.items():
            if not isinstance(amount, (int, float)) or amount < 0:
                raise serializers.ValidationError(
                    f"La deducción '{key}' debe ser un monto positivo"
                )
        
        return value


class FiscalLimitsResponseSerializer(serializers.Serializer):
    """Serializador para respuesta de límites fiscales"""
    uvt_2024 = serializers.IntegerField()
    fiscal_limits = serializers.JSONField()
    deduction_categories = serializers.JSONField()
    tax_brackets = serializers.JSONField()


class AnalysisResultSerializer(serializers.Serializer):
    """Serializador para resultados de análisis fiscal"""
    success = serializers.BooleanField()
    processing_time = serializers.FloatField()
    processing_steps = serializers.ListField(child=serializers.CharField())
    analysis_date = serializers.DateTimeField()
    
    # Resultados específicos
    parser_results = serializers.JSONField()
    fiscal_analysis = serializers.JSONField()
    anomaly_detection = serializers.JSONField()
    consistency_validation = serializers.JSONField()
    final_recommendations = serializers.JSONField()
    user_friendly_summary = serializers.JSONField()
    
    # Campos opcionales para errores
    error = serializers.CharField(required=False)
