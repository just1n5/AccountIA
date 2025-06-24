import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Alert } from '../components/ui/Alert';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import FileUpload from '../components/declarations/FileUpload';
import ProcessingStatus from '../components/declarations/ProcessingStatus';
import DataReview from '../components/declarations/DataReview';
import declarationService, { Declaration } from '../services/declarationService';
import documentService, { Document } from '../services/documentService';

enum WizardStep {
  UPLOAD = 'upload',
  PROCESSING = 'processing',
  REVIEW = 'review',
  COMPLETE = 'complete'
}

const DeclarationWizard: React.FC = () => {
  const { declarationId } = useParams<{ declarationId: string }>();
  const navigate = useNavigate();
  
  // DEBUG: Verificar declarationId desde URL
  console.log('DeclarationWizard - declarationId desde useParams:', declarationId);
  console.log('DeclarationWizard - URL actual:', window.location.pathname);
  
  const [currentStep, setCurrentStep] = useState<WizardStep>(WizardStep.UPLOAD);
  const [declaration, setDeclaration] = useState<Declaration | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('');

  // Cargar declaración y documentos al montar el componente
  useEffect(() => {
    if (declarationId) {
      loadDeclarationData();
    }
  }, [declarationId]);

  // Polling para verificar el estado del procesamiento
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (currentStep === WizardStep.PROCESSING) {
      interval = setInterval(() => {
        checkProcessingStatus();
      }, 3000); // Verificar cada 3 segundos
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [currentStep]);

  const loadDeclarationData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      if (!declarationId) {
        throw new Error('ID de declaración no encontrado');
      }

      // Cargar declaración
      const declarationData = await declarationService.getById(declarationId);
      setDeclaration(declarationData);

      // Cargar documentos
      await loadDocuments();
      
      // Determinar el paso actual basado en el estado
      await determineCurrentStep();
      
    } catch (err: any) {
      console.error('Error loading declaration data:', err);
      setError(err.message || 'Error cargando declaración');
    } finally {
      setIsLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      if (!declarationId) return;
      
      // Con documentService.getByDeclaration() ya manejando la extracción,
      // esto debería retornar directamente el array
      const documentsArray = await documentService.getByDeclaration(declarationId);
      console.log('DeclarationWizard - documentsArray from service:', documentsArray);
      
      setDocuments(documentsArray);
    } catch (err) {
      console.error('Error loading documents:', err);
    }
  };

  const determineCurrentStep = async () => {
    try {
      if (!declarationId) return;
      
      const hasProcessedExogena = await documentService.hasProcessedExogena(declarationId);
      
      if (hasProcessedExogena) {
        setCurrentStep(WizardStep.REVIEW);
      } else {
        const exogenaDoc = documents.find(doc => doc.file_type === 'exogena_report');
        
        if (!exogenaDoc) {
          setCurrentStep(WizardStep.UPLOAD);
        } else if (exogenaDoc.upload_status === 'processing') {
          setCurrentStep(WizardStep.PROCESSING);
          setProcessingStatus('Procesando archivo...');
        } else if (exogenaDoc.upload_status === 'error') {
          setCurrentStep(WizardStep.UPLOAD);
          setError('Error procesando archivo. Por favor, inténtalo de nuevo.');
        } else {
          setProcessingStatus('Procesando archivo...');
        }
      }
    } catch (err) {
      console.error('Error determining current step:', err);
    }
  };

  const checkProcessingStatus = async () => {
    try {
      if (!declarationId) return;
      
      await loadDocuments();
      const exogenaDoc = documents.find(doc => doc.file_type === 'exogena_report');
      
      if (exogenaDoc) {
        if (exogenaDoc.upload_status === 'processed') {
          setCurrentStep(WizardStep.REVIEW);
          setProcessingStatus('¡Procesamiento completado!');
        } else if (exogenaDoc.upload_status === 'error') {
          setCurrentStep(WizardStep.UPLOAD);
          setError('Error procesando archivo. Por favor, inténtalo de nuevo.');
        } else {
          setProcessingStatus('Procesando archivo...');
        }
      }
    } catch (err) {
      console.error('Error checking processing status:', err);
    }
  };

  // Handlers de eventos
  const handleFileUploaded = async (documentId: string) => {
    try {
      setCurrentStep(WizardStep.PROCESSING);
      setUploadProgress(100);
      setProcessingStatus('Archivo subido, iniciando procesamiento...');
        
      // Recargar documentos
      await loadDocuments();
    } catch (err) {
      setError('Error después de subir archivo');
      console.error('Error handling file upload:', err);
    }
  };

  const handleUploadProgress = (progress: number) => {
    setUploadProgress(progress);
  };

  const handleReprocess = async () => {
    const exogenaDoc = documents.find(doc => doc.file_type === 'exogena_report');
    if (!exogenaDoc) return;
      
    try {
      await documentService.reprocess(exogenaDoc.id);
      setCurrentStep(WizardStep.PROCESSING);
      setError(null);
    } catch (err) {
      setError('Error iniciando re-procesamiento');
      console.error('Error reprocessing:', err);
    }
  };

  const handleContinueToReview = () => {
    setCurrentStep(WizardStep.REVIEW);
  };

  const handleBackToUpload = () => {
    setCurrentStep(WizardStep.UPLOAD);
    setError(null);
  };

  const handleCompleteDeclaration = async () => {
    try {
      if (!declaration) return;
      
      await declarationService.markAsCompleted(declaration.id);
      setCurrentStep(WizardStep.COMPLETE);
    } catch (err) {
      setError('Error completando declaración');
      console.error('Error completing declaration:', err);
    }
  };

  // Renderizado condicional por paso
  const renderStepContent = () => {
    // DEBUG: Verificar estado de documents
    console.log('DeclarationWizard - documents state:', documents);
    console.log('DeclarationWizard - documents tipo:', typeof documents);
    console.log('DeclarationWizard - documents es array?:', Array.isArray(documents));
    
    switch (currentStep) {
      case WizardStep.UPLOAD:
        return (
          <FileUpload
            declarationId={declarationId!}
            onFileUploaded={handleFileUploaded}
            onUploadProgress={handleUploadProgress}
            existingDocuments={documents} // Ya debería ser array siempre
            onReprocess={handleReprocess}
          />
        );
          
      case WizardStep.PROCESSING:
        return (
          <ProcessingStatus
            status={processingStatus}
            progress={uploadProgress}
            onCheckStatus={checkProcessingStatus}
          />
        );
          
      case WizardStep.REVIEW:
        const exogenaDoc = documents.find(doc =>
          doc.file_type === 'exogena_report' && doc.upload_status === 'processed'
        );
          
        return (
          <DataReview
            declarationId={declarationId!}
            document={exogenaDoc}
            onComplete={handleCompleteDeclaration}
            onBackToUpload={handleBackToUpload}
          />
        );
          
      case WizardStep.COMPLETE:
        return (
          <Card className="p-8 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-6" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              ¡Declaración Completada!
            </h2>
            <p className="text-gray-600 mb-6">
              Tu declaración de renta ha sido procesada exitosamente.
            </p>
            <div className="flex justify-center space-x-4">
              <Button
                onClick={() => navigate('/app/declarations')}
                variant="outline"
              >
                Ver Todas las Declaraciones
              </Button>
              <Button
                onClick={() => navigate('/app')}
              >
                Ir al Dashboard
              </Button>
            </div>
          </Card>
        );
          
      default:
        return null;
    }
  };

  const getStepNumber = (step: WizardStep): number => {
    switch (step) {
      case WizardStep.UPLOAD: return 1;
      case WizardStep.PROCESSING: return 2;
      case WizardStep.REVIEW: return 3;
      case WizardStep.COMPLETE: return 4;
      default: return 1;
    }
  };

  const getStepTitle = (step: WizardStep): string => {
    switch (step) {
      case WizardStep.UPLOAD: return 'Subir Documentos';
      case WizardStep.PROCESSING: return 'Procesamiento';
      case WizardStep.REVIEW: return 'Revisar Información';
      case WizardStep.COMPLETE: return 'Completado';
      default: return '';
    }
  };

  const isStepCompleted = (step: WizardStep): boolean => {
    const currentStepNumber = getStepNumber(currentStep);
    const stepNumber = getStepNumber(step);
    return stepNumber < currentStepNumber || currentStep === WizardStep.COMPLETE;
  };

  const isStepCurrent = (step: WizardStep): boolean => {
    return step === currentStep;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!declaration) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Declaración no encontrada
          </h2>
          <Button onClick={() => navigate('/app')}>
            Volver al Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/app')}
                className="flex items-center"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Declaración de Renta {declaration.fiscal_year}
                </h1>
                <p className="text-sm text-gray-600">
                  {getStepTitle(currentStep)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stepper */}
        <div className="mb-8">
          <nav aria-label="Progress">
            <ol className="flex items-center">
              {Object.values(WizardStep).filter(step => step !== WizardStep.COMPLETE).map((step, index) => {
                const stepNumber = getStepNumber(step);
                const isCompleted = isStepCompleted(step);
                const isCurrent = isStepCurrent(step);
                const isLast = index === Object.values(WizardStep).filter(s => s !== WizardStep.COMPLETE).length - 1;

                return (
                  <li key={step} className={`relative ${!isLast ? 'pr-8 sm:pr-20' : ''}`}>
                    {!isLast && (
                      <div className="absolute inset-0 flex items-center" aria-hidden="true">
                        <div className={`h-0.5 w-full ${
                          isCompleted ? 'bg-blue-600' : 'bg-gray-200'
                        }`} />
                      </div>
                    )}
                    <div className="relative flex items-center justify-center">
                      {isCompleted ? (
                        <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
                          <CheckCircle className="w-5 h-5 text-white" />
                        </div>
                      ) : isCurrent ? (
                        <div className="h-8 w-8 rounded-full border-2 border-blue-600 bg-white flex items-center justify-center">
                          <span className="h-2.5 w-2.5 rounded-full bg-blue-600" />
                        </div>
                      ) : (
                        <div className="h-8 w-8 rounded-full border-2 border-gray-300 bg-white flex items-center justify-center">
                          <span className="h-2.5 w-2.5 rounded-full bg-transparent" />
                        </div>
                      )}
                    </div>
                    <div className="absolute top-10 left-1/2 transform -translate-x-1/2">
                      <span className={`text-xs font-medium ${
                        isCurrent ? 'text-blue-600' : isCompleted ? 'text-gray-900' : 'text-gray-500'
                      }`}>
                        {getStepTitle(step)}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ol>
          </nav>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert type="error" className="mb-6">
            <span>{error}</span>
          </Alert>
        )}

        {/* Step Content */}
        <div className="space-y-6">
          {renderStepContent()}
        </div>

        {/* Navigation (only show in certain steps) */}
        {(currentStep === WizardStep.REVIEW) && (
          <div className="mt-8 flex justify-between">
            <Button
              variant="outline"
              onClick={handleBackToUpload}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver a Subir Archivo
            </Button>
            
            <Button
              onClick={handleCompleteDeclaration}
            >
              Completar Declaración
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeclarationWizard;