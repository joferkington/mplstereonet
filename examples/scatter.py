import numpy as np
import matplotlib.pyplot as plt
import mplstereonet
np.random.seed(1)

strikes = np.arange(0, 360, 15)
dips = 45 * np.ones(strikes.size)
magnitude = np.random.random(strikes.size)

# Convert our strikes and dips to stereonet coordinates
lons, lats = mplstereonet.pole(strikes, dips)

# Now we'll plot our data and color by magnitude
fig, ax = mplstereonet.subplots()
sm = ax.scatter(lons, lats, c=magnitude, s=50, cmap='gist_earth')

ax.grid()
plt.show()


