SELECT x.dimstudyparticipantkey,
    x.prior_hiv_test_result,
    x.self_report_hiv_test_result,
    x.hiv_test_result,
    x.citizen_ind,
    x.community_name,
    x.has_omang,
    x.omang_nbr,
    x.gender,
    x.perm_resident,
    x.parttime_resident,
    x.interview_date,
    a.rdbcalculatedage::integer AS rdbcalculatedage
   FROM crosstab('
select dimstudyparticipantkey,formcode,coalesce(responsetext,htcintakeformresponse) as response
from dw.facthtcintakeform a
left outer join dw.dimhtcformresponse b on
        a.dimhtcformquestionkey = b.dimhtcformquestionkey and
        a.htcintakeformresponse = responsecode
where formcode in
(
''Q29B'',
''99'',
''Q31'',
''Q11'',
''Q1'',
''Q11A'',
''Q11B'',
''Q14'',
''Q10'',
''Q10A'',
''INTERVIEW_DATE''
)
and iscurrent = true
and importfilename||tabletid in (
select importfilename||tabletid from dw.facthtcintakeform a
inner join dw.dimhtcformquestion c on
        a.dimhtcformquestionkey = c.dimhtcformquestionkey
where ((formcode = ''Q31'' and htcintakeformresponse = ''1'')
or (formcode = ''Q29B'' and htcintakeformresponse = ''1''))
and formversion in
(
 ''IndividualIntakeFormEngV8'',
 ''IndividualIntakeFormEngV8.1'',
 ''IndividualIntakeFormEngV9''
)
and iscurrent = true
) order by 1,2
'::text, 'values
(''Q29B''::text),
(''99''::text),
(''Q31''::text),
(''Q11''::text),
(''Q1''::text),
(''Q11A''::text),
(''Q11B''::text),
(''Q14''::text),
(''Q10''::text),
(''Q10A''::text),
(''INTERVIEW_DATE'')'::text) x(dimstudyparticipantkey integer, prior_hiv_test_result text, self_report_hiv_test_result text, hiv_test_result text, citizen_ind text, community_name text, has_omang text, omang_nbr text, gender text, perm_resident text, parttime_resident text, interview_date text)
     JOIN dw.dimstudyparticipant a ON x.dimstudyparticipantkey = a.dimstudyparticipantkey
UNION ALL
 SELECT x.dimstudyparticipantkey,
    x.prior_hiv_test_result,
    x.self_report_hiv_test_result,
    x.hiv_test_result,
    x.citizen_ind,
    x.community_name,
    x.has_omang,
    x.omang_nbr,
    x.gender,
    x.perm_resident,
    x.parttime_resident,
    x.interview_date,
    a.rdbcalculatedage::integer AS rdbcalculatedage
   FROM crosstab('
select dimstudyparticipantkey,formcode,coalesce(responsetext,htcintakeformresponse) as response
from dw.facthtcintakeform a
left outer join dw.dimhtcformresponse b on
        a.dimhtcformquestionkey = b.dimhtcformquestionkey and
        a.htcintakeformresponse = responsecode
where formcode in
(
''Q29B'',
''Q29C'',
''Q30I'',
''Q11'',
''Q1'',
''Q11A'',
''Q11B'',
''Q14'',
''Q10'',
''Q10A'',
''INTERVIEW_DATE''
)
and iscurrent = true
and importfilename||tabletid in (
select importfilename||tabletid from dw.facthtcintakeform a
inner join dw.dimhtcformquestion c on
        a.dimhtcformquestionkey = c.dimhtcformquestionkey
where ((formcode = ''Q30I'' and htcintakeformresponse = ''1'')
or (formcode = ''Q29B'' and htcintakeformresponse = ''1'')
or (formcode = ''Q29C'' and htcintakeformresponse = ''1''))
and formversion in
(
''IndividualIntakeFormEngV10'',
''IndividualIntakeFormEngV11'',
''IndividualIntakeFormEngV12'',
''IndividualIntakeFormEngV13''
)

and iscurrent = true
) order by 1,2
'::text, 'values
(''Q29B''::text),
(''Q29C''::text),
(''Q30I''::text),
(''Q11''::text),
(''Q1''::text),
(''Q11A''::text),
(''Q11B''::text),
(''Q14''::text),
(''Q10''::text),
(''Q10A''::text),
(''INTERVIEW_DATE'')'::text) x(dimstudyparticipantkey integer, prior_hiv_test_result text, self_report_hiv_test_result text, hiv_test_result text, citizen_ind text, community_name text, has_omang text, omang_nbr text, gender text, perm_resident text, parttime_resident text, interview_date text)
     JOIN dw.dimstudyparticipant a ON x.dimstudyparticipantkey = a.dimstudyparticipantkey