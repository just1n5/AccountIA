import React, { useState, useEffect } from 'react';
import { Upload, FileText, Check, X, AlertCircle, Info } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';
import api from '../../services/api';

interface DocumentUploadProps {
  declaration: any;
  supportDocuments: any[];
  onDocumentsUpdated: (documents: any[]) => void;
  isLoading?: boolean;
}

interface DocumentRequest {
  id: string;
  type: string;
  title: string;
  description: string;
  required: boolean;
  uploaded?: boolean;
  document?: any;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  declaration,
  supportDocuments,
  onDocumentsUpdated,
  isLoading
}) => {
  const [requestedDocuments, setRequestedDocuments] = useState<DocumentRequest[]>([]);
  const [uploadingDocument, setUploadingDocument] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simular documentos solicitados basados en los datos procesados
    // En una implementación real, esto vendría de la IA
    const mockRequests: DocumentRequest[] = [
      {
        id: '1',
        type: 'health_invoice',
        title: 'Facturas de Salud',
        description: 'Detectamos pagos a servicios de salud. Adjunta las facturas para aplicar deducciones.',
        required: true
      },
      {
        id: '2',
        type: 'mortgage_certificate',
        title: 'Certificado de Crédito Hipotecario',
        description: 'Si tienes un crédito hipotecario, puedes deducir los intereses pagados.',
        required: false
      },
      {
        id: '3',
        type: 'education_invoice',
        title: 'Facturas de Educación',
        description: 'Los gastos en educación de dependientes pueden ser deducibles.',
        required: false
      },
      {
        id: '4',
        type: 'pension_certificate',
        title: 'Certificado de Aportes a Pensión Voluntaria',
        description: 'Los aportes voluntarios a pensión reducen tu base gravable.',
        required: false
      }
    ];

    setRequestedDocuments(mockRequests);
  }, [declaration]);

  const handleFileSelect = async (documentRequest: DocumentRequest, file: File) => {
    setError(null);
    setUploadingDocument(documentRequest.id);

    try {
      // Iniciar la carga del archivo
      const initResponse = await api.post(
        `/api/v1/declarations/${declaration.id}/documents/initiate_upload/`,
        {
          file_name: file.name,
          file_type: documentRequest.type,
          file_size: file.size,
          mime_type: file.type,
          description: documentRequest.title
        }
      );

      const { document_id, upload_url } = initResponse.data;

      // Subir el archivo directamente a la URL firmada
      const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type
        }
      });

      if (!uploadResponse.ok) {
        throw new Error('Error al subir el archivo');
      }

      // Actualizar el estado del documento
      await api.put(`/api/v1/documents/${document_id}/update_status/`, {
        upload_status: 'uploaded'
      });

      // Actualizar el estado local
      const updatedRequests = requestedDocuments.map(req => {
        if (req.id === documentRequest.id) {
          return {
            ...req,
            uploaded: true,
            document: {
              id: document_id,
              name: file.name,
              size: file.size
            }
          };
        }
        return req;
      });

      setRequestedDocuments(updatedRequests);
      onDocumentsUpdated([...supportDocuments, { id: document_id, request_id: documentRequest.id }]);

    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al subir el documento');
      console.error('Error uploading document:', err);
    } finally {
      setUploadingDocument(null);
    }
  };

  const handleRemoveDocument = async (documentRequest: DocumentRequest) => {
    try {
      if (documentRequest.document) {
        await api.delete(`/api/v1/documents/${documentRequest.document.id}/`);
      }

      const updatedRequests = requestedDocuments.map(req => {
        if (req.id === documentRequest.id) {
          return {
            ...req,
            uploaded: false,
            document: undefined
          };
        }
        return req;
      });

      setRequestedDocuments(updatedRequests);
      onDocumentsUpdated(
        supportDocuments.filter(doc => doc.request_id !== documentRequest.id)
      );
    } catch (err: any) {
      setError('Error al eliminar el documento');
      console.error('Error removing document:', err);
    }
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

  const requiredDocumentsCount = requestedDocuments.filter(doc => doc.required).length;
  const uploadedRequiredCount = requestedDocuments.filter(doc => doc.required && doc.uploaded).length;
  const allRequiredUploaded = uploadedRequiredCount === requiredDocumentsCount;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Documentos de Soporte</h2>

      <Alert type="info" className="mb-6">
        <Info className="w-4 h-4" />
        <span>
          Basándonos en tu información, hemos identificado algunos documentos que podrían 
          ayudarte a optimizar tu declaración. Los marcados como requeridos son necesarios 
          para validar las deducciones detectadas.
        </span>
      </Alert>

      {error && (
        <Alert type="error" className="mb-6">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </Alert>
      )}

      <div className="space-y-4 mb-6">
        {requestedDocuments.map((docRequest) => (
          <Card key={docRequest.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-1">
                  <h3 className="font-medium text-gris-900">
                    {docRequest.title}
                  </h3>
                  {docRequest.required && (
                    <span className="ml-2 px-2 py-1 text-xs bg-rojo-error text-white rounded">
                      Requerido
                    </span>
                  )}
                </div>
                <p className="text-sm text-gris-700 mb-3">
                  {docRequest.description}
                </p>

                {docRequest.uploaded && docRequest.document ? (
                  <div className="flex items-center justify-between bg-verde-exito/10 rounded-lg p-3">
                    <div className="flex items-center space-x-3">
                      <Check className="w-5 h-5 text-verde-exito" />
                      <div>
                        <p className="text-sm font-medium text-gris-900">
                          {docRequest.document.name}
                        </p>
                        <p className="text-xs text-gris-700">
                          {formatFileSize(docRequest.document.size)}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemoveDocument(docRequest)}
                      className="p-1 hover:bg-white rounded transition-colors"
                      disabled={uploadingDocument !== null}
                    >
                      <X className="w-4 h-4 text-gris-700" />
                    </button>
                  </div>
                ) : (
                  <div>
                    <input
                      type="file"
                      id={`file-${docRequest.id}`}
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleFileSelect(docRequest, file);
                        }
                      }}
                      className="hidden"
                      disabled={uploadingDocument !== null}
                    />
                    <label
                      htmlFor={`file-${docRequest.id}`}
                      className={`
                        inline-flex items-center px-4 py-2 border border-gris-300 
                        rounded-lg text-sm font-medium text-gris-700 bg-white 
                        hover:bg-gris-50 focus:outline-none focus:ring-2 
                        focus:ring-offset-2 focus:ring-azul-principal cursor-pointer
                        ${uploadingDocument !== null ? 'opacity-50 cursor-not-allowed' : ''}
                      `}
                    >
                      {uploadingDocument === docRequest.id ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-azul-principal mr-2"></div>
                          Subiendo...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          Seleccionar archivo
                        </>
                      )}
                    </label>
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="bg-gris-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-gris-700" />
            <span className="text-sm text-gris-700">
              Documentos requeridos: {uploadedRequiredCount} de {requiredDocumentsCount}
            </span>
          </div>
          {allRequiredUploaded && (
            <div className="flex items-center space-x-2 text-verde-exito">
              <Check className="w-5 h-5" />
              <span className="text-sm font-medium">Todos los documentos requeridos cargados</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;