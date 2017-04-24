import os
import sys

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import matplotlib.path as mplpath
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from shapely.geometry import Polygon, MultiPolygon

import numpy as np
import pandas as pd
import geopandas as gpd

import glob

##############################################################################
# First function to remove the zeros in front of the index codes
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

# Creating paths to register the clicked point.
# Needs a geoframe with the columns 'GEN' (Names), 'RS' (Indices) and
# 'geometry' (containing the shapes)
def shp_path_creation(geoframe):
    x_coords = []
    y_coords = []
    ShapeName = []
    ShapeIndex = []
    Paths = []

    # Iterate through the geometry column, and if it is a MultiPolygon type,
    # Then it iterates through that as well.
    for index, shape in enumerate(geoframe['geometry']):
        if isinstance(shape, Polygon):
            # Extract the x/y coords from the shape
            x, y = shape.exterior.coords.xy
            # Store in an array
            arr2d = np.asarray([x, y]).T
            # Store in an array as matplotlib path, and store xs/ys in list
            Path = mplpath.Path(arr2d)
            Paths.append(Path)
            x_coords.append(x)
            y_coords.append(y)
            # Store shape names and indices in list
            ShapeName.append(geoframe['GEN'].iloc[index])
            ShapeIndex.append(geoframe['RS'].iloc[index])
        if isinstance(shape, MultiPolygon):
            for part in shape:
                x, y = part.exterior.coords.xy
                arr2d = np.asarray([x, y]).T
                Path = mplpath.Path(arr2d)
                Paths.append(Path)
                x_coords.append(x)
                y_coords.append(y)
                ShapeName.append(geoframe['GEN'].iloc[index])
                ShapeIndex.append(geoframe['RS'].iloc[index])

    # Create DataFrame from all the lists
    nestedList = [ShapeName, ShapeIndex, Paths, x_coords, y_coords]
    df = pd.DataFrame(data=nestedList).T
    df.columns=['Name', 'Index', 'Paths', 'x_coords', 'y_coords']
    # Create a PatchCollection from the paths
    patcheslist = []
    for path in df['Paths']:
        patch = patches.PathPatch(path, facecolor='white', lw=2)
        patcheslist.append(patch)

    patch_collection = PatchCollection(patcheslist, alpha=0.01, lw=2)

    return df, patch_collection, Paths

# Expand the data to match it with the extended shapefile.
def data_expansion(geoframe, datadict):
    datasets = datadict.keys()
    processed_sets = []
    for dataset in datasets:
        temp_df = pd.DataFrame(columns=list(datadict[dataset]))
        for index, shape in enumerate(geoframe['geometry']):
            if isinstance(shape, Polygon):
                temp_df = temp_df.append(datadict[dataset].iloc[index])
            elif isinstance(shape, MultiPolygon):
                for part in shape:
                    temp_df = temp_df.append(datadict[dataset].iloc[index])
        processed_sets.append(temp_df)
    # Store it again in a dictionary
    dictionary = dict(zip(datasets, processed_sets))

    return dictionary


def shp_and_data_selection(shpdir, shpname, datadir):
    homedir = os.getcwd()
    # Extract shapefile and process it first
    os.chdir(shpdir)
    origin_geoframe = gpd.read_file(shpname)
    origin_geoframe['RS'] = split_zeros_indices(origin_geoframe['RS'])
    # Return to homedir
    os.chdir(homedir)
    # Go to datadir
    os.chdir(datadir)
    # Get all csv files in this directory
    # Make sure there are only the csv files you want in this directory
    datafiles = glob.glob('*.csv')
    datasets = []
    names = []
    for f in datafiles:
        data = pd.read_csv(f, encoding='latin_1', index_col=0)
        name = f.replace('.csv', '')
        datasets.append(data)
        names.append(name)

    datadict = dict(zip(names, datasets))
    datadict = data_expansion(origin_geoframe, datadict)

    os.chdir(homedir)

    return origin_geoframe, datadict





# The class Plot creates a plotting instance from matplotlib, based on the
# geoframe and data
class Plot():
    # Initially many functions are called to create the plot and use the
    # interactive functions
    def __init__(self, original_geoframe, data):
        # Making all variables part of the class
        self.geoframe_origin = original_geoframe
        self.geoframe_processed, self.p, self.Paths = shp_path_creation(self.geoframe_origin)

        self.fig, self.ax = plt.subplots(figsize=(8,8))
        self.fig.subplots_adjust(left=0.30, bottom=0.30)

        self.data = data
        self.dataset_used= data[list(data)[0]]
        self.ts(self.dataset_used)
        # Create an initial, uncoloured plot
        for i in range(len(self.geoframe_processed)):
            self.ax.fill(self.geoframe_processed['x_coords'].iloc[i], self.geoframe_processed['y_coords'].iloc[i],
                         facecolor=(1,1,1), edgecolor='black', alpha=0.25)

        self.ax.add_collection(self.p)
        # Create the time slider instance
        self.timelineaxes = plt.axes([0.3, 0.1, 0.65, 0.03], facecolor=(1,1,1))
        self.slidertimeline = widgets.Slider(self.timelineaxes, 'TimeLine', min(self.timesteps),
                                        max(self.timesteps), valinit=min(self.timesteps),
                                        valfmt='%0.0f')
        # Call the slider function
        self.slidertimeline.on_changed(self.slider_update)

        # Creating the radiobuttons for selecting the dataset
        self.rbsaxes = plt.axes([0.01, 0.30, 0.225, 0.65], facecolor=(1,1,1), frameon=True)
        self.lables = tuple(list(self.data))
        self.rbs = widgets.RadioButtons(self.rbsaxes, self.lables, active=self.lables[0])
        # (Re)setting circle sizes to nice circles
        rpos = self.rbsaxes.get_position().get_points()
        fh = self.fig.get_figheight()
        fw = self.fig.get_figwidth()
        rscale = (rpos[:,1].ptp() / rpos[:,0].ptp()) * (fh / fw)
        for circle in self.rbs.circles:
            circle.height /= rscale
        # The function that is called after a radiobutton is clicked
        self.rbs.on_clicked(self.rbs_update)

        # Calling the function after a Landkreis is clicked
        cid = self.fig.canvas.mpl_connect('button_press_event', self.mouseclick_pressed)

    # Extract the timesteps from the dataset
    def ts(self, dataframe):
        columns = list(dataframe)
        self.timesteps = []
        for i in range(1, len(columns)):
            self.timesteps.append(float(columns[i]))

    # After a Landkreis is clicked, a new figure is created and the raw data
    # is plotted.
    def mouseclick_pressed(self, event):
        for index, shape in enumerate(self.Paths):
            if shape.contains_point((event.xdata, event.ydata)):
                print('You pressed landkreis {}, ID {}'.format(self.geoframe_processed['Name'].iloc[index],
                                                               self.geoframe_processed['Index'].iloc[index]))
                figi = plt.figure()
                ax = figi.add_subplot(111)
                data = self.dataset_used
                datacols = list(data)
                x = []
                y = []
                for i, t in enumerate(datacols):
                    try:
                        v = float(t)
                        x.append(v)
                        y.append(data.iloc[index, i])
                    except (ValueError, TypeError) as err:
                        continue
                        raise err

                ax.plot(x, y, 'r-')
                ax.set_title(self.geoframe_processed['Name'].iloc[index] + '\n' +
                             str(self.geoframe_processed['Index'].iloc[index]))

                figi.show()

    # The slider update function (after interacting the graph with the slider)
    def slider_update(self, val):
        self.ax.cla()
        self.var = self.slidertimeline.val
        self.colorcodings = self.colorcoding()
        for i in range(len(self.geoframe_processed)):
            self.ax.fill(self.geoframe_processed['x_coords'].iloc[i], self.geoframe_processed['y_coords'].iloc[i],
                         facecolor=self.codings[i], edgecolor='black', alpha=0.25)

    # Radiobuttons update
    def rbs_update(self, label):
        self.dataset_used = self.data[label]

    # Colorcoding function (STILL UNDER CONSTRUCTION)
    def colorcoding(self):
        self.codings = []
        self.normalized_series = pd.Series()
        colors = [(0,1,0), (0,0.75,0), (0.25,0.75,0),
                  (0.25,0.5,0), (0.5,0.5,0), (0.5,0.25,0),
                  (0.75,0.25,0), (0.75,0,0), (1,0,0), (1,1,1)]

        for t in list(self.dataset_used):
            if t == str(int(self.var)):
                timeframe_data = self.dataset_used[t]
                maximum = max(timeframe_data)
                minimum = min(timeframe_data)
                normalized = (timeframe_data-minimum)/(maximum-minimum)
                self.normalized_series = normalized

        for i in self.normalized_series:
            if i<=0.2:
                self.codings.append(colors[0])
            elif i>0.2 and i<=0.3:
                self.codings.append(colors[1])
            elif i>0.3 and i<=0.4:
                self.codings.append(colors[2])
            elif i>0.4 and i<=0.5:
                self.codings.append(colors[3])
            elif i>0.5 and i<=0.6:
                self.codings.append(colors[4])
            elif i>0.6 and i<=0.7:
                self.codings.append(colors[5])
            elif i>0.7 and i<=0.8:
                self.codings.append(colors[6])
            elif i>0.8 and i<=0.9:
                self.codings.append(colors[7])
            elif i>0.9 and i<=1:
                self.codings.append(colors[8])
            else:
                self.codings.append(colors[9])

################################################################################
# The main program if ran from terminal.

def main():
#    origin_geoframe = gpd.read_file('../data/geographic/vg2500_geo84/vg2500_krs.shp')
#    origin_geoframe['RS'] = split_zeros_indices(origin_geoframe['RS'])

    print('If you do not enter any directory or file, the program takes a default')
    print('In that case, just hit [enter]...')
    shapedir = str(input('Where is the shapefile located? Enter the full directory: ') or '../shp')
    shapename = str(input('What is the name of the shapefile? Enter the full name: ') or 'GER_krs.shp')
    datadir = str(input('Where is the data located? Enter the full directory: ') or '../data')

    origin_geoframe, datadict = shp_and_data_selection(shapedir, shapename, datadir)

    plot = Plot(origin_geoframe, datadict)

    plt.show()

if __name__ == '__main__':
    main()
    sys.exit()
