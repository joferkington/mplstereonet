import numpy as np
import re
from . import stereonet_math as smath

def parse_strike_dip(strike, dip):
    """
    Parses strings of strike and dip and returns strike and dip measurements
    following the right-hand-rule.

    Dip directions are parsed, and if the measurement does not follow the
    right-hand-rule, the opposite end of the strike measurement is returned.

    Accepts either quadrant-formatted or azimuth-formatted strikes.

    For example, this would convert a strike of "N30E" and a dip of "45NW" to
    a strike of 210 and a dip of 45.

    Parameters
    ----------
    strike : string
        A strike measurement. May be in azimuth or quadrant format.
    dip : string
        The dip angle and direction of a plane.

    Returns
    -------
    azi : float
        Azimuth in degrees of the strike of the plane with dip direction
        indicated following the right-hand-rule.
    dip : float
        Dip of the plane in degrees.
    """
    strike = parse_azimuth(strike)
    dip, direction = split_trailing_letters(dip)

    if direction is not None:
        expected_direc = strike + 90
        if opposite_end(expected_direc, direction):
            strike += 180

    if strike > 360:
        strike -= 360

    return strike, dip

def parse_rake(strike, dip, rake):
    """
    Parses strings of strike, dip, and rake and returns a strike, dip, and rake
    measurement following the right-hand-rule, with the "end" of the strike
    that the rake is measured from indicated by the sign of the rake (positive
    rakes correspond to the strike direction, negative rakes correspond to the
    opposite end).

    Accepts either quadrant-formatted or azimuth-formatted strikes.

    For example, this would convert a strike of "N30E", dip of "45NW", with a
    rake of "10NE" to a strike of 210, dip of 45, and rake of 170.

    Rake angles returned by this function will always be between 0 and 180

    If no directions are specified, the measuriement is assumed to follow the
    usual right-hand-rule convention.

    Parameters
    ----------
    strike : string
        A strike measurement. May be in azimuth or quadrant format.
    dip : string
        The dip angle and direction of a plane.
    rake : string
        The rake angle and direction that the rake is measured from.

    Returns
    -------
    strike, dip, rake : floats
        Measurements of strike, dip, and rake following the conventions
        outlined above.
    """
    strike, dip = parse_strike_dip(strike, dip)
    rake, direction = split_trailing_letters(rake)

    if direction is not None:
        if opposite_end(strike, direction):
            rake = -rake

    if rake < 0:
        rake += 180
    elif rake > 180:
        rake -= 180

    return strike, dip, rake

def parse_plunge_bearing(plunge, bearing):
    """
    Parses strings of plunge and bearing and returns a consistent plunge and
    bearing measurement as floats. Plunge angles returned by this function will
    always be between 0 and 90.

    If no direction letter(s) is present, the plunge is assumed to be measured
    from the end specified by the bearing. If a direction letter(s) is present,
    the bearing will be switched to the opposite (180 degrees) end if the
    specified direction corresponds to the opposite end specified by the
    bearing.

    Parameters
    ----------
    plunge : string
        A plunge measurement.
    bearing : string
        A bearing measurement. May be in azimuth or quadrant format.

    Returns
    -------
    plunge, bearing: floats
        The plunge and bearing following the conventions outlined above.

    Examples
    ---------

        >>> parse_plunge_bearing("30NW", 160)
        ... (30, 340)

    """
    bearing = parse_azimuth(bearing)
    plunge, direction = split_trailing_letters(plunge)

    if direction is not None:
        if opposite_end(bearing, direction):
            bearing +=180

    if plunge < 0:
        bearing += 180
        plunge = -plunge
    if plunge > 90:
        bearing += 180
        plunge = 180 - plunge

    if bearing > 360:
        bearing -= 360

    return plunge, bearing

def dip_direction2strike(azimuth):
    """
    Converts a planar measurment of dip direction using the dip-azimuth
    convention into a strike using the right-hand-rule.

    Parameters
    ----------
    azimuth : number or string
        The dip direction of the plane in degrees. This can be either a
        numerical azimuth in the 0-360 range or a string representing a quadrant
        measurement (e.g. N30W).

    Returns
    -------
    strike : number
        The strike of the plane in degrees following the right-hand-rule.
    """
    azimuth = parse_azimuth(azimuth)
    strike = azimuth - 90
    if strike < 0:
        strike += 360
    return strike

def strike2dip_direction(strike):
    """
    Converts a planar measurement of strike using the right-hand-rule into the
    dip direction (i.e. the direction that the plane dips).

    Parameters
    ----------
    strike : number or string
        The strike direction of the plane in degrees. This can be either a
        numerical azimuth in the 0-360 range or a string representing a quadrant
        measurement (e.g. N30W).

    Returns
    -------
    azimuth : number
        The dip direction of the plane in degrees (0-360).
    """
    strike = parse_azimuth(strike)
    dip_direction = strike + 90
    if dip_direction > 360:
        dip_direction -= 360
    return dip_direction

def opposite_end(azimuth, quadrant):
    direc = quadrantletter_to_azimuth(quadrant)
    dot = np.dot(_azimuth2vec(direc), _azimuth2vec(azimuth))
    return dot < 0

def split_trailing_letters(item):
    # Match things like 45NW, 45E, 45WNW, etc
    letters = re.search(r'[NESWnesw]', item)
    if letters is None:
        return float(item), None
    else:
        measurement = item[:letters.start()]
        direction = item[letters.start():]
        return float(measurement), direction

def circmean(azimuths):
    azimuths = np.radians(azimuths)
    x = np.cos(azimuths)
    y = np.sin(azimuths)
    return np.degrees(np.arctan2(y.mean(), x.mean()))

def quadrantletter_to_azimuth(letters):
    letters = letters.strip()
    azimuth = {'N':0, 'S':180, 'E':90, 'W':270}

    azi = azimuth[letters[-1]]
    for letter in letters[1::-1]:
        azi = circmean([azi, azimuth[letter]])
    return azi

def _azimuth2vec(azi):
    azi = np.radians(azi)
    return np.cos(azi), np.sin(azi)

def parse_azimuth(azimuth):
    """
    Parses an azimuth measurement in azimuth or quadrant format.

    Parameters
    -----------
    azimuth : string or number
        An azimuth measurement in degrees or a quadrant measurement of azimuth.

    Returns
    -------
    azi : float
        The azimuth in degrees clockwise from north (range: 0-360)

    See Also
    --------
    parse_quadrant_measurement
    parse_strike_dip
    parse_plunge_bearing
    """
    try:
        azimuth = float(azimuth)
    except ValueError:
        if not azimuth[0].isalpha():
            raise ValueError('Ambiguous azimuth: {}'.format(azimuth))
        azimuth = parse_quadrant_measurement(azimuth)
    return azimuth

def parse_quadrant_measurement(quad_azimuth):
    """
    Parses a quadrant measurement of the form "AxxB", where A and B are cardinal
    directions and xx is an angle measured relative to those directions.

    In other words, it converts a measurement such as E30N into an azimuth of
    60 degrees, or W10S into an azimuth of 260 degrees.

    For ambiguous quadrant measurements such as "N30S", a ValueError is raised.

    Parameters
    -----------
    quad_azimuth : string
        An azimuth measurement in quadrant form.

    Returns
    -------
    azi : float
        An azimuth in degrees clockwise from north.

    See Also
    --------
    parse_azimuth
    """
    def rotation_direction(first, second):
        return np.cross(_azimuth2vec(first), _azimuth2vec(second))

    # Parse measurement
    quad_azimuth = quad_azimuth.strip()
    try:
        first_dir = quadrantletter_to_azimuth(quad_azimuth[0].upper())
        sec_dir = quadrantletter_to_azimuth(quad_azimuth[-1].upper())
    except KeyError:
        raise ValueError('{} is not a valid azimuth'.format(quad_azimuth))

    angle = float(quad_azimuth[1:-1])

    # Convert quadrant measurement into an azimuth
    direc = rotation_direction(first_dir, sec_dir)
    azi = first_dir + direc * angle

    # Catch ambiguous measurements such as N10S and raise an error
    if abs(direc) < 0.9:
        raise ValueError('{} is not a valid azimuth'.format(quad_azimuth))

    # Ensure that 0 <= azi <= 360
    if azi < 0:
        azi += 360
    elif azi > 360:
        azi -= 360

    return azi
