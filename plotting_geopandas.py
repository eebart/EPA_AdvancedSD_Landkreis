import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def split_zeros_indices(arealcodes):
    if isinstance(arealcodes, pd.Series):
        NewArealCode = []
        for i in range(len(arealcodes)):
            if arealcodes[i][0] == '0':
                sliced = arealcodes[i][1:]
                NewArealCode.append(int(sliced))
            else:
                NewArealCode.append(int(arealcodes[i]))

        # Updating GeoFrame
        return NewArealCode
    else:
        print('Not a Series')

def similarity_check(s1, s2):
    # intersects = pd.Series(np.intersect1d(GeoFrame['RS'], DataKreisCodes))
    intersects = pd.Series(list(set(s1).intersection(s2)))

    if len(intersects) == len(s1) & len(intersects) == len(s2):
        print('Series do contain the same values')
        return True
    else:
        print('Series do not contain the same values')
        print('...Go cleaning again')
        return False






def main():
    # Reading shape file
    GeoFrame = gpd.read_file('vg2500_krs.shp')
    # Removing the 0 in front of the index,
    # so indices from both files become similar
    GeoFrame['RS'] = split_zeros_indices(GeoFrame['RS'])
    Kreiscodes = GeoFrame['RS']

    # Reading data file
    all_kreise_data = pd.read_csv('data_final.csv', index_col=0)
    DataKreisCodes = all_kreise_data['Index']

    # Get all data that can be shown in the map
    alldata = list(all_kreise_data)
    for d in alldata:
        print(d)
    #print(alldata)
    if similarity_check(Kreiscodes, DataKreisCodes):
        # Start with data handling
        GeoFrame = GeoFrame.sort_values(by='RS', kind='mergesort')
        all_kreise_data = all_kreise_data.sort_values(by='Index',
                                                      kind='mergesort')
        all_kreise_data = all_kreise_data.reset_index(drop=True)
        GeoFrame = GeoFrame.reset_index(drop=True)

        kreisedata = all_kreise_data['Total_age']
        GeoFrame = GeoFrame.join(kreisedata)
        GeoFrame.plot(column='Total_age', scheme='QUANTILES', cmap='bwr', k=5, legend=True)
        plt.show()

# Filter specific Kreise
#print(GeoFrame.loc[GeoFrame['GEN'] == 'Greiz'])

# All kreise
#for kreis in GeoFrame['GEN']:
#    print(kreis)


if __name__ == "__main__":
    main()
    sys.exit(0)
