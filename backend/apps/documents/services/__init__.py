"""
Servicios para la app de documentos
"""

from .storage_service import get_gcs_service, GoogleCloudStorageService

__all__ = ['get_gcs_service', 'GoogleCloudStorageService']
