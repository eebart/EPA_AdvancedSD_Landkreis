import numpy as np
import pandas as pd
import os
import csv

os.chdir('AllDataFromDatabase')

births = pd.read_csv('Births.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')
basicInfoHospitals = pd.read_csv('BasicInfoHospitals.csv', skiprows=4,
                                 engine='python', skipfooter=4, header=1,
                                 index_col=0, sep=';', encoding='latin1')
RehabAndPrevention = pd.read_csv('BasicInfoHospitalsRehabilitationAndPrevention.csv',
                                 skiprows=4, engine='python', skipfooter=4,
                                 header=1, index_col=0, sep=';',
                                 encoding='latin1')
deaths = pd.read_csv('Deaths.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')
higherEdu = pd.read_csv('HigherEducated.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')
AgeGender = pd.read_csv('PopulationAgeGender.csv', skiprows=4, engine='python',
                         skipfooter=4, header=3, index_col=0, sep=';',
                         encoding='latin1')
workingAge = pd.read_csv('SomethingLikePeopleWorkinh.csv',
                          skiprows=4, engine='python', skipfooter=4,
                          header=2, index_col=0, sep=';',
                          encoding='latin1')
surface = pd.read_csv('SurfaceSquareKM.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')
unemployed = pd.read_csv('unemployed.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')
WorthArea = pd.read_csv('WorthArea.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')

#print(births.head(10))


headers = list(births)
stadte = births[headers[1]]

kreise = births[births[headers[1]].str.contains('kreis')]
kreise = kreise.append(births[births[headers[1]].str.contains('Kreis')])
