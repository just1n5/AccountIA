"""
Servicio para gestión de almacenamiento en Google Cloud Storage.
"""
import os
import hashlib
import mimetypes
from datetime import timedelta
from typing import Optional, Dict, Any, BinaryIO, List
import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

# Importaciones condicionales para desarrollo/producción
try:
    from google.cloud import storage
    from google.cloud.storage import Blob
    from google.auth.exceptions import DefaultCredentialsError
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    storage = None
    Blob = None

logger = logging.getLogger(__name__)


class StorageService:
    """
    Servicio base para almacenamiento de archivos.
    """
    
    def generate_signed_url(self, blob_name: str, expiration: int = 3600, method: str = 'PUT') -> str:
        """Genera una URL firmada para acceso temporal."""
        raise NotImplementedError
    
    def upload_file(self, file_obj: BinaryIO, blob_name: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Sube un archivo al almacenamiento."""
        raise NotImplementedError
    
    def download_file(self, blob_name: str) -> bytes:
        """Descarga un archivo del almacenamiento."""
        raise NotImplementedError
    
    def delete_file(self, blob_name: str) -> bool:
        """Elimina un archivo del almacenamiento."""
        raise NotImplementedError
    
    def file_exists(self, blob_name: str) -> bool:
        """Verifica si un archivo existe."""
        raise NotImplementedError


class GoogleCloudStorageService(StorageService):
    """
    Servicio para interactuar con Google Cloud Storage.
    """
    
    def __init__(self):
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImproperlyConfigured(
                "google-cloud-storage no está instalado. "
                "Instala con: pip install google-cloud-storage"
            )
        
        self.bucket_name = getattr(settings, 'GCS_BUCKET_NAME', None)
        if not self.bucket_name:
            raise ImproperlyConfigured("GCS_BUCKET_NAME no está configurado en settings")
        
        try:
            # Inicializar cliente de Storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Verificar que el bucket existe
            if not self.bucket.exists():
                logger.warning(f"Bucket {self.bucket_name} no existe. Creándolo...")
                self.bucket = self.client.create_bucket(self.bucket_name, location="US")
                
        except DefaultCredentialsError:
            logger.error(
                "No se encontraron credenciales de Google Cloud. "
                "Configura GOOGLE_APPLICATION_CREDENTIALS o usa gcloud auth."
            )
            raise
        except Exception as e:
            logger.error(f"Error al inicializar Google Cloud Storage: {str(e)}")
            raise
    
    def generate_signed_url(
        self, 
        blob_name: str, 
        expiration: int = 3600, 
        method: str = 'PUT',
        content_type: Optional[str] = None
    ) -> str:
        """
        Genera una URL firmada para subida/descarga directa.
        
        Args:
            blob_name: Nombre del blob en GCS
            expiration: Tiempo de expiración en segundos
            method: Método HTTP (PUT para subida, GET para descarga)
            content_type: Tipo MIME del archivo
            
        Returns:
            URL firmada
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Configurar headers si es necesario
            headers = {}
            if content_type and method == 'PUT':
                headers['Content-Type'] = content_type
            
            url = blob.generate_signed_url(
                version='v4',
                expiration=timedelta(seconds=expiration),
                method=method,
                headers=headers
            )
            
            logger.info(f"URL firmada generada para {blob_name} con método {method}")
            return url
            
        except Exception as e:
            logger.error(f"Error al generar URL firmada: {str(e)}")
            raise
    
    def upload_file(
        self, 
        file_obj: BinaryIO, 
        blob_name: str, 
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Sube un archivo a Google Cloud Storage.
        
        Args:
            file_obj: Objeto archivo a subir
            blob_name: Nombre del blob en GCS
            content_type: Tipo MIME del archivo
            metadata: Metadatos adicionales
            
        Returns:
            Información del archivo subido
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Calcular checksum antes de subir
            file_obj.seek(0)
            file_content = file_obj.read()
            file_obj.seek(0)
            
            checksum = hashlib.sha256(file_content).hexdigest()
            file_size = len(file_content)
            
            # Configurar tipo de contenido
            if not content_type:
                content_type = mimetypes.guess_type(blob_name)[0] or 'application/octet-stream'
            
            # Configurar metadatos
            blob_metadata = metadata or {}
            blob_metadata.update({
                'checksum': checksum,
                'uploaded_at': str(timezone.now()),
                'original_size': str(file_size)
            })
            
            blob.metadata = blob_metadata
            
            # Subir archivo
            blob.upload_from_file(
                file_obj,
                content_type=content_type,
                client=self.client
            )
            
            # Configurar permisos (privado por defecto)
            blob.make_private()
            
            logger.info(f"Archivo subido exitosamente: {blob_name}")
            
            return {
                'blob_name': blob_name,
                'size': file_size,
                'content_type': content_type,
                'checksum': checksum,
                'public_url': blob.public_url,
                'media_link': blob.media_link,
                'etag': blob.etag,
                'created_at': blob.time_created,
                'updated_at': blob.updated
            }
            
        except Exception as e:
            logger.error(f"Error al subir archivo: {str(e)}")
            raise
    
    def download_file(self, blob_name: str) -> bytes:
        """
        Descarga un archivo de Google Cloud Storage.
        
        Args:
            blob_name: Nombre del blob en GCS
            
        Returns:
            Contenido del archivo en bytes
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileNotFoundError(f"El archivo {blob_name} no existe")
            
            content = blob.download_as_bytes()
            logger.info(f"Archivo descargado: {blob_name}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error al descargar archivo: {str(e)}")
            raise
    
    def download_to_file(self, blob_name: str, destination_path: str) -> str:
        """
        Descarga un archivo a una ubicación local.
        
        Args:
            blob_name: Nombre del blob en GCS
            destination_path: Ruta de destino local
            
        Returns:
            Ruta del archivo descargado
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileNotFoundError(f"El archivo {blob_name} no existe")
            
            blob.download_to_filename(destination_path)
            logger.info(f"Archivo descargado a: {destination_path}")
            
            return destination_path
            
        except Exception as e:
            logger.error(f"Error al descargar archivo: {str(e)}")
            raise
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Elimina un archivo de Google Cloud Storage.
        
        Args:
            blob_name: Nombre del blob en GCS
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if blob.exists():
                blob.delete()
                logger.info(f"Archivo eliminado: {blob_name}")
                return True
            else:
                logger.warning(f"Archivo no encontrado para eliminar: {blob_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {str(e)}")
            raise
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Verifica si un archivo existe en GCS.
        
        Args:
            blob_name: Nombre del blob en GCS
            
        Returns:
            True si existe
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error al verificar archivo: {str(e)}")
            return False
    
    def get_file_metadata(self, blob_name: str) -> Dict[str, Any]:
        """
        Obtiene los metadatos de un archivo.
        
        Args:
            blob_name: Nombre del blob en GCS
            
        Returns:
            Metadatos del archivo
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileNotFoundError(f"El archivo {blob_name} no existe")
            
            # Recargar metadatos
            blob.reload()
            
            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'etag': blob.etag,
                'created_at': blob.time_created,
                'updated_at': blob.updated,
                'metadata': blob.metadata,
                'public_url': blob.public_url,
                'media_link': blob.media_link
            }
            
        except Exception as e:
            logger.error(f"Error al obtener metadatos: {str(e)}")
            raise
    
    def list_files(self, prefix: Optional[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Lista archivos en el bucket.
        
        Args:
            prefix: Prefijo para filtrar archivos
            max_results: Número máximo de resultados
            
        Returns:
            Lista de archivos con sus metadatos
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, max_results=max_results)
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created_at': blob.time_created,
                    'updated_at': blob.updated
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error al listar archivos: {str(e)}")
            raise


class LocalStorageService(StorageService):
    """
    Servicio de almacenamiento local para desarrollo.
    """
    
    def __init__(self):
        self.storage_root = os.path.join(settings.MEDIA_ROOT, 'local_storage')
        os.makedirs(self.storage_root, exist_ok=True)
        logger.info(f"Usando almacenamiento local en: {self.storage_root}")
    
    def _get_file_path(self, blob_name: str) -> str:
        """Obtiene la ruta completa del archivo."""
        # Asegurar que el directorio existe
        file_path = os.path.join(self.storage_root, blob_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path
    
    def generate_signed_url(
        self, 
        blob_name: str, 
        expiration: int = 3600, 
        method: str = 'PUT',
        content_type: Optional[str] = None
    ) -> str:
        """
        Genera una URL para el almacenamiento local.
        En desarrollo, simplemente devuelve una URL local.
        """
        # En desarrollo, usar una URL simple
        base_url = getattr(settings, 'MEDIA_URL', '/media/')
        return f"{base_url}local_storage/{blob_name}"
    
    def upload_file(
        self, 
        file_obj: BinaryIO, 
        blob_name: str, 
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Guarda un archivo en el sistema local.
        """
        try:
            file_path = self._get_file_path(blob_name)
            
            # Leer contenido
            file_obj.seek(0)
            content = file_obj.read()
            
            # Calcular checksum
            checksum = hashlib.sha256(content).hexdigest()
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Guardar metadatos
            metadata_path = f"{file_path}.meta"
            import json
            with open(metadata_path, 'w') as f:
                json.dump({
                    'content_type': content_type or 'application/octet-stream',
                    'checksum': checksum,
                    'size': len(content),
                    'metadata': metadata or {}
                }, f)
            
            logger.info(f"Archivo guardado localmente: {file_path}")
            
            return {
                'blob_name': blob_name,
                'size': len(content),
                'content_type': content_type,
                'checksum': checksum,
                'path': file_path
            }
            
        except Exception as e:
            logger.error(f"Error al guardar archivo: {str(e)}")
            raise
    
    def download_file(self, blob_name: str) -> bytes:
        """
        Lee un archivo del sistema local.
        """
        try:
            file_path = self._get_file_path(blob_name)
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"El archivo {blob_name} no existe")
            
            with open(file_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error al leer archivo: {str(e)}")
            raise
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Elimina un archivo del sistema local.
        """
        try:
            file_path = self._get_file_path(blob_name)
            metadata_path = f"{file_path}.meta"
            
            deleted = False
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted = True
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {str(e)}")
            raise
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Verifica si un archivo existe localmente.
        """
        file_path = self._get_file_path(blob_name)
        return os.path.exists(file_path)


def get_storage_service() -> StorageService:
    """
    Factory para obtener el servicio de almacenamiento apropiado.
    """
    use_gcs = getattr(settings, 'USE_GOOGLE_CLOUD_STORAGE', False)
    
    if use_gcs and GOOGLE_CLOUD_AVAILABLE:
        try:
            return GoogleCloudStorageService()
        except Exception as e:
            logger.warning(f"No se pudo inicializar GCS, usando almacenamiento local: {str(e)}")
            return LocalStorageService()
    else:
        return LocalStorageService()



