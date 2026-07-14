from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
import datetime


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for Docker containers.
    Returns service status and dependencies health.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'Ks Financial App Backend',
        'version': '1.0.0',
        'dependencies': {}
    }
    
    # Check database connection
    try:
        connection.ensure_connection()
        health_status['dependencies']['database'] = {
            'status': 'healthy',
            'backend': connection.settings_dict['ENGINE']
        }
    except Exception as e:
        health_status['dependencies']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Check cache (if configured)
    try:
        cache.get('health_check')
        health_status['dependencies']['cache'] = {
            'status': 'healthy'
        }
    except Exception as e:
        health_status['dependencies']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes/Docker.
    Checks if the service is ready to accept traffic.
    """
    is_ready = True
    reasons = []
    
    # Check database
    try:
        connection.ensure_connection()
    except Exception as e:
        is_ready = False
        reasons.append(f'Database not ready: {str(e)}')
    
    if is_ready:
        return Response({
            'status': 'ready',
            'timestamp': datetime.datetime.now().isoformat()
        })
    else:
        return Response({
            'status': 'not_ready',
            'reasons': reasons,
            'timestamp': datetime.datetime.now().isoformat()
        }, status=503)
