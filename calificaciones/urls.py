from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
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
    
    # Nuevo: Registro de Usuario
    path('registro/', views.registro, name='registro_usuario'),
]
