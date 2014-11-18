def subplots(nrows=1, ncols=1, sharex=False, sharey=False, squeeze=True,
            subplot_kw=None, hemisphere='lower', projection='equal_area',
            **fig_kw):
    """
    Identical to matplotlib.pyplot.subplots, except that this will default to
    producing equal-area stereonet axes.

    This prevents constantly doing:

        >>> fig, ax = plt.subplot(subplot_kw=dict(projection='stereonet'))

    or

        >>> fig = plt.figure()
        >>> ax = fig.add_subplot(111, projection='stereonet')

    Using this function also avoids having ``mplstereonet`` continually appear
    to be an unused import when one of the above methods are used.

    Parameters
    -----------
    nrows : int
      Number of rows of the subplot grid.  Defaults to 1.

    ncols : int
      Number of columns of the subplot grid.  Defaults to 1.

    hemisphere : string
        Currently this has no effect. When upper hemisphere and dual
        hemisphere plots are implemented, this will control which hemisphere
        is displayed.

    projection : string
        The projection for the axes. Defaults to 'equal_area'--an equal-area
        (a.k.a. "Schmidtt") stereonet. May also be 'equal_angle' for an
        equal-angle (a.k.a. "Wulff") stereonet or any other valid matplotlib
        projection (e.g. 'polar' or 'rectilinear' for a "normal" axes).

    The following parameters are identical to matplotlib.pyplot.subplots:

    sharex : string or bool
      If *True*, the X axis will be shared amongst all subplots.  If
      *True* and you have multiple rows, the x tick labels on all but
      the last row of plots will have visible set to *False*
      If a string must be one of "row", "col", "all", or "none".
      "all" has the same effect as *True*, "none" has the same effect
      as *False*.
      If "row", each subplot row will share a X axis.
      If "col", each subplot column will share a X axis and the x tick
      labels on all but the last row will have visible set to *False*.

    sharey : string or bool
        If *True*, the Y axis will be shared amongst all subplots. If
        *True* and you have multiple columns, the y tick labels on all but
        the first column of plots will have visible set to *False*
        If a string must be one of "row", "col", "all", or "none".
        "all" has the same effect as *True*, "none" has the same effect
        as *False*.
        If "row", each subplot row will share a Y axis.
        If "col", each subplot column will share a Y axis and the y tick
        labels on all but the last row will have visible set to *False*.

    *squeeze* : bool
        If *True*, extra dimensions are squeezed out from the
        returned axis object:

        - if only one subplot is constructed (nrows=ncols=1), the
          resulting single Axis object is returned as a scalar.

        - for Nx1 or 1xN subplots, the returned object is a 1-d numpy
          object array of Axis objects are returned as numpy 1-d
          arrays.

        - for NxM subplots with N>1 and M>1 are returned as a 2d
          array.

       If *False*, no squeezing at all is done: the returned axis
        object is always a 2-d array contaning Axis instances, even if it
        ends up being 1x1.

    *subplot_kw* : dict
        Dict with keywords passed to the
        :meth:`~matplotlib.figure.Figure.add_subplot` call used to
        create each subplots.

    *fig_kw* : dict
        Dict with keywords passed to the :func:`figure` call.  Note that all
        keywords not recognized above will be automatically included here.

    Returns
    --------
    fig, ax : tuple

        - *fig* is the :class:`matplotlib.figure.Figure` object

        - *ax* can be either a single axis object or an array of axis
           objects if more than one supblot was created.  The dimensions
           of the resulting array can be controlled with the squeeze
           keyword, see above.
    """
    import matplotlib.pyplot as plt
    if projection in ['equal_area', 'equal_angle']:
        projection += '_stereonet'
    if subplot_kw == None:
        subplot_kw = {}
    subplot_kw['projection'] = projection
    return plt.subplots(nrows, ncols, sharex=sharex, sharey=sharey,
                        squeeze=squeeze, subplot_kw=subplot_kw, **fig_kw)

