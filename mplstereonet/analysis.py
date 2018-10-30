import numpy as np

from . import stereonet_math

def fit_girdle(*args, **kwargs):
    """
    Fits a plane to a scatter of points on a stereonet (a.k.a. a "girdle").

    Input arguments will be interpreted as poles, lines, rakes, or "raw"
    longitudes and latitudes based on the ``measurement`` keyword argument.
    (Defaults to ``"poles"``.)

    Parameters
    ----------

    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``strikes`` & ``dips``, both
        array-like sequences representing poles to planes.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        *measurement* kwarg controls how these arguments are interpreted.

    measurement : {'poles', 'lines', 'rakes', 'radians'}, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"poles"``.  May be one of the following:

            ``"poles"`` : Arguments are assumed to be sequences of strikes and
                dips of planes. Poles to these planes are used for density
                contouring.
            ``"lines"`` : Arguments are assumed to be sequences of plunges and
                bearings of linear features.
            ``"rakes"`` : Arguments are assumed to be sequences of strikes,
                dips, and rakes along the plane.
            ``"radians"`` : Arguments are assumed to be "raw" longitudes and
                latitudes in the underlying projection's coordinate system.

    bidirectional : boolean, optional
        Whether or not the antipode of each measurement will be used in the
        calculation. For almost all use cases, it should. Defaults to True.

    Returns
    -------
    strike, dip: floats
        The strike and dip of the plane.

    Notes
    -----
    The pole to the best-fit plane is extracted by calculating the smallest
    eigenvector of the covariance matrix of the input measurements in cartesian
    3D space.

    Examples
    --------
    Calculate the plunge of a cylindrical fold axis from a series of strike/dip
    measurements of bedding from the limbs:

        >>> strike = [270, 334, 270, 270]
        >>> dip = [20, 15, 80, 78]
        >>> s, d = mplstereonet.fit_girdle(strike, dip)
        >>> plunge, bearing = mplstereonet.pole2plunge_bearing(s, d)

    """
    vec = 0 # Smallest eigenvector will be the pole
    return _sd_of_eigenvector(args, vec=vec, **kwargs)

def fit_pole(*args, **kwargs):
    """
    Fits the pole to a plane to a "bullseye" of points on a stereonet.

    Input arguments will be interpreted as poles, lines, rakes, or "raw"
    longitudes and latitudes based on the ``measurement`` keyword argument.
    (Defaults to ``"poles"``.)

    Parameters
    ----------

    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``strike`` & ``dip``, both
        array-like sequences representing poles to planes.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        *measurement* kwarg controls how these arguments are interpreted.

    measurement : {'poles', 'lines', 'rakes', 'radians'}, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"poles"``.  May be one of the following:

            ``"poles"`` : Arguments are assumed to be sequences of strikes and
                dips of planes. Poles to these planes are used for density
                contouring.
            ``"lines"`` : Arguments are assumed to be sequences of plunges and
                bearings of linear features.
            ``"rakes"`` : Arguments are assumed to be sequences of strikes,
                dips, and rakes along the plane.
            ``"radians"`` : Arguments are assumed to be "raw" longitudes and
                latitudes in the underlying projection's coordinate system.

    bidirectional : boolean, optional
        Whether or not the antipode of each measurement will be used in the
        calculation. For almost all use cases, it should. Defaults to True.

    Returns
    -------

    strike, dip: floats
        The strike and dip of the plane.

    Notes
    -----

    The pole to the best-fit plane is extracted by calculating the largest
    eigenvector of the covariance matrix of the input measurements in cartesian
    3D space.

    Examples
    --------

    Find the average strike/dip of a series of bedding measurements

        >>> strike = [270, 65, 280, 300]
        >>> dip = [20, 15, 10, 5]
        >>> strike0, dip0 = mplstereonet.fit_pole(strike, dip)

    """
    vec = -1 # Largest eigenvector will be the pole
    return _sd_of_eigenvector(args, vec=vec, **kwargs)

def _sd_of_eigenvector(data, vec, measurement='poles', bidirectional=True):
    """Unifies ``fit_pole`` and ``fit_girdle``."""
    lon, lat = _convert_measurements(data, measurement)
    vals, vecs = cov_eig(lon, lat, bidirectional)
    x, y, z = vecs[:, vec]
    s, d = stereonet_math.geographic2pole(*stereonet_math.cart2sph(x, y, z))
    return s[0], d[0]

def eigenvectors(*args, **kwargs):
    """
    Finds the 3 eigenvectors and eigenvalues of the 3D covariance matrix of a
    series of geometries.  This can be used to fit a plane/pole to a dataset or
    for shape fabric analysis (e.g. Flinn/Hsu plots).

    Input arguments will be interpreted as poles, lines, rakes, or "raw"
    longitudes and latitudes based on the *measurement* keyword argument.
    (Defaults to ``"poles"``.)

    Parameters
    ----------

    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``strike`` & ``dip``, both
        array-like sequences representing poles to planes.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        *measurement* kwarg controls how these arguments are interpreted.

    measurement : {'poles', 'lines', 'rakes', 'radians'}, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"poles"``.  May be one of the following:

            ``"poles"`` : Arguments are assumed to be sequences of strikes and
                dips of planes. Poles to these planes are used for density
                contouring.
            ``"lines"`` : Arguments are assumed to be sequences of plunges and
                bearings of linear features.
            ``"rakes"`` : Arguments are assumed to be sequences of strikes,
                dips, and rakes along the plane.
            ``"radians"`` : Arguments are assumed to be "raw" longitudes and
                latitudes in the underlying projection's coordinate system.

    bidirectional : boolean, optional
        Whether or not the antipode of each measurement will be used in the
        calculation. For almost all use cases, it should. Defaults to True.

    Returns
    -------

    plunges, bearings, values : sequences of 3 floats each
        The plunges, bearings, and eigenvalues of the three eigenvectors of the
        covariance matrix of the input data.  The measurements are returned
        sorted in descending order relative to the eigenvalues. (i.e. The
        largest eigenvector/eigenvalue is first.)

    Examples
    --------

    Find the eigenvectors as plunge/bearing and eigenvalues of the 3D
    covariance matrix of a series of planar measurements:

        >>> strikes = [270, 65, 280, 300]
        >>> dips = [20, 15, 10, 5]
        >>> plu, azi, vals = mplstereonet.eigenvectors(strikes, dips)
    """
    lon, lat = _convert_measurements(args, kwargs.get('measurement', 'poles'))
    vals, vecs = cov_eig(lon, lat, kwargs.get('bidirectional', True))
    lon, lat = stereonet_math.cart2sph(*vecs)
    plunges, bearings = stereonet_math.geographic2plunge_bearing(lon, lat)
    # Largest eigenvalue first...
    return plunges[::-1], bearings[::-1], vals[::-1]

def cov_eig(lon, lat, bidirectional=True):
    lon = np.atleast_1d(np.squeeze(lon))
    lat = np.atleast_1d(np.squeeze(lat))
    if bidirectional:
        # Include antipodes in calculation...
        lon2, lat2 = stereonet_math.antipode(lon, lat)
        lon, lat = np.hstack([lon, lon2]), np.hstack([lat, lat2])
    xyz = np.column_stack(stereonet_math.sph2cart(lon, lat))
    cov = np.cov(xyz.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = eigvals.argsort()
    return eigvals[order], eigvecs[:, order]

def _convert_measurements(data, measurement):
    def do_nothing(x, y):
        return x, y
    func = {'poles':stereonet_math.pole,
            'lines':stereonet_math.line,
            'rakes':stereonet_math.rake,
            'radians':do_nothing}[measurement]
    return func(*data)

def find_mean_vector(*args, **kwargs):
    """
    Returns the mean vector for a set of measurments. By default, this expects
    the input to be plunges and bearings, but the type of input can be
    controlled through the ``measurement`` kwarg.

    Parameters
    ----------

    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``plunge`` & ``bearing``, both
        array-like sequences representing linear features.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        *measurement* kwarg controls how these arguments are interpreted.


    measurement : string, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"lines"``.  May be one of the following:

            ``"poles"`` : strikes, dips
                Arguments are assumed to be sequences of strikes and dips of
                planes. Poles to these planes are used for analysis.
            ``"lines"`` : plunges, bearings
                Arguments are assumed to be sequences of plunges and bearings
                of linear features.
            ``"rakes"`` : strikes, dips, rakes
                Arguments are assumed to be sequences of strikes, dips, and
                rakes along the plane.
            ``"radians"`` : lon, lat
                Arguments are assumed to be "raw" longitudes and latitudes in
                the stereonet's underlying coordinate system.

    Returns
    -------

    mean_vector : tuple of two floats
        The plunge and bearing of the mean vector (in degrees).

    r_value : float
        The length of the mean vector (a value between 0 and 1).
    """
    lon, lat = _convert_measurements(args, kwargs.get('measurement', 'lines'))
    vector, r_value = stereonet_math.mean_vector(lon, lat)
    plunge, bearing = stereonet_math.geographic2plunge_bearing(*vector)
    return (plunge[0], bearing[0]), r_value

def find_fisher_stats(*args, **kwargs):
    """
    Returns the mean vector and summary statistics for a set of measurements.
    By default, this expects the input to be plunges and bearings, but the type
    of input can be controlled through the ``measurement`` kwarg.

    Parameters
    ----------
    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``plunge`` & ``bearing``, both
        array-like sequences representing linear features.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        *measurement* kwarg controls how these arguments are interpreted.

    conf : number
        The confidence level (0-100). Defaults to 95%, similar to 2 sigma.

    measurement : string, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"lines"``.  May be one of the following:

            ``"poles"`` : strikes, dips
                Arguments are assumed to be sequences of strikes and dips of
                planes. Poles to these planes are used for analysis.
            ``"lines"`` : plunges, bearings
                Arguments are assumed to be sequences of plunges and bearings
                of linear features.
            ``"rakes"`` : strikes, dips, rakes
                Arguments are assumed to be sequences of strikes, dips, and
                rakes along the plane.
            ``"radians"`` : lon, lat
                Arguments are assumed to be "raw" longitudes and latitudes in
                the stereonet's underlying coordinate system.

    Returns
    -------

    mean_vector: tuple of two floats
        A set consisting of the plunge and bearing of the mean vector (in
        degrees).

    stats : tuple of three floats
        ``(r_value, confidence, kappa)``
        The ``r_value`` is the magnitude of the mean vector as a number between
        0 and 1.
        The ``confidence`` radius is the opening angle of a small circle that
        corresponds to the confidence in the calculated direction, and is
        dependent on the input ``conf``.
        The ``kappa`` value is the dispersion factor that quantifies the amount
        of dispersion of the given vectors, analgous to a variance/stddev.
    """
    # How the heck did this wind up as a separate function?
    lon, lat = _convert_measurements(args, kwargs.get('measurement', 'lines'))
    conf = kwargs.get('conf', 95)
    center, stats = stereonet_math.fisher_stats(lon, lat, conf)
    plunge, bearing = stereonet_math.geographic2plunge_bearing(*center)
    mean_vector = (plunge[0], bearing[0])
    return mean_vector, stats

def kmeans(*args, **kwargs):
    """
    Find centers of multi-modal clusters of data using a kmeans approach
    modified for spherical measurements.

    Parameters
    ----------

    *args : 2 or 3 sequences of measurements
        By default, this will be expected to be ``strike`` & ``dip``, both
        array-like sequences representing poles to planes.  (Rake measurements
        require three parameters, thus the variable number of arguments.) The
        ``measurement`` kwarg controls how these arguments are interpreted.

    num : int
        The number of clusters to find. Defaults to 2.

    bidirectional : bool
        Whether or not the measurements are bi-directional linear/planar
        features or directed vectors. Defaults to True.

    tolerance : float
        Iteration will continue until the centers have not changed by more
        than this amount. Defaults to 1e-5.

    measurement : string, optional
        Controls how the input arguments are interpreted. Defaults to
        ``"poles"``.  May be one of the following:

            ``"poles"`` : strikes, dips
                Arguments are assumed to be sequences of strikes and dips of
                planes. Poles to these planes are used for analysis.
            ``"lines"`` : plunges, bearings
                Arguments are assumed to be sequences of plunges and bearings
                of linear features.
            ``"rakes"`` : strikes, dips, rakes
                Arguments are assumed to be sequences of strikes, dips, and
                rakes along the plane.
            ``"radians"`` : lon, lat
                Arguments are assumed to be "raw" longitudes and latitudes in
                the stereonet's underlying coordinate system.

    Returns
    -------

    centers : An Nx2 array-like
        Longitude and latitude in radians of the centers of each cluster.
    """
    lon, lat = _convert_measurements(args, kwargs.get('measurement', 'poles'))
    num = kwargs.get('num', 2)
    bidirectional = kwargs.get('bidirectional', True)
    tolerance = kwargs.get('tolerance', 1e-5)

    points = lon, lat
    dist = lambda x: stereonet_math.angular_distance(x, points, bidirectional)

    center_lon = np.random.choice(lon, num)
    center_lat = np.random.choice(lat, num)
    centers = np.column_stack([center_lon, center_lat])

    while True:
        dists = np.array([dist(item) for item in centers]).T
        closest = dists.argmin(axis=1)

        new_centers = []
        for i in range(num):
            mask = mask = closest == i
            _, vecs = cov_eig(lon[mask], lat[mask], bidirectional)
            new_centers.append(stereonet_math.cart2sph(*vecs[:,-1]))

        if np.allclose(centers, new_centers, atol=tolerance):
            break
        else:
            centers = new_centers

    return centers
