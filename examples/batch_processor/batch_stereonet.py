from __future__ import print_function
from os.path import splitext, basename
import matplotlib.pyplot as plt
import numpy as np
import mplstereonet
'''
A basic implementation of batch processing of fold data. Each fold's data is in a separate datafile, with the data from the limbs. This script accepts a list of datafiles and will plot the poles, then calculate and plot the fold axis and the axial plane of the fold.

The datafile is simply a .csv file with the following columns:
Location:   The location of the file. Can be relative to the present directory.
Title:      The title that the graph needs to be given.
Azi:        Whether the readings are in strike or azimuth. `True` here will cause the readings to be converted from azimuth to strike.

The script will create a plot for each fold as a .png file. It will also save the plunge and bearing of the fold axis, and the strike and dip of the axial plane to a text file.

You will need to have a folder for the graphs and text to be saved into.
'''
def main(datasource, azi = False, plot_planes=False, filled_contour=True, title='Fold 1'):
    """
    This will control the plotting of everything else.

    Parameters:
        * datasource:string File containing strike/dip or azimuth/dip readings
        * azi:bool Are the readings azimuthal or strike?
        * plot_planes:bool Do you want to plot planes or just poles to planes?

    Returns:
        None, but will save a .png of the stereonet to the same location as the file.
    """
    print ('===============\nImporting data from: ', datasource)
    #datasource = '/path/to/file/'
    data = np.genfromtxt(datasource, delimiter=',', names=True, dtype=None)
    strike_readings = [i[0] for i in data]
    if azi:
        strike_readings = [mplstereonet.utilities.dip_direction2strike(i) for i in strike_readings]
    dip_readings = [i[1] for i in data]
    print ('Data imported from: ', datasource)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='stereonet', zorder=25)
    ax.grid()
    ax.pole(strike_readings, dip_readings, 'wo', markersize=3, alpha=0.6)
    if filled_contour:
        cax = ax.density_contourf(strike_readings, dip_readings, measurement='poles', method="exponential_kamb", cmap='viridis')
    else:
        cax = ax.density_contour(strike_readings, dip_readings, measurement='poles', method="exponential_kamb", cmap='viridis')
        print ('Plotted contoured poles')
    if plot_planes:
        ax.plane(strike_readings, dip_readings, 'k', markersize=2, alpha=0.4)
        print ('Plotted contoured planes')

    centres = mplstereonet.kmeans(strike_readings, dip_readings, num=2)
    strike_cent, dip_cent = mplstereonet.geographic2pole(*zip(*centres))
    ax.pole(strike_cent, dip_cent, 'ro', ms=8)
    print ('Plotted centres of pole clusters')

    mid, _ = mplstereonet.find_mean_vector(*zip(*centres), measurement='radians')
    midx, midy = mplstereonet.line(*mid)
    axis_s, axis_d = mplstereonet.fit_girdle(*zip(*centres), measurement='radians')
    ax.plane(axis_s, axis_d, color='yellow', linestyle='--')
    ax.pole(axis_s, axis_d, color='green', marker='o', ms=10, zorder=30)

    xp, yp = mplstereonet.pole(axis_s, axis_d)
    x, y = [xp[0], midx], [yp[0], midy]
    axial_s, axial_dip = mplstereonet.fit_girdle(x, y, measurement='radians')
    ax.plane(axial_s, axial_dip, color='yellow', lw=2.5)
    axial_plane = (axial_s, axial_dip)
    print ('Plotted axial plane and fold axis')

    (plunge,), (bearing,) = mplstereonet.pole2plunge_bearing(axis_s, axis_d)
    '''
    #This is a block for if you want to point out the fold axis explicitly. It is already going to be visible in a textbox though.
    lon, lat = mplstereonet.pole(axis_s, axis_d)
    template = u'P/B of Fold Axis\n{:02.0f}\u00b0/{:03.0f}\u00b0'
    bbox_props = dict(boxstyle="round,pad=0.3", fc="w", ec="k", lw=2, alpha=0.35)
    ax.annotate(template.format(plunge, bearing), ha='center', va='bottom',
                xy=(lon, lat), xytext=(-50, 20), textcoords='offset points',
                arrowprops=dict(arrowstyle='fancy', facecolor='w', connectionstyle="arc3,rad=1"), bbox=bbox_props, zorder=31)
    print ('Annotated P/B')
    '''

    fig.colorbar(cax, shrink=0.55)
    ax.set_title( title.upper(), fontsize=16, y=1.07 )

    useful_numbers = u'P/B of Fold Axis: \n{0}/{1}\nS/D of Axial Plane: \n{2}/{3}'.format(str(round(plunge,2)), str(round(bearing,2)), str(round(axial_s,2)), str(round(axial_dip,2)))
    bbox_props = dict(boxstyle="round,pad=0.3", fc="w", ec="k", lw=2, alpha=0.35)
    ax.text( 1, 0.1, useful_numbers, ha='left', va='top', bbox=bbox_props, color='grey', clip_on=False, transform=ax.transAxes)

    basefilename = splitext(basename(datasource))[0]
    image_filename = 'graphs/{0}.png'.format(basefilename)
    plt.savefig(image_filename, dpi=175)
    print ('Saved plot', image_filename)

    text_filename = 'other/{0}.txt'.format(basefilename)
    with open(text_filename, 'w') as f:
        f.write(useful_numbers)
    print ('Check {0} for axial plane and fold axis values'.format(text_filename))


if __name__ == '__main__':
    files = 'folds.csv'
    datafiles = np.genfromtxt(files, delimiter=',', names=True, dtype=None)

    [main(i[0], azi = i[2], title= i[1]) for i in datafiles]
