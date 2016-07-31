from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'bcpp_rdb'
    institution = 'Botswana-Harvard AIDS Institute'
    verbose_name = 'BCPP Research Database (CDC)'
