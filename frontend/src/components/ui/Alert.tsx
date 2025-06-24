// frontend/src/components/ui/Alert.tsx - VERSIÓN MEJORADA

import React from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { Button } from './Button';

export interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  closable?: boolean;
  className?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  onClose,
  closable = false,
  className = '',
  icon,
  action
}) => {
  const baseClasses = 'p-4 rounded-lg border flex items-start space-x-3 transition-all duration-300 animate-in slide-in-from-top-2';
  
  const typeClasses = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconMap = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info
  };

  const IconComponent = iconMap[type];
  const iconColorClasses = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600'
  };

  return (
    <div className={`${baseClasses} ${typeClasses[type]} ${className}`}>
      {/* Icon */}
      <div className="flex-shrink-0">
        {icon || <IconComponent className={`w-5 h-5 ${iconColorClasses[type]}`} />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="text-sm font-medium mb-1">{title}</h4>
        )}
        <div className="text-sm">{children}</div>
        
        {/* Action button */}
        {action && (
          <div className="mt-3">
            <Button
              size="sm"
              variant="secondary"
              onClick={action.onClick}
              className="text-xs"
            >
              {action.label}
            </Button>
          </div>
        )}
      </div>

      {/* Close button */}
      {(closable || onClose) && (
        <div className="flex-shrink-0">
          <button
            onClick={onClose}
            className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${iconColorClasses[type]} hover:bg-white hover:bg-opacity-20`}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

// 🎯 COMPONENTE ADICIONAL: Toast Notifications
export interface ToastProps extends Omit<AlertProps, 'closable'> {
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export const Toast: React.FC<ToastProps> = ({
  duration = 5000,
  position = 'top-right',
  onClose,
  ...alertProps
}) => {
  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const positionClasses = {
    'top-right': 'fixed top-4 right-4 z-50',
    'top-left': 'fixed top-4 left-4 z-50',
    'bottom-right': 'fixed bottom-4 right-4 z-50',
    'bottom-left': 'fixed bottom-4 left-4 z-50'
  };

  return (
    <div className={`${positionClasses[position]} max-w-sm w-full`}>
      <Alert {...alertProps} onClose={onClose} closable />
    </div>
  );
};

// 🎯 HOOK: Para gestionar toasts fácilmente
export const useToast = () => {
  const [toasts, setToasts] = React.useState<Array<ToastProps & { id: string }>>([]);

  const addToast = (toast: ToastProps) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { ...toast, id }]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const ToastContainer = () => (
    <>
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </>
  );

  return {
    addToast,
    removeToast,
    ToastContainer,
    toasts
  };
};

export default Alert;