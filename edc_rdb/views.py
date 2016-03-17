from datatableview import helpers
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from edc_bootstrap.views import EdcEditableDatatableView, EdcContextMixin, EdcDatatableView

from .forms import UploadFileForm, XEditableUpdateCommunityForm
from .models import ImportHistory, BhsSubject
from .upload_file import Upload
from braces.views import LoginRequiredMixin
from datatableview.datatables import Datatable
from datatableview.columns import DateTimeColumn, TextColumn
from datatableview.views.base import DatatableView
from edc_bootstrap.datatables.columns import MyBooleanColumn


class BhsSubjectDatabable(Datatable):

#     subject = TextColumn(
#         "Subject",
#         sources=['identifier'],
#         processor=helpers.link_to_model)

    registration_datetime = DateTimeColumn(
        'Registered',
        sources=['registration_datetime'],
        processor=helpers.format_date("%Y-%m-%d", localize=True))

    updated = DateTimeColumn(
        'Last Updated',
        sources=['updated'],
        processor=helpers.format_date("%Y-%m-%d", localize=True))

    created = DateTimeColumn(
        "Created",
        sources=['created'],
        processor=helpers.format_date("%Y-%m-%d", localize=True))

    referred = MyBooleanColumn(
        'Referred',
        sources=['referred'])

    referral_new_pos = MyBooleanColumn(
        'New POS',
        sources=['referral_new_pos'],
        processor=helpers.make_boolean_checkmark)

    referral_on_art = MyBooleanColumn(
        'On ART',
        sources=['referral_on_art'],
        processor=helpers.make_boolean_checkmark)

    referral_vl_drawn = MyBooleanColumn(
        'VL',
        sources=['referral_vl_drawn'],
        processor=helpers.make_boolean_checkmark)

    citizen = MyBooleanColumn(
        'Citizen',
        sources=['citizen'],
        processor=helpers.make_boolean_checkmark)

#     community = TextColumn(
#         'Community',
#         sources=['community_name'],
#         processor=helpers.make_xeditable(placeholder="Community Name"))

    class Meta:
        structure_template = "edc_bootstrap/bootstrap_structure.html"
        columns = ['identifier', 'registration_datetime', ]
        ordering = ['identifier']
        # hidden_columns = ['id', 'omang', 'omang_hash', 'hiv_status', 'referred']


class BhsSubjectView(LoginRequiredMixin, EdcContextMixin, EdcEditableDatatableView):
    model = BhsSubject
    xeditable_form_class = XEditableUpdateCommunityForm
    datatable_class = BhsSubjectDatabable


class ImportHistoryDatatable(Datatable):

    created = DateTimeColumn(
        "Created",
        sources=['created'],
        processor=helpers.format_date("%Y-%m-%d", localize=True))

    class Meta:
        structure_template = "edc_bootstrap/bootstrap_structure.html"
        hidden_columns = ['session', 'file_format']


class ImportHistoryDatatableView(LoginRequiredMixin, EdcContextMixin, EdcDatatableView):

    model = ImportHistory
    ordering = ['-created']
    datatable_class = ImportHistoryDatatable


class UploadView(LoginRequiredMixin, EdcContextMixin, FormView):

    form_class = UploadFileForm
    template_name = 'upload_file.html'
    success_url = '/upload/'
    upload_status = None
    page_title = 'Upload Patient Data'

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context['upload_history'] = ImportHistory.objects.filter(
            user=self.request.user).order_by('-created')[0:25]
        datatable = ImportHistoryDatatableView().get_datatable(url=reverse('import_history'))
        context['datatable'] = datatable
        context['page_title'] = self.page_title
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        upload_file = Upload(
            self.request.FILES['csv_file'],
            identity_field=form.cleaned_data['identity_field'],
            filename=form.cleaned_data['csv_file'].name,
            user=self.request.user,
            source=form.cleaned_data['source'],
            description=form.cleaned_data['description'],
        )
        context['session'] = upload_file.import_history.pk
        context['records'] = upload_file.import_history.records
        print(upload_file.import_history.__dict__)
        print(upload_file.import_history.status)
        if upload_file.import_history.status == 'success':
            context['success'] = upload_file.import_history.status
        else:
            context['failed'] = upload_file.import_history.message
            context['header_fields'] = upload_file.import_history.file_format.header
        return self.render_to_response(context)
