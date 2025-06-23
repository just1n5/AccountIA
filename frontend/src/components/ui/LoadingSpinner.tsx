import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = 'primary',
  className = '' 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6',
    large: 'w-8 h-8'
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    white: 'text-white'
  };

  return (
    <div className={`inline-block animate-spin ${sizeClasses[size]} ${colorClasses[color]} ${className}`}>
      <svg
        className="w-full h-full"
        fill="none"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          d="m100 50c0 27.614-22.386 50-50 50s-50-22.386-50-50 22.386-50 50-50 50 22.386 50 50z"
          fill="currentColor"
        />
        <path
          className="opacity-75"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          fill="currentColor"
        />
      </svg>
    </div>
  );
};

// Componente de spinner con texto
export const LoadingSpinnerWithText: React.FC<{
  text?: string;
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}> = ({ 
  text = 'Cargando...', 
  size = 'medium', 
  color = 'primary',
  className = '' 
}) => {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <LoadingSpinner size={size} color={color} />
      <span className="text-sm text-gray-600">{text}</span>
    </div>
  );
};

// Componente de overlay de carga para pantalla completa
export const LoadingOverlay: React.FC<{
  isVisible: boolean;
  text?: string;
  backdrop?: boolean;
}> = ({ 
  isVisible, 
  text = 'Cargando...', 
  backdrop = true 
}) => {
  if (!isVisible) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${
      backdrop ? 'bg-black bg-opacity-50' : ''
    }`}>
      <div className="bg-white rounded-lg p-6 shadow-lg">
        <LoadingSpinnerWithText text={text} size="large" />
      </div>
    </div>
  );
};

export default LoadingSpinner;
