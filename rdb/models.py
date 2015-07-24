from django.db import models


class StudyParticipant(models.Model):

    study_participant = models.IntegerField(
        primary_key=True,
        db_column='dimcommonstudyparticipantkey'
    )

    omang_hash = models.CharField(
        max_length=36,
        null=True,
        db_column='omangnumber')

    bhs_identifier = models.CharField(
        max_length=25,
        db_column='bhssubjectid')

    htc_identifier = models.CharField(
        max_length=25,
        db_column='htcid')

    def __str__(self):
        return '({})'.format(', '.join((self.bhs_identifier, self.htc_identifier, str(self.study_participant))))

    class Meta:
        app_label = 'rdb'
        db_table = 'dimcommonstudyparticipant'


class BhsParticipant(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='export_uuid')

    study_participant = models.ForeignKey(
        to=StudyParticipant,
        to_field='study_participant',
        db_column='dimcommonstudyparticipantkey'
    )

    bhs_identifier = models.CharField(
        max_length=25,
        db_column='subject_identifier')

    omang_hash = models.CharField(
        max_length=36,
        null=True,
        db_column='omang')

    def __str__(self):
        return self.bhs_identifier

    class Meta:
        app_label = 'rdb'
        db_table = 'bhssubject_temp'


class HtcParticipant(models.Model):

    study_participant = models.IntegerField(
        primary_key=True,
        db_column='dimcurrentstudyparticipantkey')

    htc_identifier = models.CharField(
        max_length=25,
        db_column='htcid')

    omang_hash = models.CharField(
        max_length=36,
        null=True,
        db_column='omangnumber')

    age = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        db_column='rdbcalculatedage')

    gender = models.CharField(
        max_length=15,
        null=True)

    def __str__(self):
        return self.htc_identifier

    class Meta:
        app_label = 'rdb'
        db_table = 'dimcurrentstudyparticipant'


class PimsPatient(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='dimpimspatientkey')

    omang_hash = models.CharField(
        max_length=36,
        db_column='idno')

    gender = models.CharField(
        max_length=3,
        null=True)

    dob = models.DateTimeField(
        null=True)

    clinic_name = models.CharField(
        max_length=25,
        null=True,
        db_column='pimsclinicname',
    )

    citizenship = models.CharField(
        max_length=25,
        null=True,
    )

    clinical_stage_id = models.IntegerField(
        null=True,
        db_column='currentclinicalstageid'
    )

    registration_id = models.IntegerField(
        null=True,
        db_column='latestregistrationid'
    )

    regimen_id = models.IntegerField(
        null=True,
        db_column='currentregimenid'
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        app_label = 'rdb'
        db_table = 'dimpimspatient'


class PimsHaartRegimen(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='dimpimshaartinitiationkey')

    regimen_line = models.CharField(
        max_length=25,
        null=True,
        db_column='regimenline')

    regimen = models.CharField(
        max_length=100,
        null=True,
        db_column='regimen')

    program = models.CharField(
        max_length=25,
        null=True,
        db_column='txprogram')

    def __str__(self):
        return '{} ({})'.format(self.regimen, self.regimen_line)

    class Meta:
        app_label = 'rdb'
        db_table = 'dimpimshaartinitiation'


class PimsHaartInitiation(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='factpimshaartinitiationkey')

    study_participant = models.ForeignKey(
        to=StudyParticipant,
        to_field='study_participant',
        db_column='dimcommonstudyparticipantkey'
    )

    haart_regimen = models.ForeignKey(
        to=PimsHaartRegimen,
        to_field='id',
        db_column='dimpimshaartinitiationkey',
    )

    pims_patient = models.ForeignKey(
        to=PimsPatient,
        to_field='id',
        db_column='dimpimspatientkey')

    clinic_name = models.CharField(
        max_length=25,
        null=True,
        db_column='pimsclinicname')

    baseline_cd4 = models.IntegerField(
        null=True,
        db_column='baselinecd4count')

    class Meta:
        app_label = 'rdb'
        db_table = 'factpimshaartinitiation'


class PimsHaartRegistration(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='factpimsartpatientregistrationkey')

    study_participant = models.IntegerField(
        null=True,
        db_column='dimcommonstudyparticipantkey'
    )

    pims_patient = models.ForeignKey(
        to=PimsPatient,
        to_field='id',
        db_column='dimpimspatientkey')

    registration_date = models.DateField(
        null=True,
        db_column='regdatekey')

    sourcesystempatientregistrationid = models.IntegerField(blank=True, null=True)
    dimclinickey = models.BigIntegerField(blank=True, null=True)

    class Meta:
        app_label = 'rdb'
        db_table = 'factpimsartpatientregistration'
        unique_together = (('dimclinickey', 'sourcesystempatientregistrationid'),)