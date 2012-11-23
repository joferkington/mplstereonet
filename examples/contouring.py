import matplotlib.pyplot as plt
import numpy as np
import mplstereonet

# Fix random seed so that output is consistent
np.random.seed(1977)

fig, ax = plt.subplots(subplot_kw=dict(projection='stereonet'))

strike, dip = 90, 80
num = 10
strikes = strike + 10 * np.random.randn(num)
dips = dip + 10 * np.random.randn(num)

cax = ax.density_contourf(strikes, dips, measurement='poles')
                          
ax.pole(strikes, dips)
ax.grid(True)
fig.colorbar(cax)

plt.show()
