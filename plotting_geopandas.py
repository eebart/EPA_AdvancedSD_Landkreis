import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

GeoFrame = gpd.read_file('vg2500_krs.shp')
'''
GeoFrame.plot()
plt.show()
'''
# Filter specific Kreise
#print(GeoFrame.loc[GeoFrame['GEN'] == 'Greiz'])

# All kreise
#for kreis in GeoFrame['GEN']:
#    print(kreis)
