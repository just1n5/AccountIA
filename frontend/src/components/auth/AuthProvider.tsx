import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { auth } from '../../config/firebase';

// Tipos para el contexto de autenticación
interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  
  // Métodos de autenticación
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, displayName?: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  
  // Estado
  isAuthenticated: boolean;
}

// Crear el contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook personalizado para usar el contexto
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Convertir Firebase User a nuestro AuthUser
const mapFirebaseUser = (firebaseUser: User): AuthUser => ({
  uid: firebaseUser.uid,
  email: firebaseUser.email,
  displayName: firebaseUser.displayName,
  photoURL: firebaseUser.photoURL,
  emailVerified: firebaseUser.emailVerified,
});

// Provider de autenticación
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Configurar Google Provider
  const googleProvider = new GoogleAuthProvider();
  googleProvider.setCustomParameters({
    prompt: 'select_account'
  });

  // Registro con email y contraseña
  const signUp = async (email: string, password: string, displayName?: string): Promise<void> => {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Actualizar el perfil con el nombre si se proporciona
      if (displayName && result.user) {
        await updateProfile(result.user, { displayName });
      }
    } catch (error: any) {
      console.error('Error en registro:', error);
      throw new Error(getAuthErrorMessage(error.code));
    }
  };

  // Inicio de sesión con email y contraseña
  const signIn = async (email: string, password: string): Promise<void> => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error: any) {
      console.error('Error en inicio de sesión:', error);
      throw new Error(getAuthErrorMessage(error.code));
    }
  };

  // Inicio de sesión con Google
  const signInWithGoogle = async (): Promise<void> => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (error: any) {
      console.error('Error en inicio de sesión con Google:', error);
      throw new Error(getAuthErrorMessage(error.code));
    }
  };

  // Cerrar sesión
  const logout = async (): Promise<void> => {
    try {
      await signOut(auth);
    } catch (error: any) {
      console.error('Error al cerrar sesión:', error);
      throw new Error('Error al cerrar sesión');
    }
  };

  // Recuperar contraseña
  const resetPassword = async (email: string): Promise<void> => {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (error: any) {
      console.error('Error al enviar email de recuperación:', error);
      throw new Error(getAuthErrorMessage(error.code));
    }
  };

  // Escuchar cambios en el estado de autenticación
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        setUser(mapFirebaseUser(firebaseUser));
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Valores del contexto
  const value: AuthContextType = {
    user,
    loading,
    signIn,
    signUp,
    signInWithGoogle,
    logout,
    resetPassword,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Función para mapear códigos de error de Firebase a mensajes legibles
const getAuthErrorMessage = (errorCode: string): string => {
  switch (errorCode) {
    case 'auth/user-not-found':
      return 'No existe una cuenta con este correo electrónico';
    case 'auth/wrong-password':
      return 'Contraseña incorrecta';
    case 'auth/email-already-in-use':
      return 'Ya existe una cuenta con este correo electrónico';
    case 'auth/weak-password':
      return 'La contraseña debe tener al menos 6 caracteres';
    case 'auth/invalid-email':
      return 'Correo electrónico inválido';
    case 'auth/too-many-requests':
      return 'Demasiados intentos fallidos. Intenta más tarde';
    case 'auth/popup-closed-by-user':
      return 'Inicio de sesión cancelado';
    case 'auth/popup-blocked':
      return 'Popup bloqueado por el navegador';
    default:
      return 'Error de autenticación. Intenta nuevamente';
  }
};
