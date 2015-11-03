from .models import SubjectReferral


class Summary:

    def __init__(self):
        self.report = {}
        self.communities = [
            'bokaa', 'digawana', 'lentsweletau', 'lerala', 'letlhakeng',
            'maunatlala', 'mmankgodi', 'mmathethe', 'molapowabojang',
            'oodi', 'otse', 'ramokgonami', 'ranaka', 'sefophe', 'shoshong',
            'test_community', 'mmadinare', 'metsimotlhabe', 'tati_siding',
            'nkange', 'sebina', 'mathangwane', 'mmandunyane', 'rakops',
            'tsetsebjwe', 'gweta', 'gumare', 'shakawe', 'masunga', 'nata',
            'sefhare']

    def summarize(self):
        self.report = {}
        for community in self.communities:
            self.report.update({community: [
                SubjectReferral.objects.filter(
                    referral_clinic=community,
                    cd4_result__lte=350).count(),
                SubjectReferral.objects.filter(
                    referral_clinic=community,
                    cd4_result__gt=350).count(),
                SubjectReferral.objects.filter(
                    referral_clinic=community,
                    cd4_result__gt=350,
                    cd4_result__lte=500).count()]
            })
