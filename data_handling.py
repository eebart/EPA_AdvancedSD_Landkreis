import numpy as np
import pandas as pd
import os
import csv

os.chdir('AllDataFromDatabase')

landkreise = pd.read_csv('Landkreise.csv',encoding='UTF-8')

births = pd.read_csv('Births.csv',encoding='UTF-8')
basicInfoHospitals = pd.read_csv('BasicInfoHospitals.csv',
                                 engine='python',encoding='UTF-8')
rehabAndPrevention = pd.read_csv('BasicInfoHospitalsRehabilitationAndPrevention.csv',
                                 engine='python',encoding='UTF-8')
deaths = pd.read_csv('Deaths.csv',
                     engine='python',encoding='UTF-8')
higherEdu = pd.read_csv('HigherEducated.csv',
                         engine='python',header=2,encoding='UTF-8')
ageGender = pd.read_csv('PopulationAgeGender.csv',
                         engine='python',header=1,encoding='UTF-8')
workingAge = pd.read_csv('SomethingLikePeopleWorkinh.csv',
                         engine='python',header=1,encoding='UTF-8')
surface = pd.read_csv('SurfaceSquareKM.csv',
                      engine='python',encoding='UTF-8')
unemployed = pd.read_csv('unemployed.csv',
                         engine='python',encoding='UTF-8')
WorthArea = pd.read_csv('WorthArea.csv',
                         engine='python',encoding='UTF-8')

headers = list(births)
# TODO Match names in landkreise with names in each file (string parsing, wheee!!!)
birth_kreise = births[births[headers[1]].str.contains('kreis|Kreis')]
matches = {}
for index, row in landkreise.iterrows():
    match = None
    for district in row['District'].split(';'):
        match = birth_kreise[birth_kreise['Name'].str.contains(district,case=False)]
        # TODO replace Name with District string
    matches[district] = match
    if (len(match)>1):
        print(row.District)
        print(match)
        # TODO this should be empty. Solve these errors

# kreise.to_csv('test.csv',encoding='UTF-8')
