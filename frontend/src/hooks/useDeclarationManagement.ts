// frontend/src/hooks/useDeclarationManagement.ts

import { useState, useEffect, useCallback, useMemo } from 'react';
import declarationService, { Declaration } from '../services/declarationService';

interface UseDeclarationManagementState {
  declarations: Declaration[];
  isLoading: boolean;
  isRefreshing: boolean;
  isCreating: boolean;
  error: string | null;
  stats: {
    totalDeclarations: number;
    currentYearDeclaration?: Declaration;
    lastDeclaration?: Declaration;
    hasCurrentYear: boolean;
  } | null;
}

interface UseDeclarationManagementActions {
  fetchDeclarations: (showRefresh?: boolean) => Promise<void>;
  createDeclaration: (fiscalYear: number) => Promise<Declaration | null>;
  refreshDeclarations: () => Promise<void>;
  clearError: () => void;
  retry: () => Promise<void>;
}

type UseDeclarationManagementReturn = UseDeclarationManagementState & UseDeclarationManagementActions;

export const useDeclarationManagement = (): UseDeclarationManagementReturn => {
  // 🔥🔥🔥 HOOK NUEVO CARGADO - v2024.6.23.1 🔥🔥🔥
  console.log('[HOOK] useDeclarationManagement CARGADO - v2024.6.23.1');
  
  const [declarations, setDeclarations] = useState<Declaration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentYear = new Date().getFullYear() - 1; // Generalmente se declara el año anterior

  // 🎯 OPTIMIZACIÓN: Memoización de estadísticas
  const stats = useMemo(() => {
    if (!declarations.length) return null;
    
    const currentYearDeclaration = declarations.find(d => d.fiscal_year === currentYear);
    const totalDeclarations = declarations.length;
    const lastDeclaration = declarations[0]; // Asume que están ordenadas por fecha
    
    return {
      totalDeclarations,
      lastDeclaration,
      currentYearDeclaration,
      hasCurrentYear: !!currentYearDeclaration
    };
  }, [declarations, currentYear]);

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

  // 🎯 OPTIMIZACIÓN: Función de creación con mejor feedback
  const createDeclaration = useCallback(async (fiscalYear: number): Promise<Declaration | null> => {
    try {
      setIsCreating(true);
      setError(null);
      
      // Verificar si ya existe
      const existingDeclaration = declarations.find(d => d.fiscal_year === fiscalYear);
      if (existingDeclaration) {
        setError(`Ya existe una declaración para el año ${fiscalYear}`);
        return null;
      }
      
      console.log('[CREATE] Creando declaracion para el año:', fiscalYear);
      console.log('[STATE] Estado actual de declaraciones:', declarations.length);
      
      const requestData = { fiscal_year: fiscalYear };
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

  // 🎯 OPTIMIZACIÓN: Fetch inicial automático
  useEffect(() => {
    fetchDeclarations();
  }, [fetchDeclarations]);

  // 🎯 OPTIMIZACIÓN: Auto-refresh cada 5 minutos cuando está activo
  useEffect(() => {
    const interval = setInterval(() => {
      // Solo refrescar si no hay operaciones en curso y no hay errores
      if (!isLoading && !isRefreshing && !isCreating && !error) {
        fetchDeclarations(true);
      }
    }, 5 * 60 * 1000); // 5 minutos

    return () => clearInterval(interval);
  }, [isLoading, isRefreshing, isCreating, error, fetchDeclarations]);

  return {
    // Estado
    declarations,
    isLoading,
    isRefreshing,
    isCreating,
    error,
    stats,
    
    // Acciones
    fetchDeclarations,
    createDeclaration,
    refreshDeclarations,
    clearError,
    retry
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
export type DeclarationManagement = UseDeclarationManagementReturn;
export type DeclarationHook = ReturnType<typeof useDeclaration>;

export default useDeclarationManagement;