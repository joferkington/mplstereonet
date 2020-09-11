""" 
Demonstrating more control on the parameters (e.g. friction angle and lateral 
limits) of the analysis and plotting style for planar sliding. Similar for 
wedge and toppling failure.
"""

import matplotlib.pyplot as plt
import mplstereonet
import mplstereonet.kinematic_analysis as kinematic


# Set up the analysis with friction angle and lateral limits
P2 = kinematic.PlanarSliding(strike=0, dip=80, fric_angle=40, latlim=30)

# Plotting
fig, ax = mplstereonet.subplots(figsize=(6,9))
P2.plot_kinematic(
    daylight_kws = {'ec':'b', 'label':'Daylight Envelope'},
    friction_kws = {'ec':'green', 'label':'Friction Cone (40$^\circ$)',
                    'ls':'-.'},
    lateral_kws = {'color':'purple', 'label':'Lateral Limits ($\pm30^\circ$)',
                   'ls':'--'},
    main_kws = {'color':'orange'}, 
    secondary_kws = {'color':'cyan'},
    slope_kws = {'color':'r', 'label':'Slope Face (80/090)'},
    ax=ax)
ax.grid(linestyle=':')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))
plt.show()
