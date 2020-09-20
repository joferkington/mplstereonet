""" Basic plots of three failure modes"""

import matplotlib.pyplot as plt
import mplstereonet.kinematic_analysis as kinematic

# Set up analyses
strike, dip = 200, 75
P1 = kinematic.PlanarSliding(strike, dip)
T1 = kinematic.FlexuralToppling(strike, dip)
W1 = kinematic.WedgeSliding(strike, dip)

# Start plotting
fig = plt.figure(figsize=(15, 6))

# Plot planar sliding
ax1 = fig.add_subplot(131, projection='stereonet')
P1.plot_kinematic(ax=ax1)
ax1.set_title('Planar Sliding', loc='left')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))

# Plot flexural toppling
ax2 = fig.add_subplot(132, projection='stereonet')
T1.plot_kinematic(ax=ax2)
ax2.set_title('Flexural Toppling', loc='left')
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))

# Plot wedge sliding
ax3 = fig.add_subplot(133, projection='stereonet')
W1.plot_kinematic(ax=ax3)
ax3.set_title('Wedge Sliding', loc='left')
ax3.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))

plt.show()
