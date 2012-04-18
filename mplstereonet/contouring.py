import numpy as np
import stereonet_math
import matplotlib.delaunay as delaunay


def points_on_hemisphere(num):
    """
    Generates `num` points on a hemisphere using a golden section spiral.
    """
    num = num * 2
    inc = np.pi * (3 - np.sqrt(5))
    off = 2.0 / num
    k = np.arange(num)
    y = k * off - 1 + off / 2.0
    r = np.sqrt(1 - y**2)
    phi = k * inc
    x = np.cos(phi) * r
    z = np.sin(phi) * r
    hemisphere = x > 0
    return x[hemisphere], y[hemisphere], z[hemisphere]

def count_points(lons, lats, func, k, num=10000):
    xyz_counters = np.vstack(points_on_hemisphere(num)).T
    xyz_points = stereonet_math.sph2cart(lons, lats)
    xyz_points = np.vstack(xyz_points).T

    totals = np.zeros(xyz_counters.shape[0], dtype=np.float)
    for i, xyz in enumerate(xyz_counters):
        cos_dist = np.abs(np.dot(xyz, xyz_points.T))
        totals[i] = k * func(cos_dist, k) / float(cos_dist.size)

    totals[totals < 0] = 0
    counter_lon, counter_lat = stereonet_math.cart2sph(*xyz_counters.T)
    return counter_lon, counter_lat, totals

def grid_data(lons, lats, z, gridsize=(200,200)):
    bound = np.pi / 2.0 + 0.1
    nrows, ncols = gridsize
    xmin, xmax, ymin, ymax = -bound, bound, -bound, bound

    tri = delaunay.Triangulation(lons, lats)
    interp = delaunay.LinearInterpolator(tri, z, default_value=0)

    slices = np.s_[xmin : xmax : ncols * 1j, ymin : ymax : nrows * 1j]
    zi = interp[slices]

    xi, yi = np.ogrid[slices]
    return xi.ravel(), yi.ravel(), zi

def contour_grid(*args, **kwargs):
    def do_nothing(x, y):
        return x, y
    measurement = kwargs.get('measurement', 'poles')
    num_counters = kwargs.get('num_counters', 10000)
    func = {'poles':stereonet_math.pole,
            'lines':stereonet_math.line,
            'rakes':stereonet_math.rake,
            'radians':do_nothing}[measurement]
    lon, lat = func(*args)

    method = kwargs.get('method', 'kamb')
    sigma = kwargs.get('sigma', 3)
    func = {'linear_inverse_kamb':linear_inverse_kamb,
            'square_inverse_kamb':square_inverse_kamb,
            'schmidt':schmidt_count,
            'kamb':kamb_count,
            'exponential_kamb':exponential_kamb,
            }[method]
    counter_lon, counter_lat, totals = count_points(lon, lat, func, sigma,
                                                    num_counters)
    xi, yi, zi = grid_data(counter_lon, counter_lat, totals)
    return xi, yi, zi

def exponential_kamb(cos_dist, sigma=3):
    n = float(cos_dist.size)
    f = 2 * (1.0 + n / sigma**2)
    count = np.exp(f * (cos_dist - 1)).sum()
    units = np.sqrt(n * (f/2 - 1) / f**2)
    return (count - 0.5) / units

def linear_inverse_kamb(cos_dist, sigma=3):
    n = float(cos_dist.size)
    radius = kamb_radius(n, sigma)
    cos_dist = cos_dist[cos_dist >= radius]
    count = ((2.0 / radius) * (cos_dist - radius)).sum()
    return (count - 0.5) / kamb_units(n, radius)

def square_inverse_kamb(cos_dist, sigma=3):
    n = float(cos_dist.size)
    radius = kamb_radius(n, sigma)
    cos_dist = cos_dist[cos_dist >= radius]
    count = ((3.0 / radius**2) * (cos_dist - radius)**2).sum()
    return (count - 0.5) / kamb_units(n, radius)

def kamb_radius(n, sigma):
    a = sigma**2 / (1.0 * n + sigma**2)
    return 1 - a

def kamb_units(n, radius):
    return np.sqrt(n * radius * (1 - radius))

def kamb_count(cos_dist, sigma=3):
    n = float(cos_dist.size)
    dist = kamb_radius(n, sigma)
    count = (cos_dist >= dist).sum()
    return (count - 0.5) / kamb_units(n, dist)

def schmidt_count(cos_dist, sigma=None):
    radius = 0.01
    count = ((1 - cos_dist) <= radius).sum()
    return (count - 0.5) / (cos_dist.size * radius)

