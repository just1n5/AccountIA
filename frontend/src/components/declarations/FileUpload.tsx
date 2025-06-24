import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { Card } from '../ui/Card';
import documentService, { Document } from '../../services/documentService';

interface FileUploadProps {
  declarationId: string;
  onFileUploaded: (documentId: string) => void;
  onUploadProgress?: (progress: number) => void;
  existingDocuments?: Document[];
  onReprocess?: () => void;
  maxSize?: number;
}

const FileUpload: React.FC<FileUploadProps> = ({
  declarationId,
  onFileUploaded,
  onUploadProgress,
  existingDocuments = [], // Asegurar que siempre sea un array
  onReprocess,
  maxSize = 50 * 1024 * 1024 // 50MB
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStage, setUploadStage] = useState('');

  // Verificar si ya existe un documento de exógena
  console.log('FileUpload - existingDocuments:', existingDocuments);
  console.log('FileUpload - existingDocuments tipo:', typeof existingDocuments);
  console.log('FileUpload - es array?:', Array.isArray(existingDocuments));
  
  // Con el documentService corregido, esto debería ser siempre un array
  const existingExogena = Array.isArray(existingDocuments) 
    ? existingDocuments.find(doc => doc.file_type === 'exogena_report')
    : undefined;

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);

    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0].code === 'file-too-large') {
        setError(`El archivo es demasiado grande. Tamaño máximo: ${maxSize / 1024 / 1024}MB`);
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setError('Solo se aceptan archivos Excel (.xlsx, .xls)');
      } else {
        setError('Error al cargar el archivo. Por favor, intenta de nuevo.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validar archivo antes de subirlo
      const validation = documentService.validateFile(file);
      if (!validation.valid) {
        setError(validation.error!);
        return;
      }

      setSelectedFile(file);
      await handleUpload(file);
    }
  }, [declarationId, maxSize]);

  const handleUpload = async (file: File) => {
    // DEBUG: Verificar declarationId
    console.log('FileUpload - declarationId recibido:', declarationId);
    console.log('FileUpload - tipo:', typeof declarationId);
    console.log('FileUpload - existingDocuments:', existingDocuments);
    console.log('FileUpload - existingDocuments tipo:', typeof existingDocuments);
    console.log('FileUpload - es array?:', Array.isArray(existingDocuments));
    
    if (!declarationId) {
    setError('Error: No se proporcionó ID de declaración');
    return;
  }
    
    try {
      setIsUploading(true);
      setUploadProgress(0);
      setError(null);

      // Para testing, usar upload directo
      setUploadStage('Subiendo archivo...');
      setUploadProgress(20);
      onUploadProgress?.(20);

      // Crear FormData
      const formData = new FormData();
      formData.append('file', file);

      setUploadProgress(50);
      onUploadProgress?.(50);

      // Upload directo al endpoint de testing
      const response = await fetch(
        `http://localhost:8000/api/v1/declarations/${declarationId}/upload-testing/`,
        {
          method: 'POST',
          body: formData,
        }
      );

      setUploadProgress(90);
      onUploadProgress?.(90);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
        throw new Error(errorData.error || `Error HTTP ${response.status}`);
      }

      const result = await response.json();
      
      setUploadProgress(100);
      onUploadProgress?.(100);
      setUploadStage('¡Completado!');

      // Notificar que el upload fue exitoso
      onFileUploaded(result.document_id);
      
    } catch (err: any) {
      console.error('Error uploading file:', err);
      setError(err.message || 'Error subiendo archivo');
    } finally {
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxSize,
    multiple: false,
    disabled: isUploading
  });

  const removeFile = () => {
    setSelectedFile(null);
    setError(null);
    setUploadProgress(0);
    setUploadStage('');
  };

  const formatFileSize = (size: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let index = 0;
    let formattedSize = size;

    while (formattedSize >= 1024 && index < units.length - 1) {
      formattedSize /= 1024;
      index++;
    }

    return `${formattedSize.toFixed(1)} ${units[index]}`;
  };

  const getStatusDisplay = (status: string) => {
    const statusConfig = {
      pending: { label: 'Pendiente', color: 'text-gray-600', icon: FileText },
      uploading: { label: 'Subiendo', color: 'text-blue-600', icon: Upload },
      uploaded: { label: 'Subido', color: 'text-green-600', icon: CheckCircle },
      processing: { label: 'Procesando', color: 'text-blue-600', icon: RefreshCw },
      processed: { label: 'Procesado', color: 'text-green-600', icon: CheckCircle },
      error: { label: 'Error', color: 'text-red-600', icon: AlertCircle }
    };
    
    return statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
  };

  // Si ya existe un documento de exógena, mostrar su estado
  if (existingExogena) {
    const statusDisplay = getStatusDisplay(existingExogena.upload_status);
    const StatusIcon = statusDisplay.icon;

    return (
      <Card className="p-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Archivo de Información Exógena
          </h3>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <StatusIcon className={`w-6 h-6 ${statusDisplay.color}`} />
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  {existingExogena.original_file_name}
                </p>
                <p className="text-sm text-gray-600">
                  Estado: <span className={statusDisplay.color}>{statusDisplay.label}</span>
                  {existingExogena.file_size && (
                    <span> • {formatFileSize(existingExogena.file_size)}</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Mostrar errores si los hay */}
          {existingExogena.upload_status === 'error' && existingExogena.processing_errors.length > 0 && (
            <Alert type="error">
              <AlertCircle className="w-4 h-4" />
              <div>
                <p className="font-medium">Error procesando archivo:</p>
                <ul className="mt-1 list-disc list-inside text-sm">
                  {existingExogena.processing_errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            </Alert>
          )}

          {/* Botones de acción */}
          <div className="flex space-x-3">
            {existingExogena.upload_status === 'error' && onReprocess && (
              <Button onClick={onReprocess} variant="outline">
                <RefreshCw className="w-4 h-4 mr-2" />
                Reprocesar
              </Button>
            )}
            
            <Button
              onClick={() => {
                setSelectedFile(null);
                setError(null);
                // Aquí podrías implementar la eliminación del documento existente
                // y permitir subir uno nuevo
              }}
              variant="outline"
            >
              Subir Nuevo Archivo
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Subir Archivo de Información Exógena
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Sube tu archivo Excel con la información exógena de la DIAN
          </p>
        </div>

        {!selectedFile ? (
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
              transition-colors duration-200
              ${isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-blue-500'
              }
              ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            
            <p className="text-gray-900 font-medium mb-2">
              {isDragActive
                ? 'Suelta el archivo aquí'
                : 'Arrastra y suelta tu archivo de información exógena aquí'
              }
            </p>
            
            <p className="text-gray-600 text-sm mb-4">
              o haz clic para seleccionar
            </p>
            
            <p className="text-gray-500 text-xs">
              Formatos aceptados: .xlsx, .xls • Tamaño máximo: {maxSize / 1024 / 1024}MB
            </p>
          </div>
        ) : (
          <div className="border border-gray-300 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-600">{formatFileSize(selectedFile.size)}</p>
                </div>
              </div>
              
              {!isUploading && (
                <button
                  onClick={removeFile}
                  className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                  aria-label="Remover archivo"
                >
                  <X className="w-5 h-5 text-gray-600" />
                </button>
              )}
            </div>
            
            {isUploading && (
              <div className="mt-4 space-y-3">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>{uploadStage}</span>
                  <span>{Math.round(uploadProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <Alert type="error">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </Alert>
        )}

        {/* Información adicional */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
            </div>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">¿Qué es la información exógena?</p>
              <p>
                Es el archivo Excel que puedes descargar desde el portal de la DIAN con toda tu 
                información de ingresos, retenciones y certificados del año fiscal.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default FileUpload;