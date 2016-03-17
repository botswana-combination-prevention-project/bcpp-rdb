from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ValidationError
from datatableview.forms import XEditableUpdateForm


class UploadFileForm(forms.Form):

    csv_file = forms.FileField(
        label='Select a csv file to upload')

    source = forms.CharField(
        label='Provide a short name to describe the source of data',
        max_length=10,
        help_text='for example, IPMS, PIMS')

    identity_field = forms.CharField(
        label='Provide the name of the identity column',
        help_text='for example, omang, IDNo, ...')

    description = forms.CharField(
        label='Provide a short description of the contents')

    hash_identity = forms.BooleanField(
        label='Hash identity field on import.',
        initial=True,
        help_text='Untick if identity field is already hashed.')

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_enctype = "multipart/form-data"
        self.helper.add_input(Submit('submit', 'Submit'))


class XEditableUpdateCommunityForm(XEditableUpdateForm):

    def clean_value(self):
        value = self.cleaned_data['value']
        if value not in ['ranaka', 'otse']:
            raise ValidationError('Invalid community name')
        return value
