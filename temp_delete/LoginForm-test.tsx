import React, { useState } from 'react';
import { useAuth } from './AuthProvider';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, LogIn } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface LoginFormProps {
  onSuccess?: () => void;
}

export const LoginFormTest: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const { signIn, signInWithGoogle, loading } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      toast.error('Por favor completa todos los campos');
      return;
    }

    setIsLoading(true);
    try {
      await signIn(formData.email, formData.password);
      toast.success('¡Bienvenido a AccountIA!');
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

  // Estilos inline para testing
  const inputContainerStyle = {
    position: 'relative' as const,
    width: '100%'
  };

  const iconLeftStyle = {
    position: 'absolute' as const,
    left: '16px',
    top: '50%',
    transform: 'translateY(-50%)',
    color: '#9CA3AF',
    pointerEvents: 'none' as const
  };

  const iconRightStyle = {
    position: 'absolute' as const,
    right: '16px',
    top: '50%',
    transform: 'translateY(-50%)',
    color: '#9CA3AF',
    cursor: 'pointer',
    background: 'none',
    border: 'none'
  };

  const inputWithIconStyle = {
    width: '100%',
    paddingLeft: '56px', // 3.5rem = 56px
    paddingRight: '16px',
    paddingTop: '12px',
    paddingBottom: '12px',
    border: '1px solid #D1D5DB',
    borderRadius: '8px',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.2s'
  };

  const inputWithBothIconsStyle = {
    ...inputWithIconStyle,
    paddingRight: '56px'
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Iniciar Sesión (TEST)
          </h2>
          <p className="text-gray-600">
            Versión de prueba con estilos inline
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Correo Electrónico
            </label>
            <div style={inputContainerStyle}>
              <Mail style={iconLeftStyle} size={20} />
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                style={inputWithIconStyle}
                placeholder="ejemplo@correo.com"
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <div style={inputContainerStyle}>
              <Lock style={iconLeftStyle} size={20} />
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                value={formData.password}
                onChange={handleInputChange}
                style={inputWithBothIconsStyle}
                placeholder="Tu contraseña"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={iconRightStyle}
                disabled={isLoading}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Iniciando...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                TEST - Iniciar Sesión
              </>
            )}
          </button>
        </form>

        {/* Volver al original */}
        <div className="mt-4 text-center">
          <Link
            to="/login"
            className="text-sm text-blue-600 hover:text-blue-700 transition-colors"
          >
            ← Volver al formulario original
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginFormTest;
