import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  fullScreen?: boolean;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  message,
  fullScreen = false,
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  const containerClasses = fullScreen 
    ? 'min-h-screen bg-gray-50 flex items-center justify-center p-4'
    : 'flex items-center justify-center p-4';

  return (
    <div className={`${containerClasses} ${className}`}>
      <div className="text-center">
        <Loader2 className={`${sizeClasses[size]} text-blue-600 animate-spin mx-auto mb-3`} />
        {message && (
          <p className={`text-gray-600 ${textSizeClasses[size]}`}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;