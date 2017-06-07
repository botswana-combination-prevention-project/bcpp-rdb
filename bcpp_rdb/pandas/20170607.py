import numpy as np
import os
import pandas as pd

from dateutil.parser import parse

# files
path = '/Users/erikvw/Documents/bcpp/pims/20170607/'
bcpp_subjects_file = os.path.join(
    path, 'bcpp_subjects_2016-07-31-122804.524479+0200.csv')
seroconverters_file = os.path.join(
    path, 'seroconverters01JUN17.csv')
pims_file = os.path.join(path, 'pims_haart_2017-06-07-1326116452540200.csv')
htc_file = os.path.join(path, 'htc_2017-06-07-1327252560230200.csv')
export_file = os.path.join(
    path, 'seroconverters01JUN17_with_pims.csv')
