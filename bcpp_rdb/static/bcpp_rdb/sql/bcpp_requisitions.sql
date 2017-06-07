select v.subject_identifier, requisition_identifier, requisition_datetime, drawn_datetime,
req.panel_name, specimen_type, primary_aliquot_identifier, identifier_prefix, a.visit_code, hm.survey_schedule, is_drawn, reason_not_drawn, received,received_datetime,
study_site_name, packed, packed_datetime, shipped, shipped_datetime
from bcpp_subject_subjectrequisition as req
left join bcpp_subject_subjectvisit as v on v.id=req.subject_visit_id
left join member_householdmember as hm on hm.id=v.household_member_id
left join household_householdstructure as hs on hs.id=hm.household_structure_id
left join bcpp_subject_appointment as a on a.id=v.appointment_id
