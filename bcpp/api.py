from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource, fields

from .models import SubjectConsent  # , SubjectVisit, SubjectReferral


class SubjectConsentResource(ModelResource):
    class Meta:
        queryset = SubjectConsent.objects.all()
        resource_name = 'subject_consent'
        fields = ['subject_identifier',
                  'identity',
                  'dob',
                  'gender',
                  'citizen',
                  'consent_datetime']
        allowed_methods = ['get']
        filtering = {
            'identity': ['exact'],
            'subject_identifier': ['exact', 'contains'],
        }
        authorization = ReadOnlyAuthorization()
        authentication = Authentication()


# class SubjectVisitResource(ModelResource):
# 
#     class Meta:
#         queryset = SubjectVisit.objects.all()
#         resource_name = 'subject_visit'
#         allowed_methods = ['get']
#         authorization = ReadOnlyAuthorization()
#         authentication = Authentication()
# 
# 
# class SubjectReferralResource(ModelResource):
# 
#     subject_visit = fields.ToManyField(
#         SubjectVisitResource, 'subject_visit')
# 
#     class Meta:
#         queryset = SubjectReferral.objects.all()
#         resource_name = 'subject_referral'
#         fields = ['subject_identifier',
#                   'subject_referred',
#                   'referral_code',
#                   'referral_appt_date',
#                   'referral_clinic',
#                   'hiv_result',
#                   'new_pos',
#                   'on_art',
#                   'vl_sample_drawn',
#                   'vl_sample_drawn_datetime',
#                   # 'subject_visit'
#                   ]
#         allowed_methods = ['get']
#         filtering = {
#             'subject_identifier': ['exact', 'contains'],
#         }
#         authorization = ReadOnlyAuthorization()
#         authentication = Authentication()
