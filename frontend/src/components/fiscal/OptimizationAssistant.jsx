import React, { useState, useMemo } from 'react';
import { 
  LightBulbIcon,
  BanknotesIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

/**
 * Asistente de Optimización Fiscal
 * Muestra recomendaciones inteligentes para maximizar deducciones y minimizar impuestos
 */
export const OptimizationAssistant = ({
  recommendations = [],
  currentAnalysis,
  onRecommendationToggle,
  onDocumentUpload,
  onRecalculate,
  showPotentialSavings = true
}) => {
  const [selectedRecommendations, setSelectedRecommendations] = useState(new Set());
  const [filter, setFilter] = useState('all'); // all, high, medium, low
  const [sortBy, setSortBy] = useState('savings'); // savings, urgency, effort

  // Filtrar y ordenar recomendaciones
  const processedRecommendations = useMemo(() => {
    let filtered = recommendations;

    // Aplicar filtro por prioridad
    if (filter !== 'all') {
      filtered = filtered.filter(rec => rec.priority === filter);
    }

    // Ordenar según criterio seleccionado
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'savings':
          return (b.potential_saving || 0) - (a.potential_saving || 0);
        case 'urgency':
          const urgencyOrder = { 'urgent': 4, 'high': 3, 'medium': 2, 'low': 1 };
          return (urgencyOrder[b.priority] || 0) - (urgencyOrder[a.priority] || 0);
        case 'effort':
          const effortOrder = { 'low': 3, 'medium': 2, 'high': 1 };
          return (effortOrder[b.effort_level] || 0) - (effortOrder[a.effort_level] || 0);
        default:
          return 0;
      }
    });

    return filtered;
  }, [recommendations, filter, sortBy]);

  // Calcular ahorros totales
  const totalPotentialSavings = useMemo(() => {
    return selectedRecommendations.size > 0
      ? [...selectedRecommendations].reduce((total, id) => {
          const rec = recommendations.find(r => r.id === id);
          return total + (rec?.potential_saving || 0);
        }, 0)
      : recommendations.reduce((total, rec) => total + (rec.potential_saving || 0), 0);
  }, [recommendations, selectedRecommendations]);

  const handleRecommendationSelect = (recommendation) => {
    const newSelected = new Set(selectedRecommendations);
    
    if (newSelected.has(recommendation.id)) {
      newSelected.delete(recommendation.id);
    } else {
      newSelected.add(recommendation.id);
    }
    
    setSelectedRecommendations(newSelected);
    onRecommendationToggle?.(recommendation, newSelected.has(recommendation.id));
  };

  if (!recommendations || recommendations.length === 0) {
    return <EmptyOptimizationState />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6" data-testid="optimization-assistant">
      {/* Header con resumen */}
      <OptimizationHeader 
        totalSavings={totalPotentialSavings}
        selectedCount={selectedRecommendations.size}
        totalCount={recommendations.length}
        currentAnalysis={currentAnalysis}
      />

      {/* Controles de filtro y ordenamiento */}
      <OptimizationControls
        filter={filter}
        sortBy={sortBy}
        onFilterChange={setFilter}
        onSortChange={setSortBy}
        recommendationsCount={processedRecommendations.length}
      />

      {/* Lista de recomendaciones */}
      <div className="space-y-4" data-testid="recommendations-list">
        {processedRecommendations.map((recommendation, index) => (
          <RecommendationCard
            key={recommendation.id || index}
            recommendation={recommendation}
            isSelected={selectedRecommendations.has(recommendation.id)}
            onSelect={() => handleRecommendationSelect(recommendation)}
            onDocumentUpload={onDocumentUpload}
            rank={index + 1}
          />
        ))}
      </div>

      {/* Panel de acciones */}
      {selectedRecommendations.size > 0 && (
        <ActionPanel
          selectedCount={selectedRecommendations.size}
          totalSavings={totalPotentialSavings}
          onRecalculate={onRecalculate}
          onClearSelection={() => setSelectedRecommendations(new Set())}
        />
      )}

      {/* Información adicional */}
      <OptimizationTips />
    </div>
  );
};

const OptimizationHeader = ({ totalSavings, selectedCount, totalCount, currentAnalysis }) => (
  <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white p-6" data-testid="optimization-header">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center space-x-3">
        <LightBulbIcon className="w-8 h-8" />
        <h2 className="text-2xl font-bold">Asistente de Optimización</h2>
      </div>
      
      <div className="text-right">
        <div className="text-3xl font-bold" data-testid="total-savings">
          ${totalSavings.toLocaleString()}
        </div>
        <div className="text-sm opacity-90">Ahorro potencial</div>
      </div>
    </div>
    
    <div className="grid grid-cols-3 gap-4 text-center">
      <div className="bg-white bg-opacity-20 rounded-lg p-3">
        <div className="text-2xl font-bold">{totalCount}</div>
        <div className="text-sm opacity-90">Recomendaciones</div>
      </div>
      
      <div className="bg-white bg-opacity-20 rounded-lg p-3">
        <div className="text-2xl font-bold">{selectedCount}</div>
        <div className="text-sm opacity-90">Seleccionadas</div>
      </div>
      
      <div className="bg-white bg-opacity-20 rounded-lg p-3">
        <div className="text-2xl font-bold">
          {currentAnalysis?.tax_calculation?.saldo_a_pagar > 0 ? 
            Math.round((totalSavings / currentAnalysis.tax_calculation.saldo_a_pagar) * 100) :
            0
          }%
        </div>
        <div className="text-sm opacity-90">Reducción impuesto</div>
      </div>
    </div>
  </div>
);

const OptimizationControls = ({ 
  filter, 
  sortBy, 
  onFilterChange, 
  onSortChange, 
  recommendationsCount 
}) => (
  <div className="bg-white rounded-lg border p-4 flex flex-wrap items-center justify-between gap-4" data-testid="optimization-controls">
    <div className="flex items-center space-x-4">
      <span className="text-sm font-medium text-gray-700">Filtrar por prioridad:</span>
      <select
        value={filter}
        onChange={(e) => onFilterChange(e.target.value)}
        className="border border-gray-300 rounded-md px-3 py-1 text-sm"
        data-testid="priority-filter"
      >
        <option value="all">Todas ({recommendationsCount})</option>
        <option value="urgent">Urgentes</option>
        <option value="high">Alta</option>
        <option value="medium">Media</option>
        <option value="low">Baja</option>
      </select>
    </div>
    
    <div className="flex items-center space-x-4">
      <span className="text-sm font-medium text-gray-700">Ordenar por:</span>
      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value)}
        className="border border-gray-300 rounded-md px-3 py-1 text-sm"
        data-testid="sort-select"
      >
        <option value="savings">Mayor ahorro</option>
        <option value="urgency">Urgencia</option>
        <option value="effort">Menor esfuerzo</option>
      </select>
    </div>
  </div>
);

const RecommendationCard = ({ 
  recommendation, 
  isSelected, 
  onSelect, 
  onDocumentUpload,
  rank 
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const priorityColors = {
    urgent: 'border-red-500 bg-red-50',
    high: 'border-orange-500 bg-orange-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-blue-500 bg-blue-50'
  };

  const effortIcons = {
    low: '⭐',
    medium: '⭐⭐',
    high: '⭐⭐⭐'
  };

  return (
    <div 
      className={`border rounded-lg transition-all duration-200 ${
        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
      data-testid={`recommendation-${recommendation.id}`}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3">
            {/* Checkbox de selección */}
            <input
              type="checkbox"
              checked={isSelected}
              onChange={onSelect}
              className="mt-1 h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              data-testid="recommendation-checkbox"
            />
            
            {/* Ranking */}
            <div className="flex-shrink-0 w-8 h-8 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
              {rank}
            </div>
            
            {/* Contenido principal */}
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {recommendation.title}
              </h3>
              
              <p className="text-gray-600 mb-3" data-testid="recommendation-description">
                {recommendation.description}
              </p>
              
              {/* Métricas clave */}
              <div className="flex flex-wrap items-center gap-4 text-sm">
                <div className="flex items-center space-x-1">
                  <BanknotesIcon className="w-4 h-4 text-green-600" />
                  <span className="font-medium text-green-600" data-testid="potential-saving">
                    ${recommendation.potential_saving?.toLocaleString() || '0'}
                  </span>
                  <span className="text-gray-500">ahorro</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <ClockIcon className="w-4 h-4 text-gray-500" />
                  <span>Esfuerzo: {effortIcons[recommendation.effort_level]} {recommendation.effort_level}</span>
                </div>
                
                {recommendation.deadline && (
                  <div className="flex items-center space-x-1">
                    <CalendarIcon className="w-4 h-4 text-orange-500" />
                    <span className="text-orange-600">{recommendation.deadline}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Badge de prioridad */}
          <span className={`px-3 py-1 text-xs font-medium rounded-full ${
            recommendation.priority === 'urgent' ? 'bg-red-100 text-red-800' :
            recommendation.priority === 'high' ? 'bg-orange-100 text-orange-800' :
            recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {recommendation.priority?.toUpperCase()}
          </span>
        </div>
        
        {/* Botones de acción */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            data-testid="show-details"
          >
            {showDetails ? 'Ocultar detalles' : 'Ver detalles'}
          </button>
          
          <div className="flex space-x-2">
            {recommendation.requires_documents && (
              <button
                onClick={() => onDocumentUpload?.(recommendation)}
                className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                data-testid="upload-documents"
              >
                <DocumentTextIcon className="w-4 h-4 mr-1" />
                Subir documentos
              </button>
            )}
          </div>
        </div>
        
        {/* Detalles expandidos */}
        {showDetails && (
          <RecommendationDetails recommendation={recommendation} />
        )}
      </div>
    </div>
  );
};

const RecommendationDetails = ({ recommendation }) => (
  <div className="mt-4 pt-4 border-t border-gray-200" data-testid="recommendation-details">
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Base legal */}
      {recommendation.legal_base && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">📖 Base Legal</h4>
          <p className="text-sm text-gray-600">{recommendation.legal_base}</p>
        </div>
      )}
      
      {/* Documentos requeridos */}
      {recommendation.required_documents && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">📄 Documentos Necesarios</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {recommendation.required_documents.map((doc, index) => (
              <li key={index} className="flex items-center space-x-2">
                <CheckCircleIcon className="w-4 h-4 text-gray-400" />
                <span>{doc}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Pasos de implementación */}
      {recommendation.implementation_steps && (
        <div className="md:col-span-2">
          <h4 className="font-medium text-gray-900 mb-2">✅ Pasos para Implementar</h4>
          <ol className="text-sm text-gray-600 space-y-1">
            {recommendation.implementation_steps.map((step, index) => (
              <li key={index} className="flex items-start space-x-2">
                <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
                  {index + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  </div>
);

const ActionPanel = ({ selectedCount, totalSavings, onRecalculate, onClearSelection }) => (
  <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg p-4 z-50" data-testid="action-panel">
    <div className="max-w-4xl mx-auto flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <span className="text-lg font-medium text-gray-900">
          {selectedCount} recomendación{selectedCount !== 1 ? 'es' : ''} seleccionada{selectedCount !== 1 ? 's' : ''}
        </span>
        
        <span className="text-lg font-bold text-green-600">
          ${totalSavings.toLocaleString()} ahorro potencial
        </span>
      </div>
      
      <div className="flex space-x-3">
        <button
          onClick={onClearSelection}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
        >
          Limpiar selección
        </button>
        
        <button
          onClick={onRecalculate}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
          data-testid="recalculate-button"
        >
          Recalcular con selecciones
        </button>
      </div>
    </div>
  </div>
);

const OptimizationTips = () => (
  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6" data-testid="optimization-tips">
    <h3 className="font-medium text-gray-900 mb-3 flex items-center">
      <LightBulbIcon className="w-5 h-5 text-yellow-500 mr-2" />
      💡 Consejos del Contador Digital
    </h3>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
      <div className="space-y-2">
        <h4 className="font-medium">🎯 Priorizar</h4>
        <ul className="space-y-1">
          <li>• Implementa primero las recomendaciones urgentes</li>
          <li>• Enfócate en mayor ahorro con menor esfuerzo</li>
          <li>• Respeta las fechas límite fiscales</li>
        </ul>
      </div>
      
      <div className="space-y-2">
        <h4 className="font-medium">📋 Documentación</h4>
        <ul className="space-y-1">
          <li>• Conserva todos los soportes digitalmente</li>
          <li>• Organiza por tipo de deducción</li>
          <li>• Verifica que estén dentro del año fiscal</li>
        </ul>
      </div>
    </div>
    
    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
      <div className="flex items-start space-x-2">
        <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-yellow-800">
          <strong>Importante:</strong> Estas recomendaciones son estimaciones basadas en su información. 
          Consulte con un contador profesional para casos complejos.
        </div>
      </div>
    </div>
  </div>
);

const EmptyOptimizationState = () => (
  <div className="text-center p-12" data-testid="empty-optimization">
    <LightBulbIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      Sin recomendaciones disponibles
    </h3>
    <p className="text-gray-600">
      Complete el análisis fiscal para ver recomendaciones personalizadas.
    </p>
  </div>
);

export default OptimizationAssistant;