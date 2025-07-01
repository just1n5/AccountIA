"""
Vistas API para declaraciones - SIMPLIFICADAS PARA DESARROLLO.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db import models

from .models import Declaration, IncomeRecord
from .serializers import (
    DeclarationSummarySerializer,
    DeclarationDetailSerializer,
    CreateDeclarationSerializer,
    UpdateDeclarationStatusSerializer,
    UpdateDeclarationSerializer,
    DuplicateDeclarationSerializer,
    BulkDeclarationActionSerializer,
    DeclarationStatsSerializer,
    IncomeRecordSerializer
)

import logging

logger = logging.getLogger(__name__)


class DeclarationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de declaraciones - SIMPLIFICADO PARA DESARROLLO.
    """
    permission_classes = [AllowAny]  # Sin permisos para desarrollo
    
    def get_queryset(self):
        """
        Retorna declaraciones con optimizaciones.
        SIMPLIFICADO: Sin filtros de usuario para desarrollo.
        """
        print(f"[DEBUG] DeclarationViewSet.get_queryset()")
        
        # Base queryset con optimizaciones
        queryset = Declaration.objects.select_related('user').prefetch_related('documents', 'income_records')
        
        # SIMPLIFICADO: En desarrollo, retornar todas las declaraciones activas
        queryset = queryset.filter(is_active=True)
        
        # Filtros por parámetros de consulta
        fiscal_year = self.request.query_params.get('fiscal_year')
        status_filter = self.request.query_params.get('status')
        
        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        print(f"[DEBUG] Queryset final: {queryset.count()} declaraciones")
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Retorna el serializador apropiado según la acción.
        """
        if self.action == 'list':
            return DeclarationSummarySerializer
        elif self.action == 'create':
            return CreateDeclarationSerializer
        elif self.action in ['retrieve']:
            return DeclarationDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateDeclarationSerializer
        return DeclarationSummarySerializer
    
    def list(self, request, *args, **kwargs):
        """
        Lista declaraciones - SIMPLIFICADO.
        """
        print(f"[DEBUG] DeclarationViewSet.list() - START")
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            response_data = {
                'results': serializer.data,
                'count': queryset.count()
            }
            
            print(f"[DEBUG] Lista exitosa: {len(serializer.data)} declaraciones")
            return Response(response_data)
            
        except Exception as e:
            print(f"[ERROR] Error en list(): {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error listando declaraciones: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva declaración - SIMPLIFICADO.
        """
        print(f"[DEBUG] DeclarationViewSet.create() - START")
        print(f"[DEBUG] Request data: {request.data}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                declaration = serializer.save()
                print(f"[DEBUG] Declaración creada: {declaration.id} - {declaration.title}")
            
            # Serializar la respuesta con el serializador detallado
            response_serializer = DeclarationDetailSerializer(declaration)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"[ERROR] Error en create(): {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error creando declaración: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtiene una declaración específica - SIMPLIFICADO.
        """
        print(f"[DEBUG] DeclarationViewSet.retrieve() - START")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            print(f"[ERROR] Error en retrieve(): {str(e)}")
            return Response(
                {'error': f'Error obteniendo declaración: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza una declaración - SIMPLIFICADO.
        """
        print(f"[DEBUG] DeclarationViewSet.update() - START")
        try:
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
            
            # Retornar con serializador detallado
            response_serializer = DeclarationDetailSerializer(instance)
            return Response(response_serializer.data)
            
        except Exception as e:
            print(f"[ERROR] Error en update(): {str(e)}")
            return Response(
                {'error': f'Error actualizando declaración: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina una declaración (soft delete) - SIMPLIFICADO.
        """
        print(f"[DEBUG] DeclarationViewSet.destroy() - START")
        try:
            instance = self.get_object()
            
            if not instance.is_editable:
                return Response(
                    {'error': 'Esta declaración no se puede eliminar en su estado actual'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            instance.soft_delete()
            logger.info(f"Declaración {instance.id} eliminada (soft delete)")
            
            return Response({
                'message': 'Declaración eliminada exitosamente',
                'declaration_id': str(instance.id)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"[ERROR] Error en destroy(): {str(e)}")
            return Response(
                {'error': f'Error eliminando declaración: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtiene estadísticas de declaraciones - SIMPLIFICADO.
        """
        print(f"[DEBUG] DeclarationViewSet.stats() - START")
        try:
            # SIMPLIFICADO: Estadísticas de todas las declaraciones activas
            active_declarations = Declaration.objects.filter(is_active=True)
            
            # Calcular estadísticas básicas
            stats = {
                'total_declarations': active_declarations.count(),
                'active_declarations': active_declarations.filter(is_active=True).count(),
                'completed_declarations': active_declarations.filter(status='completed').count(),
                'draft_declarations': active_declarations.filter(status='draft').count(),
                'declarations_by_year': {},
                'declarations_by_status': {},
                'total_income_all': 0,
                'total_withholdings_all': 0,
                'last_declaration': None
            }
            
            # Agrupar por año y acumular totales
            for declaration in active_declarations:
                year = str(declaration.fiscal_year)
                stats['declarations_by_year'][year] = stats['declarations_by_year'].get(year, 0) + 1
                
                # Acumular totales
                stats['total_income_all'] += float(declaration.total_income)
                stats['total_withholdings_all'] += float(declaration.total_withholdings)
            
            # Agrupar por estado
            status_counts = active_declarations.values('status').annotate(
                count=models.Count('id')
            )
            for item in status_counts:
                stats['declarations_by_status'][item['status']] = item['count']
            
            # Última declaración
            last_declaration = active_declarations.first()
            if last_declaration:
                stats['last_declaration'] = DeclarationSummarySerializer(last_declaration).data
            
            serializer = DeclarationStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            print(f"[ERROR] Error en stats(): {str(e)}")
            return Response(
                {'error': f'Error obteniendo estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IncomeRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar registros de ingresos - SIMPLIFICADO.
    """
    serializer_class = IncomeRecordSerializer
    permission_classes = [AllowAny]  # Sin permisos para desarrollo
    
    def get_queryset(self):
        """
        Filtra los registros por declaración - SIMPLIFICADO.
        """
        print(f"[DEBUG] IncomeRecordViewSet.get_queryset()")
        
        declaration_id = self.kwargs.get('declaration_pk')
        
        if declaration_id:
            # SIMPLIFICADO: Sin verificar usuario
            declaration = get_object_or_404(Declaration, id=declaration_id)
            return IncomeRecord.objects.filter(declaration=declaration)
        
        # SIMPLIFICADO: Retornar todos los registros
        return IncomeRecord.objects.all().select_related('declaration')
