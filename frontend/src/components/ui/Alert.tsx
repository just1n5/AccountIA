import React from 'react';
import { cn } from '../../utils/cn';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: 'info' | 'success' | 'warning' | 'error';
  children: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  className,
  children,
  ...props
}) => {
  const typeClasses = {
    info: 'bg-azul-claro border-azul-principal text-azul-principal',
    success: 'bg-verde-exito/10 border-verde-exito text-verde-exito',
    warning: 'bg-amarillo-advertencia/10 border-amarillo-advertencia text-amarillo-advertencia',
    error: 'bg-rojo-error/10 border-rojo-error text-rojo-error'
  };
  
  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg border flex items-start space-x-3',
        typeClasses[type],
        className
      )}
      role="alert"
      {...props}
    >
      {children}
    </div>
  );
};