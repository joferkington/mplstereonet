import numpy as np

from . import stereonet_math

def fit_girdle(*args, **kwargs):
    """
    Fits a plane to a scatter of points on a stereonet (a.k.a. a "girdle").

    Input arguments will be interpreted as poles, lines, rakes, or "raw"
    longitudes and latitudes based on the *measurement* keyword argument.
    (Defaults to "poles".)

    Parameters
    ----------
    *args : A variable number of sequences of measurements. By default, this
        will be expected to be *strike* & *dip*, both array-like sequences
        representing poles to planes.  (Rake measurements require three
        parameters, thus the variable number of arguments.) The *measurement*
        kwarg controls how these arguments are interpreted.
    measurement : {'poles', 'lines', 'rakes', 'radians'}, optional
        Controls how the input arguments are interpreted. Defaults to "poles".
        May be one of the following:
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
    longitudes and latitudes based on the *measurement* keyword argument.
    (Defaults to "poles".)

    Parameters
    ----------
    *args : A variable number of sequences of measurements. By default, this
        will be expected to be *strike* & *dip*, both array-like sequences
        representing poles to planes.  (Rake measurements require three
        parameters, thus the variable number of arguments.) The *measurement*
        kwarg controls how these arguments are interpreted.
    measurement : {'poles', 'lines', 'rakes', 'radians'}, optional
        Controls how the input arguments are interpreted. Defaults to "poles".
        May be one of the following:
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

def calculate_eigenvector(*args, **kwargs):
    """
    Finds the 3 eigenvectors of a series of geometries.

    Input arguments will be interpreted as poles, lines, rakes, or "raw"
    longitudes and latitudes based on the *measurement* keyword argument.
    (Defaults to "poles".)

    Parameters
    ----------
    *args : A variable number of sequences of measurements. By default, this
        will be expected to be *strike* & *dip*, both array-like sequences
        representing poles to planes.  (Rake measurements require three
        parameters, thus the variable number of arguments.) The *measurement*
        kwarg controls how these arguments are interpreted.
    measurement : {'poles', 'lines', 'rakes', 'radians'}, optional
        Controls how the input arguments are interpreted. Defaults to "poles".
        May be one of the following:
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
    One list, with 3 rows, each corresponding to the strike and dip of the
    eigenvector and the eigenvalue:

    [[s1,d1,e1],[s2,d2,e2],[s3,d3,e3]]

    Examples
    --------
    Find the eigenvectors of a series of planes:

        >>> strike = [270, 65, 280, 300]
        >>> dip = [20, 15, 10, 5]
        >>> eigenvector = mplstereonet.calculate_eigenvector(strike, dip)
    """
    eigen = []
    lon, lat = _convert_measurements(args, measurement)
    vals, vecs = cov_eig(lon, lat, bidirectional)
    for f in range(3):
        x, y, z = vecs[:, f]
        s, d = stereonet_math.geographic2pole(*stereonet_math.cart2sph(x, y, z))
        eigen.append([s[0], d[0], vals[f]])
    return eigen[0], eigen[1], eigen[2]

def _sd_of_eigenvector(data, vec, measurement='poles', bidirectional=True):
    """Unifies ``fit_pole`` and ``fit_girdle``."""
    lon, lat = _convert_measurements(data, measurement)
    vals, vecs = cov_eig(lon, lat, bidirectional)
    x, y, z = vecs[:, vec]
    s, d = stereonet_math.geographic2pole(*stereonet_math.cart2sph(x, y, z))
    return s[0], d[0]

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

