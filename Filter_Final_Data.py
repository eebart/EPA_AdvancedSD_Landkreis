import pandas as pd
import numpy as np
import os

all_data = pd.read_csv('data_final.csv')
#print(all_data['Total_births'])

data4model = all_data[['Index', 'Name', 'Total_births', 'Beds in hospitals (JD)_hospital',
                       'Total_deaths', 'Graduates, Male_edu', 'Graduates, Female_edu',
                       'Total_age', 'Total_workingAge', 'Total Unemployed_unemployed',
                       'Area (km^2)_surface']]
print(data4model.head())
