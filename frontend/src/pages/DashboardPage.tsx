import React from 'react';
import { useAuth } from '../components/auth/AuthProvider';
import { 
  FileText, 
  Plus, 
  Calendar, 
  TrendingUp, 
  Bell,
  Settings,
  LogOut,
  User
} from 'lucide-react';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">AccountIA</h1>
              </div>
            </div>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
                <Bell className="w-5 h-5" />
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="text-sm">
                  <p className="font-medium text-gray-900">{user?.displayName || 'Usuario'}</p>
                  <p className="text-gray-500">{user?.email}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-2 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                title="Cerrar sesión"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              ¡Bienvenido, {user?.displayName?.split(' ')[0] || 'Usuario'}!
            </h2>
            <p className="text-gray-600">
              Tu asesor fiscal inteligente está listo para ayudarte con tu declaración de renta.
            </p>
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FileText className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">Declaraciones</h3>
                  <p className="text-2xl font-bold text-blue-600">0</p>
                  <p className="text-sm text-gray-500">En progreso</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Calendar className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">Año Fiscal</h3>
                  <p className="text-2xl font-bold text-green-600">2024</p>
                  <p className="text-sm text-gray-500">Actual</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">Ahorros</h3>
                  <p className="text-2xl font-bold text-purple-600">$0</p>
                  <p className="text-sm text-gray-500">Estimados</p>
                </div>
              </div>
            </div>
          </div>

          {/* Main action */}
          <div className="bg-white rounded-lg shadow p-8 text-center mb-8">
            <div className="mx-auto w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mb-6">
              <Plus className="w-12 h-12 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Crear mi Declaración 2024
            </h3>
            <p className="text-gray-600 mb-6">
              Comienza tu declaración de renta con la ayuda de nuestra IA especializada. 
              Te guiaremos paso a paso para optimizar tu declaración.
            </p>
            <button 
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors duration-200 inline-flex items-center gap-2"
              onClick={() => {
                // TODO: Implementar navegación al flujo de declaración
                alert('Funcionalidad en desarrollo - Próximamente disponible');
              }}
            >
              <Plus className="w-5 h-5" />
              Empezar Declaración
            </button>
          </div>

          {/* Recent activity */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Actividad Reciente</h3>
            </div>
            <div className="p-6">
              <div className="text-center text-gray-500 py-8">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">No hay actividad reciente</p>
                <p>Cuando comiences tu primera declaración, verás tu actividad aquí.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
