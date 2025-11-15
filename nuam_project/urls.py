from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from calificaciones import views as calificaciones_views

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Actualizado URLs de autenticación con login y logout para auditoría
    path('login/', calificaciones_views.login_view, name='login'),
    path('logout/', calificaciones_views.logout_view, name='logout'),
    
    # URLs de la aplicación calificaciones
    path('', include('calificaciones.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
