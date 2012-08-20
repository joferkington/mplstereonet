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

Density Contouring
------------------
`mplstereonet` also provides a few different methods of producing contoured
orientation density diagrams.

The `ax.density_contour` and `ax.density_contourf` axes methods provide density
contour lines and filled density contours, respectively.  "Raw" density grids
can be produced with the `mplstereonet.density_grid` function.

As a basic example::

    import matplotlib.pyplot as plt
    import numpy as np
    import mplstereonet
    
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

.. image:: http://joferkington.github.com/mplstereonet/images/contouring.png
    :alt: Orientation density contours.
    :align: center


By default, a modified Kamb method with exponential smoothing [Vollmer1995]_ is
used to estimate the orientation density distribution. Other methods (such as
the "traditional" Kamb [Kamb1956]_ and "Schmidt" (a.k.a. 1%) methods) are
available as well. The method and expected count (in standard deviations) can
be controlled by the `method` and `sigma` keyword arguments, respectively.

.. image:: http://joferkington.github.com/mplstereonet/images/contour_angelier_data.png
    :alt: Orientation density contours.
    :align: center


References
----------

.. [Kamb1956] Kamb, 1959. Ice Petrofabric Observations from Blue Glacier,
       Washington, in Relation to Theory and Experiment. Journal of
       Geophysical Research, Vol. 64, No. 11, pp. 1891--1909.

.. [Vollmer1995] Vollmer, 1995. C Program for Automatic Contouring of Spherical
       Orientation Data Using a Modified Kamb Method. Computers &
       Geosciences, Vol. 21, No. 1, pp. 31--49.


