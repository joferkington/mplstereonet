mplstereonet
============
`mplstereonet` provides lower-hemisphere equal-area stereonets for matplotlib.

Basic Usage
-----------
In most cases, you'll want to ``import mplstereonet`` and then make an axes
with ``projection="stereonet"``.

As an example::

    import matplotlib.pyplot as plt
    import mplstereonet

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='stereonet')

    strike, dip = 315, 30
    ax.plane(strike, dip, 'g-', linewidth=2)
    ax.pole(strike, dip, 'g^', markersize=18)
    ax.rake(strike, dip, -25)
    ax.grid()

    plt.show()

.. image:: http://joferkington.github.com/mplstereonet/images/basic.png
    :alt: A basic stereonet with a plane, pole to the plane, and rake along the plane
    :align: center
    
Planes, lines, poles, and rakes can be plotted using axes methods (e.g.
``ax.line(plunge, bearing)`` or ``ax.rake(strike, dip, rake_angle)``).

All planar measurements are expected to follow the right-hand-rule to indicate
dip direction. As an example, 315/30S would be 135/30 follwing the right-hand
rule.


