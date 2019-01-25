import numpy as np
from matplotlib.path import Path
from matplotlib.transforms import Transform

class BaseStereonetTransform(Transform):
    """An abstract base class for all forward and inverse transforms relating
    to stereonets. Not meant to be initiated directly."""
    input_dims = 2
    output_dims = 2
    is_separable = False

    def __init__(self, center_longitude, center_latitude, resolution):
        """
        Create a new transform.  Resolution is the number of steps to
        interpolate between each input line segment to approximate its path in
        projected space.
        """
        Transform.__init__(self)
        self._resolution = resolution
        self._center_longitude = center_longitude
        self._center_latitude = center_latitude

    def transform_path_non_affine(self, path):
        # Only interpolate paths with only two points.
        # This will interpolate grid lines but leave more complex paths (e.g.
        # contours) alone. If we don't do this, we'll have problems with
        # contourf and other plotting functions. There should be a better way...
        # We also need to skip interpolating paths that explicitly ask to not
        # be interpolated (e.g. a Line2D path with 2 points)
        if path._interpolation_steps == 1:
            ipath = path
        elif len(path.vertices) == 2:
            ipath = path.interpolated(self._resolution)
        else:
            ipath = path
        return Path(self.transform(ipath.vertices), ipath.codes)
    transform_path_non_affine.__doc__ = \
            Transform.transform_path_non_affine.__doc__

    # We need to override transform_path with mpl <= v1.1.x, as well. See
    # <http://matplotlib.org/1.1.1/examples/api/custom_projection_example.html>
    # for a full discussion...
    transform_path = transform_path_non_affine
    transform_path.__doc__ = Transform.transform_path.__doc__

    # For older (v1.1.x) versions of matplotlib, we need to implement transform
    # explicitly, instead of just "transform_non_affine" (and implementing
    # the non-affine portion directly as "transform" causes major problems with
    # v1.2.x and newer)
    def transform(self, ll):
        return self.transform_affine(self.transform_non_affine(ll))
    transform.__doc__ = Transform.transform.__doc__

    def inverted(self):
        """Return the inverse of the transform."""
        # This is a bit of hackery so that we can put a single "inverse"
        # function here. If we just made "self._inverse_type" point to the class
        # in question, it wouldn't be defined yet. This way, it's done at
        # at runtime and we avoid the definition problem. Hackish, but better
        # than repeating code everywhere or making a relatively complex
        # metaclass.
        inverse_type = globals()[self._inverse_type]
        return inverse_type(self._center_longitude, self._center_latitude,
                            self._resolution)
    inverted.__doc__ = Transform.inverted.__doc__



# Both the Lambert and Stereographic projections are very mathematically
# similar, so we'll inherit from base classes that describes the common math.
class BaseForwardTransform(BaseStereonetTransform):
    """A base class for both Lambert and Stereographic forward transforms."""
    _inverse_type = 'BaseInvertedTransform'
    def transform_non_affine(self, ll):
        longitude = ll[:, 0:1]
        latitude  = ll[:, 1:2]
        clong = self._center_longitude
        clat = self._center_latitude
        cos_lat = np.cos(latitude)
        sin_lat = np.sin(latitude)
        diff_long = longitude - clong
        cos_diff_long = np.cos(diff_long)

        inner_k = (1.0 +
                   np.sin(clat)*sin_lat +
                   np.cos(clat)*cos_lat*cos_diff_long)
        # Prevent divide-by-zero problems
        inner_k = np.where(inner_k == 0.0, 1e-15, inner_k)
        k = self._calculate_k(inner_k)
        x = k*cos_lat*np.sin(diff_long)
        y = k*(np.cos(clat)*sin_lat -
               np.sin(clat)*cos_lat*cos_diff_long)

        return np.concatenate((x, y), 1)
    transform_non_affine.__doc__ = \
            BaseStereonetTransform.transform_non_affine.__doc__

    def _calculate_k(self, inner_k):
        """Subclasses must implement!."""
        pass

class BaseInvertedTransform(BaseStereonetTransform):
    """A base class for both Lambert and Stereographic inverse transforms."""
    _inverse_type = 'BaseForwardTransform'
    def transform_non_affine(self, xy):
        x = xy[:, 0:1]
        y = xy[:, 1:2]
        clong = self._center_longitude
        clat = self._center_latitude
        p = np.sqrt(x*x + y*y)
        p = np.where(p == 0.0, 1e-9, p)
        c = self._calculate_c(p)
        sin_c = np.sin(c)
        cos_c = np.cos(c)

        lat = np.arcsin(cos_c*np.sin(clat) + ((y*sin_c*np.cos(clat)) / p))
        lon = clong + np.arctan(
                (x*sin_c) / (p*np.cos(clat)*cos_c - y*np.sin(clat)*sin_c))

        return np.concatenate((lon, lat), 1)
    transform_non_affine.__doc__ = \
            BaseStereonetTransform.transform_non_affine.__doc__


    def _calculate_c(self, p):
        """Subclasses must implement!."""
        pass

class LambertTransform(BaseForwardTransform):
    """The Lambert (a.k.a. "equal area") forward transform."""
    _inverse_type = 'InvertedLambertTransform'
    def _calculate_k(self, inner_k):
        return np.sqrt(2.0 / inner_k)

class InvertedLambertTransform(BaseInvertedTransform):
    """The Lambert (a.k.a. "equal area") inverse transform."""
    _inverse_type = 'LambertTransform'
    def _calculate_c(self, p):
        return 2.0 * np.arcsin(0.5 * p)

class StereographicTransform(BaseForwardTransform):
    """The Stereographic (a.k.a. "equal angle") forward transform."""
    _inverse_type = 'InvertedStereographicTransform'
    def _calculate_k(self, inner_k):
        return 2 / inner_k

class InvertedStereographicTransform(BaseInvertedTransform):
    """The Stereographic (a.k.a. "equal angle") inverse transform."""
    _inverse_type = 'StereographicTransform'
    def _calculate_c(self, p):
        return 2.0 * np.arctan(0.5 * p)
