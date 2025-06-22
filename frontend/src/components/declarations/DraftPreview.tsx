import React from 'react';
import { FileText, DollarSign, Download, Info, CheckCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';

interface DraftPreviewProps {
  declaration: any;
  processedData: any;
  supportDocuments: any[];
  isLoading?: boolean;
}

const DraftPreview: React.FC<DraftPreviewProps> = ({
  declaration,
  processedData,
  supportDocuments,
  isLoading
}) => {
  if (isLoading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-azul-principal mx-auto mb-4"></div>
        <p className="text-gris-700">Generando tu borrador...</p>
      </div>
    );
  }

  const formatCurrency = (value: string | number): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  // Datos simulados para el ejemplo
  const summaryData = {
    totalIncome: declaration?.total_income || 85000000,
    totalWithholdings: declaration?.total_withholdings || 12000000,
    totalDeductions: 15000000,
    taxableIncome: 70000000,
    calculatedTax: 8500000,
    balance: -3500000 // Negativo = a favor
  };

  const deductions = [
    { concept: 'Intereses de vivienda', amount: 8000000 },
    { concept: 'Medicina prepagada', amount: 3500000 },
    { concept: 'Dependientes', amount: 2500000 },
    { concept: 'Aportes voluntarios a pensión', amount: 1000000 }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Borrador de tu Declaración</h2>
        <p className="text-gris-700">
          Revisa el resumen de tu declaración de renta {declaration?.fiscal_year}
        </p>
      </div>

      <Alert type="success" className="mb-6">
        <CheckCircle className="w-4 h-4" />
        <span>
          ¡Excelente! Hemos optimizado tu declaración. 
          {summaryData.balance < 0 
            ? ` Tienes un saldo a favor de ${formatCurrency(Math.abs(summaryData.balance))}.`
            : ` Tu impuesto a pagar es ${formatCurrency(summaryData.balance)}.`
          }
        </span>
      </Alert>

      {/* Resumen principal */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="font-semibold text-lg mb-4">Ingresos y Retenciones</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gris-700">Total de Ingresos:</span>
              <span className="font-medium">{formatCurrency(summaryData.totalIncome)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gris-700">(-) Deducciones:</span>
              <span className="font-medium text-verde-exito">
                {formatCurrency(summaryData.totalDeductions)}
              </span>
            </div>
            <div className="pt-3 border-t border-gris-300">
              <div className="flex justify-between">
                <span className="text-gris-700">(=) Renta Líquida Gravable:</span>
                <span className="font-bold">{formatCurrency(summaryData.taxableIncome)}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold text-lg mb-4">Cálculo del Impuesto</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gris-700">Impuesto Calculado:</span>
              <span className="font-medium">{formatCurrency(summaryData.calculatedTax)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gris-700">(-) Retenciones en la Fuente:</span>
              <span className="font-medium">{formatCurrency(summaryData.totalWithholdings)}</span>
            </div>
            <div className="pt-3 border-t border-gris-300">
              <div className="flex justify-between items-center">
                <span className="text-gris-700 font-medium">
                  {summaryData.balance < 0 ? 'Saldo a Favor:' : 'Total a Pagar:'}
                </span>
                <span className={`text-xl font-bold ${
                  summaryData.balance < 0 ? 'text-verde-exito' : 'text-rojo-error'
                }`}>
                  {formatCurrency(Math.abs(summaryData.balance))}
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Detalle de deducciones */}
      <Card className="p-6 mb-8">
        <h3 className="font-semibold text-lg mb-4">Deducciones Aplicadas</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gris-300">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gris-700 uppercase tracking-wider">
                  Concepto
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gris-700 uppercase tracking-wider">
                  Valor
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gris-300">
              {deductions.map((deduction, index) => (
                <tr key={index}>
                  <td className="px-4 py-3 text-sm text-gris-900">
                    {deduction.concept}
                  </td>
                  <td className="px-4 py-3 text-sm text-gris-900 text-right">
                    {formatCurrency(deduction.amount)}
                  </td>
                </tr>
              ))}
              <tr className="bg-gris-50 font-semibold">
                <td className="px-4 py-3 text-sm text-gris-900">
                  Total Deducciones
                </td>
                <td className="px-4 py-3 text-sm text-gris-900 text-right">
                  {formatCurrency(summaryData.totalDeductions)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Documentos adjuntos */}
      <Card className="p-6 mb-8">
        <h3 className="font-semibold text-lg mb-4">Documentos de Soporte</h3>
        <div className="flex items-center space-x-2 text-verde-exito mb-4">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm">
            {supportDocuments.length} documentos adjuntos correctamente
          </span>
        </div>
        <p className="text-sm text-gris-700">
          Todos tus documentos han sido procesados y almacenados de forma segura. 
          Estarán disponibles para consulta en tu historial de declaraciones.
        </p>
      </Card>

      {/* Información adicional */}
      <Alert type="info" className="mb-6">
        <Info className="w-4 h-4" />
        <div>
          <p className="font-medium mb-1">Importante:</p>
          <ul className="list-disc list-inside text-sm space-y-1">
            <li>Este es un borrador preliminar basado en la información proporcionada.</li>
            <li>El cálculo final puede variar según cambios normativos o información adicional.</li>
            <li>Conserva todos los documentos de soporte por al menos 5 años.</li>
          </ul>
        </div>
      </Alert>

      {/* Acciones */}
      <div className="bg-gris-50 rounded-lg p-6">
        <h3 className="font-semibold text-lg mb-4">¿Qué sigue?</h3>
        <p className="text-gris-700 mb-4">
          Para obtener tu declaración completa y el formulario 210 diligenciado, 
          realiza el pago único de nuestro servicio.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            variant="secondary"
            className="flex items-center justify-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Descargar Resumen (PDF)
          </Button>
          <Button
            className="flex items-center justify-center bg-verde-exito hover:bg-verde-exito/90"
          >
            <DollarSign className="w-4 h-4 mr-2" />
            Pagar y Obtener Declaración Completa
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DraftPreview;