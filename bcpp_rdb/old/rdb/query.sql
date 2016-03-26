select regdatekey, pims_patient.* 
from dw.factPIMSARTPatientRegistration pims_art 
left join dw.dimcurrentpimspatient pims_patient
on pims_art.dimcommonstudyparticipantkey=pims_patient.dimcommonstudyparticipantkey
where pimsclinicname='Otse' LIMIT 25


idno, idtype, regfacilitycode, regdate, patregno
dimcurrentpimspatientkey  sourcesystempatientid