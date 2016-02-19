import matplotlib.pyplot as plt
import numpy as np
import mplstereonet
fig = plt.figure()
ax = fig.add_subplot(111, projection='stereonet',
            center_latitude=np.radians(90), center_longitude=np.radians(0))
ax.plane(315, 10)
ax.grid(True)
plt.show()
