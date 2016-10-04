from django.apps import AppConfig as DjangoAppConfig


from edc_base.apps import AppConfig as EdcBaseAppConfigParent


class EdcBaseAppConfig(EdcBaseAppConfigParent):
    institution = 'Botswana-Harvard AIDS Institute'
    project_name = 'BCPP Research Database (CDC)'


class AppConfig(DjangoAppConfig):
    name = 'bcpp_rdb'
