import numpy as np
import mplstereonet
from mplstereonet.stereonet_math import sph2cart, cart2sph

class TestFitting():
    def test_fit_girdle(self):
        for strike in range(0, 370, 10):
            for dip in range(0, 100, 10):
                lon, lat = mplstereonet.plane(strike, dip)
                strikes, dips = mplstereonet.geographic2pole(lon, lat)
                s, d = mplstereonet.fit_girdle(strikes, dips)
                self.compare_strikedip(strike, dip, s, d)

    def test_fit_girdle_noisy(self):
        np.random.seed(1)
        for strike in range(0, 370, 10):
            for dip in range(0, 100, 10):
                lon, lat = mplstereonet.plane(strike, dip)
                lon += np.radians(np.random.normal(0, 1, lon.shape))
                lat += np.radians(np.random.normal(0, 1, lat.shape))
                s_noisy, d_noisy = mplstereonet.geographic2pole(lon, lat)
                s, d = mplstereonet.fit_girdle(s_noisy, d_noisy)
                ang_dist = self.cos_distance(strike, dip, s, d)
                assert ang_dist < 2 or (180 - ang_dist) < 2

    def test_cov_eig(self):
        x, y, z = 3 * [np.linspace(-1, 1, 10)]
        lon, lat = cart2sph(x, y, z)
        vals, vecs = mplstereonet.cov_eig(lon, lat)
        p = vecs[:,-1]
        assert np.allclose([p[0], p[0], p[0]], p)

    def test_fit_pole(self):
        np.random.seed(1)
        for strike in range(0, 370, 10):
            for dip in range(0, 100, 10):
                s, d = mplstereonet.fit_pole([strike], [dip])
                self.compare_strikedip(strike, dip, s, d)

    def test_fit_pole_noisy(self):
        np.random.seed(1)
        for strike in range(0, 370, 10):
            for dip in range(0, 100, 10):
                lon, lat = mplstereonet.pole(strike, dip)
                lon = lon + np.radians(np.random.normal(0, 1, 100))
                lat = lat + np.radians(np.random.normal(0, 1, 100))
                s_noisy, d_noisy = mplstereonet.geographic2pole(lon, lat)
                s, d = mplstereonet.fit_pole(s_noisy, d_noisy)
                ang_dist = self.cos_distance(strike, dip, s, d)
                assert ang_dist < 2 or (180 - ang_dist) < 2

    def cos_distance(self, strike1, dip1, strike2, dip2):
        """Angular distance betwen the poles of two planes."""
        xyz1 = sph2cart(*mplstereonet.pole(strike1, dip1))
        xyz2 = sph2cart(*mplstereonet.pole(strike2, dip2))
        r1, r2 = np.linalg.norm(xyz1), np.linalg.norm(xyz2)
        dot = np.dot(np.squeeze(xyz1), np.squeeze(xyz2)) / r1 / r2
        return np.abs(np.degrees(np.arccos(dot)))

    def compare_strikedip(self, strike1, dip1, strike2, dip2):
        """Avoids ambiguities in strike/dip convention when dip is 0 or 90."""
        convert = lambda a, b: sph2cart(*mplstereonet.pole(a, b))
        x1, y1, z1 = convert(strike1, dip1)
        x2, y2, z2 = convert(strike2, dip2)
        rtol, atol = 1e-7, 1e-7
        try:
            assert np.allclose([x1, y1, z1], [x2, y2, z2], rtol, atol)
        except AssertionError:
            # Antipode is also acceptable in this case....
            assert np.allclose([x1, y1, z1], [-x2, -y2, -z2], rtol, atol)
