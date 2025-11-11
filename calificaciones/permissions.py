"""
Sistema de permisos basado en roles
"""
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def tiene_rol(usuario, nombre_rol):
    """Verifica si un usuario tiene un rol específico"""
    try:
        return usuario.perfilusuario.rol.nombre_rol == nombre_rol
    except:
        return False


def es_administrador(usuario):
    """Verifica si el usuario es administrador"""
    return usuario.is_superuser or tiene_rol(usuario, 'Administrador')


def es_analista(usuario):
    """Verifica si el usuario es analista"""
    return tiene_rol(usuario, 'Analista Financiero')


def es_auditor(usuario):
    """Verifica si el usuario es auditor"""
    return tiene_rol(usuario, 'Auditor')


def puede_crear_calificaciones(usuario):
    """Puede crear/editar calificaciones: Administrador o Analista"""
    return es_administrador(usuario) or es_analista(usuario)


def puede_eliminar_calificaciones(usuario):
    """Puede eliminar calificaciones: Solo Administrador"""
    return es_administrador(usuario)


def puede_ver_logs(usuario):
    """Puede ver logs: Administrador o Auditor"""
    return es_administrador(usuario) or es_auditor(usuario)


# Decoradores personalizados
def requiere_administrador(function):
    """Decorador que requiere rol de Administrador"""
    def check_admin(user):
        if not user.is_authenticated:
            return False
        if es_administrador(user):
            return True
        return False
    
    actual_decorator = user_passes_test(
        check_admin,
        login_url='/login/',
        redirect_field_name='next'
    )
    return actual_decorator(function)


def requiere_analista_o_admin(function):
    """Decorador que requiere rol de Analista o Administrador"""
    def check_analista_admin(user):
        if not user.is_authenticated:
            return False
        return puede_crear_calificaciones(user)
    
    actual_decorator = user_passes_test(
        check_analista_admin,
        login_url='/login/',
        redirect_field_name='next'
    )
    return actual_decorator(function)


def requiere_permiso_lectura(function):
    """Decorador básico - todos los usuarios autenticados pueden leer"""
    def check_authenticated(user):
        return user.is_authenticated
    
    actual_decorator = user_passes_test(
        check_authenticated,
        login_url='/login/',
        redirect_field_name='next'
    )
    return actual_decorator(function)
