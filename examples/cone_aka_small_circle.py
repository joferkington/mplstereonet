"""
Demonstrates plotting small circles (cones) on a stereonet.
"""
import matplotlib.pyplot as plt
import numpy as np
import mplstereonet

# Generate some scattered strikes and dips
num = 100
strike0, dip0 = 315, 85
strike = np.random.normal(strike0, 5, num)
dip = np.random.normal(dip0, 5, num)

# Convert the strike/dip of the pole to plane to a plunge/bearing
plunge, bearing = mplstereonet.stereonet_math.pole2plunge_bearing(strike0, dip0)

fig, ax = mplstereonet.subplots()
ax.pole(strike, dip, color='k')

# We want the plunge and bearing repeated 3 times for three circles...
plunge, bearing = 3 * list(plunge), 3 * list(bearing)
ax.cone(plunge, bearing, [5, 10, 15], facecolor='', zorder=4, linewidth=2,
        edgecolors=['red', 'green', 'blue'])

plt.show()
