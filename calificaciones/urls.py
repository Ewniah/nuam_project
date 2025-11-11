"""
URLs del módulo de calificaciones
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Calificaciones CRUD
    path('calificaciones/', views.listar_calificaciones, name='listar_calificaciones'),
    path('calificaciones/crear/', views.crear_calificacion, name='crear_calificacion'),
    path('calificaciones/editar/<int:pk>/', views.editar_calificacion, name='editar_calificacion'),
    path('calificaciones/eliminar/<int:pk>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    
    # Instrumentos CRUD
    path('instrumentos/', views.listar_instrumentos, name='listar_instrumentos'),
    path('instrumentos/crear/', views.crear_instrumento, name='crear_instrumento'),
    path('instrumentos/editar/<int:pk>/', views.editar_instrumento, name='editar_instrumento'),
    
    # Carga masiva
    path('carga-masiva/', views.carga_masiva, name='carga_masiva'),
    
    # Exportación de reportes
    path('calificaciones/exportar/excel/', views.exportar_calificaciones_excel, name='exportar_excel'),
    path('calificaciones/exportar/csv/', views.exportar_calificaciones_csv, name='exportar_csv'),

    # Perfil de usuario
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),

]
