// frontend/src/components/ui/PageHeader.tsx
import React from 'react';
import { CheckCircle, FileText, Info, AlertTriangle, XCircle } from 'lucide-react';

interface Badge {
  text: string;
  variant: 'success' | 'warning' | 'error' | 'info';
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  fileName?: string;
  badge?: Badge;
  actions?: React.ReactNode;
  className?: string;
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  fileName,
  badge,
  actions,
  className = ''
}) => {
  const getBadgeStyles = (variant: Badge['variant']) => {
    const styles = {
      success: 'bg-green-50 text-green-800 border-green-200',
      warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
      error: 'bg-red-50 text-red-800 border-red-200',
      info: 'bg-blue-50 text-blue-800 border-blue-200'
    };
    return styles[variant];
  };

  const getBadgeIcon = (variant: Badge['variant']) => {
    const icons = {
      success: <CheckCircle className="w-4 h-4" />,
      warning: <AlertTriangle className="w-4 h-4" />,
      error: <XCircle className="w-4 h-4" />,
      info: <Info className="w-4 h-4" />
    };
    return icons[variant];
  };

  return (
    <header className={`mb-8 ${className}`}>
      {/* Main Title Row */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 leading-tight">
            {title}
          </h1>
        </div>

        {/* Badge */}
        {badge && (
          <div className={`
            inline-flex items-center px-3 py-2 rounded-lg border text-sm font-medium
            ${getBadgeStyles(badge.variant)}
          `}>
            {getBadgeIcon(badge.variant)}
            <span className="ml-2">{badge.text}</span>
          </div>
        )}

        {/* Actions */}
        {actions && (
          <div className="ml-4">
            {actions}
          </div>
        )}
      </div>

      {/* File Information */}
      {fileName && (
        <div className="flex items-center mb-3">
          <div className="flex items-center text-gray-600">
            <FileText className="w-5 h-5 mr-2 text-gray-400" />
            <span className="text-base">
              Archivo: <span className="font-medium text-gray-900">{fileName}</span>
            </span>
          </div>
        </div>
      )}

      {/* Subtitle */}
      {subtitle && (
        <p className="text-lg text-gray-600 leading-relaxed max-w-3xl">
          {subtitle}
        </p>
      )}
    </header>
  );
};

export default PageHeader;
