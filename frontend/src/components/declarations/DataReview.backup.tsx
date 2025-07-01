import React, { useState, useEffect } from 'react';
import { FileText, DollarSign, TrendingUp, AlertCircle, Info, CheckCircle, ArrowRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';
import { Button } from '../ui/Button';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import documentService, { Document } from '../../services/documentService';

interface DataReviewProps {
  declarationId: string;
  document?: Document;
  onComplete: () => void;
  onBackToUpload: () => void;
}

const DataReview: React.FC<DataReviewProps> = ({ 
  declarationId, 
  document, 
  onComplete, 
  onBackToUpload 
}) => {
  const [processedData, setProcessedData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (document && document.upload_status === 'processed') {
      console.log('✅ Documento procesado encontrado:', document);
      console.log('✅ Datos procesados:', document.processed_data);
      
      // Usar los datos que ya están en el documento
      if (document.processed_data) {
        setProcessedData(document.processed_data);
        setIsLoading(false);
      } else {
        // Si no hay datos en el documento, intentar cargarlos
        loadProcessedData();
      }
    } else {
      console.log('⚠️ Documento no procesado o no encontrado:', document);
      setIsLoading(false);
    }
  }, [document]);

  const loadProcessedData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      if (!document) {
        throw new Error('No hay documento para procesar');
      }

      // Intentar obtener datos del servicio como fallback
      try {
        const data = await documentService.getProcessedData(document.id);
        setProcessedData(data);
      } catch (serviceError) {
        console.log('⚠️ Servicio no disponible, usando datos del documento');
        // Usar los datos que ya están en el documento
        if (document.processed_data) {
          setProcessedData(document.processed_data);
        } else {
          throw new Error('No hay datos procesados disponibles');
        }
      }
    } catch (err: any) {
      console.error('Error loading processed data:', err);
      setError(err.message || 'Error cargando datos procesados');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Card className="p-8 text-center">
        <LoadingSpinner size="large" />
        <p className="text-gray-600 mt-4">Cargando datos procesados...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-8 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Error cargando datos</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <div className="flex justify-center space-x-4">
          <Button variant="outline" onClick={onBackToUpload}>
            Volver a Subir Archivo
          </Button>
          <Button onClick={loadProcessedData}>
            Reintentar
          </Button>
        </div>
      </Card>
    );
  }

  if (!document || !processedData) {
    return (
      <Card className="p-8 text-center">
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No hay datos para revisar</h3>
        <p className="text-gray-600 mb-4">
          Aún no hay información procesada para mostrar.
        </p>
        <Button onClick={onBackToUpload}>
          Subir Archivo
        </Button>
      </Card>
    );
  }

  const { 
    metadata, 
    records, 
    resumen, 
    clasificacion_cedulas,
    errors = [], 
    warnings = [] 
  } = processedData || {};

  const formatCurrency = (value: string | number): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return '$0';
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
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Revisión de Información Exógena</h2>
            <p className="text-gray-600 mt-1">
              Archivo: {document.original_file_name}
            </p>
          </div>
          <div className="flex items-center space-x-2 text-green-600">
            <CheckCircle className="w-6 h-6" />
            <span className="font-medium">Procesado exitosamente</span>
          </div>
        </div>
      </Card>

      {/* Alertas de errores y advertencias */}
      {errors.length > 0 && (
        <Alert type="error">
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
        <Alert type="warning">
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Ingresos</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatCurrency(metadata?.total_ingresos || resumen?.ingresos_laborales + resumen?.ingresos_capital || 0)}
              </p>
            </div>
            <DollarSign className="w-10 h-10 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Retenciones</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatCurrency(metadata?.total_retenciones || resumen?.retenciones_laborales + resumen?.retenciones_capital || 0)}
              </p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Registros Procesados</p>
              <p className="text-3xl font-bold text-gray-900">
                {metadata?.total_registros || records?.length || 'N/A'}
              </p>
              {metadata?.archivo_procesado && (
                <p className="text-sm text-gray-500">
                  {metadata.archivo_procesado}
                </p>
              )}
            </div>
            <FileText className="w-10 h-10 text-gray-600" />
          </div>
        </Card>
      </div>

      {/* Desglose por tipo de ingreso */}
      {records && records.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Registros de Ingresos</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tercero
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Concepto
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valor Bruto
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Retenciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {records.map((record: any, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {record.nombre_tercero}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {record.descripcion_concepto}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">
                      {formatCurrency(record.valor_bruto || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">
                      {formatCurrency(record.valor_retencion || 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Desglose por cédula tributaria */}
      {clasificacion_cedulas && Object.keys(clasificacion_cedulas).length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Clasificación por Cédula Tributaria</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(clasificacion_cedulas).map(([cedula, data]: [string, any]) => (
              <div key={cedula} className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">
                  {getScheduleLabel(cedula)}
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Registros:</span>
                    <span className="font-medium text-gray-900">{data.registros || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Ingresos:</span>
                    <span className="font-medium text-gray-900">{formatCurrency(data.total_ingresos || 0)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Retenciones:</span>
                    <span className="font-medium text-gray-900">{formatCurrency(data.total_retenciones || 0)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Resumen adicional si existe */}
      {resumen && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Resumen Adicional</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600">Ingresos Laborales</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(resumen.ingresos_laborales || 0)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Ingresos de Capital</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(resumen.ingresos_capital || 0)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Retenciones Laborales</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(resumen.retenciones_laborales || 0)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Retenciones de Capital</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(resumen.retenciones_capital || 0)}</p>
            </div>
            {metadata?.periodo_fiscal && (
              <div>
                <p className="text-sm text-gray-600">Período Fiscal</p>
                <p className="text-2xl font-bold text-gray-900">{metadata.periodo_fiscal}</p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Información sobre próximos pasos */}
      <Alert type="info">
        <Info className="w-4 h-4" />
        <div>
          <p className="font-medium">¡Información procesada exitosamente!</p>
          <p className="mt-1">
            Esta es una clasificación preliminar basada en tu información exógena. 
            En el siguiente paso, nuestra IA te ayudará a identificar deducciones y 
            optimizaciones aplicables a tu caso específico.
          </p>
        </div>
      </Alert>

      {/* Botón de continuar */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">¿Todo se ve correcto?</h3>
            <p className="text-gray-600">
              Si la información procesada es correcta, puedes continuar con el análisis de IA.
            </p>
          </div>
          <Button
            onClick={onComplete}
            size="lg"
            className="flex items-center"
          >
            Continuar con IA
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default DataReview;