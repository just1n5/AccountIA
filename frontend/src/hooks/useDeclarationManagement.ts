// frontend/src/hooks/useDeclarationManagement.ts

import { useState, useEffect, useCallback, useMemo } from 'react';
import declarationService, { 
  Declaration, 
  DeclarationStats, 
  DuplicateDeclarationRequest,
  BulkActionRequest
} from '../services/declarationService';

interface UseDeclarationManagementState {
  declarations: Declaration[];
  isLoading: boolean;
  isRefreshing: boolean;
  isCreating: boolean;
  isDuplicating: boolean;
  isDeleting: boolean;
  isBulkActioning: boolean;
  error: string | null;
  stats: {
    totalDeclarations: number;
    currentYearDeclaration?: Declaration;
    lastDeclaration?: Declaration;
    hasCurrentYear: boolean;
    // Nuevas estadísticas
    activeDeclarations: number;
    completedDeclarations: number;
    draftDeclarations: number;
    declarationsByYear: Record<string, number>;
    declarationsByStatus: Record<string, number>;
  } | null;
  filters: {
    fiscalYear?: number;
    status?: string;
    showDeleted?: boolean;
  };
}

interface UseDeclarationManagementActions {
  fetchDeclarations: (showRefresh?: boolean) => Promise<void>;
  createDeclaration: (fiscalYear: number, title?: string) => Promise<Declaration | null>;
  duplicateDeclaration: (id: string, options?: DuplicateDeclarationRequest) => Promise<Declaration | null>;
  deleteDeclaration: (id: string) => Promise<boolean>;
  restoreDeclaration: (id: string) => Promise<Declaration | null>;
  bulkAction: (request: BulkActionRequest) => Promise<boolean>;
  updateDeclarationStatus: (id: string, status: string) => Promise<Declaration | null>;
  refreshDeclarations: () => Promise<void>;
  setFilters: (filters: Partial<UseDeclarationManagementState['filters']>) => void;
  clearFilters: () => void;
  clearError: () => void;
  retry: () => Promise<void>;
  getDeclarationsByYear: (year: number) => Declaration[];
  getDeclarationsByStatus: (status: string) => Declaration[];
}

type UseDeclarationManagementReturn = UseDeclarationManagementState & UseDeclarationManagementActions;

export const useDeclarationManagement = (): UseDeclarationManagementReturn => {
  // 🔥🔥🔥 HOOK MÚLTIPLES DECLARACIONES - v2024.6.25.1 🔥🔥🔥
  console.log('[HOOK] useDeclarationManagement MÚLTIPLES DECLARACIONES - v2024.6.25.1');
  
  const [declarations, setDeclarations] = useState<Declaration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isDuplicating, setIsDuplicating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isBulkActioning, setIsBulkActioning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<UseDeclarationManagementState['filters']>({});

  const currentYear = new Date().getFullYear() - 1; // Generalmente se declara el año anterior

  // 🎯 OPTIMIZACIÓN: Memoización de estadísticas avanzadas
  const stats = useMemo(() => {
    if (!declarations.length) return null;
    
    const activeDeclarations = declarations.filter(d => d.is_active);
    const currentYearDeclaration = activeDeclarations.find(d => d.fiscal_year === currentYear);
    const lastDeclaration = activeDeclarations[0]; // Asume que están ordenadas por fecha
    
    // Agrupar por año
    const declarationsByYear: Record<string, number> = {};
    activeDeclarations.forEach(d => {
      const year = d.fiscal_year.toString();
      declarationsByYear[year] = (declarationsByYear[year] || 0) + 1;
    });
    
    // Agrupar por estado
    const declarationsByStatus: Record<string, number> = {};
    activeDeclarations.forEach(d => {
      declarationsByStatus[d.status] = (declarationsByStatus[d.status] || 0) + 1;
    });
    
    return {
      totalDeclarations: declarations.length,
      activeDeclarations: activeDeclarations.length,
      completedDeclarations: activeDeclarations.filter(d => declarationService.isCompleted(d)).length,
      draftDeclarations: activeDeclarations.filter(d => d.status === 'draft').length,
      lastDeclaration,
      currentYearDeclaration,
      hasCurrentYear: !!currentYearDeclaration,
      declarationsByYear,
      declarationsByStatus
    };
  }, [declarations, currentYear]);
  
  // 🎯 OPTIMIZACIÓN: Memoización de declaraciones filtradas
  const filteredDeclarations = useMemo(() => {
    let filtered = declarations;
    
    // Filtro por estado activo/inactivo
    if (!filters.showDeleted) {
      filtered = filtered.filter(d => d.is_active);
    }
    
    // Filtro por año fiscal
    if (filters.fiscalYear) {
      filtered = filtered.filter(d => d.fiscal_year === filters.fiscalYear);
    }
    
    // Filtro por estado
    if (filters.status) {
      filtered = filtered.filter(d => d.status === filters.status);
    }
    
    return filtered;
  }, [declarations, filters]);

  // 🎯 OPTIMIZACIÓN: Función de fetch con mejor manejo de errores
  const fetchDeclarations = useCallback(async (showRefresh = false) => {
    try {
      if (showRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError(null);
      
      const response = await declarationService.list();
      setDeclarations(response.results);
    } catch (err: any) {
      console.error('Error fetching declarations:', err);
      
      // 🎯 OPTIMIZACIÓN: Mejor manejo de errores específicos
      if (err.response?.status === 401) {
        setError('Sesión expirada. Por favor, inicia sesión nuevamente.');
      } else if (err.response?.status === 500) {
        setError('Error del servidor. Inténtalo de nuevo en unos minutos.');
      } else if (!navigator.onLine) {
        setError('Sin conexión a internet. Verifica tu conexión.');
      } else {
        setError(err.response?.data?.error || 'Error al cargar las declaraciones');
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // 🎯 OPTIMIZACIÓN: Función de creación con título personalizado
  const createDeclaration = useCallback(async (fiscalYear: number, title?: string): Promise<Declaration | null> => {
    try {
      setIsCreating(true);
      setError(null);
      
      // Generar título automático si no se proporciona
      const finalTitle = title || declarationService.generateTitle(fiscalYear, declarations.filter(d => d.is_active));
      
      console.log('[CREATE] Creando declaracion para el año:', fiscalYear);
      console.log('[STATE] Estado actual de declaraciones:', declarations.length);
      
      const requestData = { 
        fiscal_year: fiscalYear,
        title: finalTitle
      };
      console.log('[REQUEST] Request data:', requestData);
      
      const response = await declarationService.create(requestData);
      
      console.log('[SUCCESS] Declaracion creada - Respuesta completa:', response);
      console.log('[TYPE] Tipo de respuesta:', typeof response);
      console.log('[KEYS] Propiedades de respuesta:', Object.keys(response || {}));
      
      // 🎯 VALIDACIÓN ROBUSTA: Verificar estructura de respuesta
      if (!response) {
        console.error('[ERROR] Respuesta es null o undefined');
        setError('Error: No se recibio respuesta del servidor');
        return null;
      }
      
      if (typeof response !== 'object') {
        console.error('[ERROR] Respuesta no es un objeto:', typeof response);
        setError('Error: Respuesta invalida del servidor');
        return null;
      }
      
      if (!response.id) {
        console.error('[ERROR] Respuesta sin ID:', response);
        console.error('[DEBUG] Campos disponibles:', Object.keys(response));
        setError('Error: La declaracion fue creada pero sin ID valido');
        return null;
      }
      
      console.log('[SUCCESS] Declaracion creada exitosamente con ID:', response.id);
      
      // 🎯 OPTIMIZACIÓN: Actualizar estado local inmediatamente
      setDeclarations(prev => {
        console.log('[UPDATE] Actualizando lista de declaraciones:', prev.length, '->', prev.length + 1);
        return [response, ...prev];
      });
      
      return response;
      
    } catch (err: any) {
      console.error('[ERROR] Error creating declaration:', err);
      console.error('[DEBUG] Error type:', typeof err);
      console.error('[DEBUG] Error keys:', Object.keys(err || {}));
      console.error('[DEBUG] Response data:', err.response?.data);
      console.error('[DEBUG] Response status:', err.response?.status);
      
      // 🎯 OPTIMIZACIÓN: Manejo específico de errores de creación
      if (err.response?.status === 400) {
        const validationErrors = err.response?.data;
        if (validationErrors?.fiscal_year) {
          setError(validationErrors.fiscal_year[0]);
        } else if (validationErrors?.non_field_errors) {
          setError(validationErrors.non_field_errors[0]);
        } else {
          setError('Datos inválidos para crear la declaración');
        }
      } else if (err.response?.status === 409) {
        setError(`Ya existe una declaración para el año ${fiscalYear}`);
      } else if (err.response?.status === 500) {
        setError('Error del servidor al crear la declaración. Inténtalo de nuevo.');
      } else if (!navigator.onLine) {
        setError('Sin conexión a internet. No se pudo crear la declaración.');
      } else {
        const errorMessage = err.response?.data?.error || err.message || 'Error al crear la declaracion';
        console.error('[FINAL] Final error message:', errorMessage);
        setError(errorMessage);
      }
      return null;
    } finally {
      setIsCreating(false);
    }
  }, [declarations]);
  
  // 🆕 NUEVA FUNCIONALIDAD: Duplicar declaración
  const duplicateDeclaration = useCallback(async (id: string, options: DuplicateDeclarationRequest = {}): Promise<Declaration | null> => {
    try {
      setIsDuplicating(true);
      setError(null);
      
      console.log('[DUPLICATE] Duplicando declaración:', id, options);
      
      const response = await declarationService.duplicate(id, options);
      
      console.log('[DUPLICATE] Declaración duplicada exitosamente:', response.id);
      
      // Actualizar estado local
      setDeclarations(prev => [response, ...prev]);
      
      return response;
      
    } catch (err: any) {
      console.error('[ERROR] Error duplicating declaration:', err);
      setError(err.message || 'Error al duplicar la declaración');
      return null;
    } finally {
      setIsDuplicating(false);
    }
  }, []);
  
  // 🆕 NUEVA FUNCIONALIDAD: Eliminar declaración
  const deleteDeclaration = useCallback(async (id: string): Promise<boolean> => {
    try {
      setIsDeleting(true);
      setError(null);
      
      console.log('[DELETE] Eliminando declaración:', id);
      
      await declarationService.delete(id);
      
      console.log('[DELETE] Declaración eliminada exitosamente');
      
      // Marcar como inactiva en el estado local
      setDeclarations(prev => 
        prev.map(d => 
          d.id === id 
            ? { ...d, is_active: false, deleted_at: new Date().toISOString() }
            : d
        )
      );
      
      return true;
      
    } catch (err: any) {
      console.error('[ERROR] Error deleting declaration:', err);
      setError(err.message || 'Error al eliminar la declaración');
      return false;
    } finally {
      setIsDeleting(false);
    }
  }, []);
  
  // 🆕 NUEVA FUNCIONALIDAD: Restaurar declaración
  const restoreDeclaration = useCallback(async (id: string): Promise<Declaration | null> => {
    try {
      setError(null);
      
      console.log('[RESTORE] Restaurando declaración:', id);
      
      const response = await declarationService.restore(id);
      
      console.log('[RESTORE] Declaración restaurada exitosamente:', response.id);
      
      // Actualizar estado local
      setDeclarations(prev => 
        prev.map(d => 
          d.id === id 
            ? { ...response, is_active: true, deleted_at: null }
            : d
        )
      );
      
      return response;
      
    } catch (err: any) {
      console.error('[ERROR] Error restoring declaration:', err);
      setError(err.message || 'Error al restaurar la declaración');
      return null;
    }
  }, []);
  
  // 🆕 NUEVA FUNCIONALIDAD: Acciones en lote
  const bulkAction = useCallback(async (request: BulkActionRequest): Promise<boolean> => {
    try {
      setIsBulkActioning(true);
      setError(null);
      
      console.log('[BULK] Ejecutando acción en lote:', request);
      
      const response = await declarationService.bulkAction(request);
      
      console.log('[BULK] Acción completada:', response);
      
      // Refrescar declaraciones para obtener el estado actualizado
      await fetchDeclarations(true);
      
      return response.results.every(r => r.success);
      
    } catch (err: any) {
      console.error('[ERROR] Error in bulk action:', err);
      setError(err.message || 'Error en acción en lote');
      return false;
    } finally {
      setIsBulkActioning(false);
    }
  }, []);
  
  // 🆕 NUEVA FUNCIONALIDAD: Actualizar estado de declaración
  const updateDeclarationStatus = useCallback(async (id: string, status: string): Promise<Declaration | null> => {
    try {
      setError(null);
      
      console.log('[UPDATE_STATUS] Actualizando estado:', id, status);
      
      const response = await declarationService.updateStatus(id, status);
      
      console.log('[UPDATE_STATUS] Estado actualizado exitosamente');
      
      // Actualizar estado local
      setDeclarations(prev => 
        prev.map(d => 
          d.id === id 
            ? { ...d, ...response }
            : d
        )
      );
      
      return response;
      
    } catch (err: any) {
      console.error('[ERROR] Error updating status:', err);
      setError(err.message || 'Error al actualizar estado');
      return null;
    }
  }, []);

  // 🎯 NUEVA FUNCIONALIDAD: Refresh específico
  const refreshDeclarations = useCallback(() => {
    return fetchDeclarations(true);
  }, [fetchDeclarations]);

  // 🎯 NUEVA FUNCIONALIDAD: Limpiar error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // 🎯 NUEVA FUNCIONALIDAD: Retry en caso de error
  const retry = useCallback(() => {
    return fetchDeclarations();
  }, [fetchDeclarations]);
  
  // 🆕 FUNCIONALIDADES DE FILTRADO
  const setFilters = useCallback((newFilters: Partial<UseDeclarationManagementState['filters']>) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }));
  }, []);
  
  const clearFilters = useCallback(() => {
    setFiltersState({});
  }, []);
  
  // 🆕 FUNCIONALIDADES DE CONSULTA
  const getDeclarationsByYear = useCallback((year: number): Declaration[] => {
    return declarations.filter(d => d.fiscal_year === year && d.is_active);
  }, [declarations]);
  
  const getDeclarationsByStatus = useCallback((status: string): Declaration[] => {
    return declarations.filter(d => d.status === status && d.is_active);
  }, [declarations]);

  // 🎯 OPTIMIZACIÓN: Fetch inicial automático
  useEffect(() => {
    fetchDeclarations();
  }, [fetchDeclarations]);

  // 🎯 OPTIMIZACIÓN: Auto-refresh cada 5 minutos cuando está activo
  useEffect(() => {
    const interval = setInterval(() => {
      // Solo refrescar si no hay operaciones en curso y no hay errores
      if (!isLoading && !isRefreshing && !isCreating && !isDuplicating && !isDeleting && !isBulkActioning && !error) {
        fetchDeclarations(true);
      }
    }, 5 * 60 * 1000); // 5 minutos

    return () => clearInterval(interval);
  }, [isLoading, isRefreshing, isCreating, isDuplicating, isDeleting, isBulkActioning, error, fetchDeclarations]);

  return {
    // Estado
    declarations: filteredDeclarations,
    isLoading,
    isRefreshing,
    isCreating,
    isDuplicating,
    isDeleting,
    isBulkActioning,
    error,
    stats,
    filters,
    
    // Acciones
    fetchDeclarations,
    createDeclaration,
    duplicateDeclaration,
    deleteDeclaration,
    restoreDeclaration,
    bulkAction,
    updateDeclarationStatus,
    refreshDeclarations,
    setFilters,
    clearFilters,
    clearError,
    retry,
    getDeclarationsByYear,
    getDeclarationsByStatus
  };
};

// 🎯 HOOK ADICIONAL: Para gestión de declaración individual
export const useDeclaration = (id: string) => {
  const [declaration, setDeclaration] = useState<Declaration | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDeclaration = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await declarationService.getById(id);
      setDeclaration(response);
    } catch (err: any) {
      console.error('Error fetching declaration:', err);
      setError(err.response?.data?.error || 'Error al cargar la declaración');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  const updateDeclaration = useCallback(async (updates: Partial<Declaration>) => {
    if (!declaration) return null;

    try {
      const response = await declarationService.update(declaration.id, updates);
      setDeclaration(response);
      return response;
    } catch (err: any) {
      console.error('Error updating declaration:', err);
      setError(err.response?.data?.error || 'Error al actualizar la declaración');
      return null;
    }
  }, [declaration]);

  useEffect(() => {
    if (id) {
      fetchDeclaration();
    }
  }, [id, fetchDeclaration]);

  return {
    declaration,
    isLoading,
    error,
    fetchDeclaration,
    updateDeclaration,
    clearError: () => setError(null)
  };
};

// 🎯 TIPOS DE UTILIDAD
// 🆕 HOOK PARA ESTADÍSTICAS AVANZADAS
export const useDeclarationStats = () => {
  const [stats, setStats] = useState<DeclarationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await declarationService.getStats();
      setStats(response);
    } catch (err: any) {
      console.error('Error fetching stats:', err);
      setError(err.message || 'Error obteniendo estadísticas');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    isLoading,
    error,
    fetchStats,
    clearError: () => setError(null)
  };
};

export type DeclarationManagement = UseDeclarationManagementReturn;
export type DeclarationHook = ReturnType<typeof useDeclaration>;
export type DeclarationStatsHook = ReturnType<typeof useDeclarationStats>;

export default useDeclarationManagement;