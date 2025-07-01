import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  BanknotesIcon,
  ChartBarIcon,
  LightBulbIcon 
} from '@heroicons/react/24/outline';

/**
 * Dashboard Principal de Análisis Fiscal Inteligente
 * Muestra el resumen ejecutivo del análisis realizado por AccountIA
 */
export const FiscalAnalysisDashboard = ({ 
  data, 
  loading = false, 
  error = null,
  onRetry,
  onOptimizeMore
}) => {
  const [activeTab, setActiveTab] = useState('resumen');

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  if (!data || !data.success) {
    return <EmptyState />;
  }

  const { 
    fiscal_analysis, 
    final_recommendations,
    user_friendly_summary,
    anomaly_detection,
    consistency_validation
  } = data;

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6" data-testid="fiscal-dashboard">
      {/* Header con resumen ejecutivo */}
      <DashboardHeader summary={user_friendly_summary} />
      
      {/* Navegación por tabs */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna principal */}
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'resumen' && (
            <ResumenTab 
              fiscalAnalysis={fiscal_analysis}
              recommendations={final_recommendations}
            />
          )}
          
          {activeTab === 'anomalias' && (
            <AnomaliasTab anomalies={anomaly_detection} />
          )}
          
          {activeTab === 'validacion' && (
            <ValidacionTab validation={consistency_validation} />
          )}
        </div>
        
        {/* Sidebar con acciones rápidas */}
        <div className="space-y-4">
          <ActionsSidebar 
            recommendations={final_recommendations?.recommendations || []}
            onOptimizeMore={onOptimizeMore}
          />
        </div>
      </div>
    </div>
  );
};

const LoadingState = () => (
  <div className="flex flex-col items-center justify-center p-12" data-testid="loading-state">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4" role="progressbar"></div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">Analizando su información fiscal</h3>
    <p className="text-gray-600 text-center max-w-md">
      Nuestro contador digital está procesando su información exógena y aplicando las reglas fiscales...
    </p>
  </div>
);

const ErrorState = ({ error, onRetry }) => (
  <div className="text-center p-12" data-testid="error-state">
    <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">Error en el análisis</h3>
    <p className="text-gray-600 mb-4" data-testid="error-message">{error}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        data-testid="retry-button"
      >
        Intentar nuevamente
      </button>
    )}
  </div>
);

const EmptyState = () => (
  <div className="text-center p-12" data-testid="empty-state">
    <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">Sin datos para mostrar</h3>
    <p className="text-gray-600">
      Cargue su archivo de información exógena para ver el análisis fiscal.
    </p>
  </div>
);

const DashboardHeader = ({ summary }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6" data-testid="dashboard-header">
    <div className="flex items-center justify-between mb-4">
      <h1 className="text-2xl font-bold text-gray-900">Análisis Fiscal Inteligente</h1>
      <div className={`px-3 py-1 rounded-full text-sm font-medium ${
        summary?.is_ready 
          ? 'bg-green-100 text-green-800' 
          : 'bg-yellow-100 text-yellow-800'
      }`}>
        {summary?.is_ready ? 'Listo para declarar' : 'Requiere atención'}
      </div>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <MetricCard
        title="Score General"
        value={`${summary?.overall_score || 0}/100`}
        icon={<ChartBarIcon className="h-5 w-5" />}
        color={summary?.overall_score >= 85 ? 'green' : summary?.overall_score >= 70 ? 'yellow' : 'red'}
        testId="overall-score"
      />
      
      <MetricCard
        title="Problemas Críticos"
        value={summary?.critical_issues_count || 0}
        icon={<ExclamationTriangleIcon className="h-5 w-5" />}
        color={summary?.critical_issues_count === 0 ? 'green' : 'red'}
        testId="critical-issues"
      />
      
      <MetricCard
        title="Recomendaciones"
        value={summary?.recommendations_count || 0}
        icon={<LightBulbIcon className="h-5 w-5" />}
        color="blue"
        testId="recommendations-count"
      />
      
      <MetricCard
        title="Tiempo Estimado"
        value={summary?.estimated_time || 'N/A'}
        icon={<BanknotesIcon className="h-5 w-5" />}
        color="gray"
        testId="estimated-time"
      />
    </div>
    
    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
      <p className="text-blue-800 font-medium" data-testid="main-message">
        {summary?.main_message || 'Análisis en progreso...'}
      </p>
    </div>
  </div>
);

const MetricCard = ({ title, value, icon, color, testId }) => {
  const colorClasses = {
    green: 'text-green-600 bg-green-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    red: 'text-red-600 bg-red-50',
    blue: 'text-blue-600 bg-blue-50',
    gray: 'text-gray-600 bg-gray-50'
  };

  return (
    <div className="text-center" data-testid={testId}>
      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg mb-2 ${colorClasses[color]}`}>
        {icon}
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-600">{title}</div>
    </div>
  );
};

const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'resumen', name: 'Resumen Fiscal', count: null },
    { id: 'anomalias', name: 'Anomalías', count: '2' },
    { id: 'validacion', name: 'Validación', count: null }
  ];

  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            data-testid={`tab-${tab.id}`}
          >
            {tab.name}
            {tab.count && (
              <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
};

const ResumenTab = ({ fiscalAnalysis, recommendations }) => (
  <div className="space-y-6" data-testid="resumen-tab">
    {/* Cálculo fiscal */}
    <FiscalCalculationCard analysis={fiscalAnalysis} />
    
    {/* Próximos pasos */}
    <NextStepsCard steps={recommendations?.next_steps || []} />
  </div>
);

const FiscalCalculationCard = ({ analysis }) => {
  if (!analysis?.tax_calculation) return null;

  const { tax_calculation, cedulas_totals } = analysis;

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6" data-testid="fiscal-calculation">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Cálculo Fiscal</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-medium text-gray-700 mb-3">Ingresos por Cédula</h4>
          <div className="space-y-2">
            {Object.entries(cedulas_totals || {}).map(([cedula, data]) => (
              <div key={cedula} className="flex justify-between text-sm">
                <span className="capitalize">{cedula.replace('_', ' ')}</span>
                <span className="font-medium" data-testid={`cedula-${cedula}`}>
                  ${data.ingresos_brutos?.toLocaleString() || '0'}
                </span>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h4 className="font-medium text-gray-700 mb-3">Resultado Final</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Base Gravable</span>
              <span className="font-medium" data-testid="base-gravable">
                ${tax_calculation.base_gravable?.toLocaleString() || '0'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Impuesto Calculado</span>
              <span className="font-medium">
                ${tax_calculation.impuesto_calculado?.toLocaleString() || '0'}
              </span>
            </div>
            <div className="flex justify-between text-sm border-t pt-2">
              <span className="font-medium">
                {tax_calculation.saldo_a_favor > 0 ? 'Saldo a Favor' : 'Saldo a Pagar'}
              </span>
              <span className={`font-bold ${
                tax_calculation.saldo_a_favor > 0 ? 'text-green-600' : 'text-red-600'
              }`} data-testid="saldo-final">
                ${(tax_calculation.saldo_a_favor || tax_calculation.saldo_a_pagar || 0).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const NextStepsCard = ({ steps }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6" data-testid="next-steps">
    <h3 className="text-lg font-medium text-gray-900 mb-4">Próximos Pasos</h3>
    
    <div className="space-y-4">
      {steps.map((step, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
            {step.step}
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">{step.title}</h4>
            <p className="text-sm text-gray-600 mt-1">{step.description}</p>
            {step.estimated_time && (
              <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                ⏱️ {step.estimated_time}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  </div>
);

const AnomaliasTab = ({ anomalies }) => (
  <div className="space-y-4" data-testid="anomalias-tab">
    {anomalies?.anomalies?.map((anomaly, index) => (
      <AnomalyCard key={index} anomaly={anomaly} />
    )) || <p className="text-gray-500">No se detectaron anomalías.</p>}
  </div>
);

const AnomalyCard = ({ anomaly }) => {
  const severityColors = {
    critical: 'border-red-500 bg-red-50',
    high: 'border-orange-500 bg-orange-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-blue-500 bg-blue-50'
  };

  return (
    <div className={`border-l-4 p-4 rounded-r-lg ${severityColors[anomaly.severity] || severityColors.low}`}>
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium text-gray-900">{anomaly.title}</h4>
          <p className="text-sm text-gray-700 mt-1">{anomaly.description}</p>
          {anomaly.recommendation && (
            <p className="text-sm text-gray-600 mt-2">
              <strong>Recomendación:</strong> {anomaly.recommendation}
            </p>
          )}
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          anomaly.severity === 'critical' ? 'bg-red-100 text-red-800' :
          anomaly.severity === 'high' ? 'bg-orange-100 text-orange-800' :
          anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {anomaly.severity?.toUpperCase()}
        </span>
      </div>
    </div>
  );
};

const ValidacionTab = ({ validation }) => (
  <div className="space-y-4" data-testid="validacion-tab">
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Validación de Consistencia</h3>
      
      {validation?.consistency_score && (
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span>Score de Consistencia</span>
            <span className="font-medium">{validation.consistency_score.score}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                validation.consistency_score.score >= 85 ? 'bg-green-500' : 
                validation.consistency_score.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${validation.consistency_score.score}%` }}
            ></div>
          </div>
        </div>
      )}
      
      <p className="text-sm text-gray-600">
        {validation?.consistency_score?.description || 'Validación en progreso...'}
      </p>
    </div>
  </div>
);

const ActionsSidebar = ({ recommendations, onOptimizeMore }) => (
  <div className="space-y-4" data-testid="actions-sidebar">
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <h3 className="font-medium text-gray-900 mb-3">Acciones Rápidas</h3>
      
      <div className="space-y-2">
        <button className="w-full text-left p-3 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors">
          📄 Generar Borrador 210
        </button>
        
        <button className="w-full text-left p-3 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors">
          📋 Lista de Documentos
        </button>
        
        <button 
          onClick={onOptimizeMore}
          className="w-full text-left p-3 bg-purple-50 text-purple-700 rounded-md hover:bg-purple-100 transition-colors"
        >
          🎯 Optimizar Más
        </button>
      </div>
    </div>
    
    {/* Recomendaciones rápidas */}
    {recommendations?.length > 0 && (
      <div className="bg-white rounded-lg shadow-sm border p-4" data-testid="recommendations">
        <h3 className="font-medium text-gray-900 mb-3">Recomendaciones</h3>
        
        <div className="space-y-3">
          {recommendations.slice(0, 3).map((rec, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-3">
              <h4 className="text-sm font-medium text-gray-900">{rec.title}</h4>
              <p className="text-xs text-gray-600 mt-1">
                Ahorro: ${rec.potential_saving?.toLocaleString() || '0'}
              </p>
            </div>
          ))}
        </div>
        
        {recommendations.length > 3 && (
          <button className="text-sm text-blue-600 hover:text-blue-800 mt-3">
            Ver todas las recomendaciones →
          </button>
        )}
      </div>
    )}
  </div>
);

export default FiscalAnalysisDashboard;