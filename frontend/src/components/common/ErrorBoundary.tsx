import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Actualizar el state para mostrar la UI de error
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log del error
    console.error('🔥 ErrorBoundary caught an error:', error);
    console.error('📍 Error Info:', errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Aquí podrías enviar el error a un servicio de monitoreo como Sentry
    // this.logErrorToService(error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // UI de fallback personalizada
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="max-w-lg w-full p-8 text-center">
            <div className="mb-6">
              <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                ¡Oops! Algo salió mal
              </h1>
              <p className="text-gray-600">
                Se ha producido un error inesperado. Nuestro equipo ha sido notificado.
              </p>
            </div>

            {/* Mostrar información del error solo en desarrollo */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 text-left">
                <details className="bg-gray-100 p-4 rounded-lg">
                  <summary className="cursor-pointer font-medium text-gray-700 mb-2">
                    Detalles del Error (Solo visible en desarrollo)
                  </summary>
                  <div className="text-sm font-mono text-red-600 whitespace-pre-wrap">
                    {this.state.error.message}
                  </div>
                  {this.state.errorInfo && (
                    <div className="mt-2 text-xs font-mono text-gray-600 whitespace-pre-wrap">
                      {this.state.errorInfo.componentStack}
                    </div>
                  )}
                </details>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button onClick={this.handleReload} className="flex items-center justify-center">
                <RefreshCw className="w-4 h-4 mr-2" />
                Reintentar
              </Button>
              <Button 
                variant="secondary" 
                onClick={this.handleGoHome}
                className="flex items-center justify-center"
              >
                <Home className="w-4 h-4 mr-2" />
                Ir al Inicio
              </Button>
            </div>

            <div className="mt-6 text-sm text-gray-500">
              <p>
                Si el problema persiste, contáctanos en{' '}
                <a 
                  href="mailto:soporte@accountia.co" 
                  className="text-blue-600 hover:underline"
                >
                  soporte@accountia.co
                </a>
              </p>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;