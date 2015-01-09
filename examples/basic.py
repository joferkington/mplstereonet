"""
As an example of basic functionality, let's plot a plane, the pole to the
plane, and a rake along the plane.
"""
import matplotlib.pyplot as plt
import mplstereonet

fig = plt.figure()
ax = fig.add_subplot(111, projection='stereonet')

# Measurements follow the right-hand-rule to indicate dip direction
strike, dip = 315, 30

ax.plane(strike, dip, 'g-', linewidth=2)
ax.pole(strike, dip, 'g^', markersize=18)
ax.rake(strike, dip, -25)

ax.grid()

plt.show()
