import React from 'react';
import { Card } from '../ui/Card';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Button } from '../ui/Button';
import { CheckCircle, AlertTriangle, RefreshCw, Clock } from 'lucide-react';

interface ProcessingStatusProps {
  status: string;
  progress: number;
  onCheckStatus: () => void;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  progress,
  onCheckStatus
}) => {
  const getStatusIcon = () => {
    if (status.includes('completado') || status.includes('Completado')) {
      return <CheckCircle className="w-8 h-8 text-green-500" />;
    } else if (status.includes('error') || status.includes('Error')) {
      return <AlertTriangle className="w-8 h-8 text-red-500" />;
    } else {
      return <LoadingSpinner size="large" />;
    }
  };

  const getStatusColor = () => {
    if (status.includes('completado') || status.includes('Completado')) {
      return 'text-green-700';
    } else if (status.includes('error') || status.includes('Error')) {
      return 'text-red-700';
    } else {
      return 'text-blue-700';
    }
  };

  const getProgressBarColor = () => {
    if (status.includes('completado') || status.includes('Completado')) {
      return 'bg-green-500';
    } else if (status.includes('error') || status.includes('Error')) {
      return 'bg-red-500';
    } else {
      return 'bg-blue-500';
    }
  };

  return (
    <Card className="p-8">
      <div className="text-center space-y-6">
        {/* Icono de estado */}
        <div className="flex justify-center">
          {getStatusIcon()}
        </div>

        {/* Mensaje de estado */}
        <div>
          <h3 className={`text-lg font-semibold ${getStatusColor()}`}>
            Procesamiento de Archivo
          </h3>
          <p className="text-gray-600 mt-2">
            {status}
          </p>
        </div>

        {/* Barra de progreso */}
        <div className="w-full">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progreso</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-300 ${getProgressBarColor()}`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Información adicional */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center text-blue-700">
            <Clock className="w-5 h-5 mr-2" />
            <span className="text-sm">
              El procesamiento puede tomar entre 1-3 minutos dependiendo del tamaño del archivo
            </span>
          </div>
        </div>

        {/* Botón de verificación */}
        <div className="pt-4">
          <Button
            onClick={onCheckStatus}
            variant="outline"
            className="mx-auto"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Verificar Estado
          </Button>
        </div>

        {/* Estados específicos */}
        {status.includes('error') && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="text-red-700 text-sm">
              <p className="font-medium">¿Qué puedes hacer?</p>
              <ul className="mt-2 space-y-1 list-disc list-inside">
                <li>Verifica que el archivo sea un Excel válido (.xlsx o .xls)</li>
                <li>Asegúrate de que contiene datos de información exógena</li>
                <li>Intenta con un archivo más pequeño si el actual es muy grande</li>
                <li>Contacta soporte si el problema persiste</li>
              </ul>
            </div>
          </div>
        )}

        {status.includes('completado') && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="text-green-700 text-sm">
              <p className="font-medium">¡Procesamiento exitoso!</p>
              <p className="mt-1">
                Tu archivo ha sido procesado correctamente. Puedes continuar con la revisión de los datos.
              </p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ProcessingStatus;