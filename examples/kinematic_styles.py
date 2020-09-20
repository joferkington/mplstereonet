""" 
Demonstrating more control on the parameters (e.g. friction angle and lateral 
limits) of the analysis and plotting style for planar sliding and toppling 
failure. Similar for wedge failure.
"""

import matplotlib.pyplot as plt
import mplstereonet
import mplstereonet.kinematic_analysis as kinematic

# Set up the analysis with friction angle and lateral limits
P2 = kinematic.PlanarSliding(strike=0, dip=80, fric_angle=40, latlim=30)
T2 = kinematic.FlexuralToppling(strike=0, dip=80, fric_angle=40, latlim=30)

# Start plotting
fig, (ax1, ax2) = mplstereonet.subplots(ncols=2, figsize=(12,9))

# Customizing with the kwargs - example with planar sliding failure
P2.plot_kinematic(
    daylight_kws = {'ec':'b', 'label':'Daylight Envelope'},
    friction_kws = {'ec':'green', 'label':'Friction Cone (40$^\circ$)',
                    'ls':'-.'},
    lateral_kws = {'color':'purple', 'label':'Lateral Limits ($\pm30^\circ$)',
                   'ls':'--'},
    main_kws = {'color':'orange'}, 
    secondary_kws = {'color':'cyan'},
    slope_kws = {'color':'r', 'label':'Slope Face (80/090)'},
    ax=ax1)
ax1.grid(linestyle=':')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))

# Or alternatively, elements in the plot can be customized with the output 
# artists - example with flexural toppling failure
T2_artists = T2.plot_kinematic(ax=ax2)
plt.setp(T2_artists['main'], color='orange')
plt.setp(T2_artists['slope'], color='r', label='Slope Face (80/090)')
plt.setp(T2_artists['slip'], color='b',
         label='Slip Limit (Friction angle 40$^\circ$)')
plt.setp(T2_artists['lateral'], color='purple', ls='--')
# Set label on one lateral limit artist only to avoid duplicated labels
plt.setp(T2_artists['lateral'][0], label='Lateral Limits ($\pm30^\circ$)')
ax2.grid(linestyle=':')
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))

plt.show()
