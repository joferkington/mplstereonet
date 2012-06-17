import numpy as np
import mplstereonet.stereonet_math as smath

class TestGeographic2various:
    def setup(self):
        self.strike_dip = (
                [315, 45],
                [45, 45],
                [135, 45],
                [225, 45],
                [0, 80],
                [90, 80],
                [180, 80],
                )

    def test_geographic2pole(self):
        for (strike, dip) in self.strike_dip:
            lon, lat = smath.pole(strike, dip)
            assert np.allclose(smath.geographic2pole(lon, lat), 
                               [[strike], [dip]])

    def test_geographic2plunge_bearing(self):
        for (bearing, plunge) in self.strike_dip:
            lon, lat = smath.line(plunge, bearing)
            assert np.allclose(smath.geographic2plunge_bearing(lon, lat),
                               [[plunge], [bearing]])

class TestNormal2Pole:
    def setup(self):
        self.data = (
                [(1, 0, 0), (180, 90)],
                [(0, 1, 0), (90, 90)],
                [(0, 0, 1), (0, 0)],
                )
    def test_normal2pole(self):
        for (x,y,z), (strike, dip) in self.data:
            assert np.allclose(smath.normal2pole(x,y,z), [[strike], [dip]])

class TestWorld2StereonetConversions:
    def setup(self):
        self.data = (
                # x, y, z     lon, lat (radians)
                [(0, 0, -1),  (0, 0)],
                [(1, 0, 0),   (np.pi/2, 0)],
                [(-1, 0, 0),  (-np.pi/2, 0)],
                [(0, 1, 0),   (0, np.pi/2)],
                [(0, -1, 0),  (0, -np.pi/2)],
                )

    def test_xyz2stereonet(self):
        for (x,y,z), (lon, lat) in self.data:
            assert np.allclose(smath.xyz2stereonet(x,y,z), [[lon],[lat]])

    def test_stereonet2xyz(self):
        for (x,y,z), (lon, lat) in self.data:
            assert np.allclose(smath.stereonet2xyz(lon, lat), [[x],[y],[z]])

class TestCartesianSphericalConversions:
    def setup(self):
        self.data = (
                # Cartesian    # Spherical (radians)
                [(0, 1, 0),    (np.pi/2, 0)],
                )

    def test_cart2sph(self):
        for (x,y,z), (lon, lat) in self.data:
            assert np.allclose(smath.cart2sph(x, y, z), [lon, lat])

    def test_sph2cart(self):
        for (x,y,z), (lon, lat) in self.data:
            assert np.allclose(smath.sph2cart(lon, lat), [x, y, z])

    def test_cart2sph_conversion_and_inverse(self):
        for (x,y,z), _ in self.data:
            lon, lat = smath.cart2sph(x,y,z)
            x1, y1, z1 = smath.sph2cart(lon, lat)
            assert np.allclose([x,y,z], [x1, y1, z1])

    def test_sph2cart_conversion_and_inverse(self):
        for _, (lon, lat) in self.data:
            x,y,z = smath.sph2cart(lon, lat)
            lon1, lat1 = smath.cart2sph(x,y,z)
            assert np.allclose([lon, lat], [lon1, lat1])


