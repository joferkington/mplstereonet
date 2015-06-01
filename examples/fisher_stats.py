"""
This example shows how the Fisher statistics can be computed and displayed. Using data from:

Fisher, N.I., Lewis, T., Embleton, B.J.J. (1993) "Statistical Analysis of Spherical Data"

---------------------------
Example 5.21 / Example 5.23
---------------------------
Data:           Table B2    (page 279)
Mean Vector:    144.2/57.2  (page 130)
K-Value:        109         (page 130)
Fisher-Angle:   2.7°        (page 132)
"""

import matplotlib.pyplot as plt
import mplstereonet as mpl

fig = plt.figure()
ax = fig.add_subplot(111, projection='stereonet')

decl = [122.5, 130.5, 132.5, 148.5, 140.0, 133.0, 157.5, 153.0, 140.0, 147.5, 142.0, 163.5, 141.0, 156.0, 139.5, 153.5, 151.5, 147.5, 141.0, 143.5, 131.5, 147.5, 147.0, 149.0, 144.0, 139.5]
incl = [55.5, 58.0, 44.0, 56.0, 63.0, 64.5, 53.0, 44.5, 61.5, 54.5, 51.0, 56.0, 59.5, 56.5, 54.0, 47.5, 61.0, 58.5, 57.0, 67.5, 62.5, 63.5, 55.5, 62.0, 53.5, 58.0]
confidence = 95

ax.line(incl, decl, color="#000000", markersize=2)
vector, stats = mpl.find_fisher_stats(incl, decl, conf=confidence)
lbl = "Mean Vector: {}/{}\nConfidence: {} %\nFisher Angle: {}°\nR-Value {}\nK-Value: {}".format(
                round(vector[0], 1), round(vector[1], 1), confidence,
                round(stats[1], 2), round(stats[0], 3), round(stats[2], 2))

ax.line(vector[0], vector[1], color="#ff0000", label=lbl)
ax.cone(vector[0], vector[1], stats[1], facecolor="None", color="#ff0000")

ax.legend(bbox_to_anchor=(1.1, 1.1))
plt.show()
