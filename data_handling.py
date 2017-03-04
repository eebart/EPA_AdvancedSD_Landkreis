import numpy as np
import pandas as pd

def fixWorthArea(worthArea):
    groups = worthArea.groupby(['Index','Name'])

    allGroups = []
    columns = ['Index','Name']
    for group in groups:
        df = group[1]
        if len(columns) == 2:
            headers = df[['Type','Row Label']].copy()
            headers['total'] = headers['Type'] + " - Total (" + headers['Row Label'] + ")"
            headers['buildingLand'] = headers['Type'] + " - Building Land (" + headers['Row Label'] + ")"
            columns.extend(headers['total'].tolist())
            columns.extend(headers['buildingLand'].tolist())

        dataRow = [group[0][0],group[0][1].strip()]

        dataRow.extend(df['Total'].tolist())
        dataRow.extend(df['Building land'].tolist())

        allGroups.append(dataRow)

    updated = pd.DataFrame(allGroups,columns=columns)
    return worthArea

def loadCSVs(parentdir):
    return {
        'births':pd.read_csv(parentdir + 'Births.csv',encoding='UTF-8'),
        'hospital':pd.read_csv(parentdir + 'BasicInfoHospitals.csv',encoding='UTF-8'),
        'deaths':pd.read_csv(parentdir + 'Deaths.csv',encoding='UTF-8'),
        'edu':pd.read_csv(parentdir + 'HigherEducated.csv',encoding='UTF-8'),
        'age':pd.read_csv(parentdir + 'PopulationAgeGender.csv',encoding='UTF-8'),
        'workingAge':pd.read_csv(parentdir + 'SomethingLikePeopleWorkinh.csv',encoding='UTF-8'),
        'surface':pd.read_csv(parentdir + 'SurfaceSquareKM.csv',encoding='UTF-8'),
        'unemployed':pd.read_csv(parentdir + 'unemployed.csv',encoding='UTF-8'),
        'worthArea':fixWorthArea(pd.read_csv(parentdir + 'WorthArea.csv',encoding='UTF-8'))
    }

#Run initially to verify that landkreise names are common for all elements
def checkNameCommonality(allFrames):
    for index in allFrames:
        if (not allFrames[index]['Index'].dtype == np.int64):
            allFrames[index]['Name']=allFrames[index]['Name'].str.strip()
            allFrames[index] = allFrames[index][allFrames[index]['Index'].astype(str).str.isdigit()].copy()
            allFrames[index]['Index'] = pd.to_numeric(allFrames[index]['Index'])

    frames = list(allFrames.values())

    mismatched = False
    for i in range(len(frames)):
        for j in range(i+1,len(frames)):
            test = pd.merge(frames[i],frames[j], on=['Index'], how='outer')
            test['matched'] = test['Name_x'] == test['Name_y']
            test = test[['Index','Name_x','Name_y','matched']].dropna()
            if (len(test[test['matched']==False])>0):
                print('Index {} and {} did not match: {}'.format(i,j,len(test[test['matched']==False])))
                print(test[test['matched']==False].to_string(index=False))
                mismatched = True

    if (not mismatched):
        print('All common names matched up. Good to go!')

def selectLandkreise(dataDir):
    # Make sure that we only have the 402 Landkreise left in the superduper dataframe.
    everything = loadEverything()
    landkreise = pd.read_csv(dataDir + 'Landkreise.csv',encoding='UTF-8')

    landkreise['Type'] = landkreise['Type'].replace('', 'Kreis')
    cleaned = landkreise.merge(everything.drop('Name',1),on=['Index'],how='inner')
    cleaned.to_csv(dataDir + 'cleaned.csv',encoding='UTF-8')

    print('Saved cleaned dataset')

    return cleaned

def saveEverything(allFrames):
    for index in allFrames:
        if (not allFrames[index]['Index'].dtype == np.int64):
            allFrames[index]['Name']=allFrames[index]['Name'].str.strip()
            allFrames[index] = allFrames[index][allFrames[index]['Index'].astype(str).str.isdigit()].copy()
            allFrames[index]['Index'] = pd.to_numeric(allFrames[index]['Index'])

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

    print('Saving everything to super duper data file')

    everything.to_csv('everything.csv',encoding='UTF-8',index=False)
    return everything

def loadEverything():
    return pd.read_csv('everything.csv',encoding='UTF-8')

dataDir = 'AllDataFromDatabase/'

allFrames = loadCSVs(dataDir)
checkNameCommonality(allFrames)
everything = saveEverything(allFrames)

cleaned = selectLandkreise(dataDir)
