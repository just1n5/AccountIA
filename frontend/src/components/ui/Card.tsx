import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className, children, ...props }) => {
  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gris-300 shadow-sm',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};