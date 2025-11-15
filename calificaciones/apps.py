from django.apps import AppConfig


class CalificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calificaciones'
    verbose_name = 'CALIFICACIONES'  # Se agregó para personalizar el nombre en el admin
    
    def ready(self):
        """Importa signals cuando la app está lista"""
        import calificaciones.signals
