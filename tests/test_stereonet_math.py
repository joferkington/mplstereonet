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

class TestVector2Pole:
    def setup(self):
        self.data = (
                [(1, 0, 0), (180, 90)],
                [(0, 1, 0), (90, 90)],
                [(0, 0, 1), (0, 0)],
                )
    def test_vector2pole(self):
        for (x,y,z), (strike, dip) in self.data:
            assert np.allclose(smath.vector2pole(x,y,z), [[strike], [dip]])

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

    def test_round_trip(self):
        for x in np.arange(-1, 1.1, 0.1):
            for y in np.arange(-1, 1.1, 0.1):
                for z in np.arange(-1, 1.1, 0.1):
                    if np.allclose([x, y, z], [0, 0, 0]):
                        continue
                    xyz2 = smath.sph2cart(*smath.cart2sph(x, y, z))
                    xyz2 /= np.linalg.norm(xyz2)
                    xyz1 = np.array([x, y, z]) / np.linalg.norm([x, y, z])
                    assert np.allclose(xyz1, xyz2)

class TestProjectOntoPlane:
    def setup(self):
        self.data = [
                     (315, 40, 10),
                     (315, 40, -10),
                     (135, 30, 20),
                     (135, 30, -20),
                     (45, 80, 80),
                     (45, 80, -80),
                     (90, 90, 90),
                     (0, 0, 0),
                    ]

    def test_rake_back_to_rakes(self):
        for strike, dip, rake in self.data:
            lon, lat = smath.rake(strike, dip, rake)
            plunge, bearing = smath.geographic2plunge_bearing(lon, lat)
            newrake = smath.project_onto_plane(strike, dip, plunge, bearing)
            assert np.allclose(rake, newrake)

    def test_offset_back_to_rake(self):
        for strike, dip, rake in self.data:
            # Displace the line perpendicular to the plane...
            line = smath.sph2cart(*smath.rake(strike, dip, rake))
            norm = smath.sph2cart(*smath.pole(strike, dip))
            line = np.array(line) + 0.5 * np.array(norm)

            # Project the "displaced" line back onto the plane...
            lon, lat = smath.cart2sph(*line)
            plunge, bearing = smath.geographic2plunge_bearing(lon, lat)
            newrake = smath.project_onto_plane(strike, dip, plunge, bearing)
            assert np.allclose(rake, newrake)

    def test_multiple_rakes(self):
        strike, dip, rake = np.array(self.data).T

        lon, lat = smath.rake(strike, dip, rake)
        plunge, bearing = smath.geographic2plunge_bearing(lon, lat)
        newrake = smath.project_onto_plane(strike, dip, plunge, bearing)
        assert np.allclose(rake, newrake)

class TestPlaneIntersection:
    def setup(self):
        self.data = [
                     [[0, 90, 90, 80], [80, 180]],
                     [[0, 90, 270, 80], [80, 0]],
                    ]

    def test_basic(self):
        for planes, correct in self.data:
            result = smath.plane_intersection(*planes)
            assert np.allclose(np.hstack(result), correct)

    def test_multiple(self):
        planes = np.array([item[0] for item in self.data]).T
        results = smath.plane_intersection(*planes)
        correct = np.array([item[1] for item in self.data]).T
        assert np.allclose(results, correct)

class TestAntipode:
    def setup(self):
        self.data = [
                     [(0, 0),  (np.pi, 0)],
                     [(0, np.pi/2), (0, -np.pi/2)],
                     [(0.5, 1), (0.5 - np.pi, -1)],
                    ]

    def test_basic(self):
        for indata, outdata in self.data:
            x, y = smath.antipode(*indata)
            compare_lonlat(x, y, *outdata)

    def test_multiple(self):
        (inlon, outlon), (inlat, outlat) = np.array(self.data).T
        compare_lonlat(outlon, outlat, *smath.antipode(inlon, inlat))

    def test_roundtrip(self):
        for strike in range(0, 370, 10):
            for dip in range(0, 100, 10):
                lon, lat = smath.pole(strike, dip)
                lon2, lat2 = smath.antipode(*smath.antipode(lon, lat))
                compare_lonlat(lon, lat, lon2, lat2)

    def test_cos_distance(self):
        for lon in range(0, 370, 10):
            for lat in range(-90, 100, 10):
                lon1, lat1 = np.radians([lon, lat])
                lon2, lat2 = smath.antipode(lon1, lat1)
                xyz1 = smath.sph2cart(lon1, lat1)
                xyz2 = smath.sph2cart(lon2, lat2)
                mag = np.linalg.norm(np.cross(xyz1, xyz2))
                assert np.allclose(0, mag)

class TestAngularDistance:
    def test_antipode_distance(self):
        for lon in range(0, 370, 10):
            for lat in range(-90, 100, 10):
                point1 = np.radians([lon, lat])
                point2 = smath.antipode(*point1)
                dist = smath.angular_distance(point1, point2, False)
                msg = 'Failed at {}, {}'.format(lon, lat)
                assert np.allclose(dist, np.pi), msg
    
    def test_shapes(self):
        points = np.zeros(10), np.zeros(10)
        dist = smath.angular_distance(points, [0, np.pi / 2])
        assert np.allclose(dist, np.pi / 2)

        dist = smath.angular_distance([0, np.pi / 2], points)
        assert np.allclose(dist, np.pi / 2)

        dist = smath.angular_distance(points, points)
        assert np.allclose(dist, 0)

    def test_directional(self):
        first, second = smath.line(30, 270), smath.line(40, 90)
        dist = smath.angular_distance(first, second, bidirectional=True)
        assert np.allclose(dist, np.radians(70))

        dist = smath.angular_distance(first, second, bidirectional=False)
        assert np.allclose(dist, np.radians(110))

def compare_lonlat(lon1, lat1, lon2, lat2):
    """Avoid ambiguities in strike/dip or lon/lat conventions."""
    x1, y1, z1 = smath.sph2cart(lon1, lat1)
    x2, y2, z2 = smath.sph2cart(lon2, lat2)
    assert np.allclose([x1, y1, z1], [x2, y2, z2], atol=1e-7)
