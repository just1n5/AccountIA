// frontend/src/components/declarations/SummaryCards.tsx
import React from 'react';
import { 
  DollarSign, 
  TrendingDown, 
  Calculator, 
  FileText, 
  TrendingUp,
  Users,
  Building 
} from 'lucide-react';
import { Card } from '../ui/Card';
import { formatCurrency, formatNumber } from '../../utils/formatters';

interface SummaryData {
  total_records: number;
  total_ingresos_brutos: number;
  total_retenciones: number;
  total_ingresos_netos: number;
  terceros_count?: number;
  conceptos_count?: number;
}

interface SummaryCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  description?: string;
  trend?: {
    value: string;
    type: 'positive' | 'negative' | 'neutral';
  };
  format?: 'currency' | 'number' | 'text';
  className?: string;
}

interface SummaryCardsProps {
  summary: SummaryData;
  className?: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  icon,
  description,
  trend,
  format = 'currency',
  className = ''
}) => {
  const formatValue = (val: number | string): string => {
    if (typeof val === 'string') return val;
    
    switch (format) {
      case 'currency':
        return formatCurrency(val);
      case 'number':
        return formatNumber(val);
      default:
        return val.toString();
    }
  };

  const getTrendStyles = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive':
        return 'text-verde-exito';
      case 'negative':
        return 'text-red-600';
      case 'neutral':
        return 'text-gray-600';
    }
  };

  const getTrendIcon = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive':
        return <TrendingUp className="w-4 h-4" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <Card className={`p-6 border border-gray-200 hover:shadow-lg transition-all duration-200 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Icon and Title */}
          <div className="flex items-center mb-3">
            <div className="p-2 bg-azul-claro rounded-lg mr-3">
              {icon}
            </div>
            <h3 className="text-sm font-medium text-gray-700 leading-tight">
              {title}
            </h3>
          </div>
          
          {/* Value */}
          <p className="text-2xl font-bold text-gray-900 mb-2 leading-none">
            {formatValue(value)}
          </p>
          
          {/* Description */}
          {description && (
            <p className="text-sm text-gray-500 leading-relaxed">
              {description}
            </p>
          )}
        </div>
        
        {/* Trend Indicator */}
        {trend && (
          <div className={`flex items-center text-sm font-medium ${getTrendStyles(trend.type)}`}>
            {getTrendIcon(trend.type)}
            <span className="ml-1">{trend.value}</span>
          </div>
        )}
      </div>
    </Card>
  );
};

const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, className = '' }) => {
  const cards = [
    {
      title: 'Total Ingresos Brutos',
      value: summary.total_ingresos_brutos,
      icon: <DollarSign className="w-5 h-5 text-azul-principal" />,
      description: 'Ingresos reportados por terceros',
      format: 'currency' as const
    },
    {
      title: 'Total Retenciones',
      value: summary.total_retenciones,
      icon: <TrendingDown className="w-5 h-5 text-azul-principal" />,
      description: 'Retenciones aplicadas',
      format: 'currency' as const
    },
    {
      title: 'Ingresos Netos',
      value: summary.total_ingresos_netos,
      icon: <Calculator className="w-5 h-5 text-azul-principal" />,
      description: 'Brutos menos retenciones',
      format: 'currency' as const,
      trend: {
        value: 'Base gravable',
        type: 'neutral' as const
      }
    },
    {
      title: 'Registros Procesados',
      value: summary.total_records,
      icon: <FileText className="w-5 h-5 text-azul-principal" />,
      description: 'Total de registros encontrados',
      format: 'number' as const
    }
  ];

  // Add optional cards if data is available
  const optionalCards = [];
  
  if (summary.terceros_count !== undefined) {
    optionalCards.push({
      title: 'Terceros Informantes',
      value: summary.terceros_count,
      icon: <Building className="w-5 h-5 text-azul-principal" />,
      description: 'Empresas que reportaron',
      format: 'number' as const
    });
  }

  if (summary.conceptos_count !== undefined) {
    optionalCards.push({
      title: 'Conceptos Únicos',
      value: summary.conceptos_count,
      icon: <Users className="w-5 h-5 text-azul-principal" />,
      description: 'Tipos de ingresos',
      format: 'number' as const
    });
  }

  const allCards = [...cards, ...optionalCards];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Title */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">
          Resumen de Información
        </h2>
        <span className="text-sm text-gray-500">
          Valores en COP
        </span>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {allCards.map((card, index) => (
          <SummaryCard
            key={index}
            title={card.title}
            value={card.value}
            icon={card.icon}
            description={card.description}
            format={card.format}
            trend={card.trend}
          />
        ))}
      </div>

      {/* Additional Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
          </div>
          <div className="ml-3">
            <h4 className="text-sm font-medium text-blue-900 mb-1">
              Información procesada automáticamente
            </h4>
            <p className="text-sm text-blue-700">
              Los datos mostrados provienen directamente de tu archivo de información exógena. 
              Hemos clasificado automáticamente tus ingresos según la normativa tributaria colombiana.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export { SummaryCard };
export default SummaryCards;
