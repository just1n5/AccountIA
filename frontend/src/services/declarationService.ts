import api from './api';

// Tipos de datos
export interface Declaration {
  id: string;
  title: string;
  user_id?: string;
  user_email?: string;
  fiscal_year: number;
  status: string;
  status_display: string;
  total_income: string | number;
  total_withholdings: string | number;
  preliminary_tax: string | number | null;
  balance: string | number | null;
  declaration_data?: any;
  income_records?: any[];
  is_editable: boolean;
  has_documents: boolean;
  documents_count: number;
  progress_percentage: number;
  income_summary?: {
    by_type: Record<string, any>;
    by_schedule: Record<string, any>;
  };
  processing_errors?: string[];
  processing_warnings?: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  completed_at?: string | null;
  paid_at?: string | null;
  // Campos legacy para compatibilidad
  summary_data?: {
    total_income: number;
    total_withholdings: number;
    preliminary_tax: number;
  };
  document_count?: number; // Alias para documents_count
}

export interface CreateDeclarationRequest {
  title?: string;
  fiscal_year: number;
}

export interface UpdateDeclarationRequest {
  title?: string;
  fiscal_year?: number;
  status?: string;
  summary_data?: {
    total_income?: number;
    total_withholdings?: number;
    preliminary_tax?: number;
  };
}

export interface DuplicateDeclarationRequest {
  new_title?: string;
  copy_income_records?: boolean;
}

export interface BulkActionRequest {
  declaration_ids: string[];
  action: 'delete' | 'restore' | 'archive';
}

export interface DeclarationStats {
  total_declarations: number;
  active_declarations: number;
  completed_declarations: number;
  draft_declarations: number;
  declarations_by_year: Record<string, number>;
  declarations_by_status: Record<string, number>;
  total_income_all: string | number;
  total_withholdings_all: string | number;
  last_declaration: Declaration | null;
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
  // Nuevos campos
  active_declarations: number;
  completed_declarations: number;
  draft_declarations: number;
  declarations_by_year: Record<string, number>;
  declarations_by_status: Record<string, number>;
}

export interface DeclarationsByYearResponse {
  fiscal_year: number;
  count: number;
  declarations: Declaration[];
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
  private readonly baseUrl = ''; // Las URLs base ya están manejadas por api.ts

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
   * Elimina una declaración (soft delete)
   */
  async delete(id: string): Promise<{ message: string; declaration_id: string }> {
    try {
      const response = await api.delete(
        `${this.baseUrl}/declarations/${id}/`
      );
      return response;
    } catch (error: any) {
      console.error('Error deleting declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error eliminando declaración'
      );
    }
  }

  /**
   * Duplica una declaración
   */
  async duplicate(id: string, request: DuplicateDeclarationRequest = {}): Promise<Declaration> {
    try {
      const response = await api.post<Declaration>(
        `${this.baseUrl}/declarations/${id}/duplicate/`,
        request
      );
      return response;
    } catch (error: any) {
      console.error('Error duplicating declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error duplicando declaración'
      );
    }
  }

  /**
   * Restaura una declaración eliminada
   */
  async restore(id: string): Promise<Declaration> {
    try {
      const response = await api.post<Declaration>(
        `${this.baseUrl}/declarations/${id}/restore/`
      );
      return response;
    } catch (error: any) {
      console.error('Error restoring declaration:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error restaurando declaración'
      );
    }
  }

  /**
   * Realiza acciones en lote sobre múltiples declaraciones
   */
  async bulkAction(request: BulkActionRequest): Promise<{
    action: string;
    total_processed: number;
    results: Array<{
      id: string;
      success: boolean;
      message: string;
    }>;
  }> {
    try {
      const response = await api.post(
        `${this.baseUrl}/declarations/bulk_action/`,
        request
      );
      return response;
    } catch (error: any) {
      console.error('Error in bulk action:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error en acción en lote'
      );
    }
  }

  /**
   * Obtiene estadísticas avanzadas de declaraciones
   */
  async getStats(): Promise<DeclarationStats> {
    try {
      const response = await api.get<DeclarationStats>(
        `${this.baseUrl}/declarations/stats/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting stats:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error obteniendo estadísticas'
      );
    }
  }

  /**
   * Obtiene declaraciones de un año específico
   */
  async getByYear(year: number): Promise<DeclarationsByYearResponse> {
    try {
      const response = await api.get<DeclarationsByYearResponse>(
        `${this.baseUrl}/declarations/by_year/?year=${year}`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting declarations by year:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error obteniendo declaraciones del año'
      );
    }
  }

  /**
   * Actualiza el estado de una declaración
   */
  async updateStatus(id: string, status: string): Promise<Declaration> {
    try {
      const response = await api.post<Declaration>(
        `${this.baseUrl}/declarations/${id}/update_status/`,
        { status }
      );
      return response;
    } catch (error: any) {
      console.error('Error updating status:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error actualizando estado'
      );
    }
  }

  /**
   * Obtiene estadísticas del dashboard (método legacy)
   */
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // Usar el nuevo endpoint de stats y adaptar la respuesta
      const stats = await this.getStats();
      const declarations = await this.list({ page_size: 100 });
      
      const currentYear = new Date().getFullYear() - 1;
      const currentYearDeclaration = declarations.results.find(
        d => d.fiscal_year === currentYear
      );
      
      return {
        current_year_declaration: currentYearDeclaration,
        total_declarations: stats.total_declarations,
        processed_declarations: stats.completed_declarations,
        pending_declarations: stats.draft_declarations,
        total_income_current_year: currentYearDeclaration ? 
          parseFloat(currentYearDeclaration.total_income.toString()) : 0,
        potential_savings: 0, // TODO: Calcular ahorros potenciales
        active_declarations: stats.active_declarations,
        completed_declarations: stats.completed_declarations,
        draft_declarations: stats.draft_declarations,
        declarations_by_year: stats.declarations_by_year,
        declarations_by_status: stats.declarations_by_status
      };
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
      const currentYear = new Date().getFullYear() - 1; // Generalmente se declara el año anterior
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
   * Obtiene todas las declaraciones de un año específico
   */
  async getAllDeclarationsForYear(year: number): Promise<Declaration[]> {
    try {
      const response = await this.list({ 
        fiscal_year: year, 
        page_size: 100 // Asumiendo que no habrá más de 100 declaraciones por año
      });
      return response.results;
    } catch (error) {
      console.error('Error getting declarations for year:', error);
      return [];
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
    return declaration.is_editable || ['draft', 'in_progress', 'review', 'processing', 'error'].includes(declaration.status);
  }

  /**
   * Verifica si una declaración se puede procesar
   */
  canProcess(declaration: Declaration): boolean {
    return ['draft', 'in_progress', 'error'].includes(declaration.status);
  }

  /**
   * Verifica si una declaración está completa
   */
  isCompleted(declaration: Declaration): boolean {
    return ['completed', 'filed', 'paid'].includes(declaration.status);
  }

  /**
   * Verifica si una declaración se puede duplicar
   */
  canDuplicate(declaration: Declaration): boolean {
    return declaration.is_active && declaration.status !== 'processing';
  }

  /**
   * Verifica si una declaración se puede eliminar
   */
  canDelete(declaration: Declaration): boolean {
    return declaration.is_editable && ['draft', 'error'].includes(declaration.status);
  }

  /**
   * Verifica si una declaración fue eliminada
   */
  isDeleted(declaration: Declaration): boolean {
    return !declaration.is_active || !!declaration.deleted_at;
  }

  /**
   * Obtiene el progreso de una declaración (0-100)
   */
  getProgress(declaration: Declaration): number {
    return declaration.progress_percentage || 0;
  }

  /**
   * Formatea una cantidad monetaria
   */
  formatCurrency(value: string | number): string {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  }

  /**
   * Genera un título automático para una declaración
   */
  generateTitle(fiscalYear: number, existing: Declaration[] = []): string {
    const yearDeclarations = existing.filter(d => d.fiscal_year === fiscalYear);
    if (yearDeclarations.length === 0) {
      return `Declaración Renta ${fiscalYear}`;
    }
    return `Declaración Renta ${fiscalYear} #${yearDeclarations.length + 1}`;
  }

  /**
   * Obtiene el color del estado para la UI
   */
  getStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      'draft': 'bg-gray-100 text-gray-800 border-gray-200',
      'in_progress': 'bg-blue-100 text-blue-800 border-blue-200',
      'review': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'processing': 'bg-purple-100 text-purple-800 border-purple-200',
      'completed': 'bg-green-100 text-green-800 border-green-200',
      'filed': 'bg-green-100 text-green-800 border-green-200',
      'paid': 'bg-green-100 text-green-800 border-green-200',
      'error': 'bg-red-100 text-red-800 border-red-200'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
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
      'paid': 'Pagada',
      'error': 'Error'
    };
    return statusLabels[status] || status;
  }

  /**
   * Obtiene el icono del estado
   */
  getStatusIcon(status: string): string {
    const statusIcons: Record<string, string> = {
      'draft': '📝',
      'in_progress': '⚙️',
      'review': '👀',
      'processing': '🔄',
      'completed': '✅',
      'filed': '📤',
      'paid': '💰',
      'error': '❌'
    };
    return statusIcons[status] || '📄';
  }
}

// Instancia singleton del servicio
export const declarationService = new DeclarationService();
export default declarationService;

// Tipos de exportación para facilitar el uso
export type {
  Declaration,
  CreateDeclarationRequest,
  UpdateDeclarationRequest,
  DuplicateDeclarationRequest,
  BulkActionRequest,
  DeclarationStats,
  DeclarationListResponse,
  DashboardStats,
  DeclarationsByYearResponse,
  OptimizationRecommendation,
  OptimizationRecommendationsResponse
};