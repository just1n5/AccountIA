import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, FileText, DollarSign, AlertCircle, TrendingUp, LogOut, User, Settings } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';
import LoadingSpinner from '../ui/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

interface Declaration {
  id: string;
  fiscal_year: number;
  status: string;
  total_income: string;
  total_withholdings: string;
  preliminary_tax: string | null;
  balance: string | null;
  document_count: number;
  created_at: string;
  updated_at: string;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [declarations, setDeclarations] = useState<Declaration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const currentYear = new Date().getFullYear() - 1; // Generalmente se declara el año anterior

  useEffect(() => {
    fetchDeclarations();
  }, []);

  const fetchDeclarations = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/declarations/');
      setDeclarations(response.data);
    } catch (err: any) {
      setError('Error al cargar las declaraciones');
      console.error('Error fetching declarations:', err);
    } finally {
      setIsLoading(false);
    }
  };

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

  const createDeclaration = async (fiscalYear: number) => {
    try {
      setIsCreating(true);
      setError(null);
      
      console.log('Creando declaración para el año:', fiscalYear);
      
      const response = await api.post('/declarations/', {
        fiscal_year: fiscalYear
      });
      
      console.log('Declaración creada:', response.data);
      
      // Navegar al wizard con la nueva declaración usando React Router
      navigate(`/dashboard/declarations/${response.data.id}/wizard`);
      
    } catch (err: any) {
      console.error('Error creating declaration:', err);
      setError(err.response?.data?.fiscal_year?.[0] || 'Error al crear la declaración');
    } finally {
      setIsCreating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { color: 'bg-gray-500', text: 'Borrador' },
      processing: { color: 'bg-yellow-500', text: 'Procesando' },
      completed: { color: 'bg-green-500', text: 'Completada' },
      paid: { color: 'bg-blue-500', text: 'Pagada' },
      error: { color: 'bg-red-500', text: 'Error' }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    
    return (
      <span className={`px-2 py-1 text-xs font-medium text-white rounded ${config.color}`}>
        {config.text}
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
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
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
            <div className="flex items-center space-x-4">
              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900">
                      {user?.displayName || user?.email}
                    </p>
                    <p className="text-xs text-gray-500">Usuario</p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                {/* Settings Button (Optional) */}
                <Button
                  variant="secondary"
                  size="sm"
                  className="hidden sm:flex"
                  onClick={() => {/* TODO: Navigate to settings */}}
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Configuración
                </Button>

                {/* Logout Button */}
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="text-red-600 border-red-600 hover:bg-red-600 hover:text-white"
                >
                  {isLoggingOut ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                      Saliendo...
                    </>
                  ) : (
                    <>
                      <LogOut className="w-4 h-4 mr-2" />
                      Cerrar Sesión
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Bienvenido, {user?.displayName || user?.email?.split('@')[0]}
          </h2>
          <p className="text-gray-600">
            Gestiona tus declaraciones de renta de forma simple y segura
          </p>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Declaraciones Totales</p>
                <p className="text-2xl font-bold text-gray-900">{declarations?.length || 0}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Última Declaración</p>
                <p className="text-2xl font-bold text-gray-900">
                  {declarations && declarations.length > 0 ? declarations[0].fiscal_year : '-'}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Estado Actual</p>
                <p className="text-lg font-medium text-gray-900">
                  {declarations && declarations.length > 0 && declarations[0].fiscal_year === currentYear
                    ? getStatusBadge(declarations[0].status)
                    : 'Sin declaración para ' + currentYear}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-yellow-500" />
            </div>
          </Card>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert type="error" className="mb-6">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </Alert>
        )}

        {/* Acción principal */}
        {declarations && !declarations.some(d => d.fiscal_year === currentYear) && (
          <Card className="p-8 mb-8 bg-blue-50 border-blue-600">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Es hora de preparar tu declaración {currentYear}
              </h2>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                Nuestra IA analizará tu información exógena y te guiará paso a paso 
                para optimizar tu declaración y cumplir con la DIAN.
              </p>
              <Button
                size="lg"
                onClick={() => createDeclaration(currentYear)}
                disabled={isCreating}
                className="bg-green-600 hover:bg-green-700"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
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
          <h2 className="text-xl font-semibold mb-4">Historial de Declaraciones</h2>
          
          {isLoading ? (
            <LoadingSpinner 
              size="lg" 
              message="Cargando declaraciones..." 
              className="py-8" 
            />
          ) : !declarations || declarations.length === 0 ? (
            <Card className="p-8 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No tienes declaraciones anteriores</p>
              <Button onClick={() => createDeclaration(currentYear)} disabled={isCreating}>
                {isCreating ? 'Creando...' : 'Crear tu primera declaración'}
              </Button>
            </Card>
          ) : (
            <div className="grid gap-4">
              {declarations?.map((declaration) => (
                <Card key={declaration.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold">
                          Declaración {declaration.fiscal_year}
                        </h3>
                        {getStatusBadge(declaration.status)}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                        <div>
                          <p className="text-sm text-gray-500">Ingresos</p>
                          <p className="font-medium">{formatCurrency(declaration.total_income)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Retenciones</p>
                          <p className="font-medium">{formatCurrency(declaration.total_withholdings)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Balance</p>
                          <p className={`font-medium ${
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
                          <p className="font-medium">{declaration.document_count || 0}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      {declaration.status === 'draft' || declaration.status === 'processing' ? (
                        <Link to={`/dashboard/declarations/${declaration.id}/wizard`}>
                          <Button variant="secondary">Continuar</Button>
                        </Link>
                      ) : declaration.status === 'completed' ? (
                        <Link to={`/dashboard/declarations/${declaration.id}/payment`}>
                          <Button className="bg-green-600 hover:bg-green-700">
                            <DollarSign className="w-4 h-4 mr-2" />
                            Pagar
                          </Button>
                        </Link>
                      ) : (
                        <Link to={`/dashboard/declarations/${declaration.id}/summary`}>
                          <Button variant="secondary">Ver Detalles</Button>
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
    </div>
  );
};

export default Dashboard;