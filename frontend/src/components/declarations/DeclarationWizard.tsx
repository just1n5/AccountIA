import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Check, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';
import FileUpload from './FileUpload';
import DataReview from './DataReview';
import DocumentUpload from './DocumentUpload';
import DraftPreview from './DraftPreview';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

interface Step {
  id: number;
  title: string;
  description: string;
  component: React.ComponentType<any>;
}

const DeclarationWizard: React.FC = () => {
  const navigate = useNavigate();
  const { declarationId } = useParams<{ declarationId: string }>();
  const { user } = useAuth();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [declaration, setDeclaration] = useState<any>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [processedData, setProcessedData] = useState<any>(null);
  const [supportDocuments, setSupportDocuments] = useState<any[]>([]);

  const steps: Step[] = [
    {
      id: 1,
      title: 'Carga de Exógena',
      description: 'Sube tu archivo de información exógena',
      component: FileUpload
    },
    {
      id: 2,
      title: 'Revisión de Datos',
      description: 'Revisa los datos extraídos de tu archivo',
      component: DataReview
    },
    {
      id: 3,
      title: 'Documentos de Soporte',
      description: 'Adjunta los documentos solicitados',
      component: DocumentUpload
    },
    {
      id: 4,
      title: 'Borrador Final',
      description: 'Revisa tu declaración completa',
      component: DraftPreview
    }
  ];

  useEffect(() => {
    if (declarationId) {
      fetchDeclaration();
    }
  }, [declarationId]);

  const fetchDeclaration = async () => {
    try {
      setIsLoading(true);
      const response = await api.get(`/declarations/${declarationId}/`);
      setDeclaration(response.data);
    } catch (err: any) {
      setError('Error al cargar la declaración');
      console.error('Error fetching declaration:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUploaded = async (file: File) => {
    setUploadedFile(file);
    setError(null);

    try {
      setIsLoading(true);

      // Iniciar la carga del archivo
      const initResponse = await api.post(
        `/declarations/${declarationId}/documents/initiate_upload/`,
        {
          file_name: file.name,
          file_type: 'exogena_report',
          file_size: file.size,
          mime_type: file.type
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
      await api.put(`/documents/${document_id}/update_status/`, {
        upload_status: 'uploaded'
      });

      // Iniciar el procesamiento
      await api.post(`/declarations/${declarationId}/process_documents/`);

      // Esperar un momento y verificar el estado
      setTimeout(() => {
        checkProcessingStatus(document_id);
      }, 2000);

    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al procesar el archivo');
      console.error('Error uploading file:', err);
      setIsLoading(false);
    }
  };

  const checkProcessingStatus = async (documentId: string) => {
    try {
      const maxAttempts = 30; // 30 intentos * 2 segundos = 1 minuto máximo
      let attempts = 0;

      const checkStatus = async () => {
        const response = await api.get(`/documents/${documentId}/`);
        const document = response.data;

        if (document.upload_status === 'processed') {
          // Obtener datos procesados
          const processedResponse = await api.get(
            `/documents/${documentId}/processed_data/`
          );
          setProcessedData(processedResponse.data);
          setIsLoading(false);
          
          // Avanzar al siguiente paso
          setCurrentStep(2);
        } else if (document.upload_status === 'error') {
          setError('Error al procesar el archivo. Por favor, verifica el formato.');
          setIsLoading(false);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(checkStatus, 2000);
        } else {
          setError('El procesamiento está tomando más tiempo del esperado. Por favor, intenta más tarde.');
          setIsLoading(false);
        }
      };

      await checkStatus();
    } catch (err: any) {
      setError('Error al verificar el estado del procesamiento');
      console.error('Error checking status:', err);
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    try {
      setIsLoading(true);
      
      // Actualizar estado de la declaración a completada
      await api.post(`/declarations/${declarationId}/update_status/`, {
        status: 'completed'
      });

      // Navegar a la página de pago o resumen
      navigate(`/dashboard/declarations/${declarationId}/summary`);
    } catch (err: any) {
      setError('Error al completar la declaración');
      console.error('Error completing declaration:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const CurrentStepComponent = steps[currentStep - 1].component;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center text-gris-700 hover:text-gris-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver al Dashboard
        </button>
        
        <h1 className="text-3xl font-bold text-gris-900">
          Declaración de Renta {declaration?.fiscal_year}
        </h1>
        <p className="text-gris-700 mt-2">
          Sigue los pasos para completar tu declaración
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${index < steps.length - 1 ? 'flex-1' : ''}`}
            >
              <div className="flex items-center">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center
                    ${currentStep > step.id
                      ? 'bg-verde-exito text-white'
                      : currentStep === step.id
                      ? 'bg-azul-principal text-white'
                      : 'bg-gris-300 text-gris-700'
                    }
                  `}
                >
                  {currentStep > step.id ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    step.id
                  )}
                </div>
                <div className="ml-3">
                  <p
                    className={`font-medium ${
                      currentStep >= step.id ? 'text-gris-900' : 'text-gris-700'
                    }`}
                  >
                    {step.title}
                  </p>
                  <p className="text-sm text-gris-700 hidden sm:block">
                    {step.description}
                  </p>
                </div>
              </div>
              
              {index < steps.length - 1 && (
                <div
                  className={`
                    flex-1 h-1 mx-4
                    ${currentStep > step.id ? 'bg-verde-exito' : 'bg-gris-300'}
                  `}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="error" className="mb-6">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </Alert>
      )}

      {/* Step Content */}
      <Card className="mb-8">
        <CurrentStepComponent
          onFileUploaded={handleFileUploaded}
          isLoading={isLoading}
          processedData={processedData}
          declaration={declaration}
          supportDocuments={supportDocuments}
          onDocumentsUpdated={setSupportDocuments}
        />
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="secondary"
          onClick={handlePrevious}
          disabled={currentStep === 1 || isLoading}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Anterior
        </Button>

        {currentStep < steps.length ? (
          <Button
            onClick={handleNext}
            disabled={isLoading}
          >
            Siguiente
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        ) : (
          <Button
            onClick={handleComplete}
            disabled={isLoading}
            className="bg-verde-exito hover:bg-verde-exito/90"
          >
            Completar Declaración
            <Check className="w-4 h-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  );
};

export default DeclarationWizard;