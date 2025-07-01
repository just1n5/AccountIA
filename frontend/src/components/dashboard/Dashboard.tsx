// frontend/src/components/dashboard/Dashboard.tsx - CON HOOK INTEGRADO

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, FileText, DollarSign, AlertCircle, TrendingUp, LogOut, User, RefreshCw } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';
import LoadingSpinner from '../ui/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { useDeclarationManagement } from '../../hooks/useDeclarationManagement';
import declarationService from '../../services/declarationService';
// import DebugPanel from '../debug/DebugPanel';

// 🎯 OPTIMIZACIÓN: Skeleton components reutilizables
const StatCardSkeleton: React.FC = () => (
  <Card className="p-6 animate-pulse">
    <div className="flex items-center justify-between">
      <div className="space-y-2 flex-1">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
        <div className="h-8 bg-gray-200 rounded w-16"></div>
      </div>
      <div className="w-8 h-8 bg-gray-200 rounded"></div>
    </div>
  </Card>
);

const DeclarationCardSkeleton: React.FC = () => (
  <Card className="p-6 animate-pulse">
    <div className="flex items-center justify-between">
      <div className="flex-1 space-y-4">
        <div className="flex items-center space-x-3">
          <div className="h-6 bg-gray-200 rounded w-32"></div>
          <div className="h-6 bg-gray-200 rounded w-20"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-16"></div>
              <div className="h-5 bg-gray-200 rounded w-24"></div>
            </div>
          ))}
        </div>
      </div>
      <div className="ml-4">
        <div className="h-10 bg-gray-200 rounded w-24"></div>
      </div>
    </div>
  </Card>
);

const Dashboard: React.FC = () => {
  // 🔥🔥🔥 MARKER ÚNICO PARA FORZAR RECOMPILACIÓN - v2024.6.23.1 🔥🔥🔥
  console.log('[DASHBOARD] NUEVA VERSION CARGADA - v2024.6.23.1');
  
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // 🎯 OPTIMIZACIÓN: Usar el hook personalizado
  const {
    declarations,
    isLoading,
    isRefreshing,
    isCreating,
    error,
    stats,
    createDeclaration,
    refreshDeclarations,
    clearError,
    retry
  } = useDeclarationManagement();

  const [isLoggingOut, setIsLoggingOut] = React.useState(false);
  const currentYear = new Date().getFullYear() - 1;

  // 🎯 OPTIMIZACIÓN: Manejo de logout mejorado
  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  // 🎯 OPTIMIZACIÓN: Crear declaración con navegación automática
  const handleCreateDeclaration = async (fiscalYear: number) => {
    const newDeclaration = await createDeclaration(fiscalYear);
    if (newDeclaration) {
      navigate(`/dashboard/declarations/${newDeclaration.id}/wizard`);
    }
  };

  // 🎯 OPTIMIZACIÓN: Helpers para UI
  const getStatusBadge = (status: string) => {
    const colorClass = declarationService.getStatusColor?.(status) || 'bg-gray-100 text-gray-800';
    const label = declarationService.getStatusLabel?.(status) || status;
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded transition-colors ${colorClass}`}>
        {label}
      </span>
    );
  };

  const formatCurrency = (value: string | number): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Navigation */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">AccountIA</h1>
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              {/* Refresh Button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={refreshDeclarations}
                disabled={isRefreshing}
                className="hidden sm:flex"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                {isRefreshing ? 'Actualizando...' : 'Actualizar'}
              </Button>

              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900 truncate max-w-32">
                      {user?.displayName || user?.email}
                    </p>
                    <p className="text-xs text-gray-500">Usuario</p>
                  </div>
                </div>
              </div>

              {/* Logout Button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="text-red-600 border-red-600 hover:bg-red-600 hover:text-white transition-colors"
              >
                {isLoggingOut ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                    <span className="hidden sm:inline">Saliendo...</span>
                  </>
                ) : (
                  <>
                    <LogOut className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Cerrar Sesión</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Bienvenido, {user?.displayName || user?.email?.split('@')[0]}
          </h2>
          <p className="text-gray-600 text-sm sm:text-base">
            Gestiona tus declaraciones de renta de forma simple y segura
          </p>
        </div>

        {/* Estadísticas con skeleton loading */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {isLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : (
            <>
              <Card className="p-6 transition-shadow hover:shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Declaraciones Totales</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats?.totalDeclarations || 0}
                    </p>
                  </div>
                  <FileText className="w-8 h-8 text-blue-600" />
                </div>
              </Card>

              <Card className="p-6 transition-shadow hover:shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Última Declaración</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats?.lastDeclaration?.fiscal_year || '-'}
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-600" />
                </div>
              </Card>

              <Card className="p-6 transition-shadow hover:shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Estado Actual</p>
                    <div className="mt-1">
                      {stats?.hasCurrentYear ? 
                        getStatusBadge(stats.currentYearDeclaration!.status) :
                        <span className="text-sm text-gray-600">Sin declaración {currentYear}</span>
                      }
                    </div>
                  </div>
                  <AlertCircle className="w-8 h-8 text-yellow-500" />
                </div>
              </Card>
            </>
          )}
        </div>

        {/* Error Alert mejorado */}
        {error && (
          <Alert 
            type="error" 
            className="mb-6"
            onClose={clearError}
            closable
            action={{
              label: 'Reintentar',
              onClick: retry
            }}
          >
            {error}
          </Alert>
        )}

        {/* CTA para nueva declaración */}
        {!isLoading && stats && !stats.hasCurrentYear && (
          <Card className="p-8 mb-8 bg-gradient-to-r from-blue-50 to-green-50 border-blue-200 transition-all hover:shadow-lg">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Plus className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">
                Es hora de preparar tu declaración {currentYear}
              </h2>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto text-sm sm:text-base">
                Nuestra IA analizará tu información exógena y te guiará paso a paso 
                para optimizar tu declaración y cumplir con la DIAN.
              </p>
              <Button
                size="lg"
                onClick={() => handleCreateDeclaration(currentYear)}
                disabled={isCreating}
                className="bg-green-600 hover:bg-green-700 transition-all transform hover:scale-105 disabled:transform-none"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando declaración...
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5 mr-2" />
                    Crear Declaración {currentYear}
                  </>
                )}
              </Button>
            </div>
          </Card>
        )}

        {/* Lista de declaraciones */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Historial de Declaraciones</h2>
            <div className="flex items-center space-x-2">
              {/* NUEVO: Botón para crear múltiples declaraciones del mismo año */}
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleCreateDeclaration(currentYear)}
                disabled={isCreating}
                className="bg-blue-600 hover:bg-blue-700 transition-all"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Nueva Declaración
                  </>
                )}
              </Button>
              {!isLoading && declarations.length > 0 && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={refreshDeclarations}
                  disabled={isRefreshing}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                  Actualizar
                </Button>
              )}
            </div>
          </div>
          
          {isLoading ? (
            <div className="space-y-4">
              <DeclarationCardSkeleton />
              <DeclarationCardSkeleton />
            </div>
          ) : !declarations || declarations.length === 0 ? (
            <Card className="p-8 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No tienes declaraciones anteriores</p>
              <Button 
                onClick={() => handleCreateDeclaration(currentYear)} 
                disabled={isCreating}
                className="transition-all hover:scale-105"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
                  </>
                ) : (
                  'Crear tu primera declaración'
                )}
              </Button>
            </Card>
          ) : (
            <div className="grid gap-4">
              {declarations?.map((declaration, index) => (
                <Card 
                  key={declaration.id} 
                  className="p-6 transition-all hover:shadow-md animate-in slide-in-from-bottom-2"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 mb-4">
                        <h3 className="text-lg font-semibold">
                          Declaración {declaration.fiscal_year}
                        </h3>
                        {getStatusBadge(declaration.status)}
                      </div>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Ingresos</p>
                          <p className="font-medium text-sm sm:text-base">
                            {formatCurrency(declaration.total_income)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Retenciones</p>
                          <p className="font-medium text-sm sm:text-base">
                            {formatCurrency(declaration.total_withholdings)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Balance</p>
                          <p className={`font-medium text-sm sm:text-base ${
                            declaration.balance && parseFloat(declaration.balance) < 0 
                              ? 'text-green-600' 
                              : 'text-red-600'
                          }`}>
                            {declaration.balance 
                              ? formatCurrency(Math.abs(parseFloat(declaration.balance)))
                              : '-'}
                            {declaration.balance && parseFloat(declaration.balance) < 0 && ' (a favor)'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Documentos</p>
                          <p className="font-medium text-sm sm:text-base">
                            {declaration.document_count || 0}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex justify-end lg:ml-4">
                      {declaration.status === 'draft' || declaration.status === 'processing' ? (
                        <Link to={`/dashboard/declarations/${declaration.id}/wizard`}>
                          <Button variant="secondary" className="transition-all hover:scale-105">
                            Continuar
                          </Button>
                        </Link>
                      ) : declaration.status === 'completed' ? (
                        <Link to={`/dashboard/declarations/${declaration.id}/payment`}>
                          <Button className="bg-green-600 hover:bg-green-700 transition-all hover:scale-105">
                            <DollarSign className="w-4 h-4 mr-2" />
                            Pagar
                          </Button>
                        </Link>
                      ) : (
                        <Link to={`/dashboard/declarations/${declaration.id}/summary`}>
                          <Button variant="secondary" className="transition-all hover:scale-105">
                            Ver Detalles
                          </Button>
                        </Link>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
      
      {/* Debug Panel - Solo en desarrollo */}
      {/* <DebugPanel /> */}
    </div>
  );
};

export default Dashboard;