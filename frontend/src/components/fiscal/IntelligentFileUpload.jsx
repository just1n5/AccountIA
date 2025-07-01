import React, { useState, useCallback, useRef } from 'react';
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

/**
 * Componente de Carga Inteligente de Archivos
 * Maneja la carga de archivos de información exógena con validación y feedback
 */
export const IntelligentFileUpload = ({
  onFileProcessed,
  onFileError,
  acceptedFormats = ['.xlsx', '.xls'],
  maxSizeGB = 0.05, // 50MB por defecto
  allowDemo = true,
  loading = false
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, processing, success, error
  const [errorMessage, setErrorMessage] = useState('');
  const [previewData, setPreviewData] = useState(null);
  
  const fileInputRef = useRef(null);
  const maxSizeBytes = maxSizeGB * 1024 * 1024 * 1024;

  const validateFile = useCallback((file) => {
    const errors = [];
    
    // Validar extensión
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!acceptedFormats.includes(fileExtension)) {
      errors.push(`Formato no válido. Solo se permiten archivos: ${acceptedFormats.join(', ')}`);
    }
    
    // Validar tamaño
    if (file.size > maxSizeBytes) {
      errors.push(`Archivo muy grande. Máximo permitido: ${maxSizeGB}GB`);
    }
    
    // Validar nombre (detectar archivos de exógena)
    const fileName = file.name.toLowerCase();
    const exogenaKeywords = ['exogena', 'exógena', 'informacion', 'información', 'terceros'];
    const hasExogenaKeyword = exogenaKeywords.some(keyword => fileName.includes(keyword));
    
    if (!hasExogenaKeyword) {
      // Warning, no error bloqueante
      console.warn('El archivo no parece ser de información exógena');
    }
    
    return errors;
  }, [acceptedFormats, maxSizeBytes, maxSizeGB]);

  const processFile = async (file) => {
    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage('');

    try {
      // Simular progreso de carga
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Crear FormData para envío
      const formData = new FormData();
      formData.append('exogena_file', file);

      setUploadStatus('processing');
      setUploadProgress(100);

      // Llamar API de análisis fiscal
      const response = await fetch('/api/v1/fiscal/analyze/', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setUploadStatus('success');
        setPreviewData({
          filename: file.name,
          size: file.size,
          recordsCount: result.parser_results?.records?.length || 0,
          totalIncome: result.fiscal_analysis?.cedulas_totals ? 
            Object.values(result.fiscal_analysis.cedulas_totals)
              .reduce((sum, cedula) => sum + (cedula.ingresos_brutos || 0), 0) : 0
        });
        
        onFileProcessed?.(result);
      } else {
        throw new Error(result.error || 'Error procesando el archivo');
      }

    } catch (error) {
      console.error('Error procesando archivo:', error);
      setUploadStatus('error');
      setErrorMessage(error.message);
      onFileError?.(error.message);
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = useCallback((e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, []);

  const handleFileSelection = (file) => {
    const validationErrors = validateFile(file);
    
    if (validationErrors.length > 0) {
      setUploadStatus('error');
      setErrorMessage(validationErrors[0]);
      return;
    }

    processFile(file);
  };

  const handleDemoData = async () => {
    setUploadStatus('processing');
    setUploadProgress(100);
    
    try {
      const response = await fetch('/api/v1/fiscal/analyze/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ use_demo: true })
      });

      const result = await response.json();

      if (result.success) {
        setUploadStatus('success');
        setPreviewData({
          filename: 'Datos Demo AccountIA',
          size: 0,
          recordsCount: result.parser_results?.records?.length || 0,
          totalIncome: result.fiscal_analysis?.cedulas_totals ? 
            Object.values(result.fiscal_analysis.cedulas_totals)
              .reduce((sum, cedula) => sum + (cedula.ingresos_brutos || 0), 0) : 0
        });
        
        onFileProcessed?.(result);
      } else {
        throw new Error(result.error || 'Error con datos demo');
      }
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(error.message);
    }
  };

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setErrorMessage('');
    setPreviewData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Render diferentes estados
  if (uploadStatus === 'success' && previewData) {
    return <SuccessState previewData={previewData} onReset={resetUpload} />;
  }

  if (uploadStatus === 'processing' || uploadStatus === 'uploading') {
    return <ProcessingState progress={uploadProgress} status={uploadStatus} />;
  }

  return (
    <div className="max-w-2xl mx-auto" data-testid="file-upload">
      {/* Área de drag & drop */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
          isDragOver 
            ? 'border-blue-500 bg-blue-50' 
            : uploadStatus === 'error' 
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {uploadStatus === 'error' ? (
          <ErrorDisplay message={errorMessage} onRetry={resetUpload} />
        ) : (
          <UploadPrompt 
            isDragOver={isDragOver}
            onFileSelect={() => fileInputRef.current?.click()}
            acceptedFormats={acceptedFormats}
            maxSize={maxSizeGB}
          />
        )}
      </div>

      {/* Input file oculto */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileInput}
        className="hidden"
        data-testid="file-input"
      />

      {/* Botón de datos demo */}
      {allowDemo && uploadStatus !== 'error' && (
        <div className="mt-6 text-center">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">o</span>
            </div>
          </div>
          
          <button
            onClick={handleDemoData}
            disabled={loading}
            className="mt-4 inline-flex items-center px-4 py-2 border border-blue-300 text-sm font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            data-testid="demo-button"
          >
            🎯 Probar con datos demo
          </button>
          
          <p className="mt-2 text-xs text-gray-500">
            Ideal para conocer AccountIA sin subir sus datos reales
          </p>
        </div>
      )}

      {/* Información sobre formatos aceptados */}
      <FileFormatInfo acceptedFormats={acceptedFormats} />
    </div>
  );
};

const UploadPrompt = ({ isDragOver, onFileSelect, acceptedFormats, maxSize }) => (
  <div className="space-y-4">
    <div className={`mx-auto w-16 h-16 ${isDragOver ? 'text-blue-500' : 'text-gray-400'}`}>
      <CloudArrowUpIcon className="w-full h-full" />
    </div>
    
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {isDragOver ? 'Suelte el archivo aquí' : 'Suba su información exógena'}
      </h3>
      
      <p className="text-gray-600 mb-4">
        Arrastre y suelte el archivo Excel de la DIAN, o{' '}
        <button
          onClick={onFileSelect}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          seleccione desde su computador
        </button>
      </p>
    </div>
    
    <div className="text-sm text-gray-500">
      <p>Formatos: {acceptedFormats.join(', ')}</p>
      <p>Tamaño máximo: {maxSize}GB</p>
    </div>
  </div>
);

const ProcessingState = ({ progress, status }) => (
  <div className="text-center p-8" data-testid="processing-state">
    <div className="mx-auto w-16 h-16 text-blue-500 mb-4">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
    </div>
    
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      {status === 'uploading' ? 'Subiendo archivo...' : 'Procesando con IA...'}
    </h3>
    
    <p className="text-gray-600 mb-4">
      {status === 'uploading' 
        ? 'Su archivo se está cargando de forma segura'
        : 'Nuestro contador digital está analizando su información'
      }
    </p>
    
    {/* Barra de progreso */}
    <div className="max-w-md mx-auto">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>Progreso</span>
        <span>{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
    
    {status === 'processing' && (
      <div className="mt-4 text-sm text-gray-500">
        <p>⚡ Aplicando reglas fiscales...</p>
        <p>🔍 Detectando optimizaciones...</p>
        <p>📊 Calculando impuestos...</p>
      </div>
    )}
  </div>
);

const SuccessState = ({ previewData, onReset }) => (
  <div className="bg-green-50 border border-green-200 rounded-lg p-6" data-testid="success-state">
    <div className="flex items-center mb-4">
      <CheckCircleIcon className="w-8 h-8 text-green-500 mr-3" />
      <div>
        <h3 className="text-lg font-medium text-green-800">
          ¡Archivo procesado exitosamente!
        </h3>
        <p className="text-green-700">Su análisis fiscal está listo</p>
      </div>
    </div>
    
    <div className="bg-white rounded-md p-4 mb-4">
      <h4 className="font-medium text-gray-900 mb-2">Resumen del archivo:</h4>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Archivo:</span>
          <p className="font-medium" data-testid="filename">{previewData.filename}</p>
        </div>
        <div>
          <span className="text-gray-500">Registros:</span>
          <p className="font-medium" data-testid="records-count">{previewData.recordsCount}</p>
        </div>
        <div className="col-span-2">
          <span className="text-gray-500">Total ingresos:</span>
          <p className="font-medium text-lg" data-testid="total-income">
            ${previewData.totalIncome.toLocaleString()}
          </p>
        </div>
      </div>
    </div>
    
    <div className="flex space-x-3">
      <button
        onClick={onReset}
        className="flex-1 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50"
        data-testid="upload-another"
      >
        Subir otro archivo
      </button>
      
      <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
        Ver análisis completo →
      </button>
    </div>
  </div>
);

const ErrorDisplay = ({ message, onRetry }) => (
  <div className="text-center" data-testid="error-display">
    <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-red-800 mb-2">Error al procesar archivo</h3>
    <p className="text-red-700 mb-4" data-testid="error-message">{message}</p>
    
    <button
      onClick={onRetry}
      className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
      data-testid="retry-button"
    >
      <XMarkIcon className="w-4 h-4 mr-2" />
      Intentar nuevamente
    </button>
  </div>
);

const FileFormatInfo = ({ acceptedFormats }) => (
  <div className="mt-6 bg-blue-50 rounded-lg p-4">
    <h4 className="font-medium text-blue-900 mb-2">💡 Consejos para mejores resultados:</h4>
    
    <ul className="text-sm text-blue-800 space-y-1">
      <li>• Use el archivo original descargado de la DIAN</li>
      <li>• Asegúrese de que el archivo no esté corrupto</li>
      <li>• Los formatos soportados son: {acceptedFormats.join(', ')}</li>
      <li>• AccountIA detecta automáticamente la estructura de los datos</li>
    </ul>
    
    <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
      <div className="flex items-center">
        <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mr-2" />
        <p className="text-sm text-yellow-800">
          <strong>Privacidad:</strong> Sus datos se procesan de forma segura y no se almacenan permanentemente.
        </p>
      </div>
    </div>
  </div>
);

export default IntelligentFileUpload;