

class EdcRdbRouter(object):

    bcpp = ['bcpp_subject', 'bcpp_household', 'bcpp_household_member', 'bcpp_survey']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in ['rdb']:
            return 'ResearchDB'
        elif model._meta.app_label in self.bcpp:
            return 'bhp066'
        else:
            print(model._meta.app_label)
            pass
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['rdb']:
            return False
        elif model._meta.app_label in self.bcpp:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ['bcpp_rdb', 'auth', 'moh']:
            return True
        return False
