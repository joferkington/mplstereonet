import numpy as np

import matplotlib as mpl
from matplotlib.transforms import Affine2D
from matplotlib.projections import LambertAxes, register_projection
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator

import stereonet_math

class StereonetAxes(LambertAxes):
    """An axis representing a lower-hemisphere "schmitt" (a.k.a. equal area) 
    projection."""
    name = 'stereonet'
    def __init__(self, *args, **kwargs):
        self.horizon = np.radians(90)
        LambertAxes.__init__(self, *args, **kwargs)

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

    def cla(self):
        Axes.cla(self)

        # Set grid defaults...
        self.set_longitude_grid(10)
        self.set_latitude_grid(10)
        self.set_longitude_grid_ends(80)

        # Hide all ticks, but set
        self.xaxis.set_minor_locator(NullLocator())
        self.yaxis.set_minor_locator(NullLocator())
        self.xaxis.set_ticks_position('none')
        self.yaxis.set_ticks_position('none')
        self.xaxis.set_tick_params(label1On=False)
        self.yaxis.set_tick_params(label1On=False)

        self.grid(mpl.rcParams['axes.grid'])

        Axes.set_xlim(self, -self.horizon, self.horizon)
        Axes.set_ylim(self, -np.pi / 2.0, np.pi / 2.0)

        self._initialize_polar()

    def _initialize_polar(self):
        try:
            self._polar
        except AttributeError:
            fig = self.get_figure()
            self._polar = fig.add_axes(self.get_position(True), frameon=False,
                                       projection='polar')
        self._polar.set_theta_zero_location('N')
        self._polar.set_theta_direction(-1)
        self._polar.grid(False)
        self._polar.set_rticks([])
        self._polar.yaxis.set_tick_params(direction='out')

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

    def set_azimuth_ticklabels(self, labels, fontdict=None, **kwargs):
        """
        Sets the labels for the azimuthal ticks.

        Parameters
        ----------
            labels : A sequence of strings
            Additional parameters are text properties for the labels.
        """
        return self._polar.set_xticklabels(labels, fontdict, **kwargs)

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
        """
        lon, lat = stereonet_math.line(plunge, bearing)
        args, kwargs = self._point_plot_defaults(args, kwargs)
        return self.plot([lon], [lat], *args, **kwargs)

    def _point_plot_defaults(self, args, kwargs):
        """To avoid confusion for new users, this ensures that "scattered" 
        points are plotted by by `plot` instead of points joined by a line."""
        if args:
            return args, kwargs

        if 'ls' not in kwargs and 'linestyle' not in kwargs:
            kwargs['linestyle'] = 'none'
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        return args, kwargs

register_projection(StereonetAxes)

