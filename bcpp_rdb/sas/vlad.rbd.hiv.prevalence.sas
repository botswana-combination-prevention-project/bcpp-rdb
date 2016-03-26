******************************************************************;
** Program: vlad.rbd.hiv.prevalence.sas;
** Programmer: Kara Bennett;
** Purpose: checking derivation of prev_result and prev_result_known;
** Date: 4 December 2015;
** Notes:
** For total # use 2011 census numbers by gender for community (by;
** using the proportions of male/female available in Table 4 of 2011;
** census by district (applied gender distribution for each district to;
** each community) and proportions in each age category in Table 5;
** overall for the entire country of Botswana (age distribution not;
** available by district - applied the age distribution for the entire;
** country to each community);
** to determine the numerator use proportion HIV+ (ie, HIV prevalence);
** availabe in the baseline BCPP data by community, age category and;
** gender.  Then take the total determined above from the census and;
** multiply by the HIV prevalence from BCPP to get the 'numerator' - that is;
** the number of HIV+ we expect per community per age and gender;
** for purposes of checking what we are getting for Research Blood;
** Draws (RBDs);
**
** (did not use BIAS data because there are issues with this data due to;
** 30-40% refusal rate);
******************************************************************;
%include "C:\Users\KBENNETT\BCPP\SAS programs\bcpp.libraries.sas";

filename filelst "&studydir\SAS programs\analysis\vlad.rbd.hiv.prevalence.lst.txt";
filename filertf "&studydir\SAS programs\analysis\vlad.rbd.hiv.prevalence.lst.rtf";
filename filelog "&studydir\SAS programs\analysis\vlad.rbd.hiv.prevalence.log.log";

proc printto log=filelog new;
run;

ods rtf file=filertf bodytitle;

title 'BCPP';
run;

%LET exdir2 = C:\Users\KBENNETT\BCPP\Data\census data;
/*
** Import the census data by community:;
** overall population, proportion female/male, proportion in each age category;
proc import out=bcppraw.census_comm_sexage
    datafile="&exdir2\community_by_district_sex_age.csv"
    dbms=csv replace;
    getnames=yes;
    datarow=2;
    guessingrows=32767;
run;

proc contents data=bcppraw.census_comm_sexage;
run;

proc print data=bcppraw.census_comm_sexage;
run;
*/

data survey; set "S:\IID\Research Groups\Essex\Nealia\Analysis Datasets\bhs_survey.sas7bdat";
run;

proc freq data = ;

** Make a few modifications to Nealia's HIV prevalence data;
** (By community, gender and age);
data bcpp_hivp;
    set bcppn.prevalence_all;
** so name convention matches mine;
    if community='Tati_siding' then community='Tati Siding';
    else if community='Mmandunyane' then community='Mandunyane';
    else if community='Metsimotlhabe' then community='Metsimotlhaba';

** convert percents to proportion and rename variables;
    hivp_f_16_25=prev_female1/100;
    hivp_f_26_35=prev_female2/100;
    hivp_f_36_45=prev_female3/100;
    hivp_f_46_55=prev_female4/100;
    hivp_f_56_65=prev_female5/100;
    hivp_m_16_25=prev_male1/100;
    hivp_m_26_35=prev_male2/100;
    hivp_m_36_45=prev_male3/100;
    hivp_m_46_55=prev_male4/100;
    hivp_m_56_65=prev_male5/100;
run;

proc sort data=bcpp_hivp; 
    by community;
run;

proc sort data=bcppraw.census_comm_sexage out=census_comm_sexage;
    by community;
run;

** calculating HIV prevalence per community using baseline HIV prevalence collected;
** under BCPP, population estimate based on BCPP;
** and age and gender distributions from the 2011 census;

data pop_est;
    set bcpp.pop_est;
** so name convention matches mine;
    if community='Tati_siding' then community='Tati Siding';
    else if community='Mmandunyane' then community='Mandunyane';
    else if community='Metsimotlhabe' then community='Metsimotlhaba';
run;

proc sort data=pop_est;
    by community;
run;

data hivp_comm1;
    merge bcpp_hivp census_comm_sexage pop_est;
    by community;
run;

** need to impute prevalence where it is missing in the males for 16_25 and 26_35;
** age groups (due to small numbers for a few communities in the younger male group);
** used non-missing prevalence from community in that pair for imputation;
proc sort data=hivp_comm1; by pair descending hivp_m_16_25 descending hivp_m_26_35;
run;

data bcpp.hivp_comm;
    set hivp_comm1;
    by pair descending hivp_m_16_25 descending hivp_m_26_35;

    lpair=lag(pair);
    if first.pair then lpair=.;
    lhivp_m_16_25=lag(hivp_m_16_25);
    lhivp_m_26_35=lag(hivp_m_26_35);

** Make sure that filling in from same pair;
    if hivp_m_16_25=. and pair=lpair 
      then imp_hivp_m_16_25=lhivp_m_16_25;
    else imp_hivp_m_16_25=hivp_m_16_25;
    if hivp_m_26_35=. and pair=lpair
      then imp_hivp_m_26_35=lhivp_m_26_35;
    else imp_hivp_m_26_35=hivp_m_26_35;

    n_hivp_m_16_25=round(pindrop_pop_est*imp_hivp_m_16_25*p_male*p_age_15_24);
    n_hivp_f_16_25=round(pindrop_pop_est*hivp_f_16_25*p_female*p_age_15_24);
    n_hivp_m_26_35=round(pindrop_pop_est*imp_hivp_m_26_35*p_male*p_age_25_34);
    n_hivp_f_26_35=round(pindrop_pop_est*hivp_f_26_35*p_female*p_age_25_34);
    n_hivp_m_36_45=round(pindrop_pop_est*hivp_m_36_45*p_male*p_age_35_44);
    n_hivp_f_36_45=round(pindrop_pop_est*hivp_f_36_45*p_female*p_age_35_44);
    n_hivp_m_46_55=round(pindrop_pop_est*hivp_m_46_55*p_male*p_age_45_54);
    n_hivp_f_46_55=round(pindrop_pop_est*hivp_f_46_55*p_female*p_age_45_54);
    n_hivp_m_56_65=round(pindrop_pop_est*hivp_m_56_65*p_male*p_age_55_64);
    n_hivp_f_56_65=round(pindrop_pop_est*hivp_f_56_65*p_female*p_age_55_64);

    n_hivp=sum(of n_hivp_m_16_25, n_hivp_f_16_25, n_hivp_m_26_35, n_hivp_f_26_35, n_hivp_m_36_45,
                  n_hivp_f_36_45, n_hivp_m_46_55, n_hivp_f_46_55, n_hivp_m_56_65, n_hivp_f_56_65);

    label n_hivp_m_16_25='HIV+ Male subjects age 16-25'
          n_hivp_f_16_25='HIV+ Female subjects age 16-25'
          n_hivp_m_26_35='HIV+ Male subjects age 26-35'
          n_hivp_f_26_35='HIV+ Female subjects age 26-35'
          n_hivp_m_36_45='HIV+ Male subjects age 36-45'
          n_hivp_f_36_45='HIV+ Female subjects age 36-45'
          n_hivp_m_46_55='HIV+ Male subjects age 46-55'
          n_hivp_f_46_55='HIV+ Female subjects age 46-55'
          n_hivp_m_56_65='HIV+ Male subjects age 56-65'
          n_hivp_f_56_65='HIV+ Female subjects age 56-65'
          n_hivp='Estimated HIV+ for community';


run;

proc sort data=bcpp.hivp_comm;
    by pair community;
run;

options orientation=landscape;

proc print data=bcpp.hivp_comm noobs;
    var pair community n_hivp_m_16_25 n_hivp_f_16_25 n_hivp_m_26_35 n_hivp_f_26_35
        n_hivp_m_36_45 n_hivp_f_36_45 n_hivp_m_46_55 n_hivp_f_46_55 n_hivp_m_56_65
        n_hivp_f_56_65 n_hivp;
run;

data bcpp.hivp_comm_vlad;
    retain pair community n_hivp;
    set bcpp.hivp_comm;

    keep pair community n_hivp;
run;

** Excel file for Vlad;
%LET myxlsdir = C:\Users\KBENNETT\BCPP\Data\exported Excel data;

proc export data=bcpp.hivp_comm_vlad
            outfile="&myxlsdir\bcpp_hivp_bycommunity.csv"
            dbms=csv replace label;
run;
ods rtf close;

proc printto;
run;
