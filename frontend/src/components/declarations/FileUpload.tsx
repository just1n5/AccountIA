import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';

interface FileUploadProps {
  onFileUploaded: (file: File) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  isLoading?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUploaded,
  acceptedTypes = ['.xlsx', '.xls'],
  maxSize = 10 * 1024 * 1024, // 10MB
  isLoading = false
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);

    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0].code === 'file-too-large') {
        setError(`El archivo es demasiado grande. Tamaño máximo: ${maxSize / 1024 / 1024}MB`);
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setError(`Tipo de archivo no válido. Solo se aceptan: ${acceptedTypes.join(', ')}`);
      } else {
        setError('Error al cargar el archivo. Por favor, intenta de nuevo.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      onFileUploaded(file);
    }
  }, [maxSize, acceptedTypes, onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => {
      // Mapeo de extensiones a tipos MIME
      const mimeTypes: { [key: string]: string[] } = {
        '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        '.xls': ['application/vnd.ms-excel'],
        '.pdf': ['application/pdf'],
        '.jpg': ['image/jpeg'],
        '.jpeg': ['image/jpeg'],
        '.png': ['image/png']
      };
      
      if (mimeTypes[type]) {
        mimeTypes[type].forEach(mime => {
          acc[mime] = [type];
        });
      }
      return acc;
    }, {} as { [key: string]: string[] }),
    maxSize,
    multiple: false,
    disabled: isLoading
  });

  const removeFile = () => {
    setSelectedFile(null);
    setError(null);
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

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${isDragActive 
              ? 'border-azul-principal bg-azul-claro' 
              : 'border-gris-300 hover:border-azul-principal'
            }
            ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <Upload className="w-12 h-12 mx-auto mb-4 text-gris-700" />
          
          <p className="text-gris-900 font-medium mb-2">
            {isDragActive
              ? 'Suelta el archivo aquí'
              : 'Arrastra y suelta tu archivo de información exógena aquí'
            }
          </p>
          
          <p className="text-gris-700 text-sm mb-4">
            o haz clic para seleccionar
          </p>
          
          <p className="text-gris-700 text-xs">
            Formatos aceptados: {acceptedTypes.join(', ')} • Tamaño máximo: {maxSize / 1024 / 1024}MB
          </p>
        </div>
      ) : (
        <div className="border border-gris-300 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-azul-claro rounded-lg">
                <FileText className="w-6 h-6 text-azul-principal" />
              </div>
              <div>
                <p className="font-medium text-gris-900">{selectedFile.name}</p>
                <p className="text-sm text-gris-700">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            
            {!isLoading && (
              <button
                onClick={removeFile}
                className="p-1 hover:bg-gris-100 rounded-lg transition-colors"
                aria-label="Remover archivo"
              >
                <X className="w-5 h-5 text-gris-700" />
              </button>
            )}
          </div>
          
          {isLoading && (
            <div className="mt-3 pt-3 border-t border-gris-300">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-azul-principal"></div>
                <p className="text-sm text-gris-700">Procesando archivo...</p>
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <Alert type="error" className="mt-4">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </Alert>
      )}
    </div>
  );
};

export default FileUpload;