// frontend/src/components/declarations/DataTable.tsx
import React, { useState, useMemo } from 'react';
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  Filter, 
  Download,
  FileX,
  Eye,
  ArrowUpDown
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { formatCurrency } from '../../utils/formatters';

interface DataRecord {
  tercero_informante: string;
  concepto_codigo: string;
  concepto_descripcion: string;
  cedula_tipo: string;
  valor_bruto: number;
  valor_retencion: number;
  valor_neto: number;
}

interface DataTableProps {
  data: DataRecord[];
  title?: string;
  showFilters?: boolean;
  showExport?: boolean;
  maxRows?: number;
  className?: string;
}

type SortField = keyof DataRecord;
type SortDirection = 'asc' | 'desc' | null;

const Badge: React.FC<{ 
  children: React.ReactNode; 
  variant?: 'default' | 'outline'; 
  size?: 'sm' | 'md' 
}> = ({ 
  children, 
  variant = 'default', 
  size = 'sm' 
}) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full';
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    outline: 'border border-gray-300 text-gray-700 bg-white'
  };
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm'
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}>
      {children}
    </span>
  );
};

const DataTable: React.FC<DataTableProps> = ({
  data,
  title = "Detalle de Registros",
  showFilters = true,
  showExport = true,
  maxRows = 50,
  className = ''
}) => {
  const [sortField, setSortField] = useState<SortField | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCedula, setFilterCedula] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Get unique cedula types for filter
  const cedulaTypes = useMemo(() => {
    const types = [...new Set(data.map(item => item.cedula_tipo))];
    return types.sort();
  }, [data]);

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let filtered = data;

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        item.tercero_informante.toLowerCase().includes(term) ||
        item.concepto_descripcion.toLowerCase().includes(term) ||
        item.concepto_codigo.toLowerCase().includes(term)
      );
    }

    // Apply cedula filter
    if (filterCedula) {
      filtered = filtered.filter(item => item.cedula_tipo === filterCedula);
    }

    // Apply sorting
    if (sortField && sortDirection) {
      filtered = [...filtered].sort((a, b) => {
        const aValue = a[sortField];
        const bValue = b[sortField];
        
        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        const aStr = String(aValue).toLowerCase();
        const bStr = String(bValue).toLowerCase();
        
        if (sortDirection === 'asc') {
          return aStr.localeCompare(bStr);
        } else {
          return bStr.localeCompare(aStr);
        }
      });
    }

    return filtered.slice(0, maxRows);
  }, [data, searchTerm, filterCedula, sortField, sortDirection, maxRows]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredAndSortedData.slice(startIndex, startIndex + itemsPerPage);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortField(null);
        setSortDirection(null);
      } else {
        setSortDirection('asc');
      }
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400" />;
    }
    if (sortDirection === 'asc') {
      return <ChevronUp className="w-4 h-4 text-azul-principal" />;
    }
    return <ChevronDown className="w-4 h-4 text-azul-principal" />;
  };

  const exportToCSV = () => {
    const headers = [
      'Tercero Informante',
      'Código Concepto',
      'Descripción Concepto',
      'Tipo Cédula',
      'Valor Bruto',
      'Retención',
      'Valor Neto'
    ];

    const csvContent = [
      headers.join(','),
      ...filteredAndSortedData.map(row => [
        `"${row.tercero_informante}"`,
        row.concepto_codigo,
        `"${row.concepto_descripcion}"`,
        row.cedula_tipo,
        row.valor_bruto,
        row.valor_retencion,
        row.valor_neto
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'registros_exogena.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">
          {title}
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            {filteredAndSortedData.length} de {data.length} registros
          </span>
          {showExport && (
            <Button
              variant="secondary"
              size="sm"
              onClick={exportToCSV}
              className="ml-2"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar CSV
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card className="p-4 bg-gray-50">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por tercero informante o concepto..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-azul-principal focus:border-azul-principal"
                />
              </div>
            </div>

            {/* Filter by Cedula */}
            <div className="sm:w-48">
              <select
                value={filterCedula}
                onChange={(e) => setFilterCedula(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-azul-principal focus:border-azul-principal"
              >
                <option value="">Todas las cédulas</option>
                {cedulaTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            {/* Clear Filters */}
            {(searchTerm || filterCedula) && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setSearchTerm('');
                  setFilterCedula('');
                  setCurrentPage(1);
                }}
              >
                Limpiar filtros
              </Button>
            )}
          </div>
        </Card>
      )}

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('tercero_informante')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Tercero Informante</span>
                    {getSortIcon('tercero_informante')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('concepto_descripcion')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Concepto</span>
                    {getSortIcon('concepto_descripcion')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('cedula_tipo')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Cédula</span>
                    {getSortIcon('cedula_tipo')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('valor_bruto')}
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Valor Bruto</span>
                    {getSortIcon('valor_bruto')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('valor_retencion')}
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Retención</span>
                    {getSortIcon('valor_retencion')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('valor_neto')}
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Valor Neto</span>
                    {getSortIcon('valor_neto')}
                  </div>
                </th>
              </tr>
            </thead>
            
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedData.map((row, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="font-medium">
                      {row.tercero_informante}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div>
                      <div className="font-medium">{row.concepto_descripcion}</div>
                      <div className="text-gray-500 text-xs mt-1">
                        Código: {row.concepto_codigo}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant="outline" size="sm">
                      {row.cedula_tipo}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                    {formatCurrency(row.valor_bruto)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                    {formatCurrency(row.valor_retencion)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-bold">
                    {formatCurrency(row.valor_neto)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Empty State */}
        {paginatedData.length === 0 && (
          <div className="text-center py-12">
            <FileX className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg mb-2">No hay registros para mostrar</p>
            <p className="text-gray-400 text-sm">
              {searchTerm || filterCedula 
                ? 'Intenta ajustar los filtros de búsqueda' 
                : 'No se encontraron datos en el archivo procesado'
              }
            </p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
            <div className="flex items-center justify-between">
              <div className="flex-1 flex justify-between sm:hidden">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  Anterior
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  Siguiente
                </Button>
              </div>
              
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Mostrando{' '}
                    <span className="font-medium">{startIndex + 1}</span>
                    {' '}a{' '}
                    <span className="font-medium">
                      {Math.min(startIndex + itemsPerPage, filteredAndSortedData.length)}
                    </span>
                    {' '}de{' '}
                    <span className="font-medium">{filteredAndSortedData.length}</span>
                    {' '}resultados
                  </p>
                </div>
                
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      const pageNum = i + 1;
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setCurrentPage(pageNum)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            currentPage === pageNum
                              ? 'z-10 bg-azul-principal border-azul-principal text-white'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Siguiente
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default DataTable;
