// API client configuration - FIXED VERSION v2
interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

interface ApiError {
  response?: {
    data?: {
      error?: string;
      message?: string;
      detail?: string;
    };
    status?: number;
  };
  message?: string;
}

class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor() {
    // NUEVA ESTRATEGIA: baseURL siempre incluye /api/v1
    const envUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    // Limpiar cualquier /api/v1 existente y agregar uno limpio
    const cleanBaseUrl = envUrl.replace(/\/api\/v1\/?$/, '');
    this.baseURL = `${cleanBaseUrl}/api/v1`;
    
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    
    console.log('🚀 API Client initialized with baseURL:', this.baseURL);
    console.log('🔧 Environment URL:', envUrl);
    console.log('🧹 Clean base URL:', cleanBaseUrl);
    
    // Recuperar token del localStorage al inicializar
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  private async request<T = any>(
    method: string,
    url: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    // NUEVA LÓGICA: Construir URLs inteligentemente
    let fullURL: string;
    
    if (url.startsWith('http')) {
      // URL absoluta - usar tal como está
      fullURL = url;
    } else {
      // URL relativa - limpiar duplicaciones y construir correctamente
      let cleanUrl = url;
      
      // Remover /api/v1 del inicio si existe (evitar duplicación)
      if (cleanUrl.startsWith('/api/v1')) {
        cleanUrl = cleanUrl.substring(7); // Remover "/api/v1"
      }
      
      // Asegurar que empiece con /
      if (!cleanUrl.startsWith('/')) {
        cleanUrl = `/${cleanUrl}`;
      }
      
      // Construir URL final
      fullURL = `${this.baseURL}${cleanUrl}`;
    }
    
    // Log detallado para debugging
    console.log('🚀 Direct API call to backend:', method, fullURL);
    console.log('📝 URL construction:', {
      method,
      originalUrl: url,
      baseURL: this.baseURL,
      finalURL: fullURL
    });
    
    const config: RequestInit = {
      method,
      headers: {
        ...this.defaultHeaders,
        ...headers,
      },
    };

    if (data) {
      if (data instanceof FormData) {
        // Don't set Content-Type for FormData, let browser set it
        delete config.headers!['Content-Type'];
        config.body = data;
      } else {
        config.body = JSON.stringify(data);
      }
    }

    try {
      const response = await fetch(fullURL, config);
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.message || errorData.detail || errorMessage;
        } catch {
          errorMessage = response.statusText || errorMessage;
        }
        
        console.error('❌ API Error:', {
          url: fullURL,
          status: response.status,
          message: errorMessage
        });
        
        const error: ApiError = {
          response: {
            data: { error: errorMessage },
            status: response.status,
          },
          message: errorMessage,
        };
        throw error;
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const responseData = await response.json();
        console.log('✅ API Success:', method, fullURL);
        return responseData;
      } else {
        console.log('✅ API Success (non-JSON):', method, fullURL);
        return response as any;
      }
    } catch (error) {
      if (error instanceof TypeError) {
        console.error('💥 Network Error:', fullURL);
        const networkError: ApiError = {
          message: 'Error de red. Verifica tu conexión a internet.',
        };
        throw networkError;
      }
      throw error;
    }
  }

  async get<T = any>(url: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('GET', url, undefined, headers);
  }

  async post<T = any>(url: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('POST', url, data, headers);
  }

  async put<T = any>(url: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('PUT', url, data, headers);
  }

  async patch<T = any>(url: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('PATCH', url, data, headers);
  }

  async delete<T = any>(url: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>('DELETE', url, undefined, headers);
  }

  setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    console.log('🔐 Auth token set');
  }

  removeAuthToken() {
    delete this.defaultHeaders['Authorization'];
    console.log('🚪 Auth token removed');
  }

  getBaseURL(): string {
    return this.baseURL;
  }

  setBaseURL(url: string) {
    const cleanBaseUrl = url.replace(/\/api\/v1\/?$/, '');
    this.baseURL = `${cleanBaseUrl}/api/v1`;
    console.log('🔄 Base URL updated:', this.baseURL);
  }
}

// Create and export singleton instance
const api = new ApiClient();
export default api;

// Export types for use in other files
export type { ApiResponse, ApiError };
