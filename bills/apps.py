from django.apps import AppConfig


class BillsConfig(AppConfig):
    name = 'bills'
    verbose_name = 'Facturas'

    def ready(self):
        import bills.signals
