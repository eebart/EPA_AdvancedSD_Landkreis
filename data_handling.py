import numpy as np
import pandas as pd
import os
import csv

os.chdir('AllDataFromDatabase')

births = pd.read_csv('WorthArea.csv', skiprows=4, engine='python',
                     skipfooter=4, header=1, index_col=0, sep=';',
                     encoding='latin1')
#print(births.head(10))

headers = list(births)
stadte = births[headers[1]]

kreise = births[births[headers[1]].str.contains('kreis')]
print(kreise)
