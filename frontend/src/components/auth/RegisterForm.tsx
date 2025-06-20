import React, { useState } from 'react';
import { useAuth } from './AuthProvider';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, UserPlus } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface RegisterFormProps {
  onSuccess?: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const { signUp, signInWithGoogle } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = () => {
    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      toast.error('Por favor completa todos los campos');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return false;
    }

    if (formData.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return false;
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error('Por favor ingresa un correo electrónico válido');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await signUp(formData.email, formData.password, formData.name);
      toast.success('¡Cuenta creada exitosamente! Bienvenido a AccountIA');
      onSuccess?.();
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      await signInWithGoogle();
      toast.success('¡Bienvenido a AccountIA!');
      onSuccess?.();
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Crear Cuenta
          </h2>
          <p className="text-gray-600">
            Únete a AccountIA y simplifica tu declaración de renta
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nombre */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Nombre Completo
            </label>
            <div style={{ position: 'relative', width: '100%' }}>
              <User 
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#9CA3AF',
                  pointerEvents: 'none',
                  zIndex: 2
                }}
                size={20}
              />
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 56px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'all 0.2s ease',
                  backgroundColor: 'white',
                  color: '#111827',
                  boxSizing: 'border-box'
                }}
                placeholder="Tu nombre completo"
                disabled={isLoading}
                onFocus={(e) => {
                  e.target.style.borderColor = '#16A34A';
                  e.target.style.boxShadow = '0 0 0 3px rgba(22, 163, 74, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#D1D5DB';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Correo Electrónico
            </label>
            <div style={{ position: 'relative', width: '100%' }}>
              <Mail 
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#9CA3AF',
                  pointerEvents: 'none',
                  zIndex: 2
                }}
                size={20}
              />
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 56px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'all 0.2s ease',
                  backgroundColor: 'white',
                  color: '#111827',
                  boxSizing: 'border-box'
                }}
                placeholder="ejemplo@correo.com"
                disabled={isLoading}
                onFocus={(e) => {
                  e.target.style.borderColor = '#16A34A';
                  e.target.style.boxShadow = '0 0 0 3px rgba(22, 163, 74, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#D1D5DB';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <div style={{ position: 'relative', width: '100%' }}>
              <Lock 
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#9CA3AF',
                  pointerEvents: 'none',
                  zIndex: 2
                }}
                size={20}
              />
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                value={formData.password}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px 56px 12px 56px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'all 0.2s ease',
                  backgroundColor: 'white',
                  color: '#111827',
                  boxSizing: 'border-box'
                }}
                placeholder="Mínimo 6 caracteres"
                disabled={isLoading}
                onFocus={(e) => {
                  e.target.style.borderColor = '#16A34A';
                  e.target.style.boxShadow = '0 0 0 3px rgba(22, 163, 74, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#D1D5DB';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  padding: '0',
                  zIndex: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                disabled={isLoading}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#6B7280';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#9CA3AF';
                }}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Confirmar Contraseña
            </label>
            <div style={{ position: 'relative', width: '100%' }}>
              <Lock 
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#9CA3AF',
                  pointerEvents: 'none',
                  zIndex: 2
                }}
                size={20}
              />
              <input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                required
                value={formData.confirmPassword}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px 56px 12px 56px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'all 0.2s ease',
                  backgroundColor: 'white',
                  color: '#111827',
                  boxSizing: 'border-box'
                }}
                placeholder="Repite tu contraseña"
                disabled={isLoading}
                onFocus={(e) => {
                  e.target.style.borderColor = '#16A34A';
                  e.target.style.boxShadow = '0 0 0 3px rgba(22, 163, 74, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#D1D5DB';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                style={{
                  position: 'absolute',
                  right: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  padding: '0',
                  zIndex: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                disabled={isLoading}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#6B7280';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#9CA3AF';
                }}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* Terms */}
          <div className="text-sm text-gray-600">
            Al crear una cuenta, aceptas nuestros{' '}
            <Link to="/terms" className="text-green-600 hover:text-green-700 transition-colors">
              Términos de Servicio
            </Link>
            {' '}y{' '}
            <Link to="/privacy" className="text-green-600 hover:text-green-700 transition-colors">
              Política de Privacidad
            </Link>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Creando cuenta...
              </>
            ) : (
              <>
                <UserPlus className="w-5 h-5" />
                Crear Cuenta
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="my-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-2 text-gray-500">O continúa con</span>
            </div>
          </div>
        </div>

        {/* Google Sign In */}
        <button
          type="button"
          onClick={handleGoogleSignIn}
          disabled={isLoading}
          className="w-full bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continuar con Google
        </button>

        {/* Sign In Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            ¿Ya tienes cuenta?{' '}
            <Link
              to="/login"
              className="text-green-600 hover:text-green-700 font-medium transition-colors"
            >
              Inicia sesión aquí
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;
