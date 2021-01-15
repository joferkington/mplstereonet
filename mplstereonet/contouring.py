import numpy as np
from . import stereonet_math

def _count_points(lons, lats, func, sigma, gridsize=(100,100), weights=None):
    """This function actually calculates the point density of the input ("lons"
    and "lats") points at a series of counter stations. Creates "gridsize"
    regular grid of counter stations in lat-long space, calculates the distance
    to all input points at each counter station, and then calculates the
    density using "func".  Each input point is weighted by the corresponding
    item of "weights".  The weights are normalized to 1 before calculation."""
    lons = np.atleast_1d(np.squeeze(lons))
    lats = np.atleast_1d(np.squeeze(lats))

    if weights is None:
        weights = 1
    # Normalize the weights
    weights = np.asarray(weights, dtype=np.float)
    weights /= weights.mean()

    # Generate a regular grid of "counters" to measure on...
    bound = np.pi / 2.0
    nrows, ncols = gridsize
    xmin, xmax, ymin, ymax = -bound, bound, -bound, bound
    lon, lat = np.mgrid[xmin : xmax : ncols * 1j, ymin : ymax : nrows * 1j]

    xyz_counters = stereonet_math.sph2cart(lon.ravel(), lat.ravel())
    xyz_counters = np.vstack(xyz_counters).T
    xyz_points = stereonet_math.sph2cart(lons, lats)
    xyz_points = np.vstack(xyz_points).T

    # Basically, we can't model this as a convolution as we're not in cartesian
    # space, so we have to iterate through and call the kernel function at
    # each "counter".
    totals = np.zeros(xyz_counters.shape[0], dtype=np.float)
    for i, xyz in enumerate(xyz_counters):
        cos_dist = np.abs(np.dot(xyz, xyz_points.T))
        density, scale = func(cos_dist, sigma)
        density *= weights
        totals[i] = (density.sum() - 0.5) / scale

    # Traditionally, the negative values (while valid, as they represent areas
    # with less than expected point-density) are not returned.
    totals[totals < 0] = 0
    counter_lon, counter_lat = stereonet_math.cart2sph(*xyz_counters.T)
    for item in [counter_lon, counter_lat, totals]:
        item.shape = gridsize
    return counter_lon, counter_lat, totals

def density_grid(*args, **kwargs):
    """
    Estimates point density of the given linear orientation measurements
    (Interpreted as poles, lines, rakes, or "raw" longitudes and latitudes
    based on the `measurement` keyword argument.). Returns a regular (in
    lat-long space) grid of density estimates over a hemispherical surface.

    Parameters
    ----------

    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``strike`` & ``dip``, both
        array-like sequences representing poles to planes.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        ``measurement`` kwarg controls how these arguments are interpreted.

    measurement : string, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"poles"``.  May be one of the following:

            ``"poles"`` : strikes, dips
                Arguments are assumed to be sequences of strikes and dips of
                planes. Poles to these planes are used for contouring.
            ``"lines"`` : plunges, bearings
                Arguments are assumed to be sequences of plunges and bearings
                of linear features.
            ``"rakes"`` : strikes, dips, rakes
                Arguments are assumed to be sequences of strikes, dips, and
                rakes along the plane.
            ``"radians"`` : lon, lat
                Arguments are assumed to be "raw" longitudes and latitudes in
                the stereonet's underlying coordinate system.

    method : string, optional
        The method of density estimation to use. Defaults to
        ``"exponential_kamb"``. May be one of the following:

        ``"exponential_kamb"`` : Kamb with exponential smoothing
            A modified Kamb method using exponential smoothing [1]_. Units are
            in numbers of standard deviations by which the density estimate
            differs from uniform.
        ``"linear_kamb"`` : Kamb with linear smoothing
            A modified Kamb method using linear smoothing [1]_.  Units are in
            numbers of standard deviations by which the density estimate
            differs from uniform.
        ``"kamb"`` : Kamb with no smoothing
            Kamb's method [2]_ with no smoothing. Units are in numbers of
            standard deviations by which the density estimate differs from
            uniform.
        ``"schmidt"`` : 1% counts
            The traditional "Schmidt" (a.k.a. 1%) method. Counts points within
            a counting circle comprising 1% of the total area of the
            hemisphere. Does not take into account sample size.  Units are in
            points per 1% area.
        ''"fisher"'' : 1% Counting Circle Size
            Similar to Schmidt, but instead of counting points, consider a fisher
            distribution around each pole, and consider the overlapping area with
            each counting circle.
            
    sigma : int or float, optional
        The number of standard deviations defining the expected number of
        standard deviations by which a random sample from a uniform
        distribution of points would be expected to vary from being evenly
        distributed across the hemisphere.  This controls the size of the
        counting circle, and therefore the degree of smoothing.  Higher sigmas
        will lead to more smoothing of the resulting density distribution. This
        parameter only applies to Kamb-based methods.  Defaults to 3.

    gridsize : int or 2-item tuple of ints, optional
        The size of the grid that the density is estimated on. If a single int
        is given, it is interpreted as an NxN grid. If a tuple of ints is given
        it is interpreted as (nrows, ncols).  Defaults to 100.

    weights : array-like, optional
        The relative weight to be applied to each input measurement. The array
        will be normalized to sum to 1, so absolute value of the weights do not
        affect the result. Defaults to None.

    Returns
    -------
    xi, yi, zi : 2D arrays
        The longitude, latitude and density values of the regularly gridded
        density estimates. Longitude and latitude are in radians.

    See Also
    ---------
    mplstereonet.StereonetAxes.density_contourf
    mplstereonet.StereonetAxes.density_contour

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
    weights = kwargs.get('weights', None)
    try:
        gridsize = int(gridsize)
        gridsize = (gridsize, gridsize)
    except TypeError:
        pass

    func = {'poles':stereonet_math.pole,
            'lines':stereonet_math.line,
            'rakes':stereonet_math.rake,
            'radians':do_nothing}[measurement]
    lon, lat = func(*args)

    method = kwargs.get('method', 'exponential_kamb')
    sigma = kwargs.get('sigma', 3)
    func = {'linear_kamb':_linear_inverse_kamb,
            'square_kamb':_square_inverse_kamb,
            'schmidt':_schmidt_count,
            'kamb':_kamb_count,
            'exponential_kamb':_exponential_kamb,
            'fisher':_fisher
            }[method]
    lon, lat, z = _count_points(lon, lat, func, sigma, gridsize, weights)

    if method not in ('schmidt', 'kamb'):
        # This is really a bit of a plotting hack. We don't want to ever draw
        # a 0 contour for smoothed methods, as it isn't well defined.
        z[z == 0] = np.finfo(z.dtype).tiny

    return lon, lat, z

def _kamb_radius(n, sigma):
    """Radius of kernel for Kamb-style smoothing."""
    a = sigma**2 / (float(n) + sigma**2)
    return (1 - a)

def _kamb_units(n, radius):
    """Normalization function for Kamb-style counting."""
    return np.sqrt(n * radius * (1 - radius))

# All of the following kernel functions return an _unsummed_ distribution and
# a normalization factor
def _exponential_kamb(cos_dist, sigma=3):
    """Kernel function from Vollmer for exponential smoothing."""
    n = float(cos_dist.size)
    f = 2 * (1.0 + n / sigma**2)
    count = np.exp(f * (cos_dist - 1))
    units = np.sqrt(n * (f/2.0 - 1) / f**2)
    return count, units

def _linear_inverse_kamb(cos_dist, sigma=3):
    """Kernel function from Vollmer for linear smoothing."""
    n = float(cos_dist.size)
    radius = _kamb_radius(n, sigma)
    f = 2 / (1 - radius)
    cos_dist = cos_dist[cos_dist >= radius]
    count = (f * (cos_dist - radius))
    return count, _kamb_units(n, radius)

def _square_inverse_kamb(cos_dist, sigma=3):
    """Kernel function from Vollemer for inverse square smoothing."""
    n = float(cos_dist.size)
    radius = _kamb_radius(n, sigma)
    f = 3 / (1 - radius)**2
    cos_dist = cos_dist[cos_dist >= radius]
    count = (f * (cos_dist - radius)**2)
    return count, _kamb_units(n, radius)

def _kamb_count(cos_dist, sigma=3):
    """Original Kamb kernel function (raw count within radius)."""
    n = float(cos_dist.size)
    dist = _kamb_radius(n, sigma)
    count = (cos_dist >= dist).astype(float)
    return count, _kamb_units(n, dist)

def _schmidt_count(cos_dist, sigma=None):
    """Schmidt (a.k.a. 1%) counting kernel function."""
    radius = 0.01
    count = ((1 - cos_dist) <= radius).astype(float)
    # To offset the count.sum() - 0.5 required for the kamb methods...
    count = 0.5 / count.size + count
    return count, (cos_dist.size * radius)

def _fisher(cos_dist, sigma=None):
    """Fisher distribution, 1% counting circle size."""
    radius = 0.01
    cone_angle = np.sqrt(2*radius)
    # From -> DIPS - AN INTERACTIVE AND GRAPHICAL APPROACH TO THE ANALYSIS OF ORIENTATION BASED DATA
    # by Mark S. Diederichs, 1990
    # Msc Thesis
    # Data points digitised from graph in Appendix A
    # (pole-grid seperation)/(counting angle) vs. probability weighting to grid point
    x = [3.00249357093607E-06,0.0419508401727634,0.0800855110168995,0.122036351189663,0.160171022033799,0.204025443130519,0.244069699885755,0.282213378210604,0.324167220876938,0.362310899201787,0.404270746855263,0.442420430167253,0.482482701883914,0.526361142929202,0.566429419633005,0.606503701323949,0.64847856144528,0.688561850616937,0.730560730686835,0.770659032326347,0.808856755535472,0.852789241465036,0.892911563053115,0.93305189960262,0.971312675176734,1.01154308653336,1.04985790699175,1.09001625850268,1.12824400664752,1.16836332574202,1.21037421578621,1.25237009336253,1.28863721320556,1.33253066671871,1.37259293843537,1.41074562424093,1.44890431503363,1.48895457677601,1.52710125759443,1.5671515193368,1.60910836449671,1.64534245691046,1.68729629957679,1.72734055633203,1.99809341658247]
    y = [0.998425192122057,0.996784329385554,0.995149471636193,0.991933801021748,0.990298943272387,0.988655078042314,0.985442409921439,0.979083128538251,0.974292650045863,0.967933368662674,0.959993274414401,0.950484377275327,0.937822861886797,0.923580533633182,0.907769402488766,0.888808655588466,0.872994521950479,0.849309351416351,0.820896754754823,0.789337544830982,0.754631721644826,0.712042851588244,0.667885178640861,0.614278658425822,0.546501869802871,0.445651113249553,0.349527782823635,0.28647241534094,0.236018513375358,0.193435648305918,0.15872382013262,0.131886031349035,0.109781673679991,0.0876653060366634,0.0750037906481335,0.0639200856311168,0.0496867648582148,0.043324480981455,0.0353903917203239,0.0290281078435641,0.0226628214732336,0.0178813504615584,0.0130908719691704,0.00987820384829607,3.00249357088056E-06]
    
    # Calculate ratio between pole-grid seperation and counting angle (1%). Linear interpolation done using numpy
    ratio = ((1-cos_dist)/radius)
    count = np.interp(ratio, x, y, right=0)
    
    # To offset the count.sum() - 0.5 required for the kamb methods...
    count = 0.5 / count.size + count
    
    return count, (count.size * radius)
    
