from django.urls import path
from . import views
from . import views_factores
from . import views_admin

urlpatterns = [
    # Home
    path('', views_factores.home, name='home'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Calificaciones Tributarias
    path('calificaciones/', views.listar_calificaciones, name='listar_calificaciones'),
    path('calificaciones/crear/', views.crear_calificacion, name='crear_calificacion'),
    path('calificaciones/editar/<int:pk>/', views.editar_calificacion, name='editar_calificacion'),
    path('calificaciones/eliminar/<int:pk>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    
    # Instrumentos Financieros
    path('instrumentos/', views.listar_instrumentos, name='listar_instrumentos'),
    path('instrumentos/crear/', views.crear_instrumento, name='crear_instrumento'),
    path('instrumentos/editar/<int:pk>/', views.editar_instrumento, name='editar_instrumento'),
    path('instrumentos/eliminar/<int:pk>/', views.eliminar_instrumento, name='eliminar_instrumento'),
    
    # Carga Masiva
    path('carga-masiva/', views.carga_masiva, name='carga_masiva'),
    
    # Exportación
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/csv/', views.exportar_csv, name='exportar_csv'),
    
    # Perfil de Usuario
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    
    # Auditoría
    path('auditoria/', views.registro_auditoria, name='registro_auditoria'),
    
    # Registro de Usuario
    path('registro/', views.registro, name='registro_usuario'),
    
    # Gestión de Usuarios
    path('gestion/usuarios/', views_admin.admin_gestionar_usuarios, name='admin_gestionar_usuarios'),
    path('gestion/usuarios/desbloquear/<int:user_id>/', views_admin.desbloquear_cuenta_manual, name='desbloquear_cuenta'),
    path('gestion/usuarios/historial/<int:user_id>/', views_admin.ver_historial_login_usuario, name='ver_historial_login'),
    
    # Factores - Formulario Simplificado
    path('calificaciones/factores/crear/', views_factores.crear_calificacion_factores, name='crear_calificacion_factores'),
    path('calificaciones/factores/editar/<int:pk>/', views_factores.editar_calificacion_factores, name='editar_calificacion_factores'),
    
    # API
    path('api/calcular-factores/', views_factores.calcular_factores_ajax, name='calcular_factores_ajax'),
]
