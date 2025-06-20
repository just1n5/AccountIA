from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
import json

# TODO: Implementar Firebase Admin SDK para validación de tokens
# Por ahora, endpoint básico para testing

@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_auth(request):
    """
    Endpoint para autenticación con Firebase
    Recibe el token de Firebase y devuelve JWT para el backend
    """
    try:
        data = json.loads(request.body)
        firebase_token = data.get('firebase_token')
        
        if not firebase_token:
            return Response(
                {'error': 'Firebase token requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Validar token con Firebase Admin SDK
        # Por ahora, respuesta de prueba
        
        # Crear o obtener usuario (placeholder)
        user_data = {
            'uid': 'test-user-123',
            'email': 'test@example.com',
            'displayName': 'Usuario de Prueba'
        }
        
        return Response({
            'success': True,
            'user': user_data,
            'message': 'Autenticación exitosa (modo prueba)'
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'JSON inválido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def health_check(request):
    """
    Endpoint de verificación de salud para el servicio de autenticación
    """
    return Response({
        'status': 'healthy',
        'service': 'authentication',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
