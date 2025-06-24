import api from './api';

// Tipos de datos
export interface Declaration {
  id: string;
  user_id: string;
  fiscal_year: number;
  status: string;
  status_display: string;
  summary_data?: {
    total_income: number;
    total_withholdings: number;
    preliminary_tax: number;
  };
  created_at: string;
  updated_at: string;
}

export interface CreateDeclarationRequest {
  fiscal_year: number;
}

export interface UpdateDeclarationRequest {
  status?: string;
  summary_data?: {
    total_income?: number;
    total_withholdings?: number;
    preliminary_tax?: number;
  };
}

export interface DeclarationListResponse {
  results: Declaration[];
  count: number;
  next?: string;
  previous?: string;
}

export interface DashboardStats {
  current_year_declaration?: Declaration;
  total_declarations: number;
  processed_declarations: number;
  pending_declarations: number;
  total_income_current_year: number;
  potential_savings: number;
}

export interface OptimizationRecommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  potential_savings: number;
  difficulty: 'easy' | 'medium' | 'hard';
  status: 'pending' | 'applied' | 'dismissed';
  details?: any;
}

export interface OptimizationRecommendationsResponse {
  declaration_id: string;
  recommendations: OptimizationRecommendation[];
  total_potential_savings: number;
  applied_savings: number;
}

/**
 * Servicio para gestión de declaraciones
 */
class DeclarationService {
  private readonly baseUrl = '/api/v1';

  /**
   * Obtiene todas las declaraciones del usuario
   */
  async list(params?: {
    page?: number;
    page_size?: number;
    fiscal_year?: number;
    status?: string;
  }): Promise<DeclarationListResponse> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
      if (params?.fiscal_year) queryParams.append('fiscal_year', params.fiscal_year.toString());
      if (params?.status) queryParams.append('status', params.status);
      
      const url = `${this.baseUrl}/declarations/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await api.get<DeclarationListResponse>(url);
      return response;
    } catch (error: any) {
      console.error('Error listing declarations:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error obteniendo declaraciones'
      );
    }
  }

  /**
   * Obtiene una declaración específica
   */
  async getById(id: string): Promise<Declaration> {
    try {
      const response = await api.get<Declaration>(
        `${this.baseUrl}/declarations/${id}/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error obteniendo declaración'
      );
    }
  }

  /**
   * Crea una nueva declaración
   */
  async create(request: CreateDeclarationRequest): Promise<Declaration> {
    try {
      const response = await api.post<Declaration>(
        `${this.baseUrl}/declarations/`,
        request
      );
      return response;
    } catch (error: any) {
      console.error('Error creating declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error creando declaración'
      );
    }
  }

  /**
   * Actualiza una declaración existente
   */
  async update(id: string, request: UpdateDeclarationRequest): Promise<Declaration> {
    try {
      const response = await api.patch<Declaration>(
        `${this.baseUrl}/declarations/${id}/`,
        request
      );
      return response;
    } catch (error: any) {
      console.error('Error updating declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error actualizando declaración'
      );
    }
  }

  /**
   * Elimina una declaración
   */
  async delete(id: string): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/declarations/${id}/`);
    } catch (error: any) {
      console.error('Error deleting declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error eliminando declaración'
      );
    }
  }

  /**
   * Obtiene estadísticas del dashboard
   */
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      const response = await api.get<DashboardStats>(
        `${this.baseUrl}/declarations/dashboard_stats/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting dashboard stats:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error obteniendo estadísticas'
      );
    }
  }

  /**
   * Obtiene la declaración del año actual
   */
  async getCurrentYearDeclaration(): Promise<Declaration | null> {
    try {
      const currentYear = new Date().getFullYear();
      const response = await this.list({ 
        fiscal_year: currentYear, 
        page_size: 1 
      });
      return response.results.length > 0 ? response.results[0] : null;
    } catch (error) {
      console.error('Error getting current year declaration:', error);
      return null;
    }
  }

  /**
   * Marca una declaración como completada
   */
  async markAsCompleted(id: string): Promise<Declaration> {
    try {
      const response = await api.post<Declaration>(
        `${this.baseUrl}/declarations/${id}/mark_completed/`
      );
      return response;
    } catch (error: any) {
      console.error('Error marking declaration as completed:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error marcando declaración como completada'
      );
    }
  }

  /**
   * Procesa una declaración con IA
   */
  async processWithAI(id: string): Promise<{ message: string; task_id?: string }> {
    try {
      const response = await api.post(
        `${this.baseUrl}/declarations/${id}/ai_process/`
      );
      return response;
    } catch (error: any) {
      console.error('Error processing with AI:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error procesando con IA'
      );
    }
  }

  /**
   * Obtiene recomendaciones de optimización
   */
  async getOptimizationRecommendations(id: string): Promise<OptimizationRecommendationsResponse> {
    try {
      const response = await api.get<OptimizationRecommendationsResponse>(
        `${this.baseUrl}/declarations/${id}/optimization_recommendations/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting optimization recommendations:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error obteniendo recomendaciones'
      );
    }
  }

  /**
   * Aplica una recomendación de optimización
   */
  async applyRecommendation(declarationId: string, recommendationId: string): Promise<void> {
    try {
      await api.post(
        `${this.baseUrl}/declarations/${declarationId}/apply_recommendation/`,
        { recommendation_id: recommendationId }
      );
    } catch (error: any) {
      console.error('Error applying recommendation:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error aplicando recomendación'
      );
    }
  }

  /**
   * Rechaza una recomendación de optimización
   */
  async dismissRecommendation(declarationId: string, recommendationId: string): Promise<void> {
    try {
      await api.post(
        `${this.baseUrl}/declarations/${declarationId}/dismiss_recommendation/`,
        { recommendation_id: recommendationId }
      );
    } catch (error: any) {
      console.error('Error dismissing recommendation:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error rechazando recomendación'
      );
    }
  }

  /**
   * Genera el borrador de declaración en formato oficial
   */
  async generateDraft(id: string): Promise<{ download_url: string; expires_in: number }> {
    try {
      const response = await api.post(
        `${this.baseUrl}/declarations/${id}/generate_draft/`
      );
      return response;
    } catch (error: any) {
      console.error('Error generating draft:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error generando borrador'
      );
    }
  }

  /**
   * Verifica si una declaración se puede editar
   */
  isEditable(declaration: Declaration): boolean {
    return ['draft', 'in_progress', 'review'].includes(declaration.status);
  }

  /**
   * Verifica si una declaración se puede procesar
   */
  canProcess(declaration: Declaration): boolean {
    return ['draft', 'in_progress'].includes(declaration.status);
  }

  /**
   * Verifica si una declaración está completa
   */
  isCompleted(declaration: Declaration): boolean {
    return ['completed', 'filed'].includes(declaration.status);
  }

  /**
   * Obtiene el color del estado para la UI
   */
  getStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      'draft': 'bg-gray-100 text-gray-800',
      'in_progress': 'bg-blue-100 text-blue-800',
      'review': 'bg-yellow-100 text-yellow-800',
      'processing': 'bg-purple-100 text-purple-800',
      'completed': 'bg-green-100 text-green-800',
      'filed': 'bg-green-100 text-green-800',
      'error': 'bg-red-100 text-red-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  }

  /**
   * Obtiene el label del estado en español
   */
  getStatusLabel(status: string): string {
    const statusLabels: Record<string, string> = {
      'draft': 'Borrador',
      'in_progress': 'En Progreso',
      'review': 'En Revisión',
      'processing': 'Procesando',
      'completed': 'Completada',
      'filed': 'Presentada',
      'error': 'Error'
    };
    return statusLabels[status] || status;
  }
}

// Instancia singleton del servicio
export const declarationService = new DeclarationService();
export default declarationService;