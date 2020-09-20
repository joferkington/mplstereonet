""" Demonstration of checking whether failures are possible on 
discontinuities / intsersections, and highlighting them (with counts) on
the plots"""

import numpy as np
import matplotlib.pyplot as plt
import mplstereonet.kinematic_analysis as kinematic
from mplstereonet import stereonet_math

# Load data
discontinuity = np.loadtxt('kinematic_data1.txt', delimiter=',')
intersections = np.loadtxt('kinematic_data2.txt', delimiter=',')
jstrikes = discontinuity[:,1] - 90
jdips = discontinuity[:,0]
ibearings = intersections[:,1]
iplunges = intersections[:,0]

# Set up kinematic analysis 
strike, dip = 180, 75
P3 = kinematic.PlanarSliding(strike, dip)
T3 = kinematic.FlexuralToppling(strike, dip, latlim=15)
W3 = kinematic.WedgeSliding(strike, dip)

# Check data
mainP, secP = P3.check_failure(jstrikes, jdips)
mainT, _ = T3.check_failure(jstrikes, jdips)
mainW, secW = W3.check_failure(ibearings, iplunges)

# Start plotting
fig = plt.figure(figsize=(15, 6))

ax1 = fig.add_subplot(1,3,1, projection='stereonet')
ax1.set_title('Planar Sliding', loc='left')
ax2 = fig.add_subplot(1,3,2, projection='stereonet')
ax2.set_title('Flexural Toppling', loc='left')
ax3 = fig.add_subplot(1,3,3, projection='stereonet')
ax3.set_title('Wedge Sliding', loc='left')

# Set up kinematic analysis plots
P3.plot_kinematic(ax=ax1, slope_kws={'label':''}, main_kws={'label':''}, 
                  secondary_kws={'label':''})
T3.plot_kinematic(ax=ax2, slope_kws={'label':''}, main_kws={'label':''}, 
                  secondary_kws={'label':''})
W3.plot_kinematic(ax=ax3, slope_kws={'label':''}, main_kws={'label':''}, 
                  secondary_kws={'label':''})

# Plot planar sliding data
ax1.pole(jstrikes, jdips, c='k', ms=1, 
         label='Discontinuities (Poles) [{}]'.format(len(jstrikes)))
ax1.pole(jstrikes[mainP], jdips[mainP], c='r', ms=2, 
         label='Planar sliding possible [{}]'.format(sum(mainP)))
ax1.pole(jstrikes[secP], jdips[secP], c='c', ms=2, 
         label='Planar sliding partially possible [{}]'.format(sum(secP)))

# Plot flexural toppling data
ax2.pole(jstrikes, jdips, c='k', ms=1, 
         label='Discontinuities (Poles) [{}]'.format(len(jstrikes)))
ax2.pole(jstrikes[mainT], jdips[mainT], c='r',  ms=2, 
         label='Toppling possible [{}]'.format(sum(mainT)))

# Plot wedge sliding data
ax3.plot(*stereonet_math.line(iplunges, ibearings), 'ok', ms=1, 
         label='Discontinuity intersections (Lines) [{}]'.format(len(iplunges)))
ax3.plot(*stereonet_math.line(iplunges[mainW], ibearings[mainW]), 'or', ms=2, 
         label='Wedge sliding possible [{}]'.format(sum(mainW)))
ax3.plot(*stereonet_math.line(iplunges[secW], ibearings[secW]), 'oc', ms=2, 
         label='Wedge sliding possible on single plane [{}]'.format(sum(secW)))

for ax in [ax1, ax2, ax3]:
    ax.set_azimuth_ticks([0,90,180,270], labels=['N', 'E', 'S', 'W'])
    ax.grid(linestyle=':')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))
    
plt.show()
