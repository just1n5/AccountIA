import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// Configuración de Firebase desde variables de entorno
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
};

// Debug: Mostrar configuración cargada
console.log('🔥 Firebase config loaded:', {
  apiKey: firebaseConfig.apiKey ? '✅ API Key loaded' : '❌ Missing API Key',
  authDomain: firebaseConfig.authDomain || '❌ Missing Auth Domain',
  projectId: firebaseConfig.projectId || '❌ Missing Project ID',
});

// Validar que las variables de entorno críticas estén configuradas
const requiredEnvVars = [
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_AUTH_DOMAIN',
  'VITE_FIREBASE_PROJECT_ID',
];

for (const envVar of requiredEnvVars) {
  if (!import.meta.env[envVar]) {
    console.error(`❌ Missing required environment variable: ${envVar}`);
  }
}

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Exportar servicios de Firebase
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

// Configurar persistencia de autenticación
auth.useDeviceLanguage();

console.log('✅ Firebase initialized successfully');

export default app;