"""
Illustrates fitting an axial plane to two clusters of dip measurements.

In this case, we're faking it by using Anglier's fault orientation data,
but pretend these were bedding dips in two limbs of a fold instead of fault
orientations.

The steps mimic what you'd do graphically:

    1. Find the centers of the two modes of the bedding measurements
    2. Fit a girdle to them to find the plunge axis of the fold
    3. Find the midpoint along that girdle between the two centers
    4. The axial plane will be the girdle that fits the midpoint and plunge
       axis of the fold.
"""
import matplotlib.pyplot as plt
import mplstereonet

import parse_angelier_data

# Load data from Angelier, 1979
strike, dip, rake = parse_angelier_data.load()

# Plot the raw data and contour it:
fig, ax = mplstereonet.subplots()
ax.density_contour(strike, dip, rake, measurement='rakes', cmap='gist_earth',
                    sigma=1.5)
ax.rake(strike, dip, rake, marker='.', color='black')

# Find the two modes
centers = mplstereonet.kmeans(strike, dip, rake, num=2, measurement='rakes')
strike_cent, dip_cent = mplstereonet.geographic2pole(*zip(*centers))
ax.pole(strike_cent, dip_cent, 'ro', ms=12)

# Fit a girdle to the two modes
# The pole of this plane will be the plunge of the fold axis
axis_s, axis_d = mplstereonet.fit_girdle(*zip(*centers), measurement='radians')
ax.plane(axis_s, axis_d, color='green')
ax.pole(axis_s, axis_d, color='green', marker='o', ms=15)

# Now we'll find the midpoint. We could project the centers as rakes on the
# plane we just fit, but it's easier to get their mean vector instead.
mid, _ = mplstereonet.find_mean_vector(*zip(*centers), measurement='radians')
midx, midy = mplstereonet.line(*mid)

# Now let's find the axial plane by fitting another girdle to the midpoint
# and the pole of the plunge axis.
xp, yp = mplstereonet.pole(axis_s, axis_d)

x, y = [xp, midx], [yp, midy]
axial_s, axial_dip = mplstereonet.fit_girdle(x, y, measurement='radians')

ax.plane(axial_s, axial_dip, color='lightblue', lw=3)

plt.show()
