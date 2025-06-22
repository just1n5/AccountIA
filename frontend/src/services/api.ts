import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { auth } from '../config/firebase';

class ApiService {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor para agregar el token de autenticación
    this.instance.interceptors.request.use(
      async (config) => {
        try {
          const user = auth.currentUser;
          console.log('🔐 Auth interceptor - User:', user?.email || 'No user');
          if (user) {
            const token = await user.getIdToken();
            config.headers.Authorization = `Bearer ${token}`;
            console.log('✅ Token added to request:', token.substring(0, 50) + '...');
          } else {
            console.log('❌ No authenticated user found');
          }
        } catch (error) {
          console.error('❌ Error getting auth token:', error);
        }
        console.log('📤 Request URL:', config.baseURL + config.url);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor para manejar errores globalmente
    this.instance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expirado o inválido
          try {
            const user = auth.currentUser;
            if (user) {
              // Forzar refresh del token
              await user.getIdToken(true);
              
              // Reintentar la petición original
              const originalRequest = error.config;
              if (originalRequest) {
                return this.instance(originalRequest);
              }
            }
          } catch (refreshError) {
            // Si no se puede refrescar el token, redirigir al login
            window.location.href = '/login';
          }
        }

        // Manejar otros errores
        const errorMessage = this.getErrorMessage(error);
        console.error('API Error:', errorMessage);
        
        return Promise.reject(error);
      }
    );
  }

  private getErrorMessage(error: AxiosError): string {
    if (error.response) {
      // El servidor respondió con un status code fuera del rango 2xx
      const data: any = error.response.data;
      
      // Manejar diferentes formatos de error
      if (typeof data === 'string') {
        return data;
      } else if (data.error) {
        return data.error;
      } else if (data.detail) {
        return data.detail;
      } else if (data.message) {
        return data.message;
      } else if (data.non_field_errors) {
        return data.non_field_errors.join(', ');
      } else {
        // Buscar el primer mensaje de error en el objeto
        const firstError = Object.values(data).find(
          (value) => typeof value === 'string' || Array.isArray(value)
        );
        if (Array.isArray(firstError)) {
          return firstError.join(', ');
        } else if (firstError) {
          return String(firstError);
        }
      }
    } else if (error.request) {
      // La petición se hizo pero no se recibió respuesta
      return 'No se pudo conectar con el servidor. Por favor, verifica tu conexión.';
    }
    
    return error.message || 'Error desconocido';
  }

  // Métodos HTTP básicos
  async get<T = any>(url: string, config?: AxiosRequestConfig) {
    const response = await this.instance.get<T>(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    const response = await this.instance.post<T>(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    const response = await this.instance.put<T>(url, data, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    const response = await this.instance.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig) {
    const response = await this.instance.delete<T>(url, config);
    return response.data;
  }

  // Método para subir archivos
  async uploadFile(url: string, file: File, additionalData?: any) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Agregar datos adicionales si existen
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });
    }

    const response = await this.instance.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  // Método para descargar archivos
  async downloadFile(url: string, filename: string) {
    const response = await this.instance.get(url, {
      responseType: 'blob',
    });

    // Crear un enlace temporal para descargar
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
}

// Exportar instancia única
const api = new ApiService();
export default api;