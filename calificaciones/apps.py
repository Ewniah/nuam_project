from django.apps import AppConfig


class CalificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calificaciones'

    def ready(self):
        """Importa signals cuando la app esté lista"""
        import calificaciones.signals
