// frontend/src/components/declarations/WizardSteps.tsx
import React from 'react';
import { CheckCircle, Circle, Clock } from 'lucide-react';

export enum WizardStep {
  UPLOAD = 'upload',
  PROCESSING = 'processing',
  REVIEW = 'review',
  COMPLETE = 'complete'
}

interface Step {
  key: WizardStep;
  label: string;
  description?: string;
}

interface WizardStepsProps {
  currentStep: WizardStep;
  completedSteps?: WizardStep[];
  className?: string;
}

const STEPS: Step[] = [
  {
    key: WizardStep.UPLOAD,
    label: 'Subir Archivo',
    description: 'Carga tu información exógena'
  },
  {
    key: WizardStep.PROCESSING,
    label: 'Procesando',
    description: 'Analizando los datos'
  },
  {
    key: WizardStep.REVIEW,
    label: 'Revisar Datos',
    description: 'Confirma la información'
  }
];

const WizardSteps: React.FC<WizardStepsProps> = ({
  currentStep,
  completedSteps = [],
  className = ''
}) => {
  const getStepIndex = (step: WizardStep): number => {
    return STEPS.findIndex(s => s.key === step);
  };

  const currentStepIndex = getStepIndex(currentStep);

  const getStepStatus = (step: Step, index: number): 'completed' | 'current' | 'pending' => {
    if (completedSteps.includes(step.key)) return 'completed';
    if (step.key === currentStep) return 'current';
    if (index < currentStepIndex) return 'completed';
    return 'pending';
  };

  const getStepStyles = (status: 'completed' | 'current' | 'pending') => {
    switch (status) {
      case 'completed':
        return {
          circle: 'bg-verde-exito border-verde-exito text-white',
          label: 'text-verde-exito font-semibold',
          description: 'text-gray-600'
        };
      case 'current':
        return {
          circle: 'bg-azul-principal border-azul-principal text-white',
          label: 'text-azul-principal font-semibold',
          description: 'text-gray-700'
        };
      case 'pending':
        return {
          circle: 'bg-white border-gray-300 text-gray-400',
          label: 'text-gray-400',
          description: 'text-gray-400'
        };
    }
  };

  const getStepIcon = (status: 'completed' | 'current' | 'pending', stepNumber: number) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5" />;
      case 'current':
        return <Clock className="w-5 h-5" />;
      case 'pending':
        return <span className="text-sm font-medium">{stepNumber}</span>;
    }
  };

  const getConnectorStyles = (index: number): string => {
    const isCompleted = index < currentStepIndex || completedSteps.length > index;
    return isCompleted ? 'bg-verde-exito' : 'bg-gray-300';
  };

  return (
    <div className={`w-full py-6 bg-white border-b border-gray-200 ${className}`}>
      <div className="max-w-4xl mx-auto px-6">
        <nav aria-label="Progreso de declaración" className="flex justify-center">
          <ol className="flex items-center space-x-8">
            {STEPS.map((step, index) => {
              const status = getStepStatus(step, index);
              const styles = getStepStyles(status);

              return (
                <li key={step.key} className="flex items-center">
                  {/* Step Content */}
                  <div className="flex flex-col items-center text-center">
                    {/* Circle with Icon/Number */}
                    <div className={`
                      flex items-center justify-center w-10 h-10 rounded-full border-2 
                      transition-all duration-200 ${styles.circle}
                    `}>
                      {getStepIcon(status, index + 1)}
                    </div>

                    {/* Step Label */}
                    <div className="mt-3 text-center">
                      <span className={`block text-sm font-medium ${styles.label}`}>
                        {step.label}
                      </span>
                      {step.description && (
                        <span className={`block text-xs mt-1 ${styles.description}`}>
                          {step.description}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Connector Line */}
                  {index < STEPS.length - 1 && (
                    <div className="flex items-center ml-8">
                      <div className={`
                        w-16 h-0.5 transition-all duration-300
                        ${getConnectorStyles(index)}
                      `} />
                    </div>
                  )}
                </li>
              );
            })}
          </ol>
        </nav>

        {/* Progress Bar (Optional visual enhancement) */}
        <div className="mt-8 max-w-md mx-auto">
          <div className="bg-gray-200 rounded-full h-2">
            <div 
              className="bg-azul-principal h-2 rounded-full transition-all duration-500 ease-out"
              style={{ 
                width: `${((currentStepIndex + 1) / STEPS.length) * 100}%` 
              }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>0%</span>
            <span className="text-azul-principal font-medium">
              {Math.round(((currentStepIndex + 1) / STEPS.length) * 100)}% completado
            </span>
            <span>100%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WizardSteps;
