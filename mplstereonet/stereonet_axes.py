import numpy as np

import matplotlib as mpl
from matplotlib.transforms import Affine2D
from matplotlib.projections import register_projection, LambertAxes
from matplotlib.path import Path
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator

import stereonet_math
import contouring

class StereonetLambertTransform(LambertAxes.LambertTransform):
    def transform_path(self, path):
        # Only interpolate paths with only two points.
        # This will interpolate grid lines but leave more complex paths (e.g.
        # contours) alone. If we don't do this, we'll have problems with
        # contourf and other plotting functions. There should be a better way...
        if len(path.vertices) == 2:
            ipath = path.interpolated(self._resolution)
        else:
            ipath = path
        return Path(self.transform(ipath.vertices), ipath.codes)

class StereonetAxes(LambertAxes):
    """An axis representing a lower-hemisphere "schmitt" (a.k.a. equal area) 
    projection."""
    name = 'stereonet'
    RESOLUTION = 30
    def __init__(self, *args, **kwargs):
        self.horizon = np.radians(90)
        LambertAxes.__init__(self, *args, **kwargs)

    def _get_core_transform(self, resolution):
        return StereonetLambertTransform(
            self._center_longitude,
            self._center_latitude,
            resolution)

    def _get_affine_transform(self):
        transform = self._get_core_transform(1)
        xscale, _ = transform.transform_point((self.horizon, 0))  
        _, yscale = transform.transform_point((0, np.pi / 2.0))
        return Affine2D() \
            .scale(0.5 / xscale, 0.5 / yscale) \
            .translate(0.5, 0.5)

    def _set_lim_and_transforms(self):
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
        self._polar.set_position(pos, which)
        LambertAxes.set_position(self, pos, which)

    def cla(self):
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
        self._polar.set_theta_zero_location('N')
        self._polar.set_theta_direction(-1)
        self._polar.grid(False)
        self._polar.set_rticks([])

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
                the "right hand" direction indicated by the strike, while 180
                degrees or a negative angle correspond to the opposite 
                direction.
            Additional parameters are passed on to `plot`.

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
        contour_kwargs = {}
        contour_kwargs['measurement'] = kwargs.pop('measurement', 'poles')
        contour_kwargs['method'] = kwargs.pop('method', 'exponential_kamb')
        contour_kwargs['sigma'] = kwargs.pop('sigma', 3)
        contour_kwargs['gridsize'] = kwargs.pop('gridsize', 100)
        contour_kwargs['num_counters'] = kwargs.pop('num_counters', None)
        lon, lat, totals = contouring.density_grid(*args, **contour_kwargs)
        return lon, lat, totals, kwargs

    def density_contour(self, *args, **kwargs):
        lon, lat, totals, kwargs = self._contour_helper(args, kwargs)
        return self.contour(lon, lat, totals, **kwargs)

    def density_contourf(self, *args, **kwargs):
        lon, lat, totals, kwargs = self._contour_helper(args, kwargs)
        return self.contourf(lon, lat, totals, **kwargs)


register_projection(StereonetAxes)

