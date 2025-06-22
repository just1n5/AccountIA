import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { RegisterForm } from '../../components/auth/RegisterForm';
import { useAuth } from '../../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();

  // Redirect si ya está autenticado
  useEffect(() => {
    if (!loading && isAuthenticated) {
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, loading, navigate, location]);

  const handleRegisterSuccess = () => {
    // Después del registro exitoso, redirigir al dashboard
    navigate('/dashboard', { replace: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        <RegisterForm onSuccess={handleRegisterSuccess} />
        
        {/* Background decorations */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-32 w-96 h-96 rounded-full bg-green-100 opacity-20 blur-3xl"></div>
          <div className="absolute -bottom-40 -left-32 w-96 h-96 rounded-full bg-blue-100 opacity-20 blur-3xl"></div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
