"""
Middleware para gestión de contexto de auditoría.

Este middleware captura el request actual y lo almacena en thread-local storage,
permitiendo que los signals accedan a la información del usuario e IP sin 
necesidad de inspección de frames (que es frágil y puede fallar).

Diseño:
- Almacena request.user e IP en threading.local()
- Los signals consultan este contexto antes de crear logs
- Si hay contexto de request, los signals NO crean logs (la vista lo hará)
- Garantiza atribución singular con IP correcta
"""

import threading
from django.utils.deprecation import MiddlewareMixin


# Thread-local storage para el contexto de auditoría actual
_contexto_auditoria_thread_local = threading.local()


class ContextoAuditoriaMiddleware(MiddlewareMixin):
    """
    Middleware que captura y almacena el contexto del request actual
    en thread-local storage para uso en signals de auditoría.
    
    Debe ubicarse después de AuthenticationMiddleware en MIDDLEWARE.
    """
    
    def process_request(self, request):
        """
        Captura el request actual al inicio de cada petición.
        
        Args:
            request: HttpRequest con usuario autenticado
        """
        # Almacenar el request completo en thread-local
        _contexto_auditoria_thread_local.request = request
        return None
    
    def process_response(self, request, response):
        """
        Limpia el contexto al finalizar la petición para evitar memory leaks.
        
        Args:
            request: HttpRequest original
            response: HttpResponse generado
            
        Returns:
            HttpResponse sin modificar
        """
        # Limpiar el contexto thread-local
        if hasattr(_contexto_auditoria_thread_local, 'request'):
            del _contexto_auditoria_thread_local.request
        return response
    
    def process_exception(self, request, exception):
        """
        Limpia el contexto incluso si hay una excepción.
        
        Args:
            request: HttpRequest original
            exception: Excepción capturada
        """
        # Limpiar el contexto thread-local en caso de error
        if hasattr(_contexto_auditoria_thread_local, 'request'):
            del _contexto_auditoria_thread_local.request
        return None


def obtener_contexto_auditoria():
    """
    Obtiene el contexto de auditoría actual desde thread-local storage.
    
    Returns:
        dict: Diccionario con 'usuario' e 'ip_address' si hay request activo,
              None si no hay contexto (operación del sistema)
    
    Ejemplo de uso en signals:
        contexto = obtener_contexto_auditoria()
        if contexto:
            # Hay un request de usuario activo, skip (la vista registrará)
            return
        # No hay request, es operación del sistema, registrar
    """
    request = getattr(_contexto_auditoria_thread_local, 'request', None)
    
    if request is None:
        return None
    
    # Extraer IP del request
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR', None)
    
    return {
        'usuario': getattr(request, 'user', None),
        'ip_address': ip_address,
        'request': request  # Por si se necesita más contexto
    }


def hay_contexto_usuario():
    """
    Verifica si existe un contexto de usuario activo (request web).
    
    Returns:
        bool: True si hay un request activo (operación de usuario),
              False si no hay request (operación del sistema)
    
    Uso típico en signals:
        if hay_contexto_usuario():
            return  # Skip, la vista registrará
    """
    return hasattr(_contexto_auditoria_thread_local, 'request')
