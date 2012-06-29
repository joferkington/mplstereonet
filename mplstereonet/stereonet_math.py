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
        lon : Longitude in radians
        lat : Latitude in radians

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

def _rotate(lon, lat, theta):
    """
    Rotate "lon", "lat" coords (in degrees) about the X-axis by "theta" degrees. 
    This effectively simulates rotating a physical stereonet.
    Returns rotated lon, lat coords in radians.
    """
    # Convert input to numpy arrays in radians
    lon, lat = np.atleast_1d(lon, lat)
    lon, lat = map(np.radians, [lon, lat])
    theta = np.radians(theta)

    # Convert to cartesian coords for the rotation
    x, y, z = sph2cart(lon, lat)

    # This is just a rotation matrix for a rotation about the X-axis
    X = x
    Y = y*np.cos(theta) + z*np.sin(theta)
    Z = -y*np.sin(theta) + z*np.cos(theta)

    # Now convert back to spherical coords (longitude and latitude, ignore R)
    lon, lat = cart2sph(X,Y,Z) 
    return lon, lat # in radians!

def plane(strike, dip, segments=100):
    """
    Calculates the longitude and latitude of `segments` points along the 
    stereonet projection of each plane with a given `strike` and `dip` in 
    degrees.
    
    `strike` and `dip` may be sequences or single values.
    
    Parameters
    ----------
        strike : The strike of the plane(s) in degrees, with dip direction 
            indicated by the azimuth (e.g. 315 vs. 135) specified following the
            "right hand rule". 
        dip : The dip of the plane(s) in degrees.         
        segments : The number of points in the returned `lon` and `lat` arrays.
            Defaults to 100 segments.
    
    Returns:
        lon, lat : num_segments x num_strikes arrays of longitude and latitude
            in radians.
    """
    strikes, dips = np.atleast_1d(strike, dip)
    lons = np.zeros((segments, strikes.size), dtype=np.float)
    lats = lons.copy()
    for i, (strike, dip) in enumerate(zip(strikes, dips)):
        # We just plot a line of constant longitude and rotate it by the strike.
        dip = 90 - dip
        lon = dip * np.ones(segments)
        lat = np.linspace(-90, 90, segments)
        lon, lat = _rotate(lon, lat, strike)
        lons[:,i] = lon
        lats[:,i] = lat
    return lons, lats

def pole(strike, dip):
    """
    Calculates the longitude and latitude of the pole(s) to the plane(s) 
    specified by `strike` and `dip`, given in degrees.

    `strike` and `dip` may be sequences or single values.
    
    Parameters
    ----------
        strike : The strike of the plane(s) in degrees, with dip direction 
            indicated by the azimuth (e.g. 315 vs. 135) specified following the
            "right hand rule". 
        dip : The dip of the plane(s) in degrees.     

    Returns:
        lon, lat : Arrays of longitude and latitude in radians.
    """
    strike, dip = np.atleast_1d(strike, dip)
    # Plot the approriate point for a strike of 0 and rotate it
    lon, lat = -dip, 0.0
    lon, lat = _rotate(lon, lat, strike)
    return lon, lat

def rake(strike, dip, rake_angle):
    """
    Calculates the longitude and latitude of the linear feature(s) specified by
    `strike`, `dip`, and `rake_angle`.

    `strike`, `dip`, and `rake_angle` may be sequences or single values.
    
    Parameters
    ----------
        strike : The strike of the plane(s) in degrees, with dip direction 
            indicated by the azimuth (e.g. 315 vs. 135) specified following the
            "right hand rule". 
        dip : The dip of the plane(s) in degrees. 
        rake_angle : The angle of the lineation on the plane measured in degrees
            downward from horizontal. Zero degrees corresponds to the "right-
            hand" direction indicated by the strike, while 180 degrees or a 
            negative angle corresponds to the opposite direction.
    
    Returns:
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

    `plunge` and `bearing` may be sequences or single values.
    
    Parameters
    ----------
        plunge : The plunge of the line(s) in degrees. The plunge is measured 
            in degrees downward from the end of the feature specified by the 
            bearing.         
        bearing : The bearing (azimuth) of the line(s) in degrees.

    Returns:
        lon, lat : Arrays of longitude and latitude in radians.
    """
    plunge, bearing = np.atleast_1d(plunge, bearing)
    # Plot the approriate point for a bearing of 0 and rotate it
    lat = 90 - plunge
    lon = 0
    lon, lat = _rotate(lon, lat, bearing)
    return lon, lat

def plunge_bearing2pole(plunge, bearing):
    """
    Converts the given `plunge` and `bearing` in degrees to a strike and dip
    of the plane whose pole would be parallel to the line specified. (i.e. The
    pole to the plane returned would plot at the same point as the specified
    plunge and bearing.)

    `plunge` and `bearing` may be sequences or single values.
    
    Parameters
    ----------
        plunge : The plunge of the line(s) in degrees. The plunge is measured 
            in degrees downward from the end of the feature specified by the 
            bearing.         
        bearing : The bearing (azimuth) of the line(s) in degrees.

    Returns:
    --------
        strike, dip : Arrays of strikes and dips in degrees following the 
            right-hand-rule.
    """
    plunge, bearing = np.atleast_1d(plunge, bearing)
    strike = bearing + 90
    dip = 90 - plunge
    strike[strike >= 360] -= 360
    return strike, dip

def mean_vector(lons, lats):
    """
    Returns the resultant vector from a series of longitudes and latitudes

    Parameters:
    -----------
        lons : A sequence of longitudes (in radians)
        lats : A sequence of latitudes (in radians)

    Returns:
        mean_vec : A tuple of (lon, lat) in radians
        r_value : The magnitude of the resultant vector (between 0 and 1)
            This represents the degree of clustering in the data.
    """
    xyz = sph2cart(lons, lats)
    xyz = np.vstack(xyz).T
    mean_vec = xyz.mean(axis=0)
    r_value = np.linalg.norm(mean_vec) / xyz.shape[0]
    mean_vec = cart2sph(*mean_vec)
    return mean_vec, r_value

def geographic2pole(lon, lat):
    """
    Converts a longitude and latitude (from a stereonet) into the strike and dip
    of the plane whose pole lies at the given longitude(s) and latitude(s).

    Parameters:
    -----------
        lon : A sequence of longitudes (or a single longitude) in radians
        lat : A sequence of latitudes (or a single latitude) in radians

    Returns:
    --------
        strike : A sequence of strikes in degrees
        dip : A sequence of dips in degrees
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

    Parameters:
    -----------
        lon, lat : Sequences of (or single) longitudes and latitudes in radians
            as measured from a lower-hemisphere stereonet

    Returns:
    --------
        plunge : The plunge of the vector in degrees downward from horizontal.
        bearing : The bearing of the vector in degrees clockwise from north.
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

    Parameters:
    -----------
        strike1, dip1 : The strike and dip (in degrees, following the 
            right-hand-rule) of the first plane(s).
        strike2, dip2 : The strike and dip (in degrees, following the 
            right-hand-rule) of the second plane(s).

    Returns:
    --------
        plunge, bearing : The plunge and bearing(s) (in degrees) of the line 
            representing the intersection of the two planes.
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

    Parameters:
    -----------
        strike, dip : The strike and dip (in degrees, following the 
            right-hand-rule) or a sequence of strikes and dips of the plane(s).
        plunge, bearing : The plunge and bearing (in degrees) or a sequence of
            plunges and bearings of the linear feature(s) to be projected onto
            the plane.

    Returns:
    --------
        rake : A sequence of rake angles measured downwards from horizontal in 
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

    Parameters:
    -----------
        strike, dip : The strike and dip of the plane in degrees following the
            right-hand-rule.
        azimuth : The azimuth of the linear feature in degrees clockwise from
            north (i.e. a 0-360 azimuth).

    Returns:
    --------
        rake : A rake angle in degrees measured downwards from horizontal. 
            Negative values correspond to the opposite end of the strike.
    """
    plunge, bearing = plane_intersection(strike, dip, azimuth, 90)
    rake = project_onto_plane(strike, dip, plunge, bearing)
    return rake

def xyz2stereonet(x, y, z):
    """
    Converts x, y, z in _world_ cartesian coordinates into lower-hemisphere
    stereonet coordinates.

    Parameters
    ----------
        x, y, z : Sequences of world coordinates

    Returns:
    --------
        lon, lat : Sequences of longitudes and latitudes (in radians)
    """
    x, y, z = np.atleast_1d(x, y, z)
    return cart2sph(-z, x, y)

def stereonet2xyz(lon, lat):
    """
    Converts a sequence of longitudes and latitudes from a lower-hemisphere
    stereonet into _world_ x,y,z coordinates.

    Parameters
    ----------
        lon, lat : Sequences of longitudes and latitudes (in radians) from a
            lower-hemisphere stereonet

    Returns:
    --------
        x, y, z : The world x,y,z components of the vectors represented by the 
            lon, lat coordinates on the stereonet.
    """
    lon, lat = np.atleast_1d(lon, lat)
    x, y, z = sph2cart(lon, lat)
    return y, z, -x

def vector2plunge_bearing(x, y, z):
    """
    Converts a vector or series of vectors given as x, y, z in world
    coordinates into plunge/bearings.

    Parameters:
    -----------
        x : The x-component(s) of the normal vector
        y : The y-component(s) of the normal vector
        z : The z-component(s) of the normal vector

    Returns:
    --------
        plunge : The plunge of the vector in degrees downward from horizontal.
        bearing : The bearing of the vector in degrees clockwise from north.
    """
    return geographic2plunge_bearing(*xyz2stereonet(x,y,z))

def vector2pole(x, y, z):
    """
    Converts a vector or series of vectors given as x, y, z in world
    coordinates into the strike/dip of the planes whose normal vectors are 
    parallel to the specified vectors.  (In other words, each xi,yi,zi is 
    treated as a normal vector and this returns the strike/dip of the 
    corresponding plane.)

    Parameters:
    -----------
        x : The x-component(s) of the normal vector
        y : The y-component(s) of the normal vector
        z : The z-component(s) of the normal vector

    Returns:
    --------
        strike : The strike of the plane, in degrees clockwise from north.
            Dip direction is indicated by the "right hand rule".
        dip : The dip of the plane, in degrees downward from horizontal
    """
    return  geographic2pole(*xyz2stereonet(x, y, z))


