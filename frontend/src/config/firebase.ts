// Firebase configuration for AccountIA
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

// Configuración de Firebase desde variables de entorno
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

// Verificar que las variables de entorno estén disponibles
if (!firebaseConfig.apiKey) {
  throw new Error('Firebase configuration is missing. Please check your environment variables.');
}

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Inicializar Authentication
export const auth = getAuth(app);

// Inicializar Analytics (solo en producción)
export const analytics = typeof window !== 'undefined' && import.meta.env.PROD 
  ? getAnalytics(app) 
  : null;

// Configuración por defecto
auth.useDeviceLanguage(); // Usar idioma del dispositivo

export default app;
