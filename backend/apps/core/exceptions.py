"""
Custom exception handler for DRF.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied, NotFound
from django.http import Http404
import logging

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF.
    """
    # Call REST framework's exception handler first
    response = exception_handler(exc, context)

    # If response is None, it's an unhandled exception
    if response is None:
        if isinstance(exc, Http404):
            exc = NotFound(detail='Объект не найден')
        elif isinstance(exc, PermissionDenied):
            exc = PermissionDenied(detail='Доступ запрещён')
        
        response = exception_handler(exc, context)

    # Add custom error handling
    if response is not None:
        # Log the error
        logger.error(f'API Error: {response.status_code} - {response.data}')
        
        # Customize error response format
        if hasattr(response, 'data'):
            if isinstance(response.data, dict):
                # Keep DRF's default error format but add status
                response.data['status_code'] = response.status_code
    
    return response
