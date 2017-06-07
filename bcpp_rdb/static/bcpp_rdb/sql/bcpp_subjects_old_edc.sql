select consent.subject_identifier, consent.consent_datetime, consent.gender, consent.identity, consent.dob,
       consent.version, sv.survey_slug
from bcpp_subject_subjectconsent as consent
left join bcpp_household_member_householdmember as hm on hm.id=consent.household_member_id
left join bcpp_household_householdstructure as hs on hs.id=hm.household_structure_id
left join bcpp_survey_survey as sv on sv.id=hs.survey_id
left join bcpp_household_household as hh on hh.id=hs.household_id
left join bcpp_household_plot as p on p.id=hh.plot_id
