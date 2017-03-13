import sys
import numpy as numpy
import pandas as pandas

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

    updated = pandas.DataFrame(allGroups,columns=columns)
    return updated

def loadCSVs(parentdir):
    return {
        'births':pandas.read_csv(parentdir + 'Births.csv',encoding='UTF-8'),
        'hospital':pandas.read_csv(parentdir + 'BasicInfoHospitals.csv',encoding='UTF-8'),
        'deaths':pandas.read_csv(parentdir + 'Deaths.csv',encoding='UTF-8'),
        'edu':pandas.read_csv(parentdir + 'HigherEducated.csv',encoding='UTF-8'),
        'age':pandas.read_csv(parentdir + 'PopulationAgeGender.csv',encoding='UTF-8'),
        'workingAge':pandas.read_csv(parentdir + 'SomethingLikePeopleWorkinh.csv',encoding='UTF-8'),
        'surface':pandas.read_csv(parentdir + 'SurfaceSquareKM.csv',encoding='UTF-8'),
        'unemployed':pandas.read_csv(parentdir + 'unemployed.csv',encoding='UTF-8'),
        'worthArea':fixWorthArea(pandas.read_csv(parentdir + 'WorthArea.csv',encoding='UTF-8'))
    }

#Run initially to verify that landkreise names are common for all elements
def checkNameCommonality(allFrames):
    for index in allFrames:
        if (not allFrames[index]['Index'].dtype == numpy.int64):
            allFrames[index]['Name']=allFrames[index]['Name'].str.strip()
            allFrames[index] = allFrames[index][allFrames[index]['Index'].astype(str).str.isdigit()].copy()
            allFrames[index]['Index'] = pandas.to_numeric(allFrames[index]['Index'])

    frames = list(allFrames.values())

    mismatched = False
    for i in range(len(frames)):
        for j in range(i+1,len(frames)):
            test = frames[i].merge(frames[j], on=['Index'], how='outer').dropna()
            test['matched'] = test['Name_x'] == test['Name_y']
            test = test[['Index','Name_x','Name_y','matched']]
            if (len(test[test['matched']==False])>0):
                print('Index {} and {} did not match: {}'.format(i,j,len(test[test['matched']==False])))
                print(test[test['matched']==False].to_string(index=False))
                mismatched = True

    if (not mismatched):
        print('All names matched up. Good to go!')

def selectLandkreise(dataDir):
    # Make sure that we only have the 402 Landkreise left in the superduper dataframe.
    everything = loadEverything()
    landkreise = pandas.read_csv(dataDir + 'Landkreise.csv',encoding='UTF-8')

    landkreise['Type'] = landkreise['Type'].replace('', 'Kreis')
    cleaned = landkreise.merge(everything.drop('Name',1),on=['Index'],how='inner')
    cleaned.to_csv(dataDir + 'cleaned.csv',encoding='UTF-8')

    print('Saved cleaned dataset')

    return cleaned

def saveEverything(allFrames):
    for index in allFrames:
        if (not allFrames[index]['Index'].dtype == numpy.int64):
            allFrames[index]['Name']=allFrames[index]['Name'].str.strip()
            allFrames[index] = allFrames[index][allFrames[index]['Index'].astype(str).str.isdigit()].copy()
            allFrames[index]['Index'] = pandas.to_numeric(allFrames[index]['Index'])

    # drop name column from everything except first, then merge all into a large group
    everything = pandas.DataFrame()
    for index in allFrames:
        frame = allFrames[index].copy()
        cols = []
        for col in frame:
            if col == 'Name' or col == 'Index':
                cols.append(col)
            else:
                cols.append(col+'_'+index)
        frame.columns = cols

        if len(everything) == 0:
            everything = frame
        else:
            frame = frame.drop('Name',1)
            everything = everything.merge(frame,on=['Index'],how='outer')

    everything.to_csv('everything.csv',encoding='UTF-8',index=False)
    print('Done creating superduper data file.')
    return everything

def loadEverything():
    return pandas.read_csv('everything.csv',encoding='UTF-8')

def main():
    dataDir = 'AllDataFromDatabase/'

    allFrames = loadCSVs(dataDir)
    checkNameCommonality(allFrames)
    everything = saveEverything(allFrames)

    cleaned = selectLandkreise(dataDir)

if __name__ == '__main__':
    main()
    sys.exit()
