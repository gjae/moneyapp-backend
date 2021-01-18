from django.apps import AppConfig


class MovementsConfig(AppConfig):
    name = 'movements'
    verbose_name = 'Movimientos'

    def ready(self):
        import movements.signals