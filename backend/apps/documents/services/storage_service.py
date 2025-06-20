"""
Servicio de almacenamiento en Google Cloud Storage para AccountIA
"""

import os
import uuid
import datetime
import logging
from typing import Tuple, Optional

from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleCloudStorageService:
    """
    Servicio para manejar el almacenamiento de archivos en Google Cloud Storage
    """
    
    def __init__(self):
        """Inicializar el cliente de Google Cloud Storage"""
        try:
            self.project_id = getattr(settings, 'GOOGLE_CLOUD_PROJECT', 'accountia-dev-0001')
            self.bucket_name = getattr(settings, 'GCS_BUCKET_NAME', 'accountia-dev-documents-0001')
            
            # Inicializar cliente con credenciales explícitas
            credentials_path = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
            if credentials_path and os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            
            logger.info(f"✅ GoogleCloudStorageService inicializado - Proyecto: {self.project_id}, Bucket: {self.bucket_name}")
            
        except DefaultCredentialsError as e:
            logger.error(f"❌ Error de credenciales de Google Cloud: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error inicializando GoogleCloudStorageService: {str(e)}")
            raise
    
    def generate_signed_url(self, filename: str, user_id: str, content_type: str = None) -> Tuple[str, str]:
        """
        Generar URL firmada para upload directo del cliente
        
        Args:
            filename: Nombre original del archivo
            user_id: ID del usuario
            content_type: Tipo de contenido (opcional)
        
        Returns:
            Tupla con (upload_url, storage_path)
        """
        try:
            # Generar nombre único para evitar colisiones
            file_extension = self._get_file_extension(filename)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            storage_path = f"users/{user_id}/documents/{unique_filename}"
            
            blob = self.bucket.blob(storage_path)
            
            # Determinar content type si no se proporciona
            if not content_type:
                content_type = self._get_content_type(file_extension)
            
            # Generar URL firmada válida por 15 minutos
            upload_url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="PUT",
                content_type=content_type,
                headers={'x-goog-content-length-range': '0,52428800'}  # Máximo 50MB
            )
            
            logger.info(f"✅ URL firmada generada para {filename} -> {storage_path}")
            return upload_url, storage_path
            
        except Exception as e:
            logger.error(f"❌ Error generando URL firmada para {filename}: {str(e)}")
            raise
    
    def download_file(self, storage_path: str) -> bytes:
        """
        Descargar archivo desde Google Cloud Storage
        
        Args:
            storage_path: Ruta del archivo en GCS
        
        Returns:
            Contenido del archivo como bytes
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            if not blob.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {storage_path}")
            
            content = blob.download_as_bytes()
            logger.info(f"✅ Archivo descargado: {storage_path} ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error descargando archivo {storage_path}: {str(e)}")
            raise
    
    def upload_file(self, content: bytes, storage_path: str, content_type: str = None) -> str:
        """
        Subir archivo directamente a Google Cloud Storage
        
        Args:
            content: Contenido del archivo como bytes
            storage_path: Ruta donde guardar el archivo
            content_type: Tipo de contenido
        
        Returns:
            URL pública del archivo
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            if content_type:
                blob.content_type = content_type
            
            blob.upload_from_string(content)
            
            logger.info(f"✅ Archivo subido: {storage_path}")
            return f"gs://{self.bucket_name}/{storage_path}"
            
        except Exception as e:
            logger.error(f"❌ Error subiendo archivo a {storage_path}: {str(e)}")
            raise
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Eliminar archivo de Google Cloud Storage
        
        Args:
            storage_path: Ruta del archivo a eliminar
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            if blob.exists():
                blob.delete()
                logger.info(f"✅ Archivo eliminado: {storage_path}")
                return True
            else:
                logger.warning(f"⚠️ Archivo no existe: {storage_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error eliminando archivo {storage_path}: {str(e)}")
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """
        Verificar si un archivo existe en Google Cloud Storage
        
        Args:
            storage_path: Ruta del archivo
        
        Returns:
            True si el archivo existe
        """
        try:
            blob = self.bucket.blob(storage_path)
            return blob.exists()
        except Exception as e:
            logger.error(f"❌ Error verificando existencia de {storage_path}: {str(e)}")
            return False
    
    def get_file_metadata(self, storage_path: str) -> Optional[dict]:
        """
        Obtener metadatos de un archivo
        
        Args:
            storage_path: Ruta del archivo
        
        Returns:
            Diccionario con metadatos o None si no existe
        """
        try:
            blob = self.bucket.blob(storage_path)
            
            if not blob.exists():
                return None
            
            blob.reload()  # Cargar metadatos
            
            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'etag': blob.etag,
                'md5_hash': blob.md5_hash
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo metadatos de {storage_path}: {str(e)}")
            return None
    
    def _get_file_extension(self, filename: str) -> str:
        """Extraer la extensión del archivo"""
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return ''
    
    def _get_content_type(self, file_extension: str) -> str:
        """Determinar el content type basado en la extensión"""
        content_types = {
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')


class MockGoogleCloudStorageService:
    """Mock service para desarrollo sin credenciales"""
    def __init__(self):
        self.project_id = "mock-project"
        self.bucket_name = "mock-bucket"
        logger.warning("🚧 Usando Mock Google Cloud Storage Service para desarrollo")
    
    def generate_signed_url(self, filename: str, user_id: str, content_type: str = None) -> Tuple[str, str]:
        unique_filename = f"{uuid.uuid4()}.{filename.split('.')[-1] if '.' in filename else 'file'}"
        storage_path = f"users/{user_id}/documents/{unique_filename}"
        upload_url = f'https://mock-upload-url/{unique_filename}'
        return upload_url, storage_path
    
    def upload_file(self, content: bytes, storage_path: str, content_type: str = None) -> str:
        logger.info(f"📁 Mock: Subiendo archivo {storage_path}")
        return f'gs://mock-bucket/{storage_path}'
    
    def download_file(self, storage_path: str) -> bytes:
        logger.info(f"📁 Mock: Descargando archivo {storage_path}")
        return b'mock file content'
    
    def delete_file(self, storage_path: str) -> bool:
        logger.info(f"🗑️ Mock: Eliminando archivo {storage_path}")
        return True
    
    def file_exists(self, storage_path: str) -> bool:
        return False
    
    def get_file_metadata(self, storage_path: str) -> Optional[dict]:
        return None

# Variable global para lazy loading
_gcs_service = None

def get_gcs_service():
    """Get or create GCS service instance (lazy loading)"""
    global _gcs_service
    if _gcs_service is None:
        try:
            _gcs_service = GoogleCloudStorageService()
        except DefaultCredentialsError as e:
            logger.error(f"❌ Error de credenciales de Google Cloud: {e}")
            # En desarrollo, usar mock service
            if getattr(settings, 'DEBUG', True):
                _gcs_service = MockGoogleCloudStorageService()
            else:
                raise
        except Exception as e:
            logger.error(f"❌ Error inicializando Google Cloud Storage: {e}")
            if getattr(settings, 'DEBUG', True):
                _gcs_service = MockGoogleCloudStorageService()
            else:
                raise
    return _gcs_service

# Para compatibilidad con código existente
gcs_service = None  # Será inicializado mediante get_gcs_service()
