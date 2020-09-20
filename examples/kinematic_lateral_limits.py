""" 
Kinematic analysis with straight vs curved limit lines - you can also choose
for flexural toppling
"""

import matplotlib.pyplot as plt
import mplstereonet.kinematic_analysis as kinematic

P5 = kinematic.PlanarSliding(60, 75)

fig = plt.figure(figsize=(12, 6))

# Plot with curved lateral limit lines
ax1 = fig.add_subplot(1,2,1, projection='stereonet')
P5.plot_kinematic(ax=ax1)
ax1.set_title('Curved lateral limits', loc='left')

# Plot with curved lateral limit lines
ax2 = fig.add_subplot(1,2,2, projection='stereonet')
P5.plot_kinematic(ax=ax2, curved_lateral_limits=False)
ax2.set_title('Straight lateral limits', loc='left')

plt.show()
