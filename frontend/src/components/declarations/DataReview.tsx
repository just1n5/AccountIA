import React from 'react';
import { FileText, DollarSign, TrendingUp, AlertCircle, Info } from 'lucide-react';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';

interface DataReviewProps {
  processedData: any;
  isLoading?: boolean;
}

const DataReview: React.FC<DataReviewProps> = ({ processedData, isLoading }) => {
  if (isLoading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-azul-principal mx-auto mb-4"></div>
        <p className="text-gris-700">Procesando información...</p>
      </div>
    );
  }

  if (!processedData) {
    return (
      <div className="p-8 text-center">
        <FileText className="w-12 h-12 text-gris-700 mx-auto mb-4" />
        <p className="text-gris-700">No hay datos para mostrar</p>
      </div>
    );
  }

  const { processed_summary, processed_data } = processedData;
  const stats = processed_data?.stats || {};
  const errors = processed_data?.errors || [];
  const warnings = processed_data?.warnings || [];

  const formatCurrency = (value: string | number): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  const getIncomeTypeLabel = (type: string): string => {
    const labels: { [key: string]: string } = {
      salary: 'Salarios',
      honorarios: 'Honorarios',
      services: 'Servicios',
      dividends: 'Dividendos',
      interests: 'Intereses',
      rental: 'Arrendamientos',
      other: 'Otros'
    };
    return labels[type] || type;
  };

  const getScheduleLabel = (schedule: string): string => {
    const labels: { [key: string]: string } = {
      labor: 'Rentas de Trabajo',
      capital: 'Rentas de Capital',
      non_labor: 'Rentas No Laborales',
      pensions: 'Pensiones',
      dividends: 'Dividendos y Participaciones'
    };
    return labels[schedule] || schedule;
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Resumen de tu Información Exógena</h2>

      {/* Alertas de errores y advertencias */}
      {errors.length > 0 && (
        <Alert type="error" className="mb-4">
          <AlertCircle className="w-4 h-4" />
          <div>
            <p className="font-medium">Se encontraron errores:</p>
            <ul className="list-disc list-inside mt-1">
              {errors.map((error: string, index: number) => (
                <li key={index} className="text-sm">{error}</li>
              ))}
            </ul>
          </div>
        </Alert>
      )}

      {warnings.length > 0 && (
        <Alert type="warning" className="mb-4">
          <Info className="w-4 h-4" />
          <div>
            <p className="font-medium">Advertencias:</p>
            <ul className="list-disc list-inside mt-1">
              {warnings.map((warning: string, index: number) => (
                <li key={index} className="text-sm">{warning}</li>
              ))}
            </ul>
          </div>
        </Alert>
      )}

      {/* Estadísticas generales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gris-700">Total de Ingresos</p>
              <p className="text-2xl font-bold text-gris-900">
                {formatCurrency(stats.total_income || 0)}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-azul-principal" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gris-700">Total de Retenciones</p>
              <p className="text-2xl font-bold text-gris-900">
                {formatCurrency(stats.total_withholdings || 0)}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-verde-exito" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gris-700">Registros Procesados</p>
              <p className="text-2xl font-bold text-gris-900">
                {stats.processed_records || 0} de {stats.total_records || 0}
              </p>
            </div>
            <FileText className="w-8 h-8 text-gris-700" />
          </div>
        </Card>
      </div>

      {/* Desglose por tipo de ingreso */}
      {stats.income_by_type && Object.keys(stats.income_by_type).length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Ingresos por Tipo</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gris-300">
              <thead className="bg-gris-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gris-700 uppercase tracking-wider">
                    Tipo de Ingreso
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gris-700 uppercase tracking-wider">
                    Cantidad
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gris-700 uppercase tracking-wider">
                    Valor Bruto
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gris-700 uppercase tracking-wider">
                    Retenciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gris-300">
                {Object.entries(stats.income_by_type).map(([type, data]: [string, any]) => (
                  <tr key={type}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gris-900">
                      {getIncomeTypeLabel(type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gris-700 text-right">
                      {data.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gris-700 text-right">
                      {formatCurrency(data.gross_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gris-700 text-right">
                      {formatCurrency(data.withholding_amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Desglose por cédula tributaria */}
      {stats.income_by_schedule && Object.keys(stats.income_by_schedule).length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Clasificación por Cédula Tributaria</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(stats.income_by_schedule).map(([schedule, data]: [string, any]) => (
              <Card key={schedule} className="p-4">
                <h4 className="font-medium text-gris-900 mb-2">
                  {getScheduleLabel(schedule)}
                </h4>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gris-700">Registros:</span>
                    <span className="font-medium">{data.count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gris-700">Ingresos:</span>
                    <span className="font-medium">{formatCurrency(data.gross_amount)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gris-700">Retenciones:</span>
                    <span className="font-medium">{formatCurrency(data.withholding_amount)}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Nota informativa */}
      <Alert type="info" className="mt-6">
        <Info className="w-4 h-4" />
        <span>
          Esta es una clasificación preliminar basada en tu información exógena. 
          En el siguiente paso, nuestra IA te ayudará a identificar deducciones y 
          optimizaciones aplicables a tu caso.
        </span>
      </Alert>
    </div>
  );
};

export default DataReview;