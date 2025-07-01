// API client configuration - FIXED VERSION
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
    // 🔧 FIX: Asegurar que baseURL no tenga /api/v1
    const envUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    this.baseURL = envUrl.replace(/\/api\/v1\/?$/, ''); // Remover /api/v1 del final si existe
    
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    
    console.log('🔧 API Client initialized with baseURL:', this.baseURL);
    
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
    // 🔧 FIX: Construcción correcta de URL
    let fullURL: string;
    
    if (url.startsWith('http')) {
      // URL absoluta
      fullURL = url;
    } else {
      // URL relativa - asegurar que empiece con /
      const cleanUrl = url.startsWith('/') ? url : `/${url}`;
      fullURL = `${this.baseURL}${cleanUrl}`;
    }
    
    // 🔧 FIX: Log detallado para debugging
    console.log('🚀 API Request:', {
      method,
      originalUrl: url,
      fullURL,
      baseURL: this.baseURL
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
          // If we can't parse the error response, use the status text
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
        // Network error
        console.error('🌐 Network Error:', fullURL);
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

  // Set authorization token
  setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    console.log('🔑 Auth token set');
  }

  // Remove authorization token
  removeAuthToken() {
    delete this.defaultHeaders['Authorization'];
    console.log('🔑 Auth token removed');
  }

  // Get current base URL
  getBaseURL(): string {
    return this.baseURL;
  }

  // Update base URL
  setBaseURL(url: string) {
    this.baseURL = url.replace(/\/api\/v1\/?$/, ''); // Limpiar /api/v1 del final
    console.log('🔧 Base URL updated:', this.baseURL);
  }
}

// Create and export singleton instance
const api = new ApiClient();
export default api;

// Export types for use in other files
export type { ApiResponse, ApiError };
