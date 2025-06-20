// Firebase configuration - versión simplificada
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Configuración directa para evitar problemas con variables de entorno
const firebaseConfig = {
  apiKey: "AIzaSyCYr-CzvFq_KiEy_PLIs0B_hS0reYH6c1g",
  authDomain: "accountia-dev.firebaseapp.com",
  projectId: "accountia-dev",
  storageBucket: "accountia-dev.firebasestorage.app",
  messagingSenderId: "687868450492",
  appId: "1:687868450492:web:f798fd2a0fe38560b4e2b9",
  measurementId: "G-GBSZ7B1DJ6"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Inicializar Authentication
export const auth = getAuth(app);

// Configuración por defecto
auth.useDeviceLanguage();

export default app;
