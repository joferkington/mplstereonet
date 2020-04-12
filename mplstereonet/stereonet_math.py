"""
Utilities to convert between strike/dip, etc and points/lines in lat, long
space.

A stereonet in <long,lat> coordinates:
              <0,90>
               ***
            *       *
   <-90,0> *         *<90,0>
           *         *
            *       *
               ***
             <0,-90>

If strike=0, plotting lines, rakes, planes or poles to planes is simple.  For a
plane, it's a line of constant longitude at long=90-dip.  For a line, it's a
point at long=0,lat=90-dip.  For a rake, it's a point at long=90-dip,
lat=90-rake.  These points can then be rotated to the proper strike. (A
rotation matrix around the X-axis is much simpler than the trig otherwise
necessary!)

All of these assume that strikes and dips follow the "right-hand-rule".
In other words, if we're facing in the direction given for the strike, the plane
dips to our right.
"""
import numpy as np

def sph2cart(lon, lat):
    """
    Converts a longitude and latitude (or sequence of lons and lats) given in
    _radians_ to cartesian coordinates, `x`, `y`, `z`, where x=0, y=0, z=0 is
    the center of the globe.

    Parameters
    ----------
    lon : array-like
        Longitude in radians
    lat : array-like
        Latitude in radians

    Returns
    -------
    `x`, `y`, `z` : Arrays of cartesian coordinates
    """
    x = np.cos(lat)*np.cos(lon)
    y = np.cos(lat)*np.sin(lon)
    z = np.sin(lat)
    return x, y, z

def cart2sph(x, y, z):
    """
    Converts cartesian coordinates `x`, `y`, `z` into a longitude and latitude.
    x=0, y=0, z=0 is assumed to correspond to the center of the globe.
    Returns lon and lat in radians.

    Parameters
    ----------
    `x`, `y`, `z` : Arrays of cartesian coordinates

    Returns
    -------
    lon : Longitude in radians
    lat : Latitude in radians
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.arcsin(z/r)
    lon = np.arctan2(y, x)
    return lon, lat

def _rotate(lon, lat, theta, axis='x'):
    """
    Rotate "lon", "lat" coords (in _degrees_) about the X-axis by "theta"
    degrees.  This effectively simulates rotating a physical stereonet.
    Returns rotated lon, lat coords in _radians_).
    """
    # Convert input to numpy arrays in radians
    lon, lat = np.atleast_1d(lon, lat)
    lon, lat = map(np.radians, [lon, lat])
    theta = np.radians(theta)

    # Convert to cartesian coords for the rotation
    x, y, z = sph2cart(lon, lat)

    lookup = {'x':_rotate_x, 'y':_rotate_y, 'z':_rotate_z}
    X, Y, Z = lookup[axis](x, y, z, theta)

    # Now convert back to spherical coords (longitude and latitude, ignore R)
    lon, lat = cart2sph(X,Y,Z)
    return lon, lat # in radians!

def _rotate_x(x, y, z, theta):
    X = x
    Y = y*np.cos(theta) + z*np.sin(theta)
    Z = -y*np.sin(theta) + z*np.cos(theta)
    return X, Y, Z

def _rotate_y(x, y, z, theta):
    X = x*np.cos(theta) + -z*np.sin(theta)
    Y = y
    Z = x*np.sin(theta) + z*np.cos(theta)
    return X, Y, Z

def _rotate_z(x, y, z, theta):
    X = x*np.cos(theta) + -y*np.sin(theta)
    Y = x*np.sin(theta) + y*np.cos(theta)
    Z = z
    return X, Y, Z

def antipode(lon, lat):
    """
    Calculates the antipode (opposite point on the globe) of the given point or
    points. Input and output is expected to be in radians.

    Parameters
    ----------
    lon : number or sequence of numbers
        Longitude in radians
    lat : number or sequence of numbers
        Latitude in radians

    Returns
    -------
    lon, lat : arrays
        Sequences (regardless of whether or not the input was a single value or
        a sequence) of longitude and latitude in radians.
    """
    x, y, z = sph2cart(lon, lat)
    return cart2sph(-x, -y, -z)

def plane(strike, dip, segments=100, center=(0, 0)):
    """
    Calculates the longitude and latitude of `segments` points along the
    stereonet projection of each plane with a given `strike` and `dip` in
    degrees.  Returns points for one hemisphere only.

    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) in degrees, with dip direction indicated by
        the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.
    segments : number or sequence of numbers
        The number of points in the returned `lon` and `lat` arrays.  Defaults
        to 100 segments.
    center : sequence of two numbers (lon, lat)
        The longitude and latitude of the center of the hemisphere that the
        returned points will be in. Defaults to 0,0 (approriate for a typical
        stereonet).

    Returns
    -------
    lon, lat : arrays
        `num_segments` x `num_strikes` arrays of longitude and latitude in
        radians.
    """
    lon0, lat0 = center
    strikes, dips = np.atleast_1d(strike, dip)
    lons = np.zeros((segments, strikes.size), dtype=np.float)
    lats = lons.copy()
    for i, (strike, dip) in enumerate(zip(strikes, dips)):
        # We just plot a line of constant longitude and rotate it by the strike.
        dip = 90 - dip
        lon = dip * np.ones(segments)
        lat = np.linspace(-90, 90, segments)
        lon, lat = _rotate(lon, lat, strike)

        if lat0 != 0 or lon0 != 0:
            dist = angular_distance([lon, lat], [lon0, lat0], False)
            mask = dist > (np.pi / 2)
            lon[mask], lat[mask] = antipode(lon[mask], lat[mask])
            change = np.diff(mask.astype(int))
            ind = np.flatnonzero(change) + 1
            lat = np.hstack(np.split(lat, ind)[::-1])
            lon = np.hstack(np.split(lon, ind)[::-1])

        lons[:,i] = lon
        lats[:,i] = lat

    return lons, lats

def pole(strike, dip):
    """
    Calculates the longitude and latitude of the pole(s) to the plane(s)
    specified by `strike` and `dip`, given in degrees.

    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) in degrees, with dip direction indicated by
        the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.

    Returns
    -------
    lon, lat : Arrays of longitude and latitude in radians.
    """
    strike, dip = np.atleast_1d(strike, dip)
    mask = dip > 90
    dip[mask] = 180 - dip[mask]
    strike[mask] += 180
    # Plot the approriate point for a strike of 0 and rotate it
    lon, lat = -dip, 0.0
    lon, lat = _rotate(lon, lat, strike)
    return lon, lat

def rake(strike, dip, rake_angle):
    """
    Calculates the longitude and latitude of the linear feature(s) specified by
    `strike`, `dip`, and `rake_angle`.

    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) in degrees, with dip direction indicated by
        the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.
    rake_angle : number or sequence of numbers
        The angle of the lineation on the plane measured in degrees downward
        from horizontal. Zero degrees corresponds to the "right- hand"
        direction indicated by the strike, while 180 degrees or a negative
        angle corresponds to the opposite direction.

    Returns
    -------
    lon, lat : Arrays of longitude and latitude in radians.
    """
    strike, dip, rake_angle = np.atleast_1d(strike, dip, rake_angle)
    # Plot the approriate point for a strike of 0 and rotate it
    dip = 90 - dip
    lon = dip

    rake_angle = rake_angle.copy()
    rake_angle[rake_angle < 0] += 180
    lat = 90 - rake_angle

    lon, lat = _rotate(lon, lat, strike)
    return lon, lat

def line(plunge, bearing):
    """
    Calculates the longitude and latitude of the linear feature(s) specified by
    `plunge` and `bearing`.

    Parameters
    ----------
    plunge : number or sequence of numbers
        The plunge of the line(s) in degrees. The plunge is measured in degrees
        downward from the end of the feature specified by the bearing.
    bearing : number or sequence of numbers
        The bearing (azimuth) of the line(s) in degrees.

    Returns
    -------
    lon, lat : Arrays of longitude and latitude in radians.
    """
    plunge, bearing = np.atleast_1d(plunge, bearing)
    # Plot the approriate point for a bearing of 0 and rotate it
    lat = 90 - plunge
    lon = 0
    lon, lat = _rotate(lon, lat, bearing)
    return lon, lat

def cone(plunge, bearing, angle, segments=100):
    """
    Calculates the longitude and latitude of the small circle (i.e. a cone)
    centered at the given *plunge* and *bearing* with an apical angle of
    *angle*, all in degrees.

    Parameters
    ----------
    plunge : number or sequence of numbers
        The plunge of the center of the cone(s) in degrees. The plunge is
        measured in degrees downward from the end of the feature specified by
        the bearing.
    bearing : number or sequence of numbers
        The bearing (azimuth) of the center of the cone(s) in degrees.
    angle : number or sequence of numbers
        The apical angle (i.e. radius) of the cone(s) in degrees.
    segments : int, optional
        The number of vertices in the small circle.

    Returns
    -------
    lon, lat : arrays
        `num_measurements` x `num_segments` arrays of longitude and latitude in
        radians.
    """
    plunges, bearings, angles = np.atleast_1d(plunge, bearing, angle)
    lons, lats = [], []
    for plunge, bearing, angle in zip(plunges, bearings, angles):
        lat = (90 - angle) * np.ones(segments, dtype=float)
        lon = np.linspace(-180, 180, segments)
        lon, lat = _rotate(lon, lat, -plunge, axis='y')
        lon, lat = _rotate(np.degrees(lon), np.degrees(lat), bearing, axis='x')
        lons.append(lon)
        lats.append(lat)
    return np.vstack(lons), np.vstack(lats)

def plunge_bearing2pole(plunge, bearing):
    """
    Converts the given `plunge` and `bearing` in degrees to a strike and dip
    of the plane whose pole would be parallel to the line specified. (i.e. The
    pole to the plane returned would plot at the same point as the specified
    plunge and bearing.)

    Parameters
    ----------
    plunge : number or sequence of numbers
        The plunge of the line(s) in degrees. The plunge is measured in degrees
        downward from the end of the feature specified by the bearing.
    bearing : number or sequence of numbers
        The bearing (azimuth) of the line(s) in degrees.

    Returns
    -------
    strike, dip : arrays
        Arrays of strikes and dips in degrees following the right-hand-rule.
    """
    plunge, bearing = np.atleast_1d(plunge, bearing)
    strike = bearing + 90
    dip = 90 - plunge
    strike[strike >= 360] -= 360
    return strike, dip

def pole2plunge_bearing(strike, dip):
    """
    Converts the given *strike* and *dip* in dgrees of a plane(s) to a plunge
    and bearing of its pole.

    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) in degrees, with dip direction indicated by
        the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.

    Returns
    -------
    plunge, bearing : arrays
        Arrays of plunges and bearings of the pole to the plane(s) in degrees.
    """
    strike, dip = np.atleast_1d(strike, dip)
    bearing = strike - 90
    plunge = 90 - dip
    bearing[bearing < 0] += 360
    return plunge, bearing

def mean_vector(lons, lats):
    """
    Returns the resultant vector from a series of longitudes and latitudes

    Parameters
    ----------
    lons : array-like
        A sequence of longitudes (in radians)
    lats : array-like
        A sequence of latitudes (in radians)

    Returns
    -------
    mean_vec : tuple
        (lon, lat) in radians
    r_value : number
        The magnitude of the resultant vector (between 0 and 1) This represents
        the degree of clustering in the data.
    """
    xyz = sph2cart(lons, lats)
    xyz = np.vstack(xyz).T
    mean_vec = xyz.mean(axis=0)
    r_value = np.linalg.norm(mean_vec)
    mean_vec = cart2sph(*mean_vec)
    return mean_vec, r_value

def fisher_stats(lons, lats, conf=95):
    """
    Returns the resultant vector from a series of longitudes and latitudes. If
    a confidence is set the function additionally returns the opening angle
    of the confidence small circle (Fisher, 19..) and the dispersion factor
    (kappa).

    Parameters
    ----------
    lons : array-like
        A sequence of longitudes (in radians)
    lats : array-like
        A sequence of latitudes (in radians)
    conf : confidence value
        The confidence used for the calculation (float). Defaults to None.

    Returns
    -------
    mean vector: tuple
        The point that lies in the center of a set of vectors.
        (Longitude, Latitude) in radians.

    If 1 vector is passed to the function it returns two None-values. For
    more than one vector the following 3 values are returned as a tuple:

    r_value: float
        The magnitude of the resultant vector (between 0 and 1) This represents
        the degree of clustering in the data.
    angle: float
        The opening angle of the small circle that corresponds to confidence
        of the calculated direction.
    kappa: float
        A measure for the amount of dispersion of a group of layers. For
        one vector the factor is undefined. Approaches infinity for nearly
        parallel vectors and zero for highly dispersed vectors.

    """
    xyz = sph2cart(lons, lats)
    xyz = np.vstack(xyz).T
    mean_vec = xyz.mean(axis=0)
    r_value = np.linalg.norm(mean_vec)
    num = xyz.shape[0]
    mean_vec = cart2sph(*mean_vec)

    if num > 1:
        p = (100.0 - conf) / 100.0
        vector_sum = xyz.sum(axis=0)
        result_vect = np.sqrt(np.sum(np.square(vector_sum)))
        fract1 = (num - result_vect) / result_vect
        fract3 = 1.0 / (num - 1.0)
        angle = np.arccos(1 - fract1 * ((1 / p) ** fract3 - 1))
        angle = np.degrees(angle)
        kappa = (num - 1.0) / (num - result_vect)
        return mean_vec, (r_value, angle, kappa)
    else:
        return None, None

def geographic2pole(lon, lat):
    """
    Converts a longitude and latitude (from a stereonet) into the strike and dip
    of the plane whose pole lies at the given longitude(s) and latitude(s).

    Parameters
    ----------
    lon : array-like
        A sequence of longitudes (or a single longitude) in radians
    lat : array-like
        A sequence of latitudes (or a single latitude) in radians

    Returns
    -------
    strike : array
        A sequence of strikes in degrees
    dip : array
        A sequence of dips in degrees
    """
    plunge, bearing = geographic2plunge_bearing(lon, lat)
    strike = bearing + 90
    strike[strike >= 360] -= 360
    dip = 90 - plunge
    return strike, dip

def geographic2plunge_bearing(lon, lat):
    """
    Converts longitude and latitude in stereonet coordinates into a
    plunge/bearing.

    Parameters
    ----------
    lon, lat : numbers or sequences of numbers
        Longitudes and latitudes in radians as measured from a
        lower-hemisphere stereonet

    Returns
    -------
    plunge : array
        The plunge of the vector in degrees downward from horizontal.
    bearing : array
        The bearing of the vector in degrees clockwise from north.
    """
    lon, lat = np.atleast_1d(lon, lat)
    x, y, z = sph2cart(lon, lat)

    # Bearing will be in the y-z plane...
    bearing = np.arctan2(z, y)

    # Plunge is the angle between the line and the y-z plane
    r = np.sqrt(x*x + y*y + z*z)
    r[r == 0] = 1e-15
    plunge = np.arcsin(x / r)

    # Convert back to azimuths in degrees..
    plunge, bearing = np.degrees(plunge), np.degrees(bearing)
    bearing = 90 - bearing
    bearing[bearing < 0] += 360

    # If the plunge angle is upwards, get the opposite end of the line
    upwards = plunge < 0
    plunge[upwards] *= -1
    bearing[upwards] -= 180
    bearing[upwards & (bearing < 0)] += 360

    return plunge, bearing

def plane_intersection(strike1, dip1, strike2, dip2):
    """
    Finds the intersection of two planes. Returns a plunge/bearing of the linear
    intersection of the two planes.

    Also accepts sequences of strike1s, dip1s, strike2s, dip2s.

    Parameters
    ----------
    strike1, dip1 : numbers or sequences of numbers
        The strike and dip (in degrees, following the right-hand-rule) of the
        first plane(s).
    strike2, dip2 : numbers or sequences of numbers
        The strike and dip (in degrees, following the right-hand-rule) of the
        second plane(s).

    Returns
    -------
    plunge, bearing : arrays
        The plunge and bearing(s) (in degrees) of the line representing the
        intersection of the two planes.
    """
    norm1 = sph2cart(*pole(strike1, dip1))
    norm2 = sph2cart(*pole(strike2, dip2))
    norm1, norm2 = np.array(norm1), np.array(norm2)
    lon, lat = cart2sph(*np.cross(norm1, norm2, axis=0))
    return geographic2plunge_bearing(lon, lat)

def project_onto_plane(strike, dip, plunge, bearing):
    """
    Projects a linear feature(s) onto the surface of a plane. Returns a rake
    angle(s) along the plane.

    This is also useful for finding the rake angle of a feature that already
    intersects the plane in question.

    Parameters
    ----------
    strike, dip : numbers or sequences of numbers
        The strike and dip (in degrees, following the right-hand-rule) of the
        plane(s).
    plunge, bearing : numbers or sequences of numbers
        The plunge and bearing (in degrees) or of the linear feature(s) to be
        projected onto the plane.

    Returns
    -------
    rake : array
        A sequence of rake angles measured downwards from horizontal in
        degrees.  Zero degrees corresponds to the "right- hand" direction
        indicated by the strike, while a negative angle corresponds to the
        opposite direction. Rakes returned by this function will always be
        between -90 and 90 (inclusive).
    """
    # Project the line onto the plane
    norm = sph2cart(*pole(strike, dip))
    feature = sph2cart(*line(plunge, bearing))
    norm, feature = np.array(norm), np.array(feature)
    perp = np.cross(norm, feature, axis=0)
    on_plane = np.cross(perp, norm, axis=0)
    on_plane /= np.sqrt(np.sum(on_plane**2, axis=0))

    # Calculate the angle between the projected feature and horizontal
    # This is just a dot product, but we need to work with multiple measurements
    # at once, so einsum is quicker than apply_along_axis.
    strike_vec = sph2cart(*line(0, strike))
    dot = np.einsum('ij,ij->j', on_plane, strike_vec)
    rake = np.degrees(np.arccos(dot))

    # Convert rakes over 90 to negative rakes...
    rake[rake > 90] -= 180
    rake[rake < -90] += 180
    return rake

def azimuth2rake(strike, dip, azimuth):
    """
    Projects an azimuth of a linear feature onto a plane as a rake angle.

    Parameters
    ----------
    strike, dip : numbers
        The strike and dip of the plane in degrees following the
        right-hand-rule.
    azimuth : numbers
        The azimuth of the linear feature in degrees clockwise from north (i.e.
        a 0-360 azimuth).

    Returns
    -------
    rake : number
        A rake angle in degrees measured downwards from horizontal.  Negative
        values correspond to the opposite end of the strike.
    """
    plunge, bearing = plane_intersection(strike, dip, azimuth, 90)
    rake, = project_onto_plane(strike, dip, plunge, bearing)
    return rake

def xyz2stereonet(x, y, z):
    """
    Converts x, y, z in _world_ cartesian coordinates into lower-hemisphere
    stereonet coordinates.

    Parameters
    ----------
    x, y, z : array-likes
        Sequences of world coordinates

    Returns
    -------
    lon, lat : arrays
        Sequences of longitudes and latitudes (in radians)
    """
    x, y, z = np.atleast_1d(x, y, z)
    return cart2sph(-z, x, y)

def stereonet2xyz(lon, lat):
    """
    Converts a sequence of longitudes and latitudes from a lower-hemisphere
    stereonet into _world_ x,y,z coordinates.

    Parameters
    ----------
    lon, lat : array-likes
        Sequences of longitudes and latitudes (in radians) from a
        lower-hemisphere stereonet

    Returns
    -------
    x, y, z : arrays
        The world x,y,z components of the vectors represented by the lon, lat
        coordinates on the stereonet.
    """
    lon, lat = np.atleast_1d(lon, lat)
    x, y, z = sph2cart(lon, lat)
    return y, z, -x

def vector2plunge_bearing(x, y, z):
    """
    Converts a vector or series of vectors given as x, y, z in world
    coordinates into plunge/bearings.

    Parameters
    ----------
    x : number or sequence of numbers
        The x-component(s) of the normal vector
    y : number or sequence of numbers
        The y-component(s) of the normal vector
    z : number or sequence of numbers
        The z-component(s) of the normal vector

    Returns
    -------
    plunge : array
        The plunge of the vector in degrees downward from horizontal.
    bearing : array
        The bearing of the vector in degrees clockwise from north.
    """
    return geographic2plunge_bearing(*xyz2stereonet(x,y,z))

def vector2pole(x, y, z):
    """
    Converts a vector or series of vectors given as x, y, z in world
    coordinates into the strike/dip of the planes whose normal vectors are
    parallel to the specified vectors.  (In other words, each xi,yi,zi is
    treated as a normal vector and this returns the strike/dip of the
    corresponding plane.)

    Parameters
    ----------
    x : number or sequence of numbers
        The x-component(s) of the normal vector
    y : number or sequence of numbers
        The y-component(s) of the normal vector
    z : number or sequence of numbers
        The z-component(s) of the normal vector

    Returns
    -------
    strike : array
        The strike of the plane, in degrees clockwise from north.  Dip
        direction is indicated by the "right hand rule".
    dip : array
        The dip of the plane, in degrees downward from horizontal.
    """
    return  geographic2pole(*xyz2stereonet(x, y, z))

def angular_distance(first, second, bidirectional=True):
    """
    Calculate the angular distance between two linear features or elementwise
    angular distance between two sets of linear features. (Note: a linear
    feature in this context is a point on a stereonet represented
    by a single latitude and longitude.)

    Parameters
    ----------
    first : (lon, lat) 2xN array-like or sequence of two numbers
        The longitudes and latitudes of the first measurements in radians.
    second : (lon, lat) 2xN array-like or sequence of two numbers
        The longitudes and latitudes of the second measurements in radians.
    bidirectional : boolean
        If True, only "inner" angles will be returned. In other words, all
        angles returned by this function will be in the range [0, pi/2]
        (0 to 90 in degrees).  Otherwise, ``first`` and ``second``
        will be treated as vectors going from the origin outwards
        instead of bidirectional infinite lines.  Therefore, with
        ``bidirectional=False``, angles returned by this function
        will be in the range [0, pi] (zero to 180 degrees).

    Returns
    -------
    dist : array
        The elementwise angular distance between each pair of measurements in
        (lon1, lat1) and (lon2, lat2).

    Examples
    --------

    Calculate the angle between two lines specified as a plunge/bearing

        >>> angle = angular_distance(line(30, 270), line(40, 90))
        >>> np.degrees(angle)
        array([ 70.])

    Let's do the same, but change the "bidirectional" argument:

        >>> first, second = line(30, 270), line(40, 90)
        >>> angle = angular_distance(first, second, bidirectional=False)
        >>> np.degrees(angle)
        array([ 110.])

    Calculate the angle between two planes.

        >>> angle = angular_distance(pole(0, 10), pole(180, 10))
        >>> np.degrees(angle)
        array([ 20.])
    """
    lon1, lat1 = first
    lon2, lat2 = second
    lon1, lat1, lon2, lat2 = np.atleast_1d(lon1, lat1, lon2, lat2)
    xyz1 = sph2cart(lon1, lat1)
    xyz2 = sph2cart(lon2, lat2)
    # This is just a dot product, but we need to work with multiple measurements
    # at once, so einsum is quicker than apply_along_axis.
    dot = np.einsum('ij,ij->j', xyz1, xyz2)
    angle = np.arccos(dot)

    # There are numerical sensitivity issues around 180 and 0 degrees...
    # Sometimes a result will have an absolute value slighly over 1.
    if np.any(np.isnan(angle)):
        rtol = 1e-4
        angle[np.isclose(dot, -1, rtol)] = np.pi
        angle[np.isclose(dot, 1, rtol)] = 0

    if bidirectional:
        mask = angle > np.pi / 2
        angle[mask] = np.pi - angle[mask]

    return angle

def _repole(lon, lat, center):
    """
    Reproject data such that ``center`` is the north pole. Returns lon, lat
    in the new, rotated reference frame.

    This is currently a sketch for a later function. Do not assume it works
    correctly.
    """
    vec3 = sph2cart(*center)
    vec3 = np.squeeze(vec3)
    if not np.allclose(vec3, [0, 0, 1]):
        vec1 = np.cross(vec3, [0, 0, 1])
    else:
        vec1 = np.cross(vec3, [1, 0, 0])
    vec2 = np.cross(vec3, vec1)
    vecs = [item / np.linalg.norm(item) for item in [vec1, vec2, vec3]]
    basis = np.column_stack(vecs)

    xyz = sph2cart(lon, lat)
    xyz = np.column_stack(xyz)
    prime = xyz.dot(np.linalg.inv(basis))
    lon, lat = cart2sph(*prime.T)
    return lon[:,None], lat[:,None]
