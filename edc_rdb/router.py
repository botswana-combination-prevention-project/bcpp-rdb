

class EdcRdbRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'rdb':
            return 'ResearchDB'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'rdb':
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ['edc_rdb', 'auth']:
            return True
        return False
