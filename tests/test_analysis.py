import numpy as np
import mplstereonet
from mplstereonet.stereonet_math import sph2cart, cart2sph

class TestFitting:
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

class TestEigenvectors:
    def test_pb_input(self):
        for plunge in range(0, 100, 10):
            for bearing in range(0, 370, 10):
                plunges = plunge + np.array([-10, -5, 0, 5, 10])
                bearings = bearing + np.array([0, 0, 0, 0, 0])

                plu, azi, vals = mplstereonet.eigenvectors(plunges, bearings, 
                                                           measurement='lines')

                self.compare_plungebearing(plunge, bearing, plu[0], azi[0])
                assert np.allclose(vals, [1.09433342, 1.67776947e-02, 0])

    def test_sd_input(self):
        for strike in range(0, 100, 10):
            for dip in range(0, 370, 10):
                dips = dip + np.array([-10, -5, 0, 5, 10])
                strikes = strike + np.array([0, 0, 0, 0, 0])

                plu, azi, vals = mplstereonet.eigenvectors(strikes, dips)

                plunge, bearing = mplstereonet.pole2plunge_bearing(strike, dip)
                self.compare_plungebearing(plunge, bearing, plu[0], azi[0])
                assert np.allclose(vals, [1.09433342, 1.67776947e-02, 0])

    def test_rake_input(self):
        for strike in range(0, 100, 10):
            for dip in range(0, 370, 10):
                rakes = 90 + np.array([-10, -5, 0, 5, 10])
                dips = dip * np.ones_like(rakes)
                strikes = strike * np.ones_like(rakes)

                plu, azi, vals = mplstereonet.eigenvectors(strikes, dips, rakes,
                                                           measurement='rakes')

                plunge, bearing = dip, strike + 90
                self.compare_plungebearing(plunge, bearing, plu[0], azi[0])
                assert np.allclose(vals, [1.09433342, 1.67776947e-02, 0])

    def test_radian_input(self):
        for lat in range(0, 100, 10):
            for lon in range(0, 370, 10):
                lats = lat + np.array([-10, -5, 0, 5, 10])
                lons = lon * np.ones_like(lats)
                lats, lons = np.radians(lats), np.radians(lons)

                plu, azi, vals = mplstereonet.eigenvectors(lons, lats,
                                                        measurement='radians')

                plunge, bearing = mplstereonet.geographic2plunge_bearing(
                                            np.radians(lon), np.radians(lat))
                self.compare_plungebearing(plunge, bearing, plu[0], azi[0])
                assert np.allclose(vals, [1.09433342, 1.67776947e-02, 0])

    def compare_plungebearing(self, plunge1, azi1, plunge2, azi2):
        """Avoids ambiguities in plunge/bearing convention when dip is 0 or 90."""
        convert = lambda a, b: sph2cart(*mplstereonet.line(a, b))
        x1, y1, z1 = convert(plunge1, azi1)
        x2, y2, z2 = convert(plunge2, azi2)
        rtol, atol = 1e-7, 1e-7
        try:
            assert np.allclose([x1, y1, z1], [x2, y2, z2], rtol, atol)
        except AssertionError:
            # Antipode is also acceptable in this case....
            assert np.allclose([x1, y1, z1], [-x2, -y2, -z2], rtol, atol)
