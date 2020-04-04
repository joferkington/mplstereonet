import matplotlib.pyplot as plt
import mplstereonet

fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111, projection='stereonet')
strike = [200, 250]
dip = [50, 60]
ax.pole(strike, dip, 'go', markersize=10)
ax.grid()
plt.show()

