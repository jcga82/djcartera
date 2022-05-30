from django.apps import AppConfig
# from suit.apps import DjangoSuitConfig

# class SuitConfig(DjangoSuitConfig):
#     layout = 'horizontal'

class MicarteraConfig(AppConfig):
    name = 'micartera'
    verbose_name = "Mis rentas pasivas"

    def ready(self):
        pass
