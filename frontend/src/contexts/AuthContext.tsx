import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  updateProfile,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth';
import { auth } from '../config/firebase';
import api from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  updateUserProfile: (displayName: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (!isMounted) return;
      
      console.log('🔥 Firebase user changed:', firebaseUser?.email || 'No user');
      
      try {
        if (firebaseUser) {
          // Sincronizar con el backend
          const token = await firebaseUser.getIdToken();
          console.log('📤 Sending token to backend...');
          
          try {
            const response = await api.post('/auth/session/', { firebase_token: token });
            console.log('✅ Backend response:', response);
          } catch (backendError) {
            console.error('❌ Error syncing with backend:', backendError);
            // Continuar con Firebase auth aunque el backend falle
          }
          
          if (isMounted) {
            setUser(firebaseUser);
          }
        } else {
          console.log('❌ No Firebase user');
          if (isMounted) {
            setUser(null);
          }
        }
      } catch (err) {
        console.error('❌ Error in auth state change:', err);
        // Establecer el usuario de Firebase independientemente del error
        if (isMounted) {
          setUser(firebaseUser);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    });

    // Cleanup function
    return () => {
      isMounted = false;
      unsubscribe();
    };
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      console.log('📝 Attempting login with:', email);
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      console.log('✅ Firebase login successful');
      
      // Sincronizar con el backend
      const token = await userCredential.user.getIdToken();
      console.log('📤 Syncing with backend...');
      const response = await api.post('/auth/session/', { firebase_token: token });
      console.log('✅ Backend sync successful:', response);
    } catch (err: any) {
      console.error('❌ Login error:', err);
      setError(getErrorMessage(err));
      throw err;
    }
  };

  const register = async (email: string, password: string, displayName?: string) => {
    try {
      setError(null);
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // Actualizar el nombre si se proporciona
      if (displayName) {
        await updateProfile(userCredential.user, { displayName });
      }
      
      // Sincronizar con el backend
      const token = await userCredential.user.getIdToken();
      await api.post('/auth/session/', { firebase_token: token });
    } catch (err: any) {
      setError(getErrorMessage(err));
      throw err;
    }
  };

  const logout = async () => {
    try {
      setError(null);
      await signOut(auth);
    } catch (err: any) {
      setError(getErrorMessage(err));
      throw err;
    }
  };

  const resetPassword = async (email: string) => {
    try {
      setError(null);
      await sendPasswordResetEmail(auth, email);
    } catch (err: any) {
      setError(getErrorMessage(err));
      throw err;
    }
  };

  const loginWithGoogle = async () => {
    try {
      setError(null);
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      
      // Sincronizar con el backend
      const token = await userCredential.user.getIdToken();
      await api.post('/auth/session/', { firebase_token: token });
    } catch (err: any) {
      setError(getErrorMessage(err));
      throw err;
    }
  };

  const updateUserProfile = async (displayName: string) => {
    try {
      setError(null);
      if (user) {
        await updateProfile(user, { displayName });
      }
    } catch (err: any) {
      setError(getErrorMessage(err));
      throw err;
    }
  };

  const getErrorMessage = (error: any): string => {
    const errorMessages: { [key: string]: string } = {
      'auth/email-already-in-use': 'Este correo electrónico ya está registrado',
      'auth/invalid-email': 'Correo electrónico inválido',
      'auth/operation-not-allowed': 'Operación no permitida',
      'auth/weak-password': 'La contraseña debe tener al menos 6 caracteres',
      'auth/user-disabled': 'Esta cuenta ha sido deshabilitada',
      'auth/user-not-found': 'No existe una cuenta con este correo electrónico',
      'auth/wrong-password': 'Contraseña incorrecta',
      'auth/invalid-credential': 'Credenciales inválidas',
      'auth/popup-closed-by-user': 'El proceso de autenticación fue cancelado',
      'auth/network-request-failed': 'Error de conexión. Verifica tu internet',
    };

    return errorMessages[error.code] || error.message || 'Error desconocido';
  };

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    resetPassword,
    loginWithGoogle,
    updateUserProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};