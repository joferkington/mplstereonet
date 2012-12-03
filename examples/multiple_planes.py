"""
`plane`, `rake`, `line`, etc all allow plotting of multiple measurements.
"""
import matplotlib.pyplot as plt
import mplstereonet

# Make a figure with a single stereonet axes
fig, ax = mplstereonet.subplots()

# These follow the right hand rule to indicate dip direction
strikes = [22, 317, 170, 220]
dips = [10, 20, 30, 40]

# Plot the planes.
ax.plane(strikes, dips)

# Make only a single "N" azimuth tick label.
ax.set_azimuth_ticks([0], labels=['N'])

plt.show()
