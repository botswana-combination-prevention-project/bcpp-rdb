import pandas as pd
from sqlalchemy import create_engine

from bcpp_rdb.private_settings import Rdb


class CCC(object):

    """CDC data for close clinical cohort."""

    def __init__(self):
        self.engine = create_engine('postgresql://{user}:{password}@{host}/{db}'.format(
            user=Rdb.user, password=Rdb.password, host=Rdb.host, db=Rdb.name),
            connect_args={})
        with self.engine.connect() as conn, conn.begin():
            self.df_enrolled = pd.read_sql_query(self.sql_enrolled, conn)

    def sql_enrolled(self):
        """
        * If patient is from BCPP survye, oc_study_id is a BHP identifier.
        * ssid is the CDC allocated identifier of format NNN-NNNN.
        """
        return """select ssid as cdcid, oc_study_id as subject_identifier,
        appt_date from dw.oc_crf_ccc_enrollment"""

    def sql_refused(self):
        """
        * If patient is from BCPP survye, oc_study_id is a BHP identifier.
        * ssid is the CDC allocated identifier of format NNN-NNNN.
        """
        return """select ssid as cdcid, oc_study_id as subject_identifier,
        appt_date from dw.oc_crf_ccc_enrollment"""
