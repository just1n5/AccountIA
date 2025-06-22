"""
Vistas API para declaraciones.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import Declaration, IncomeRecord
from .serializers import (
    DeclarationSummarySerializer,
    DeclarationDetailSerializer,
    CreateDeclarationSerializer,
    UpdateDeclarationStatusSerializer,
    IncomeRecordSerializer
)
from apps.documents.tasks import process_declaration_documents

import logging

logger = logging.getLogger(__name__)


class DeclarationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de declaraciones.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtra las declaraciones por el usuario actual.
        """
        return Declaration.objects.filter(
            user=self.request.user
        ).select_related('user').prefetch_related('documents', 'income_records')
    
    def get_serializer_class(self):
        """
        Retorna el serializador apropiado según la acción.
        """
        if self.action == 'list':
            return DeclarationSummarySerializer
        elif self.action == 'create':
            return CreateDeclarationSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return DeclarationDetailSerializer
        return DeclarationSummarySerializer
    
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva declaración.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            declaration = serializer.save()
            logger.info(f"Nueva declaración creada: {declaration.id} para el año {declaration.fiscal_year}")
        
        # Serializar la respuesta con el serializador detallado
        response_serializer = DeclarationDetailSerializer(declaration)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza una declaración (solo si es editable).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if not instance.is_editable:
            return Response(
                {'error': 'Esta declaración no se puede editar en su estado actual'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Actualiza el estado de una declaración.
        """
        declaration = self.get_object()
        serializer = UpdateDeclarationStatusSerializer(
            data=request.data,
            context={'instance': declaration}
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        
        with transaction.atomic():
            if new_status == 'completed':
                declaration.mark_as_completed()
            elif new_status == 'paid':
                declaration.mark_as_paid()
            else:
                declaration.status = new_status
                declaration.save()
        
        logger.info(f"Estado de declaración {declaration.id} actualizado a: {new_status}")
        
        response_serializer = DeclarationDetailSerializer(declaration)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_documents(self, request, pk=None):
        """
        Inicia el procesamiento de documentos de una declaración.
        """
        declaration = self.get_object()
        
        if not declaration.has_documents:
            return Response(
                {'error': 'No hay documentos para procesar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if declaration.status != 'draft':
            return Response(
                {'error': 'Solo se pueden procesar declaraciones en estado borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar estado a procesando
        declaration.status = 'processing'
        declaration.save()
        
        # Lanzar tarea asíncrona
        process_declaration_documents.delay(declaration.id)
        
        return Response({
            'message': 'Procesamiento iniciado',
            'declaration_id': str(declaration.id),
            'status': declaration.status
        })
    
    @action(detail=True, methods=['get'])
    def income_summary(self, request, pk=None):
        """
        Obtiene un resumen de ingresos por tipo y cédula.
        """
        declaration = self.get_object()
        
        summary = {
            'total_records': declaration.income_records.count(),
            'total_income': float(declaration.total_income),
            'total_withholdings': float(declaration.total_withholdings),
            'by_type': {},
            'by_schedule': {}
        }
        
        # Agrupar por tipo de ingreso
        income_records = declaration.income_records.all()
        
        for record in income_records:
            # Por tipo
            income_type = record.income_type
            if income_type not in summary['by_type']:
                summary['by_type'][income_type] = {
                    'count': 0,
                    'gross_amount': 0,
                    'withholding_amount': 0,
                    'display_name': record.get_income_type_display()
                }
            
            summary['by_type'][income_type]['count'] += 1
            summary['by_type'][income_type]['gross_amount'] += float(record.gross_amount)
            summary['by_type'][income_type]['withholding_amount'] += float(record.withholding_amount)
            
            # Por cédula
            if record.tax_schedule:
                schedule = record.tax_schedule
                if schedule not in summary['by_schedule']:
                    summary['by_schedule'][schedule] = {
                        'count': 0,
                        'gross_amount': 0,
                        'withholding_amount': 0,
                        'display_name': record.get_tax_schedule_display()
                    }
                
                summary['by_schedule'][schedule]['count'] += 1
                summary['by_schedule'][schedule]['gross_amount'] += float(record.gross_amount)
                summary['by_schedule'][schedule]['withholding_amount'] += float(record.withholding_amount)
        
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def download_draft(self, request, pk=None):
        """
        Genera y descarga el borrador de la declaración.
        """
        declaration = self.get_object()
        
        if declaration.status not in ['completed', 'paid']:
            return Response(
                {'error': 'El borrador solo está disponible para declaraciones completadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implementar generación de PDF del formulario 210
        # Por ahora, retornar los datos en formato JSON
        
        draft_data = {
            'declaration_id': str(declaration.id),
            'fiscal_year': declaration.fiscal_year,
            'generated_at': timezone.now().isoformat(),
            'user': {
                'email': declaration.user.email,
                'name': declaration.user.get_full_name()
            },
            'summary': {
                'total_income': float(declaration.total_income),
                'total_withholdings': float(declaration.total_withholdings),
                'preliminary_tax': float(declaration.preliminary_tax) if declaration.preliminary_tax else 0,
                'balance': float(declaration.balance) if declaration.balance else 0
            },
            'income_records': IncomeRecordSerializer(
                declaration.income_records.all(),
                many=True
            ).data
        }
        
        return Response(draft_data)
    
    @action(detail=False, methods=['get'])
    def current_year(self, request):
        """
        Obtiene la declaración del año actual si existe.
        """
        current_year = timezone.now().year - 1  # Generalmente se declara el año anterior
        
        try:
            declaration = Declaration.objects.get(
                user=request.user,
                fiscal_year=current_year
            )
            serializer = DeclarationDetailSerializer(declaration)
            return Response(serializer.data)
        except Declaration.DoesNotExist:
            return Response(
                {'message': f'No existe declaración para el año {current_year}'},
                status=status.HTTP_404_NOT_FOUND
            )


class IncomeRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar registros de ingresos.
    """
    serializer_class = IncomeRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtra los registros por declaración y usuario.
        """
        declaration_id = self.kwargs.get('declaration_pk')
        
        if declaration_id:
            # Verificar que la declaración pertenece al usuario
            declaration = get_object_or_404(
                Declaration,
                id=declaration_id,
                user=self.request.user
            )
            return IncomeRecord.objects.filter(declaration=declaration)
        
        # Si no hay declaration_pk, retornar todos los registros del usuario
        return IncomeRecord.objects.filter(
            declaration__user=self.request.user
        ).select_related('declaration')
