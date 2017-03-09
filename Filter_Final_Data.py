import pandas as pd
import numpy as np
import os

all_data = pd.read_csv('data_final.csv')
#print(all_data['Total_births'])

# Birth rate (Births/total population)
# Population 20-40
# Population Adults and pre-retirees (40-retirement age)
# Retirement age = 65
# Population retired (retirement age >)
# Population density (population/area)
# Hospital beds
# Housing price (Kaufsumme)
# Total working_age
# hospitals
# Total Unemployed_unemployed
# Average life expectancy (men and women)
# Spendable income average (already merged into file, by hand)

data4model = all_data[['Index', 'Name', 'Total_births', 'Beds in hospitals (JD)_hospital',
                       'Total_deaths', 'Graduates, Male_edu', 'Graduates, Female_edu',
                       'Total_age', 'Total_workingAge', 'Total Unemployed_unemployed',
                       'Area (km^2)_surface']]
print(data4model.head())
