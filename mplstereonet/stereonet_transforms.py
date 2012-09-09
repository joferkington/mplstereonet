import numpy as np
from matplotlib.path import Path
from matplotlib.transforms import Transform

class BaseStereonetTransform(Transform):
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
    transform_path.__doc__ = Transform.transform_path.__doc__

# Both the Lambert and Stereographic projections are very mathematically 
# similar, so we'll inherit from base classes that describes the common math.
class BaseForwardTransform(BaseStereonetTransform):
    def transform(self, ll):
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
    transform.__doc__ = transform.__doc__

    def inverted(self):
        return InvertedLambertTransform(
            self._center_longitude,
            self._center_latitude,
            self._resolution)
    inverted.__doc__ = inverted.__doc__

    def _calculate_k(self, inner_k):
        """Subclasses must implement!."""
        pass

class BaseInvertedTransform(BaseStereonetTransform):
    def transform(self, xy):
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
    transform.__doc__ = BaseStereonetTransform.transform.__doc__

    def inverted(self):
        return LambertTransform(
            self._center_longitude,
            self._center_latitude,
            self._resolution)
    inverted.__doc__ = BaseStereonetTransform.inverted.__doc__

    def _calculate_c(self, p):
        """Subclasses must implement!."""
        pass

class LambertTransform(BaseForwardTransform):
    def _calculate_k(self, inner_k):
        return np.sqrt(2.0 / inner_k)

class InvertedLambertTransform(BaseInvertedTransform):
    def _calculate_c(self, p):
        return 2.0 * np.arcsin(0.5 * p)

class StereographicTransform(BaseForwardTransform):
    def _calculate_k(self, inner_k):
        return 2 / inner_k

class InvertedStereographicTransform(BaseInvertedTransform):
    def _calculate_c(self, p):
        return 2.0 * np.arctan(0.5 * p)
