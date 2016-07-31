select idno as identity256, idtype as identity_type, regdate as pims_registration_date,
initiationdatekey as pims_art_initiation_date, p.pimsclinicname, artcurrentpatientprogramstatusdescr
from dw.factpimshaartinitiation i
join dw.dimpimspatient p on i.dimpimspatientkey = p.dimpimspatientkey
where i.iscurrent=True