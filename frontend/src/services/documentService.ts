import api from './api';

// Tipos de datos
export interface Document {
  id: string;
  declaration_id: string;
  file_name: string;
  original_file_name: string;
  file_size?: number;
  file_type: string;
  mime_type: string;
  description?: string;
  upload_status: 'pending' | 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error';
  processing_errors: string[];
  processed_data?: any;
  storage_path?: string;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentUploadRequest {
  declarationId: string;
  fileName: string;
  fileType: string;
  fileSize?: number;
  mimeType?: string;
  description?: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  upload_url: string;
  storage_key: string;
  expires_in: number;
}

export interface DocumentStatusUpdateRequest {
  upload_status: 'uploaded' | 'error';
  error_message?: string;
}

export interface DocumentListResponse {
  declaration_id: string;
  documents: Document[];
  total_documents: number;
}

export interface DocumentSummaryResponse {
  declaration_id: string;
  total_documents: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  exogena_summary?: any;
}

/**
 * Servicio para gestión de documentos
 */
class DocumentService {
  private readonly baseUrl = ''; // Las URLs base ya están manejadas por api.ts

  /**
   * Obtiene el resumen detallado de un documento procesado
   */
  async getDetailedSummary(documentId: string): Promise<any> {
    try {
      const response = await api.get(
        `${this.baseUrl}/documents/${documentId}/detailed_summary/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting detailed summary:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error obteniendo resumen detallado'
      );
    }
  }

  /**
   * Obtiene un documento específico por ID
   */
  async getById(documentId: string): Promise<Document> {
    try {
      const response = await api.get<Document>(
        `${this.baseUrl}/documents/${documentId}/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting document by ID:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error obteniendo documento'
      );
    }
  }

  /**
   * Descarga un documento
   */
  async downloadDocument(documentId: string): Promise<void> {
    try {
      const { download_url } = await this.getDownloadUrl(documentId);
      
      // Abrir en nueva ventana para descargar
      window.open(download_url, '_blank');
    } catch (error: any) {
      console.error('Error downloading document:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error descargando documento'
      );
    }
  }

  /**
   * Solicita una URL firmada para subir un archivo
   */
  async requestUploadUrl(request: DocumentUploadRequest): Promise<DocumentUploadResponse> {
    try {
      const response = await api.post<DocumentUploadResponse>(
        `${this.baseUrl}/declarations/${request.declarationId}/documents/initiate_upload/`,
        {
          file_name: request.fileName,
          file_type: request.fileType,
          file_size: request.fileSize,
          mime_type: request.mimeType,
          description: request.description
        }
      );
      return response;
    } catch (error: any) {
      console.error('Error requesting upload URL:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error solicitando URL de subida'
      );
    }
  }

  /**
   * Sube un archivo directamente a GCS usando la URL firmada
   */
  async uploadFile(
    uploadUrl: string, 
    file: File, 
    onProgress?: (progress: number) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Configurar progreso
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            onProgress(percentComplete);
          }
        });
      }

      // Configurar completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          reject(new Error(`Error subiendo archivo: ${xhr.status}`));
        }
      });

      // Configurar error
      xhr.addEventListener('error', () => {
        reject(new Error('Error de red al subir archivo'));
      });

      // Realizar subida
      xhr.open('PUT', uploadUrl);
      xhr.setRequestHeader('Content-Type', file.type);
      xhr.send(file);
    });
  }

  /**
   * Actualiza el estado de un documento después de la subida
   */
  async updateStatus(
    documentId: string, 
    status: 'uploaded' | 'error',
    errorMessage?: string
  ): Promise<Document> {
    try {
      // Extraer declaration_id del documento o usar un endpoint diferente
      const response = await api.put<Document>(
        `${this.baseUrl}/documents/${documentId}/update_status/`,
        {
          upload_status: status,
          error_message: errorMessage
        }
      );
      return response;
    } catch (error: any) {
      console.error('Error updating document status:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error actualizando estado del documento'
      );
    }
  }

  /**
   * Obtiene los documentos de una declaración
   */
  async getByDeclaration(declarationId: string): Promise<Document[]> {
    try {
      const response = await api.get<any>(
        `${this.baseUrl}/declarations/${declarationId}/documents/`
      );
      
      // DEBUG: Verificar estructura de respuesta
      console.log('documentService.getByDeclaration - response:', response);
      
      // Manejar diferentes estructuras de respuesta
      if (response.results && Array.isArray(response.results)) {
        // Respuesta paginada: {results: [], count: number}
        return response.results;
      } else if (response.documents && Array.isArray(response.documents)) {
        // Respuesta con propiedad documents: {documents: []}
        return response.documents;
      } else if (Array.isArray(response)) {
        // Respuesta directa como array: []
        return response;
      } else {
        // Fallback a array vacío
        console.warn('Unexpected response structure for documents:', response);
        return [];
      }
    } catch (error: any) {
      console.error('Error getting documents by declaration:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error obteniendo documentos'
      );
    }
  }

  /**
   * Obtiene el resumen de documentos de una declaración
   */
  async getSummary(declarationId: string): Promise<DocumentSummaryResponse> {
    try {
      const response = await api.get<DocumentSummaryResponse>(
        `${this.baseUrl}/declarations/${declarationId}/documents/summary/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting document summary:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error obteniendo resumen de documentos'
      );
    }
  }

  /**
   * Obtiene los datos procesados de un documento
   */
  async getProcessedData(documentId: string): Promise<any> {
    try {
      const response = await api.get(
        `${this.baseUrl}/documents/${documentId}/processed_data/`
      );
      return response.processed_data || response;
    } catch (error: any) {
      console.error('Error getting processed data:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error obteniendo datos procesados'
      );
    }
  }

  /**
   * Solicita el reprocesamiento de un documento
   */
  async reprocess(documentId: string): Promise<void> {
    try {
      await api.post(
        `${this.baseUrl}/documents/${documentId}/reprocess/`
      );
    } catch (error: any) {
      console.error('Error reprocessing document:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error reprocesando documento'
      );
    }
  }

  /**
   * Genera URL de descarga para un documento
   */
  async getDownloadUrl(documentId: string): Promise<{ download_url: string; filename: string; expires_in: number }> {
    try {
      const response = await api.get(
        `${this.baseUrl}/documents/${documentId}/download_url/`
      );
      return response;
    } catch (error: any) {
      console.error('Error getting download URL:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error obteniendo URL de descarga'
      );
    }
  }

  /**
   * Elimina un documento
   */
  async delete(documentId: string): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/documents/${documentId}/`);
    } catch (error: any) {
      console.error('Error deleting document:', error);
      throw new Error(
        error.response?.data?.error || 
        'Error eliminando documento'
      );
    }
  }

  /**
   * Obtiene documentos generales del usuario (sin filtro por declaración)
   */
  async list(params?: {
    page?: number;
    page_size?: number;
    file_type?: string;
    upload_status?: string;
  }): Promise<Document[]> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
      if (params?.file_type) queryParams.append('file_type', params.file_type);
      if (params?.upload_status) queryParams.append('upload_status', params.upload_status);
      
      const url = `${this.baseUrl}/documents/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await api.get<Document[]>(url);
      return response.results || response as any || [];
    } catch (error: any) {
      console.error('Error listing documents:', error);
      throw new Error(
        error.response?.data?.error ||
        'Error listando documentos'
      );
    }
  }

  /**
   * Verifica si un archivo de exógena ya fue procesado para una declaración
   */
  async hasProcessedExogena(declarationId: string): Promise<boolean> {
    try {
      const documents = await this.getByDeclaration(declarationId);
      return documents.some(doc =>
        doc.file_type === 'exogena_report' &&
        doc.upload_status === 'processed'
      );
    } catch (error) {
      console.error('Error checking processed exogena:', error);
      return false;
    }
  }

  /**
   * Obtiene el documento de exógena procesado de una declaración
   */
  async getProcessedExogena(declarationId: string): Promise<Document | null> {
    try {
      const documents = await this.getByDeclaration(declarationId);
      return documents.find(doc =>
        doc.file_type === 'exogena_report' &&
        doc.upload_status === 'processed'
      ) || null;
    } catch (error) {
      console.error('Error getting processed exogena:', error);
      return null;
    }
  }

  /**
   * Valida un archivo antes de subirlo
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    // Verificar tipo de archivo
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
    ];

    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'Solo se permiten archivos Excel (.xlsx, .xls)'
      };
    }

    // Verificar tamaño (50MB máximo)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      return {
        valid: false,
        error: 'El archivo excede el tamaño máximo de 50MB'
      };
    }

    // Verificar extensión en el nombre
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
      return {
        valid: false,
        error: 'El archivo debe tener extensión .xlsx o .xls'
      };
    }

    return { valid: true };
  }

  /**
   * Upload directo para modo testing (más simple)
   */
  async uploadDirect(
    declarationId: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<any> {
    try {
      // Validar archivo
      const validation = this.validateFile(file);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      onProgress?.(10);

      // Crear FormData
      const formData = new FormData();
      formData.append('file', file);

      onProgress?.(30);

      // Upload directo usando fetch para mostrar progreso
      // Usar api.post para mantener consistencia con headers y baseURL
      const result = await api.post(
        `/declarations/${declarationId}/documents/upload_direct/`,
        formData
      );

      onProgress?.(100);

      return result;
    } catch (error) {
      console.error('Error in direct upload:', error);
      throw error;
    }
  }

  /**
   * Workflow completo de subida de archivo
   */
  async uploadWorkflow(
    declarationId: string,
    file: File,
    onProgress?: (stage: string, progress: number) => void
  ): Promise<Document> {
    try {
      // Validar archivo
      const validation = this.validateFile(file);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      onProgress?.('Solicitando URL de subida...', 10);

      // Solicitar URL de subida
      const uploadResponse = await this.requestUploadUrl({
        declarationId,
        fileName: file.name,
        fileType: 'exogena_report',
        fileSize: file.size,
        mimeType: file.type
      });

      onProgress?.('Subiendo archivo...', 30);

      // Subir archivo
      await this.uploadFile(uploadResponse.upload_url, file, (progress) => {
        onProgress?.('Subiendo archivo...', 30 + (progress * 0.6));
      });

      onProgress?.('Notificando servidor...', 95);

      // Notificar que la subida fue exitosa
      const document = await this.updateStatus(uploadResponse.document_id, 'uploaded');

      onProgress?.('¡Completado!', 100);

      return document;
    } catch (error) {
      console.error('Error in upload workflow:', error);
      throw error;
    }
  }
}

// Instancia singleton del servicio
export const documentService = new DocumentService();
export default documentService;
