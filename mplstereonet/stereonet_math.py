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
    strike[strike > 360] -= 360
    return strike, dip

def geographic2pole(lon, lat):
    plunge, bearing = geographic2plunge_bearing(lon, lat)
    strike = bearing + 90 
    strike[strike > 360] -= 360
    dip = 90 - plunge
    return strike, dip

def geographic2plunge_bearing(lon, lat):
    lon, lat = np.atleast_1d(lon, lat)
    x, y, z = sph2cart(lon, lat)

    # Bearing will be in the y-z plane...
    bearing = np.arctan2(z, y)

    # Plunge is the angle between the line and the y-z plane
    plunge = np.atan(x / np.hypot(z, y))

    # Convert back to azimuths in degrees..
    plunge, bearing = np.degrees(plunge), np.degrees(bearing)
    bearing = 90 - bearing
    bearing[bearing < 0] += 360

    return plunge, bearing



