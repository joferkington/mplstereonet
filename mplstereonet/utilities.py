import numpy as np
import re
import stereonet_math as smath

def parse_strike_dip(strike, dip):
    """
    Parses strings of strike and dip and returns strike and dip measurements 
    following the right-hand-rule.

    Dip directions are parsed, and if the measurement does not follow the 
    right-hand-rule, the opposite end of the strike measurement is returned.

    Accepts either quadrant-formatted or azimuth-formatted strikes.

    For example, this would convert a strike of "N30E" and a dip of "45NW" to
    a strike of 210 and a dip of 45.

    Parameters:
    -----------
        strike : A string representing a strike measurement. May be in azimuth 
            or quadrant format. 
        dip : A string representing the dip angle and direction of a plane.

    Returns:
    --------
        azi : A float representing the azimuth of the strike of the plane with
            dip direction indicated following the right-hand-rule.
        dip : A float representing the dip of the plane.
    """
    origstrike, origdip = strike, dip

    if strike[0].isalpha():
        strike = parse_quadrant_measurement(strike)
    else:
        strike = float(strike)

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
    rake of "10NE" to a strike of 210, dip of 45, and rake of -10.

    Rake angles returned by this function will always be between -90 and 90.

    If no directions are specified, the measurement is assumed to follow the 
    usual right-hand-rule convention.

    Parameters:
    -----------
        strike : A string representing a strike measurement. May be in azimuth 
            or quadrant format. 
        dip : A string representing the dip angle and direction of a plane.
        rake : A string representing the rake angle and direction that the rake
            is measured from.

    Returns:
    --------
        strike, dip, rake : Floating point measurements of strike, dip, and rake
            following the conventions outlined above.
    """
    strike, dip = parse_strike_dip(strike, dip)
    rake, direction = split_trailing_letters(rake)

    if direction is not None:
        if opposite_end(strike, direction):
            rake = -rake

    if rake > 90:
        rake -= 180
    if rake < -90:
        rake += 180

    return strike, dip, rake

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
    azimuth = {'N':0, 'S':180, 'E':90, 'W':270}

    azi = azimuth[letters[-1]]
    for letter in letters[1::-1]:
        azi = circmean([azi, azimuth[letter]])
    return azi

def _azimuth2vec(azi):
    azi = np.radians(azi)
    return np.cos(azi), np.sin(azi)



def parse_quadrant_measurement(quad_azimuth):
    """
    Parses a quadrant measurement of the form "AxxB", where A and B are cardinal
    directions and xx is an angle measured relative to those directions.

    In other words, it converts a measurement such as E30N into an azimuth of
    60 degrees, or W10S into an azimuth of 260 degrees.

    For ambiguous quadrant measurements such as "N30S", a ValueError is raised.

    Parameters:
    -----------
        quad_azimuth : A string representing a strike measurement in quadrant 
            form.

    Returns:
    --------
        azi : An azimuth in degrees clockwise from north.
    """
    def rotation_direction(first, second):
        return np.cross(_azimuth2vec(first), _azimuth2vec(second))

    # Parse measurement
    first_dir = quadrantletter_to_azimuth(quad_azimuth[0].upper())
    sec_dir = quadrantletter_to_azimuth(quad_azimuth[-1].upper())
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

