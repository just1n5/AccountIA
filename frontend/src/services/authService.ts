import api from './api';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  refresh_token?: string;
  expires_in?: number;
}

export interface SessionResponse {
  user: User;
  authenticated: boolean;
}

class AuthService {
  private readonly baseUrl = '/auth'; // Las URLs base ya están manejadas por api.ts
  private token: string | null = null;

  constructor() {
    // Recuperar token del localStorage al inicializar
    this.token = localStorage.getItem('auth_token');
    if (this.token) {
      api.setAuthToken(this.token);
    }
  }

  /**
   * Verificar sesión actual
   */
  async checkSession(): Promise<SessionResponse | null> {
    try {
      const response = await api.post<SessionResponse>(`${this.baseUrl}/session/`);
      return response;
    } catch (error: any) {
      console.log('No active session found');
      return null;
    }
  }

  /**
   * Login con email y password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>(`${this.baseUrl}/login/`, credentials);
      
      if (response.token) {
        this.setToken(response.token);
      }
      
      return response;
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.message ||
        'Error de autenticación'
      );
    }
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    try {
      await api.post(`${this.baseUrl}/logout/`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearToken();
    }
  }

  /**
   * Registro de nuevo usuario
   */
  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>(`${this.baseUrl}/register/`, userData);
      
      if (response.token) {
        this.setToken(response.token);
      }
      
      return response;
    } catch (error: any) {
      console.error('Registration error:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.message ||
        'Error en el registro'
      );
    }
  }

  /**
   * Obtener usuario actual
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get<User>(`${this.baseUrl}/me/`);
      return response;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  /**
   * Refresh token
   */
  async refreshToken(): Promise<string | null> {
    try {
      const response = await api.post<{ token: string }>(`${this.baseUrl}/refresh/`);
      
      if (response.token) {
        this.setToken(response.token);
        return response.token;
      }
      
      return null;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearToken();
      return null;
    }
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    return !!this.token;
  }

  /**
   * Obtener token actual
   */
  getToken(): string | null {
    return this.token;
  }

  /**
   * Establecer token
   */
  private setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
    api.setAuthToken(token);
  }

  /**
   * Limpiar token
   */
  private clearToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
    api.removeAuthToken();
  }

  /**
   * Login como guest/demo (para testing)
   */
  async loginAsGuest(): Promise<SessionResponse> {
    try {
      // Para desarrollo/testing, crear una sesión demo
      const demoUser: User = {
        id: 'demo-user',
        email: 'demo@accountia.com',
        first_name: 'Demo',
        last_name: 'User',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Crear token demo
      const demoToken = 'demo-token-' + Date.now();
      this.setToken(demoToken);

      return {
        user: demoUser,
        authenticated: true
      };
    } catch (error) {
      console.error('Guest login error:', error);
      throw error;
    }
  }
}

// Crear instancia singleton
export const authService = new AuthService();
export default authService;
