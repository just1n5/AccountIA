// API client configuration
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
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    
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
    const fullURL = url.startsWith('http') ? url : `${this.baseURL}${url}`;
    
    // Para desarrollo: si no hay token y no es un endpoint de auth, usar modo demo
    if (!this.defaultHeaders['Authorization'] && !url.includes('/auth/')) {
      console.log('🔄 Using demo mode for API calls');
      // En desarrollo, permitir algunas llamadas sin autenticación
      if (url.includes('/declarations/')) {
        return this.mockApiResponse(url, method) as T;
      }
    }
    
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
        return await response.json();
      } else {
        return response as any;
      }
    } catch (error) {
      if (error instanceof TypeError) {
        // Network error
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
  }

  // Remove authorization token
  removeAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }

  // Get current base URL
  getBaseURL(): string {
    return this.baseURL;
  }

  // Update base URL
  setBaseURL(url: string) {
    this.baseURL = url;
  }

  // Mock API responses for development
  private mockApiResponse(url: string, method: string): any {
    console.log(`🎭 Mock response for ${method} ${url}`);
    
    if (url.includes('/declarations/') && method === 'GET') {
      return {
        results: [
          {
            id: 'demo-declaration-1',
            user_id: 'demo-user-1',
            fiscal_year: 2024,
            status: 'draft',
            status_display: 'Borrador',
            total_income: '50000000',
            total_withholdings: '5000000',
            preliminary_tax: null,
            balance: null,
            document_count: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 'demo-declaration-2',
            user_id: 'demo-user-1',
            fiscal_year: 2023,
            status: 'completed',
            status_display: 'Completada',
            total_income: '45000000',
            total_withholdings: '4500000',
            preliminary_tax: '2500000',
            balance: '-2000000',
            document_count: 3,
            created_at: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 300 * 24 * 60 * 60 * 1000).toISOString()
          }
        ],
        count: 2
      };
    }
    
    if (url.includes('/declarations/') && method === 'POST') {
      // Extraer fiscal_year del request data si está disponible
      const currentYear = new Date().getFullYear() - 1;
      
      return {
        id: 'demo-declaration-' + Date.now(),
        user_id: 'demo-user-1',
        fiscal_year: currentYear,
        status: 'draft',
        status_display: 'Borrador',
        total_income: '0',
        total_withholdings: '0',
        preliminary_tax: null,
        balance: null,
        document_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
    }
    
    return { message: 'Demo response', data: [] };
  }
}

// Create and export singleton instance
const api = new ApiClient();
export default api;

// Export types for use in other files
export type { ApiResponse, ApiError };
