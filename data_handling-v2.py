import numpy as np
import pandas as pd
import os
import csv

def checkNameCommonality(allFrames):
    # Checking name commonality
    for i in range(len(allFrames)):
        for j in range(i+1,len(allFrames)):
            test = allFrames[i].merge(allFrames[j], on=['Index'], how='outer')
            test['matched'] = test['Name_x'] == test['Name_y']
            if (len(test[test['matched']==False])>0):
                print('Index {} and {} did not match: {}'.format(i,j,len(test[test['matched']==False])))
                print(test[test['matched']==False])

os.chdir('AllDataFromDatabase')

landkreise = pd.read_csv('Landkreise.csv',encoding='UTF-8')

births = pd.read_csv('Births.csv',encoding='UTF-8')
basicInfoHospitals = pd.read_csv('BasicInfoHospitals.csv',encoding='UTF-8')
deaths = pd.read_csv('Deaths.csv',encoding='UTF-8')
higherEdu = pd.read_csv('HigherEducated.csv',
                         engine='python',encoding='UTF-8')
ageGender = pd.read_csv('PopulationAgeGender.csv',
                         engine='python',encoding='UTF-8')
workingAge = pd.read_csv('SomethingLikePeopleWorkinh.csv',
                         engine='python',encoding='UTF-8')
surface = pd.read_csv('SurfaceSquareKM.csv')
unemployed = pd.read_csv('unemployed.csv')
WorthArea = pd.read_csv('WorthArea.csv')

#TODO Fix WorthArea

allFrames = {
    'births':births,
    'hospital':basicInfoHospitals,
    'deaths':deaths,
    'edu':higherEdu,
    'age':ageGender,
    'workingAge':workingAge,
    'surface':surface,
    'unemployed':unemployed
}

for index in allFrames:
    if (allFrames[index]['Index'].dtype == np.int64):
        allFrames[index] = allFrames[index][allFrames[index]['Index'] > 999]
    else:
        allFrames[index]['Name']=allFrames[index]['Name'].str.strip()
        allFrames[index]['Name']=allFrames[index]['Name'].str.strip()
        allFrames[index] = allFrames[index][(allFrames[index]['Index'].str.len() > 3) & (allFrames[index]['Index'].str.len() < 6)]
        allFrames[index]['Index'] = pd.to_numeric(allFrames[index]['Index'])

    allFrames[index] = allFrames[index][-allFrames[index]['Name'].str.contains('Kreisfreie Stadt',case=False)]

# drop name column from everything except first, then merge all into a large group
everything = pd.DataFrame()
for index in allFrames:
    cols = []
    for col in allFrames[index]:
        if col == 'Name' or col == 'Index':
            cols.append(col)
        else:
            cols.append(col+'_'+index)
    allFrames[index].columns = cols

    if len(everything) == 0:
        everything = allFrames[index]
    else:
        allFrames[index] = allFrames[index].drop('Name',1)
        everything = everything.merge(allFrames[index],on=['Index'],how='outer')

everything.to_csv('test.csv',encoding='UTF-8')

# Make sure that we only have the 402 Landkreise left in the superduper dataframe.





# cols_to_use = basicInfoHospitals.columns.difference(births.columns != 'Index')
# everything = pd.merge(births, basicInfoHospitals[cols_to_use], on=['Index'], how='outer')
#
# cols_to_use = deaths.columns.difference(everything.columns != 'Index')
# everything = pd.merge(everything, deaths[cols_to_use], on=['Index'], how='outer')
#
# cols_to_use = higherEdu.columns.difference(everything.columns != 'Index')
# everything = pd.merge(everything, higherEdu[cols_to_use], on=['Index'], how='outer')
#
# cols_to_use = ageGender.columns.difference(everything.columns != 'Index')
# everything = pd.merge(everything, ageGender[cols_to_use], on=['Index'], how='outer')
#
# cols_to_use = workingAge.columns.difference(everything.columns != 'Index')
# everything = pd.merge(everything, workingAge[cols_to_use], on=['Index'], how='outer')
#
# print(surface)
#
#
#
#
# print(everything.columns)
# kreise.to_csv('test.csv',encoding='UTF-8')
