import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Shield, 
  Zap, 
  Brain, 
  CheckCircle, 
  Star,
  Users,
  Clock,
  Calculator
} from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">AccountIA</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                Iniciar Sesión
              </Link>
              <Link
                to="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-medium"
              >
                Registrarse
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 via-white to-green-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Tu declaración de renta,{' '}
              <span className="text-blue-600">por fin simple</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Utiliza tu información exógena de la DIAN y deja que nuestra IA te guíe 
              para optimizar tu declaración y cumplir con la ley.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                to="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors inline-flex items-center justify-center gap-2"
              >
                Empieza Gratis
                <ArrowRight className="w-5 h-5" />
              </Link>
              <button 
                className="bg-white border-2 border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-4 rounded-lg font-bold text-lg transition-colors"
                onClick={() => {
                  // Scroll to demo section
                  document.getElementById('como-funciona')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Ver Cómo Funciona
              </button>
            </div>

            {/* Trust indicators */}
            <div className="flex flex-wrap justify-center items-center gap-8 text-gray-500">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                <span>Datos Cifrados</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                <span>Cumple Ley 1581</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5" />
                <span>IA Especializada</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="como-funciona" className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Cómo Funciona AccountIA
            </h2>
            <p className="text-xl text-gray-600">
              Tu declaración de renta en 3 pasos simples
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Sube tu Exógena
              </h3>
              <p className="text-gray-600">
                Carga el archivo Excel de información exógena que descargaste de la DIAN. 
                Nuestra IA lo procesará automáticamente.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Responde a la IA
              </h3>
              <p className="text-gray-600">
                Nuestro asistente inteligente te hará preguntas simples para descubrir 
                deducciones y optimizar tu declaración.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Obtén tu Borrador
              </h3>
              <p className="text-gray-600">
                Recibe un borrador optimizado de tu declaración, listo para revisar 
                y presentar ante la DIAN.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ¿Por qué elegir AccountIA?
            </h2>
            <p className="text-xl text-gray-600">
              La tecnología más avanzada al servicio de tu declaración de renta
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="text-center">
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Brain className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">IA Especializada</h3>
              <p className="text-gray-600">
                Entrenada específicamente en normativa fiscal colombiana
              </p>
            </div>

            {/* Feature 2 */}
            <div className="text-center">
              <div className="mx-auto w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">100% Seguro</h3>
              <p className="text-gray-600">
                Cumplimos con la Ley 1581 de protección de datos personales
              </p>
            </div>

            {/* Feature 3 */}
            <div className="text-center">
              <div className="mx-auto w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Súper Rápido</h3>
              <p className="text-gray-600">
                Lo que te tomaría horas, nuestra IA lo hace en minutos
              </p>
            </div>

            {/* Feature 4 */}
            <div className="text-center">
              <div className="mx-auto w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <Calculator className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Optimización</h3>
              <p className="text-gray-600">
                Encuentra todas las deducciones a las que tienes derecho
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            ¿Listo para simplificar tu declaración de renta?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Únete a miles de colombianos que ya confían en AccountIA
          </p>
          <Link
            to="/register"
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-bold text-lg transition-colors inline-flex items-center gap-2"
          >
            Empezar Gratis Ahora
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h3 className="text-xl font-bold text-white mb-4">AccountIA</h3>
            <p className="text-gray-400 mb-4">
              Tu asesor fiscal inteligente para Colombia
            </p>
            <div className="flex justify-center space-x-6 text-gray-400">
              <Link to="/terms" className="hover:text-white transition-colors">
                Términos de Servicio
              </Link>
              <Link to="/privacy" className="hover:text-white transition-colors">
                Política de Privacidad
              </Link>
              <Link to="/contact" className="hover:text-white transition-colors">
                Contacto
              </Link>
            </div>
            <div className="mt-4 text-gray-500 text-sm">
              © 2025 AccountIA. Todos los derechos reservados.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
