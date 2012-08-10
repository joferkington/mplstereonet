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

def count_points(lons, lats, func, sigma, num=10000):
    xyz_counters = np.vstack(points_on_hemisphere(num)).T
    xyz_points = stereonet_math.sph2cart(lons, lats)
    xyz_points = np.vstack(xyz_points).T

    totals = np.zeros(xyz_counters.shape[0], dtype=np.float)
    for i, xyz in enumerate(xyz_counters):
        cos_dist = np.abs(np.dot(xyz, xyz_points.T))
        totals[i] = func(cos_dist, sigma)

    totals[totals < 0] = 0
    counter_lon, counter_lat = stereonet_math.cart2sph(*xyz_counters.T)
    return counter_lon, counter_lat, totals

def grid_data(lons, lats, z, gridsize=(100,100)):
    bound = np.pi / 2.0 + 0.1
    nrows, ncols = gridsize
    xmin, xmax, ymin, ymax = -bound, bound, -bound, bound

    tri = delaunay.Triangulation(lons, lats)
    interp = delaunay.LinearInterpolator(tri, z, default_value=0)

    slices = np.s_[xmin : xmax : ncols * 1j, ymin : ymax : nrows * 1j]
    zi = interp[slices]

    xi, yi = np.ogrid[slices]
    return xi.ravel(), yi.ravel(), zi

def density_grid(*args, **kwargs):
    """
    Estimates point density of the given linear orientation measurements
    (Interpreted as poles, lines, rakes, or "raw" longitudes and latitudes
    based on the `measurement` keyword argument.). Returns a regular (in
    lat-long space) grid of density estimates over a hemispherical surface.

    Parameters
    ----------

        *args : A variable number of sequences of measurements. By default, this
            will be expected to be `strike` & `dip`, both array-like sequences
            representing poles to planes.  (Rake measurements require three
            parameters, thus the variable number of arguments.) The
            `measurement` kwarg controls how these arguments are interpreted.
        measurement : string, optional 
            Controls how the input arguments are interpreted. Defaults to
            "poles".  
            May be one of the following:
                "poles" : Arguments are assumed to be sequences of strikes and 
                    dips of planes. Poles to these planes are used for density
                    contouring.
                "lines" : Arguments are assumed to be sequences of plunges and
                    bearings of linear features.  
                "rakes" : Arguments are assumed to be sequences of strikes,
                    dips, and rakes along the plane.
                "radians" : Arguments are assumed to be "raw" longitudes and
                    latitudes in the underlying projection's coordinate system.
        method : string, optional 
            The method of density estimation to use. Defaults to
            "exponential_kamb". 
            May be one of the following:
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
            The number of standard deviations defining the expected number of
            standard deviations by which a random sample from a uniform
            distribution of points would be expected to vary from being evenly
            distributed across the hemisphere.  This controls the size of the
            counting circle, and therefore the degree of smoothing.  Higher
            sigmas will lead to more smoothing of the resulting density
            distribution. This parameter only applies to Kamb-based methods.
            Defaults to 3.
        gridsize : int or 2-item tuple of ints, optional
            The size of the grid that the density is estimated on. If a single
            int is given, it is interpreted as an NxN grid. If a tuple of ints
            is given it is interpreted as (nrows, ncols).  Defaults to 100.
        num_counters : int, optional
            The number of "counting points" (arranged following a golden
            section spiral) that density is estimated at on the surface of
            hemisphere.  This is then interpolated onto a regular grid in
            lat-long space (see "gridsize" above). Defaults to 1/2 of the total
            number of cells in the regular grid.

    Returns:
    --------
        xi, yi, zi : The longitude, latitude and density values of the regularly
            gridded density estimates. Longitude and latitude are in radians.
        
    See Also:
    ---------
        `mplstereonet.StereonetAxes.density_contourf`
        `mplstereonet.StereonetAxes.density_contour`

    References
    ----------
    .. [1] Vollmer, 1995. C Program for Automatic Contouring of Spherical
       Orientation Data Using a Modified Kamb Method. Computers &
       Geosciences, Vol. 21, No. 1, pp. 31--49.

    .. [2] Kamb, 1959. Ice Petrofabric Observations from Blue Glacier,
       Washington, in Relation to Theory and Experiment. Journal of
       Geophysical Research, Vol. 64, No. 11, pp. 1891--1909.
    """
    def do_nothing(x, y):
        return x, y
    measurement = kwargs.get('measurement', 'poles')
    gridsize = kwargs.get('gridsize', 100)
    try:
        gridsize = int(gridsize)
        gridsize = (gridsize, gridsize)
    except TypeError:
        pass

    num_counters = kwargs.get('num_counters', None)
    if num_counters is None:
        num_counters = np.product(gridsize) / 2

    func = {'poles':stereonet_math.pole,
            'lines':stereonet_math.line,
            'rakes':stereonet_math.rake,
            'radians':do_nothing}[measurement]
    lon, lat = func(*args)

    method = kwargs.get('method', 'exponential_kamb')
    sigma = kwargs.get('sigma', 3)
    func = {'linear_kamb':linear_inverse_kamb,
            'square_kamb':square_inverse_kamb,
            'schmidt':schmidt_count,
            'kamb':kamb_count,
            'exponential_kamb':exponential_kamb,
            }[method]
    counter_lon, counter_lat, totals = count_points(lon, lat, func, sigma,
                                                    num_counters)
    xi, yi, zi = grid_data(counter_lon, counter_lat, totals, gridsize)
    return xi, yi, zi

def exponential_kamb(cos_dist, sigma=3):
    n = float(cos_dist.size)
    f = 2 * (1.0 + n / sigma**2)
    count = np.exp(f * (cos_dist - 1)).sum()
    units = np.sqrt(n * (f/2.0 - 1) / f**2) 
    return (count - 0.5) / units 

def linear_inverse_kamb(cos_dist, sigma=3):
    n = float(cos_dist.size)
    radius = kamb_radius(n, sigma)
    f = 2 / (1 - radius)
    cos_dist = cos_dist[cos_dist >= radius]
    count = (f * (cos_dist - radius)).sum()
    return (count - 0.5) / kamb_units(n, radius) 

def square_inverse_kamb(cos_dist, sigma=3):
    n = float(cos_dist.size)
    radius = kamb_radius(n, sigma)
    f = 3 / (1 - radius)**2
    cos_dist = cos_dist[cos_dist >= radius]
    count = (f * (cos_dist - radius)**2).sum()
    return (count - 0.5) / kamb_units(n, radius)

def kamb_radius(n, sigma):
    a = sigma**2 / (float(n) + sigma**2)
    return (1 - a) 

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

