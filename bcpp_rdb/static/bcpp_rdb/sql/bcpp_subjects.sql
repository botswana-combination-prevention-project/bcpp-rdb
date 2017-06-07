select consent.subject_identifier, consent.consent_datetime, consent.gender, consent.identity, consent.dob,
       consent.version, hm.survey_schedule
from bcpp_subject_subjectconsent as consent
left join member_householdmember as hm on hm.id=consent.household_member_id
left join household_householdstructure as hs on hs.id=hm.household_structure_id
left join household_household as hh on hh.id=hs.household_id
left join plot_plot as p on p.id=hh.plot_id
