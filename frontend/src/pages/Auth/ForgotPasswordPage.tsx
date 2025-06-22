import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, Send, CheckCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-hot-toast';

const ForgotPasswordPage: React.FC = () => {
  const { resetPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast.error('Por favor ingresa tu correo electrónico');
      return;
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error('Por favor ingresa un correo electrónico válido');
      return;
    }

    setIsLoading(true);
    try {
      await resetPassword(email);
      setEmailSent(true);
      toast.success('Correo de recuperación enviado exitosamente');
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <div className="bg-white shadow-lg rounded-lg p-8 text-center">
            {/* Success Icon */}
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>

            {/* Success Message */}
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              ¡Correo Enviado!
            </h2>
            <p className="text-gray-600 mb-6">
              Hemos enviado las instrucciones para restablecer tu contraseña a:
            </p>
            <p className="text-lg font-medium text-blue-600 mb-6">
              {email}
            </p>
            <p className="text-sm text-gray-500 mb-8">
              Revisa tu bandeja de entrada y sigue las instrucciones. Si no ves el correo, 
              revisa tu carpeta de spam.
            </p>

            {/* Actions */}
            <div className="space-y-4">
              <Link
                to="/login"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-5 h-5" />
                Volver al Login
              </Link>
              
              <button
                onClick={() => setEmailSent(false)}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors duration-200"
              >
                Enviar a otro correo
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        <div className="bg-white shadow-lg rounded-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Recuperar Contraseña
            </h2>
            <p className="text-gray-600">
              Ingresa tu correo electrónico y te enviaremos las instrucciones 
              para restablecer tu contraseña
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="email" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
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
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                    e.target.style.borderColor = '#3B82F6';
                    e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#D1D5DB';
                    e.target.style.boxShadow = 'none';
                  }}
                />
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
                  Enviando...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Enviar Instrucciones
                </>
              )}
            </button>
          </form>

          {/* Back to Login */}
          <div className="mt-6 text-center">
            <Link
              to="/login"
              className="text-sm text-blue-600 hover:text-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Volver al Login
            </Link>
          </div>
        </div>

        {/* Background decorations */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-32 w-96 h-96 rounded-full bg-blue-100 opacity-20 blur-3xl"></div>
          <div className="absolute -bottom-40 -left-32 w-96 h-96 rounded-full bg-green-100 opacity-20 blur-3xl"></div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;