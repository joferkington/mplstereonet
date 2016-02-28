import matplotlib.pyplot as plt
import mplstereonet

fig, ax = mplstereonet.subplots()

strike, dip = 315, 30
ax.plane(strike, dip, color='lightblue')
ax.pole(strike, dip, color='green', markersize=15)
ax.rake(strike, dip, 40, marker='*', markersize=20, color='green')

ax.grid(kind='polar')
ax.set_title('Polar overlay on a Stereonet', y=1.1)
fig.subplots_adjust(top=0.8)

plt.show()
