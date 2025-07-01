// frontend/src/pages/DeclarationWizard.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, User, LogOut, RefreshCw } from 'lucide-react'; // ✅ Agregar iconos para el header
import { useAuth } from '../contexts/AuthContext';
import { declarationService } from '../services/declarationService';
import { documentService } from '../services/documentService';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Alert } from '../components/ui/Alert';
import { Button } from '../components/ui/Button'; // ✅ Agregar Button para el header

// Import improved components
import WizardSteps, { WizardStep } from '../components/declarations/WizardSteps';
import FileUpload from '../components/declarations/FileUpload';
import DataReview from '../components/declarations/DataReview';
import ProcessingStatus from '../components/declarations/ProcessingStatus';

// Types
interface Declaration {
  id: string;
  fiscal_year: number;
  status: string;
  created_at: string;
}

interface Document {
  id: string;
  file_name: string;
  file_type: string;
  upload_status: string;
  processing_summary?: any;
  created_at: string;
}

const DeclarationWizard: React.FC = () => {
  const { declarationId } = useParams<{ declarationId: string }>();
  const navigate = useNavigate();
  const { user, logout } = useAuth(); // ✅ Agregar logout al hook
  
  // Estado
  const [currentStep, setCurrentStep] = useState<WizardStep>(WizardStep.UPLOAD);
  const [completedSteps, setCompletedSteps] = useState<WizardStep[]>([]);
  const [declaration, setDeclaration] = useState<Declaration | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [isLoggingOut, setIsLoggingOut] = useState(false); // ✅ Estado para logout

  // Effects
  useEffect(() => {
    initializeWizard();
  }, [declarationId]);

  useEffect(() => {
    // Auto-check processing status when in processing step
    if (currentStep === WizardStep.PROCESSING) {
      const interval = setInterval(checkProcessingStatus, 3000);
      return () => clearInterval(interval);
    }
  }, [currentStep]);

  const initializeWizard = async () => {
    try {
      setLoading(true);
      setError(null);

      if (declarationId) {
        await Promise.all([
          loadDeclaration(),
          loadDocuments()
        ]);
      } else {
        await createNewDeclaration();
      }
    } catch (err) {
      console.error('Error initializing wizard:', err);
      setError('Error inicializando el asistente. Por favor, intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  // ✅ NUEVA FUNCIÓN: Manejar logout
  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  // ✅ NUEVA FUNCIÓN: Navegar al dashboard
  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const createNewDeclaration = async () => {
    try {
      const newDeclaration = await declarationService.create({
        fiscal_year: new Date().getFullYear(),
        status: 'draft'
      });
      
      setDeclaration(newDeclaration);
      
      // Update URL without triggering navigation
      window.history.replaceState(
        null, 
        '', 
        `/app/declaraciones/${newDeclaration.id}`
      );
    } catch (err) {
      throw new Error('Error creando nueva declaración');
    }
  };

  const loadDeclaration = async () => {
    if (!declarationId) return;
    
    try {
      const decl = await declarationService.getById(declarationId);
      setDeclaration(decl);
    } catch (err) {
      throw new Error('Error cargando declaración');
    }
  };

  const loadDocuments = async () => {
    if (!declarationId) return;
    
    try {
      const docs = await documentService.getByDeclaration(declarationId);
      setDocuments(docs);
      
      // Determine current step based on document status
      const exogenaDoc = docs.find(doc => doc.file_type === 'exogena_report');
      
      if (exogenaDoc) {
        switch (exogenaDoc.upload_status) {
          case 'processed':
            setCurrentStep(WizardStep.REVIEW);
            setCompletedSteps([WizardStep.UPLOAD, WizardStep.PROCESSING]);
            break;
          case 'processing':
          case 'uploaded':
            setCurrentStep(WizardStep.PROCESSING);
            setCompletedSteps([WizardStep.UPLOAD]);
            break;
          case 'error':
            setCurrentStep(WizardStep.UPLOAD);
            setError('Error procesando el archivo. Por favor, intenta subir el archivo nuevamente.');
            break;
          default:
            setCurrentStep(WizardStep.UPLOAD);
        }
      }
    } catch (err) {
      console.error('Error loading documents:', err);
      // Don't throw here, just log the error
    }
  };

  const checkProcessingStatus = async () => {
    const exogenaDoc = documents.find(doc => doc.file_type === 'exogena_report');
    if (!exogenaDoc) return;

    try {
      const updatedDoc = await documentService.getById(exogenaDoc.id);
      
      // Update documents array
      setDocuments(prev => 
        prev.map(doc => doc.id === updatedDoc.id ? updatedDoc : doc)
      );

      if (updatedDoc.upload_status === 'processed') {
        setCurrentStep(WizardStep.REVIEW);
        setCompletedSteps([WizardStep.UPLOAD, WizardStep.PROCESSING]);
        setProcessingStatus('Procesamiento completado exitosamente');
      } else if (updatedDoc.upload_status === 'error') {
        setCurrentStep(WizardStep.UPLOAD);
        setCompletedSteps([]);
        setError('Error procesando archivo. Por favor, inténtalo de nuevo.');
      } else {
        setProcessingStatus('Procesando archivo...');
      }
    } catch (err) {
      console.error('Error checking processing status:', err);
    }
  };

  // Event Handlers
  const handleFileUploaded = async (documentId: string) => {
    try {
      setCurrentStep(WizardStep.PROCESSING);
      setCompletedSteps([WizardStep.UPLOAD]);
      setUploadProgress(100);
      setProcessingStatus('Archivo subido, iniciando procesamiento...');
      setError(null);
      
      // Reload documents
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
      setCompletedSteps([WizardStep.UPLOAD]);
      setError(null);
      setProcessingStatus('Reiniciando procesamiento...');
    } catch (err) {
      setError('Error iniciando re-procesamiento');
      console.error('Error reprocessing:', err);
    }
  };

  const handleContinueToReview = () => {
    setCurrentStep(WizardStep.REVIEW);
    setCompletedSteps([WizardStep.UPLOAD, WizardStep.PROCESSING]);
  };

  const handleBackToUpload = () => {
    setCurrentStep(WizardStep.UPLOAD);
    setCompletedSteps([]);
    setError(null);
  };

  const handleContinueFromReview = () => {
    // Navigate to next part of the wizard (AI assistant, etc.)
    navigate(`/app/declaraciones/${declaration?.id}/asistente`);
  };

  // ✅ NUEVA FUNCIÓN: Cancelar y eliminar documento
  const handleCancelAndDelete = async () => {
    const exogenaDoc = documents.find(doc => 
      doc.file_type === 'exogena_report' && doc.upload_status === 'processed'
    );
    
    if (!exogenaDoc) {
      console.warn('No se encontró documento para eliminar');
      handleBackToUpload();
      return;
    }

    try {
      setLoading(true);
      
      // Confirmar con el usuario
      const confirmed = window.confirm(
        '¿Estás seguro de que quieres eliminar este documento y empezar de nuevo? Esta acción no se puede deshacer.'
      );
      
      if (!confirmed) {
        setLoading(false);
        return;
      }

      console.log('🗑️ Eliminando documento:', exogenaDoc.id);
      
      // Eliminar el documento
      await documentService.delete(exogenaDoc.id);
      
      // Limpiar estado
      setDocuments([]);
      setCurrentStep(WizardStep.UPLOAD);
      setCompletedSteps([]);
      setError(null);
      setProcessingStatus('');
      setUploadProgress(0);
      
      console.log('✅ Documento eliminado exitosamente');
      
    } catch (err) {
      console.error('Error eliminando documento:', err);
      setError('Error eliminando el documento. Por favor, inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  // Render step content
  const renderStepContent = () => {
    if (!declaration) return null;

    switch (currentStep) {
      case WizardStep.UPLOAD:
        return (
          <FileUpload
            declarationId={declaration.id}
            onFileUploaded={handleFileUploaded}
            onUploadProgress={handleUploadProgress}
            existingDocuments={documents}
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
        
        if (!exogenaDoc) {
          return (
            <div className="text-center py-12">
              <p className="text-gray-600">No se encontró el documento procesado.</p>
              <button 
                onClick={handleBackToUpload}
                className="mt-4 text-azul-principal hover:text-azul-principal-dark"
              >
                Volver a subir archivo
              </button>
            </div>
          );
        }
        
        return (
          <DataReview
            declarationId={declaration.id}
            document={exogenaDoc}
            onContinue={handleContinueFromReview}
            onBackToUpload={handleBackToUpload}
            onCancelAndDelete={handleCancelAndDelete} // ✅ Nueva prop
          />
        );
        
      default:
        return <div>Paso no reconocido</div>;
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 mt-4">Cargando asistente de declaración...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !declaration) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <Alert type="error" title="Error">
            {error}
          </Alert>
          <button 
            onClick={initializeWizard}
            className="mt-4 px-4 py-2 bg-azul-principal text-white rounded-lg hover:bg-azul-principal-dark"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ✅ HEADER AGREGADO */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">AccountIA</h1>
              </div>
              
              {/* Breadcrumb */}
              <nav className="hidden sm:flex items-center space-x-2 text-sm text-gray-500">
                <button 
                  onClick={handleBackToDashboard}
                  className="hover:text-gray-700 transition-colors"
                >
                  Dashboard
                </button>
                <span>›</span>
                <span>Asistente de Declaración</span>
                {declaration && (
                  <>
                    <span>›</span>
                    <span className="text-gray-900 font-medium">{declaration.fiscal_year}</span>
                  </>
                )}
              </nav>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900 truncate max-w-32">
                      {user?.displayName || user?.email}
                    </p>
                    <p className="text-xs text-gray-500">Usuario</p>
                  </div>
                </div>
              </div>

              {/* Back to Dashboard Button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleBackToDashboard}
                className="hidden sm:flex"
              >
                Dashboard
              </Button>

              {/* Logout Button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="text-red-600 border-red-600 hover:bg-red-600 hover:text-white transition-colors"
              >
                {isLoggingOut ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                    <span className="hidden sm:inline">Saliendo...</span>
                  </>
                ) : (
                  <>
                    <LogOut className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Cerrar Sesión</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* ✅ CONTENIDO PRINCIPAL */}
      {/* Wizard Steps */}
      <WizardSteps 
        currentStep={currentStep} 
        completedSteps={completedSteps}
      />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {/* Error Alert */}
        {error && (
          <div className="px-6 py-4">
            <Alert type="error" title="Error" onClose={() => setError(null)} closable>
              {error}
            </Alert>
          </div>
        )}

        {/* Step Content */}
        <div className="pb-8">
          {renderStepContent()}
        </div>
      </div>

      {/* Debug Info removido para limpieza de UI */}
    </div>
  );
};

export default DeclarationWizard;
