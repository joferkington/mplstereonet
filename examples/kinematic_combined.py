""" 
Plot a single combined plot for kinematic analysis on planar sliding, wedge 
sliding and flexural toppling

Reference:
Wyllie, D.C. and Mah, C.W. (2004) Rock Slope Engineering. 4th Edition, 
E & FN Spon, London, 431. (P.39)
"""

import numpy as np
import matplotlib.pyplot as plt
import mplstereonet.kinematic_analysis as kinematic
from mplstereonet import stereonet_math

# Import data
discontinuity = np.loadtxt('kinematic_data1.txt', delimiter=',')
intersections = np.loadtxt('kinematic_data2.txt', delimiter=',')
jstrikes = discontinuity[:,1] - 90
jdips = discontinuity[:,0]
ibearings = intersections[:,1]
iplunges = intersections[:,0]

# set up analyses
strike, dip = 90, 75
P4 = kinematic.PlanarSliding(strike, dip)
T4 = kinematic.FlexuralToppling(strike, dip)

# Plot the kinematic analysis elements
P4.plot_kinematic(main_kws={'label':'Planar / Wedge Sliding'},
                       secondary_kws={'label':'Wedge Sliding'})

T4.plot_kinematic(ax=plt.gca(), slopeface=False, construction_lines=False,
                  main_kws={'color':'blue', 'label':'Flexural Toppling'})

# Plot data (here intersections should be pltted as poles too)
ax=plt.gca()

ax.pole(jstrikes, jdips, ms=2, label='Discontiuities (Poles)')
ax.pole(ibearings-90, iplunges, '+r', label='Intersections (Poles)')

ax.legend(loc='lower left', bbox_to_anchor=(0.75, 0.9))

plt.show()
