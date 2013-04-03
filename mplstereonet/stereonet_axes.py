import numpy as np

import matplotlib as mpl
from matplotlib.transforms import Affine2D
from matplotlib.projections import register_projection, LambertAxes
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator

from . import stereonet_math
from . import contouring
from . import stereonet_transforms

class StereonetAxes(LambertAxes):
    """An axes representing a lower-hemisphere "schmitt" (a.k.a. equal area) 
    projection."""
    name = 'stereonet'
    RESOLUTION = 30
    _base_transform = stereonet_transforms.LambertTransform

    def __init__(self, *args, **kwargs):
        """Initialization is identical to a normal Axes object except for the
        following kwarg:

        Parameters:
        -----------
            rotation : number
                The rotation of the stereonet in degrees clockwise from North.

        All additional args and kwargs are identical to Axes.__init__
        """
        # There's also center_latitude and center_longitude, but I'm 
        # deliberately keeping these undocumented until they're fully supported.
        self.horizon = np.radians(90)
        self._rotation = -np.radians(kwargs.pop('rotation', 0))
        LambertAxes.__init__(self, *args, **kwargs)

    def _get_core_transform(self, resolution):
        """The projection for the stereonet as a matplotlib transform. This is
        primarily called by LambertAxes._set_lim_and_transforms."""
        return self._base_transform(self._center_longitude,
                                    self._center_latitude,
                                    resolution)

    def _get_affine_transform(self):
        """The affine portion of the base transform. This is called by 
        LambertAxes._set_lim_and_transforms."""
        transform = self._get_core_transform(self.RESOLUTION)
        # How big is the projected globe?
        xscale, _ = transform.transform_point((self.horizon, 0))  
        _, yscale = transform.transform_point((0, np.pi / 2.0))
        # Create an affine transform to stretch the projection from 0-1
        return Affine2D() \
            .rotate(np.radians(self.rotation)) \
            .scale(0.5 / xscale, 0.5 / yscale) \
            .translate(0.5, 0.5)

    def _set_lim_and_transforms(self):
        """Setup the key transforms for the axes.""" 
        # Most of the transforms are set up correctly by LambertAxes
        LambertAxes._set_lim_and_transforms(self)

        # Transform for latitude ticks. These are typically unused, but just
        # in case we need them...
        yaxis_stretch = Affine2D().scale(2 * self.horizon, 1.0)
        yaxis_stretch = yaxis_stretch.translate(-self.horizon, 0.0)

        # These are identical to LambertAxes._set_lim_and_transforms, but we 
        # need to update things to reflect the new "yaxis_stretch"
        yaxis_space = Affine2D().scale(1.0, 1.1)
        self._yaxis_transform = \
            yaxis_stretch + \
            self.transData
        yaxis_text_base = \
            yaxis_stretch + \
            self.transProjection + \
            (yaxis_space + \
             self.transAffine + \
             self.transAxes)
        self._yaxis_text1_transform = \
            yaxis_text_base + \
            Affine2D().translate(-8.0, 0.0)
        self._yaxis_text2_transform = \
            yaxis_text_base + \
            Affine2D().translate(8.0, 0.0)

    def set_position(self, pos, which='both'):
        """Identical to Axes.set_position (This docstring is overwritten)."""
        self._polar.set_position(pos, which)
        LambertAxes.set_position(self, pos, which)
    set_position.__doc__ = Axes.set_position.__doc__

    def set_rotation(self, rotation):
        """Set the rotation of the stereonet in degrees clockwise from North."""
        self._rotation = np.radians(rotation)
        self._polar.set_theta_offset(self._rotation + np.pi / 2.0)
        self.transData.invalidate()
        self.transAxes.invalidate()
        self._set_lim_and_transforms()
    def get_rotation(self):
        """The rotation of the stereonet in degrees clockwise from North."""
        return np.degrees(self._rotation)
    rotation = property(get_rotation, set_rotation)

    def cla(self):
        """Identical to Axes.cla (This docstring is overwritten)."""
        Axes.cla(self)

        # Set grid defaults...
        self.set_longitude_grid(10)
        self.set_latitude_grid(10)
        self.set_longitude_grid_ends(80)

        # Hide all ticks and tick labels for the "native" lon and lat axes
        self.xaxis.set_minor_locator(NullLocator())
        self.yaxis.set_minor_locator(NullLocator())
        self.xaxis.set_ticks_position('none')
        self.yaxis.set_ticks_position('none')
        self.xaxis.set_tick_params(label1On=False)
        self.yaxis.set_tick_params(label1On=False)

        # Set the grid on or off based on the rc params.
        self.grid(mpl.rcParams['axes.grid'])

        # Set the default limits (so that the "native" ticklabels will be
        # correct if they're turned back on)...
        Axes.set_xlim(self, -self.horizon, self.horizon)
        Axes.set_ylim(self, -np.pi / 2.0, np.pi / 2.0)

        # Set up the azimuth ticks.
        self._polar.set_theta_offset(np.radians(self.rotation + 90))
        self._polar.set_theta_direction(-1)
        self._polar.grid(False)
        self._polar.set_rticks([])
    cla.__doc__ = Axes.cla.__doc__

    @property
    def _polar(self):
        """The "hidden" polar axis used for azimuth labels."""
        # This will be called inside LambertAxes.__init__ as well as every
        # time the axis is cleared, so we need the try/except to avoid having
        # multiple hidden axes when `cla` is _manually_ called.
        try:
            return self._hidden_polar_axes
        except AttributeError:
            fig = self.get_figure()
            self._hidden_polar_axes = fig.add_axes(self.get_position(True), 
                                        frameon=False, projection='polar')
            return self._hidden_polar_axes

    def set_azimuth_ticks(self, angles, labels=None, frac=None, **kwargs):
        """
        Sets the azimuthal tick locations (Note: tick lines are not currently
        drawn or supported.).  

        Parameters
        ----------
            angles : A sequence of floats specifying the tick locations in 
                degrees.
            labels : A sequence of strings to use as a label at each location.
                Defaults to a formatted version of the specified angles.
            frac : The radial location of the tick labels. 1.0 is the along the
                edge, 1.1 would be outside, and 0.9 would be inside.
            Additional parameters are text properties for the labels.
        """
        return self._polar.set_thetagrids(angles, labels, frac, **kwargs)

    def get_azimuth_ticks(self, minor=False):
        return self._polar.get_xticks(minor)

    def set_azimuth_ticklabels(self, labels, fontdict=None, **kwargs):
        """
        Sets the labels for the azimuthal ticks.

        Parameters
        ----------
            labels : A sequence of strings
            Additional parameters are text properties for the labels.
        """
        return self._polar.set_xticklabels(labels, fontdict, **kwargs)

    def get_azimuth_ticklabels(self, minor=False):
        """Get the azimuth tick labels as a list of Text artists."""
        return self._polar.get_xticklabels(minor)

    def plane(self, strike, dip, *args, **kwargs):
        """
        Plot lines representing planes on the axes. Additional arguments and
        keyword arguments are passed on to `ax.plot`.

        `strike` and `dip` may be sequences or single values.
    
        Parameters
        ----------
            strike, dip : The strike and dip of the plane(s) in degrees. The 
                dip direction is defined by the strike following the 
                "right-hand rule". 
            segments : The number of segments to use for the line. Defaults
                to 100 segments.
            Additional parameters are passed on to `plot`.

        Returns
        -------
            A sequence of Line2D artists representing the lines specified by
            `strike` and `dip`.
        """
        segments = kwargs.pop('segments', 100)
        lon, lat = stereonet_math.plane(strike, dip, segments)
        return self.plot(lon, lat, *args, **kwargs)

    def pole(self, strike, dip, *args, **kwargs):
        """
        Plot points representing poles to planes on the axes. Additional
        arguments and keyword arguments are passed on to `ax.plot`.

        `strike` and `dip` may be sequences or single values.

        Parameters
        ----------
            strike, dip : The strike and dip of the plane(s) in degrees. The 
                dip direction is defined by the strike following the 
                "right-hand rule". 
            Additional parameters are passed on to `plot`.

        Returns
        -------
            A sequence of Line2D artists representing the point(s) specified by
            `strike` and `dip`.
        """
        lon, lat = stereonet_math.pole(strike, dip)
        args, kwargs = self._point_plot_defaults(args, kwargs)
        return self.plot(lon, lat, *args, **kwargs)

    def rake(self, strike, dip, rake_angle, *args, **kwargs):
        """
        Plot points representing lineations along planes on the axes.
        Additional arguments and keyword arguments are passed on to `plot`.

        `strike`, `dip`, and `rake_angle` may be sequences or single values.

        Parameters
        ----------
            strike, dip : The strike and dip of the plane(s) in degrees. The 
                dip direction is defined by the strike following the 
                "right-hand rule". 
            rake_angle : The angle of the lineation(s) on the plane(s) measured 
                in degrees downward from horizontal. Zero degrees corresponds to 
                the "right hand" direction indicated by the strike, while
                negative angles are measured downward from the opposite strike
                direction.
            Additional arguments are passed on to `plot`.

        Returns
        -------
            A sequence of Line2D artists representing the point(s) specified by
            `strike` and `dip`.
        """
        lon, lat = stereonet_math.rake(strike, dip, rake_angle)
        args, kwargs = self._point_plot_defaults(args, kwargs)
        return self.plot(lon, lat, *args, **kwargs)

    def line(self, plunge, bearing, *args, **kwargs):
        """
        Plot points representing linear features on the axes. Additional
        arguments and keyword arguments are passed on to `plot`.

        `plunge` and `bearing` may be sequences or single values.
    
        Parameters
        ----------
            plunge, bearing : The plunge and bearing of the line(s) in degrees.
                The plunge is measured in degrees downward from the end of the
                feature specified by the bearing. 
            Additional parameters are passed on to `plot`.

        Returns
        -------
            A sequence of Line2D artists representing the point(s) specified by
            `strike` and `dip`.
        """
        lon, lat = stereonet_math.line(plunge, bearing)
        args, kwargs = self._point_plot_defaults(args, kwargs)
        return self.plot([lon], [lat], *args, **kwargs)

    def _point_plot_defaults(self, args, kwargs):
        """To avoid confusion for new users, this ensures that "scattered" 
        points are plotted by by `plot` instead of points joined by a line.
        
        Parameters
        ----------
            args : A tuple of arguments representing additional parameters to be 
                passed to `self.plot`.
            kwargs : A dict of keyword arguments representing additional 
                parameters to be passed to `self.plot`
        Returns
        -------
            Modified versions of `args` and `kwargs`.
        """
        if args:
            return args, kwargs

        if 'ls' not in kwargs and 'linestyle' not in kwargs:
            kwargs['linestyle'] = 'none'
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        return args, kwargs

    def _contour_helper(self, args, kwargs):
        """Unify defaults and common functionality of density_contour and 
        density_contourf."""
        contour_kwargs = {}
        contour_kwargs['measurement'] = kwargs.pop('measurement', 'poles')
        contour_kwargs['method'] = kwargs.pop('method', 'exponential_kamb')
        contour_kwargs['sigma'] = kwargs.pop('sigma', 3)
        contour_kwargs['gridsize'] = kwargs.pop('gridsize', 100)
        contour_kwargs['num_counters'] = kwargs.pop('num_counters', None)
        lon, lat, totals = contouring.density_grid(*args, **contour_kwargs)
        return lon, lat, totals, kwargs

    def density_contour(self, *args, **kwargs):
        """
        Estimates point density of the given linear orientation measurements 
        (Interpreted as poles, lines, rakes, or "raw" longitudes and latitudes
        based on the `measurement` keyword argument.) and plots contour lines of
        the resulting density distribution.

        Parameters
        ----------
            *args : A variable number of sequences of measurements. 
                By default, this will be expected to be `strike` & `dip`, both
                array-like sequences representing poles to planes.  (Rake
                measurements require three parameters, thus the variable number
                of arguments.) The `measurement` kwarg controls how these 
                arguments are interpreted.
            measurement : string, optional 
                Controls how the input arguments are interpreted. Defaults to
                "poles".  May be one of the following:
                    "poles" : Arguments are assumed to be sequences of strikes
                        and dips of planes. Poles to these planes are used for
                        density contouring.
                    "lines" : Arguments are assumed to be sequences of plunges
                        and bearings of linear features.  
                    "rakes" : Arguments are assumed to be sequences of strikes,
                        dips, and rakes along the plane.
                    "radians" : Arguments are assumed to be "raw" longitudes
                        and latitudes in the underlying projection's coordinate
                        system.
            method : string, optional 
                The method of density estimation to use. Defaults to
                "exponential_kamb". May be one of the following:
                "exponential_kamb" : A modified Kamb method using exponential 
                    smoothing _[1]. Units are in numbers of standard deviations
                    by which the density estimate differs from uniform.
                "linear_kamb" : A modified Kamb method using linear smoothing 
                    _[1]. Units are in numbers of standard deviations by which
                    the density estimate differs from uniform.
                "kamb" : Kamb's method _[2] with no smoothing. Units are in
                    numbers of standard deviations by which the density
                    estimate differs from uniform.
                "schmidt" : The traditional "Schmidt" (a.k.a. 1%) method. Counts
                    points within a counting circle comprising 1% of the total
                    area of the hemisphere. Does not take into account sample
                    size. Units are in points per 1% area.
            sigma : int or float, optional
                The number of standard deviations defining the expected number
                of standard deviations by which a random sample from a uniform
                distribution of points would be expected to vary from being 
                evenly distributed across the hemisphere.  This controls the 
                size of the counting circle, and therefore the degree of 
                smoothing.  Higher sigmas will lead to more smoothing of the
                resulting density distribution. This parameter only applies to 
                Kamb-based methods.  Defaults to 3.
            gridsize : int or 2-item tuple of ints, optional
                The size of the grid that the density is estimated on. If a 
                single int is given, it is interpreted as an NxN grid. If a
                tuple of ints is given it is interpreted as (nrows, ncols). 
                Defaults to 100.
            num_counters : int, optional
                The number of "counting points" (arranged following a golden 
                section spiral) that density is estimated at on the surface of
                hemisphere.  This is then interpolated onto a regular grid in
                lat-long space (see "gridsize" above). Defaults to 1/2 of the
                total number of cells in the regular grid.

            Additional keyword arguments are passed on to matplotlib's `contour`
            function.

        Returns:
        --------
            A matplotlib ContourSet.

        See Also:
        ---------
            mplstereonet.density_grid
            mplstereonet.StereonetAxes.density_contourf
            matplotlib.pyplot.contour
            matplotlib.pyplot.clabel


        Examples:
        ---------
            Plot density contours of poles to the specified planes using a
            modified Kamb method with exponential smoothing [1]_.

            >>> strikes, dips = [120, 315, 86], [22, 85, 31]
            >>> ax.density_contour(strikes, dips)

            Plot density contours of a set of linear orientation measurements.

            >>> plunges, bearings = [-10, 20, -30], [120, 315, 86]
            >>> ax.density_contour(plunges, bearings, measurement='lines')

            Plot density contours of a set of rake measurements.

            >>> strikes, dips, rakes = [120, 315, 86], [22, 85, 31], [-5, 20, 9]
            >>> ax.density_contour(strikes, dips, rakes, measurement='rakes')

            Plot density contours of a set of "raw" longitudes and latitudes.

            >>> lon, lat = np.radians([-40, 30, -85]), np.radians([21, -59, 45])
            >>> ax.density_contour(lon, lat, measurement='radians')


            Plot density contours of poles to planes using a Kamb method [2]_
            with the density estimated on a 10x10 grid (in long-lat space) 

            >>> strikes, dips = [120, 315, 86], [22, 85, 31]
            >>> ax.density_contour(strikes, dips, method='kamb', gridsize=10)

            Plot density contours of poles to planes with contours at [1,2,3]
            standard deviations.

            >>> strikes, dips = [120, 315, 86], [22, 85, 31]
            >>> ax.density_contour(strikes, dips, levels=[1,2,3])

        References
        ----------
        .. [1] Vollmer, 1995. C Program for Automatic Contouring of Spherical
           Orientation Data Using a Modified Kamb Method. Computers &
           Geosciences, Vol. 21, No. 1, pp. 31--49.

        .. [2] Kamb, 1959. Ice Petrofabric Observations from Blue Glacier,
           Washington, in Relation to Theory and Experiment. Journal of
           Geophysical Research, Vol. 64, No. 11, pp. 1891--1909.
        """
        lon, lat, totals, kwargs = self._contour_helper(args, kwargs)
        return self.contour(lon, lat, totals, **kwargs)

    def density_contourf(self, *args, **kwargs):
        """
        Estimates point density of the given linear orientation measurements 
        (Interpreted as poles, lines, rakes, or "raw" longitudes and latitudes
        based on the `measurement` keyword argument.) and plots filled contours
        of the resulting density distribution.

        Parameters
        ----------
            *args : A variable number of sequences of measurements. 
                By default, this will be expected to be `strike` & `dip`, both
                array-like sequences representing poles to planes.  (Rake
                measurements require three parameters, thus the variable number
                of arguments.) The `measurement` kwarg controls how these 
                arguments are interpreted.
            measurement : string, optional 
                Controls how the input arguments are interpreted. Defaults to
                "poles".  May be one of the following:
                    "poles" : Arguments are assumed to be sequences of strikes
                        and dips of planes. Poles to these planes are used for
                        density contouring.
                    "lines" : Arguments are assumed to be sequences of plunges
                        and bearings of linear features.  
                    "rakes" : Arguments are assumed to be sequences of strikes,
                        dips, and rakes along the plane.
                    "radians" : Arguments are assumed to be "raw" longitudes
                        and latitudes in the underlying projection's coordinate
                        system.
            method : string, optional 
                The method of density estimation to use. Defaults to
                "exponential_kamb". May be one of the following:
                "exponential_kamb" : A modified Kamb method using exponential 
                    smoothing _[1]. Units are in numbers of standard deviations
                    by which the density estimate differs from uniform.
                "linear_kamb" : A modified Kamb method using linear smoothing 
                    _[1]. Units are in numbers of standard deviations by which
                    the density estimate differs from uniform.
                "kamb" : Kamb's method _[2] with no smoothing. Units are in
                    numbers of standard deviations by which the density
                    estimate differs from uniform.
                "schmidt" : The traditional "Schmidt" (a.k.a. 1%) method. Counts
                    points within a counting circle comprising 1% of the total
                    area of the hemisphere. Does not take into account sample
                    size. Units are in points per 1% area.
            sigma : int or float, optional
                The number of standard deviations defining the expected number
                of standard deviations by which a random sample from a uniform
                distribution of points would be expected to vary from being 
                evenly distributed across the hemisphere.  This controls the 
                size of the counting circle, and therefore the degree of 
                smoothing.  Higher sigmas will lead to more smoothing of the
                resulting density distribution. This parameter only applies to 
                Kamb-based methods.  Defaults to 3.
            gridsize : int or 2-item tuple of ints, optional
                The size of the grid that the density is estimated on. If a 
                single int is given, it is interpreted as an NxN grid. If a
                tuple of ints is given it is interpreted as (nrows, ncols).
                Defaults to 100.
            num_counters : int, optional
                The number of "counting points" (arranged following a golden 
                section spiral) that density is estimated at on the surface of
                hemisphere.  This is then interpolated onto a regular grid in
                lat-long space (see "gridsize" above). Defaults to 1/2 of the
                total number of cells in the regular grid.

            Additional keyword arguments are passed on to matplotlib's
            `contourf` function.

        Returns:
        --------
            A matplotlib `QuadContourSet`.

        See Also:
        ---------
            `mplstereonet.density_grid`
            `mplstereonet.StereonetAxes.density_contour`
            `matplotlib.pyplot.contourf`
            `matplotlib.pyplot.clabel`


        Examples:
        ---------
            Plot filled density contours of poles to the specified planes using
            a modified Kamb method with exponential smoothing [1]_.

            >>> strikes, dips = [120, 315, 86], [22, 85, 31]
            >>> ax.density_contourf(strikes, dips)

            Plot filled density contours of a set of linear orientation
            measurements.

            >>> plunges, bearings = [-10, 20, -30], [120, 315, 86]
            >>> ax.density_contourf(plunges, bearings, measurement='lines')

            Plot filled density contours of a set of rake measurements.

            >>> strikes, dips, rakes = [120, 315, 86], [22, 85, 31], [-5, 20, 9]
            >>> ax.density_contourf(strikes, dips, rakes, measurement='rakes')

            Plot filled density contours of a set of "raw" longitudes and
            latitudes.

            >>> lon, lat = np.radians([-40, 30, -85]), np.radians([21, -59, 45])
            >>> ax.density_contourf(lon, lat, measurement='radians')


            Plot filled density contours of poles to planes using a Kamb method
            [2]_ with the density estimated on a 10x10 grid (in long-lat space) 

            >>> strikes, dips = [120, 315, 86], [22, 85, 31]
            >>> ax.density_contourf(strikes, dips, method='kamb', gridsize=10)

            Plot filled density contours of poles to planes with contours at
            [1,2,3] standard deviations.

            >>> strikes, dips = [120, 315, 86], [22, 85, 31]
            >>> ax.density_contourf(strikes, dips, levels=[1,2,3])

        References
        ----------
        .. [1] Vollmer, 1995. C Program for Automatic Contouring of Spherical
           Orientation Data Using a Modified Kamb Method. Computers &
           Geosciences, Vol. 21, No. 1, pp. 31--49.

        .. [2] Kamb, 1959. Ice Petrofabric Observations from Blue Glacier,
           Washington, in Relation to Theory and Experiment. Journal of
           Geophysical Research, Vol. 64, No. 11, pp. 1891--1909.
        """
        lon, lat, totals, kwargs = self._contour_helper(args, kwargs)
        return self.contourf(lon, lat, totals, **kwargs)


class EqualAngleAxes(StereonetAxes):
    """An axes representing a lower-hemisphere "Wulff" (a.k.a. equal angle) 
    projection."""
    _base_transform = stereonet_transforms.StereographicTransform
    name = 'equal_angle_stereonet'

class EqualAreaAxes(StereonetAxes):
    """An axes representing a lower-hemisphere "Schmitt" (a.k.a. equal area) 
    projection."""
    name = 'equal_area_stereonet'

register_projection(StereonetAxes)
register_projection(EqualAreaAxes)
register_projection(EqualAngleAxes)

