import csv
import hashlib
import json

from io import TextIOWrapper

from .models import FileFormat, ImportedData
from uuid import uuid4
from edc_rdb.models import ImportHistory


class Upload:

    def __init__(self, file_object, **kwargs):
        self.file_object = file_object
        self.filename = kwargs.get('filename')
        self.encoding = kwargs.get('encoding')
        self.identity_field = kwargs.get('identity_field')
        self.user = kwargs.get('user')
        self.source = kwargs.get('source')
        self.import_history = ImportHistory.objects.create(
            session=uuid4(),
            filename=kwargs.get('filename'),
            user=kwargs.get('user').username,
            source=kwargs.get('source'),
            description=kwargs.get('description'),
            status='failed')
        self.load_to_model(**kwargs)

    def load_to_model(self, **kwargs):
        header = None
        file_object = TextIOWrapper(self.file_object.file, encoding=kwargs.get('encoding') or 'utf-8')
        reader = csv.reader(file_object)
        if not header:
            header = next(reader)
            try:
                file_format = FileFormat.objects.get(
                    header=', '.join(header), identity_field=kwargs.get('identity_field'))
            except FileFormat.DoesNotExist:
                file_format = FileFormat.objects.create(
                    header=', '.join(header),
                    identity_field=kwargs.get('identity_field'),
                    description=kwargs.get('source'))
        try:
            for row in reader:
                obj = dict(zip(header, row))
                omang = obj[file_format.identity_field]
                ImportedData.objects.create(
                    file_format=file_format,
                    omang_hash=self.hash_value(omang),
                    json=json.dumps(obj),
                    import_history=self.import_history,
                    source=kwargs.get('source'))
            self.import_history.records = ImportedData.objects.filter(import_history=self.import_history).count()
            self.import_history.file_format = file_format
            self.import_history.status = 'success'
        except KeyError as e:
            if file_format.identity_field not in str(e):
                raise KeyError(e)
            self.import_history.message = 'Invalid column name \'{}\''.format(file_format.identity_field)
            self.import_history.file_format = file_format
            self.import_history.records = 0
        self.import_history.save()
        return self.import_history

    def hash_value(self, value):
        return str(hashlib.sha256(value.encode()).hexdigest())
