"""
Find the intersection of two planes and plot it.
"""
import matplotlib.pyplot as plt
import mplstereonet

strike1, dip1 = 315, 30
strike2, dip2 = 120, 40

fig, ax = mplstereonet.subplots()

# Plot the two planes...
ax.plane(strike1, dip1)
ax.plane(strike2, dip2)

# Find the intersection of the two as a plunge/bearing
plunge, bearing = mplstereonet.plane_intersection(strike1, dip1, strike2, dip2)

# Plot the plunge/bearing
ax.line(plunge, bearing, marker='*', markersize=15)

plt.show()

