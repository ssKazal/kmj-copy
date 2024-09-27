from django.apps import AppConfig


class SkilledWorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "skilled_worker"
    verbose_name = "Skilled Worker"

    def ready(self):
        import skilled_worker.signals
