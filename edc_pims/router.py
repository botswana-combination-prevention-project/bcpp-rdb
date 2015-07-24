

class EdcPimsRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'rdb':
            return 'ResearchDB'
#         if model._meta.app_label == 'rdb':
#             return 'bhp066_master'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'rdb':
            return False
#         elif model._meta.app_label == 'edc':
#             return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'rdb':
            return False
        return None
