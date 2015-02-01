"""
In this example two planes are plottet as great circles and poles.
The planes are given as dip-direction/dip and converted to strike/dip.
The strikes and dips are passed to the 'mplstereonet.fit_girdle()' function
that calculates the best fitting plane for the poles of the planes.
The resulting plane is the optimal cross-section plane for this structure.
The pole of the resulting plane would correspond to the intersection-linear
when looking at schistosities or the fold-axis when looking at fold-hinges.
"""
import matplotlib.pyplot as plt
import numpy as np
import mplstereonet

fig, ax = mplstereonet.subplots()

dip_directions = [100, 200]
dips = [30, 40]
strikes = np.array(dip_directions) - 90

ax.pole(strikes, dips, "bo")
ax.plane(strikes, dips, color='black', lw=1)

fit_strike, fit_dip = mplstereonet.fit_girdle(strikes, dips)

ax.plane(fit_strike, fit_dip, color='red', lw=1)
ax.pole(fit_strike, fit_dip, marker='o', color='red', markersize=5)

plt.show()
