"""
Classes and functions for kinematic analysis for rock slope stability. 
Kinematic analyses for three failure modes are available: (1) Planar Sliding, 
(2) Wedge Sliding, and (3) Flexural toppling. 

References:
(1)) Wyllie, D.C. and Mah, C.W. (2004) Rock Slope Engineering. 4th Edition, 
E & FN Spon, London, 431. 
(2) DIPS software from Rocscience:
https://www.rocscience.com/help/dips/#t=dips%2FKinematic_Analysis_Overview.htm
"""

import numpy as np
from shapely import geometry, ops
from . import stereonet_math 
from .convenience_functions import subplots
from .analysis import azimuth_diff, apparent_dip
   
def daylight_envelope(strike, dip, segments=500):
    """
    Calculates the longitude and latitude of `segments` points along the
    stereonet projection of the daylight envelope of each slope face
    with a given `strike` and `dip` in degrees.

    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) (slope face) in degrees, with dip direction
        indicated by the azimuth (e.g. 315 vs. 135) specified following the 
        "right hand rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.
    segments : number or sequence of numbers
        The number of points in the returned `lon` and `lat` arrays.  Defaults
        to 500 segments.

    Returns
    -------
    lon, lat : arrays
        `num_segments` x `num_strikes` arrays of longitude and latitude in
        radians.
    """
    
    # Get apparent dips from -90 to +90 (azimuth difference) from slope dip 
    # direction, i.e. +0 to +180 from slope strike. This essentially generates 
    # points defining the great-circle plane that represents the slope face
    dl_bearings = np.linspace(0, 180, segments).reshape(segments, 1)
    dl_plunges = apparent_dip(dip, 90-dl_bearings)
    
    # More points needed for daylight envelope for steep slopes
    if dip > 89:
        # Crop original end sections at apparent dip = 0
        dl_bearings = dl_bearings[1:-1]
        # Create main section. End points cropped to avoid overlapping
        b2 = dl_bearings[1:-1]
        p2 = apparent_dip(dip, 90-b2)
        # Get the apparent dip of the cropped end points (new connection points)
        connect_dip = apparent_dip(dip, 90 - dl_bearings[0])
        # Create the two new end sections, by generating points from 
        # apparent dip = 0 to the apparent dip of the connection points 
        p1 = np.linspace(0, connect_dip, segments)
        b1 = 90 + azimuth_diff(dip, p1)
        p3 = p1[::-1]
        b3 = 90 - azimuth_diff(dip, p3)
        # Connect the 3 sections
        dl_bearings = np.vstack((b1, b2[::-1], b3))
        dl_plunges = np.vstack((p1, p2[::-1], p3))

    # Convert to lat,lon of poles
    lon, lat = stereonet_math.pole(dl_bearings-90, dl_plunges)
    lon, lat = stereonet_math._rotate(np.degrees(lon), np.degrees(lat), strike)
    return lon, lat

def _curved_latlims(angle, segments=100):
    """
    Calculates the longitude and latitude of `segments` points along the
    stereonet projection of the "curved" lateral limit bounds in both 
    direction, for strike=0. 
    """
    # Plot lines of constant latitude
    angle = np.radians(angle)
    lat1 = -angle * np.ones(segments)
    lon1 = np.linspace(-np.pi/2, np.pi/2, segments)
    lat2 = angle * np.ones(segments)
    lon2 = lon1.copy()
            
    return lon1, lat1, lon2, lat2

def _shape(shape_type, strike=0, dip=0, angle=0):
    """
    Prepare elements required to construct the kinematic analysis plots (e.g. 
    planes, cones) into Shapely geometries.
    """
    if shape_type=='plane':
        lon, lat = stereonet_math.plane(strike, dip)
        return geometry.LineString(np.hstack((lon, lat)))
    
    elif shape_type=='curved_latlims':
        lon1, lat1, lon2, lat2 = _curved_latlims(angle)
        return [geometry.LineString(np.vstack((lon1, lat1)).T), 
                geometry.LineString(np.vstack((lon2, lat2)).T)]
    
    elif shape_type=='cone':
        lon, lat = stereonet_math.cone(90, 0, angle, segments=200)
        return geometry.Polygon(np.vstack((lon[0], lat[0])).T)
    
    elif shape_type=='daylight_envelope':
        lon, lat = daylight_envelope(strike, dip)
        return geometry.Polygon(np.hstack((lon[:-1], lat[:-1])))
    
    elif shape_type=='flexural_envelope':
        p_lon, p_lat = stereonet_math.plane(0, 1e-9) # perimeter
        sl_lon, sl_lat = stereonet_math.plane(strike, dip-angle)  # slip limit
        lon = np.vstack((p_lon, np.flip(sl_lon[1:-1])))
        lat = np.vstack((p_lat, np.flip(sl_lat[1:-1])))
        return geometry.Polygon(np.hstack((lon, lat)))
    
    elif shape_type=='wedge_envelope':
        sf_lon, sf_lat = stereonet_math.plane(0, dip) # slope face
        sl_lon, sl_lat = stereonet_math.plane(0, angle) # slip limit
        lon = np.vstack((sf_lon, np.flip(sl_lon[1:-1])))
        lat = np.vstack((sf_lat, np.flip(sl_lat[1:-1])))
        return geometry.Polygon(np.hstack((lon, lat)))
    
def _set_kws(kws, polygon=False, color='None', edgecolor='None', alpha=None, 
             label=None):
    """
    Set default kws for the kinematic analysis plot elements
    """

    kws = {} if kws is None else kws
    
    if 'lw' not in kws:
        kws.setdefault('linewidth', 1)

    if polygon:
        if 'color' not in kws:
            if 'fc' not in kws:
                kws.setdefault('facecolor', color)
            if 'ec' not in kws:
                kws.setdefault('edgecolor', edgecolor)
        kws.setdefault('alpha', alpha)
    else:
        if 'c' not in kws:
            kws.setdefault('color', color)
    
    kws.setdefault('label', label)
    
    return kws
   
def _rotate_shape(shape, strike):
    """
    Rotate the Shapely geometries according to a certain strike and return the 
    latitude, longitude arrays.
    """
    if shape.geom_type == 'LineString':
        lon, lat = shape.xy
    elif shape.geom_type == 'Polygon':
        lon, lat = shape.exterior.xy    
    lon = np.degrees(lon)
    lat = np.degrees(lat)
    lon, lat = stereonet_math._rotate(lon, lat, strike)

    return np.array([lon, lat])

class PlanarSliding(object):
    """ 
    Kinematic analysis for planar sliding failures
    
    Parameters
    ----------
    strike : number
        The strike of the slope face in degrees, with dip direction indicated 
        by the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number (> 0 and <90)
        The dip of the slope face in degrees.
    fric_angle : number, default=35
        The friction angle along the sliding discontinuities, in degrees. 
        Note that the slope dip should be steeper than the friction angle, or 
        else no planar sliding zones can be generated.
    latlim : number (> 0 and <90), default=20
        The lateral limits for typical planar sliding failures, counted from 
        the dip direction of the slope face in degrees. Daylighting 
        discontinuities dipping steeper than friction angle but outside the 
        lateral limits are considered to be less probable (i.e. secdondary 
        failure zones).
    """    

    def __init__(self, strike, dip, fric_angle=35, latlim=20):
        
        self.strike = strike
        self.dip = dip
        self.fric_angle = fric_angle
        self.latlim = latlim
        
        if latlim <= 0 or latlim >= 90:
            raise ValueError('latlim must be > 0 and < 90')
            
        if dip <= 0 or dip > 90:
            raise ValueError('dip must be > 0 and <= 90')
            
        if dip <= fric_angle:
            raise ValueError('No planar sliding zones generated as the input'
                             ' slope dip is shallower than the friction angle')

    def check_failure(self, strikes, dips, curved_lateral_limits=True):
        """ 
        Check whether planar sliding failures are kinematically feasible on a 
        sequence of discontinuities
        
        Parameters
        ----------
        strikes : numbers
            The strikes of the discontinuities in degrees, with dip direction 
            indicated by the azimuth (e.g. 315 vs. 135) specified following the
            "right hand rule".
        dips : numbers
            The dip angles of the discontinuities in degrees.
        curved_lateral_limits : boolean
            Consider lateral limits as curved lines (align with small circles) 
            if set to 'True'. Straight lines through the stereonet center are 
            used if set to 'False'. Defaults to 'True'
        
        Returns
        ----------
        main: squence of booleans
            True if the discontinuity is in the main planar sliding zone
        secondary: squence of booleans
            True if the discontinuity is in the secondary planar sliding zone
        """    
        strikes = (strikes-self.strike)%360
        dipdirs = (strikes+90)%360
        
        if curved_lateral_limits:
            lons, lats = stereonet_math.pole(strikes, dips)
            lats = np.degrees(lats)
            within_lat = ((lats >= -self.latlim-1e-8) &  # with tolerance
                          (lats <= self.latlim+1e-8))
        else:
            within_lat = ((dipdirs >= 90-self.latlim) &
                          (dipdirs <= 90+self.latlim))

        llons, llats = stereonet_math.line(dips, dipdirs)
        llons = np.degrees(llons)
        daylight = llons >= 90-self.dip-1e-8  # with tolerance
        
        fric_slip = dips >= self.fric_angle
        
        main = within_lat & fric_slip & daylight
        secondary = ~within_lat & fric_slip & daylight
        
        return main, secondary
    
    def plot_kinematic(self, secondary_zone=True, construction_lines=True, 
                       slopeface=True, curved_lateral_limits=True,
                       main_kws=None, secondary_kws=None, lateral_kws=None,
                       friction_kws=None, daylight_kws=None, slope_kws=None, 
                       ax=None):
                   
        """
        Generate the planar sliding kinematic analysis plot for pole vectors. 
        (Note: The discontinuity data to be used in conjunction with this plot 
        should be displayed as POLES)
        
        This function plots the following elements on a StereonetAxes: 
        (1) main planar sliding zone
        (2) secondary planar sliding zones
        (3) construction lines, i.e. friction cone, lateral limits and 
            daylight envelope
        (4) slope face
        
        (2)-(4) are optioanl. The style of the elements above can be specified 
        with their kwargs, or on the artists returned by this function later.
        
        Parameters
        ----------
        secondary_zone : boolean
            Plot the secondary zones if set to True. Defaults to 'True'.
        construction_lines : boolean
            Plot the construction lines if set to True. Defaults to 'True'.
        slopeface : boolean
            Plot the slope face as a great-circle plane on stereonet. Defaults
            to 'True'.
        curved_lateral_limits : boolean
            Plot curved lateral limits (align with small circles) if set to 
            True, or else will be plotted as straight lines through the 
            stereonet center. Defaults to 'True'
        main_kws : dictionary
            kwargs for the main planar sliding zone 
            (matplotlib.patches.Polygon)
        secondary_kws : dictionary
            kwargs for the secondary planar sliding zones 
            (matplotlib.patches.Polygon)
        lateral_kws : dictionary
            kwargs for the lateral limits (matplotlib.lines.Line2D)
        friction_kws : dictionary
            kwargs for the friction cone (matplotlib.patches.Polygon)
        daylight_kws : dictionary
            kwargs for the daylight envelope (matplotlib.patches.Polygon)
        slope_kws : dictionary
            kwargs for the slope face (matplotlib.lines.Line2D)
        ax : StereonetAxes
            The StereonetAxes to plot on. A new StereonetAxes will be generated
            if set to 'None'. Defaults to 'None'.
        
        Returns
        -------
        result : dictionary
            A dictionary mapping each element of the kinematic analysis plot to
            a list of the artists created. The dictionary has the following 
            keys:
            - `main` : the main planar sliding zone
            - `secondary` : the two secondary planar sliding zones
            - `slope` : the slope face
            - `daylight` : the daylight envelope 
            - `friction` : the friction cone
            - `lateral` : the two lateral limits
        """
        
        # Convert the construction lines into shapely linestrings / polygons    
        daylight_envelope = _shape('daylight_envelope', strike=0, dip=self.dip)
        friction_cone = _shape('cone', angle=self.fric_angle)
        if curved_lateral_limits:
            lat_lim1, lat_lim2 = _shape('curved_latlims', angle=self.latlim)
        else:
            lat_lim1 = _shape('plane', strike=90-self.latlim, dip=90)
            lat_lim2 = _shape('plane', strike=90+self.latlim, dip=90)
        
        # Get the failure zones (as shapely polygons) from geometry interaction
        sliding_zone = daylight_envelope.difference(friction_cone)
        split_polys = ops.split(sliding_zone,lat_lim1)
        sec_zone_present = len(split_polys)==2
        if sec_zone_present:
            if split_polys[0].intersects(lat_lim2):
                sliding_zone, sec_zone1 = split_polys
            else:
                sec_zone1, sliding_zone = split_polys
                
            split_polys = ops.split(sliding_zone,lat_lim2)
            if split_polys[0].touches(sec_zone1):
                sliding_zone, sec_zone2 = split_polys
            else:
                sec_zone2, sliding_zone = split_polys
                
        # Start plotting
        if ax==None:
            figure, axes = subplots(figsize=(8, 8))
        else:
            axes = ax
        
        # List of artists to be output
        main = []
        secondary = []
        slope = []
        daylight = []
        friction = []
        lateral = []
        
        # Plot the main planar sliding zone
        main_kws = _set_kws(main_kws, polygon=True,
                            color='r', alpha=0.3,
                            label='Potential Planar Sliding Zone')
        main.extend(axes.fill(
            *_rotate_shape(sliding_zone, self.strike), **main_kws))
        
        # Plot the secondary planar sliding zones
        if secondary_zone and sec_zone_present:
            secondary_kws = _set_kws(secondary_kws, polygon=True, 
                                     color='yellow', alpha=0.3,
                                     label='Secondary Planar Sliding Zone')            
            secondary_kws2 = secondary_kws.copy()
            secondary_kws2.pop('label')
            secondary.extend(axes.fill(
                *_rotate_shape(sec_zone1, self.strike), **secondary_kws))
            secondary.extend(axes.fill(
                *_rotate_shape(sec_zone2, self.strike),**secondary_kws2))

        # Plot the slope face
        if slopeface:
            slope_kws = _set_kws(slope_kws, color='k', label='Slope Face')
            slope.extend(axes.plane(self.strike, self.dip, **slope_kws))

        # Plot the construction lines (daylight envelope, friction cone 
        # and lateral limits)
        if construction_lines:
            daylight_kws = _set_kws(daylight_kws, polygon=True, edgecolor='r')
            friction_kws = _set_kws(friction_kws, polygon=True, edgecolor='r')
            lateral_kws = _set_kws(lateral_kws, color='r')
            lateral_kws2 = lateral_kws.copy()
            lateral_kws2.pop('label')
            daylight.extend(axes.fill(
                *_rotate_shape(daylight_envelope, self.strike),**daylight_kws))
            friction.extend(axes.fill(
                *friction_cone.exterior.xy, **friction_kws))
            lateral.extend(axes.plot(
                *_rotate_shape(lat_lim1, self.strike), **lateral_kws))
            lateral.extend(axes.plot(
                *_rotate_shape(lat_lim2, self.strike), **lateral_kws2))
            
        return dict(main=main, secondary=secondary, slope=slope,
                    daylight=daylight, friction=friction, lateral=lateral)
    
class WedgeSliding(object):
    """ 
    Kinematic analysis for wedge sliding failures
    
    Parameters
    ----------
    strike : number
        The strike of the slope face in degrees, with dip direction indicated 
        by the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number (> 0 and <90)
        The dip of the slope face in degrees.
    fric_angle : number, default=35
        The friction angle along the discontinuity intersections, in degrees. 
        Note that the slope dip should be steeper than the friction angle, or 
        else no wedge sliding zones can be generated.
    """    
    
    def __init__(self, strike, dip, fric_angle=35):
        self.strike = strike
        self.dip = dip
        self.fric_angle = fric_angle
        
        if self.dip <= self.fric_angle:
            raise ValueError('No wedge sliding zones generated as the input'
                             ' slope dip is shallower than the friction angle.')
            
    def check_failure(self, bearings, plunges):
        """ 
        Check whether wedge sliding failures are kinematically feasible for a
        sequence of discontinuity intersection lines
        
        Parameters
        ----------
        bearing : number or sequence of numbers
            The bearing (azimuth) of the instersection line(s) in degrees.
        plunge : number or sequence of numbers
            The plunge of the line(s) in degrees. The plunge is measured in 
            degrees downward from the end of the feature specified by the 
            bearing.

        Returns
        ----------
        main: squence of booleans
            True if the discontinuity is in the main wedge sliding zone
        secondary: squence of booleans
            True if the discontinuity is in the secondary wedge sliding zone
        """    

        bearings = (bearings-self.strike)%360
        
        llons, llats = stereonet_math.line(plunges, bearings)
        llons = np.degrees(llons)
        daylight = llons >= 90-self.dip-1e-8 # with tolerance
        
        slip = plunges >= self.fric_angle
        
        planar = llons <= 90-self.fric_angle+1e-8 # with tolerance
        
        main = slip & daylight
        secondary = ~slip & daylight & planar
        
        return main, secondary
    
    def plot_kinematic(self, secondary_zone=True, construction_lines=True, 
                       slopeface=True, main_kws=None, secondary_kws=None, 
                       friction_kws=None, fplane_kws=None, slope_kws=None, 
                       ax=None):
        
        """
        Generate the wedge sliding kinematic analysis plot for dip vectors. 
        (Note: This plot is used to analyze intersection lines between planes
        of discontinuities, displayed as "line" features instead of poles)
        
        This function plots the following elements on a StereonetAxes: 
        (1) main wedge sliding zone
        (2) secondary wedge sliding zones
        (3) construction lines, i.e. friction cone and friction plane
        (4) slope face
        
        (2)-(4) are optioanl. The style of the elements above can be specified 
        with their kwargs, or on the artists returned by this function later.
        
        Parameters
        ----------
        secondary_zone : boolean
            Plot the secondary zones if set to True. Defaults to 'True'.
        construction_lines : boolean
            Plot the construction lines if set to True. Defaults to 'True'.
        slopeface : boolean
            Plot the slope face as a great-circle plane on stereonet. Defaults
            to 'True'.
        main_kws : dictionary
            kwargs for the main wedge sliding zone 
            (matplotlib.patches.Polygon)
        secondary_kws : dictionary
            kwargs for the secondary wedge sliding zones 
            (matplotlib.patches.Polygon)
        fplane_kws : dictionary
            kwargs for the friction plane (matplotlib.lines.Line2D)
        slope_kws : dictionary
            kwargs for the slope face (matplotlib.lines.Line2D)
        ax : StereonetAxes
            The StereonetAxes to plot on. A new StereonetAxes will be generated
            if set to 'None'. Defaults to 'None'.
        
        Returns
        -------
        result : dictionary
            A dictionary mapping each element of the kinematic analysis plot to
            a list of the artists created. The dictionary has the following 
            keys:
            - `main` : the main wedge sliding zone
            - `secondary` : the secondary wedge sliding zones (it's one polygon)
            - `slope` : the slope face
            - `friction` : the friction cone
            - `fplane` : the friction plane
        """

        # Convert the construction lines into shapely linestrings / polygons
        # -1e-2 to prevent secondary zone splitting into two polygons
        friction_cone = _shape('cone', angle=90-self.fric_angle-1e-2)  
        envelope = _shape('wedge_envelope', strike=0, 
                          dip=self.dip, angle=self.fric_angle)
        
        # Get the failure zones (as shapely polygons) from geometry interaction
        wedge_zone = envelope.intersection(friction_cone)
        sec_zone = envelope.difference(friction_cone)
        
        # Plotting
        if ax==None:
            figure, axes = subplots(figsize=(8, 8))
        else:
            axes = ax
        
        # List of artists to be output
        main = []
        secondary = []
        slope = []
        friction = []
        fplane = []

        # Plot the main wedge sliding zone
        main_kws = _set_kws(main_kws, polygon=True,
                            color='r', alpha=0.3,
                            label='Potential Wedge Sliding Zone')
        main.extend(axes.fill(
            *_rotate_shape(wedge_zone, self.strike), **main_kws))
        
        # Plot the secondary main wedge sliding zones
        if secondary_zone:
            secondary_kws = _set_kws(secondary_kws, polygon=True,
                                     color='yellow', alpha=0.3,
                                     label='Secondary Wedge Sliding Zone')
            secondary.extend(axes.fill(
                *_rotate_shape(sec_zone, self.strike), **secondary_kws))
            
        # Plot the slope face
        if slopeface:
            slope_kws = _set_kws(slope_kws, color='k', label='Slope Face')
            slope.extend(axes.plane(self.strike, self.dip, **slope_kws))

        # Plot the construction lines (friction cone and friction plane)
        if construction_lines:
            friction_kws = _set_kws(friction_kws, polygon=True, edgecolor='r')
            fplane_kws = _set_kws(fplane_kws, color='r')
            friction.extend(axes.fill(
                *friction_cone.exterior.xy, **friction_kws))
            fplane.extend(axes.plane(
                self.strike, self.fric_angle, **fplane_kws))

        return dict(main=main, secondary=secondary, slope=slope,
                    friction=friction, fplane=fplane)
    
class FlexuralToppling(object):
    """ 
    Kinematic analysis for flexural toppling failures
    
    Parameters
    ----------
    strike : number
        The strike of the slope face in degrees, with dip direction indicated 
        by the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number (> 0 and <90)
        The dip of the slope face in degrees.
    fric_angle : number, default=35
        The friction angle along the toppling discontinuities, in degrees. 
        Note that the slope dip should be steeper than the friction angle, or 
        else no toppling zones can be generated.
    latlim : number (> 0 and <90), default=20
        The lateral limits for typical flexural toppling failures, counted from 
        the dip direction of the slope face in degrees. Discontinuities dipping 
        steeper than the slip limit for flexural toppling but outside the 
        lateral limits are considered to be less probable (i.e. secdondary 
        failure zones).
    """    
    
    def __init__(self, strike, dip, fric_angle=35, latlim=20):

        self.strike = strike
        self.dip = dip
        self.fric_angle = fric_angle
        self.latlim = latlim
        
        if latlim <= 0 :
            raise ValueError('latlim must be greater than 0 degree.')
            
        if latlim >= 90 :
            raise ValueError('latlim must be smaller than 90 degrees.'
                             ' Try 90-1e-9 if you really need to use 90.')

        if self.dip <= self.fric_angle:
            raise ValueError('No flexural toppling zones generated as the input'
                             ' slope dip is shallower than the friction angle')
            
    def check_failure(self, strikes, dips, curved_lateral_limits=True):
        """ 
        Check whether flexural toppling failures are kinematically feasible on 
        a sequence of discontinuities
        
        Parameters
        ----------
        strikes : numbers
            The strikes of the discontinuities in degrees, with dip direction 
            indicated by the azimuth (e.g. 315 vs. 135) specified following the
            "right hand rule".
        dips : numbers
            The dip angles of the discontinuities in degrees.
        curved_lateral_limits : boolean
            Consider lateral limits as curved lines (align with small circles) 
            if set to 'True'. Straight lines through the stereonet center are 
            used if set to 'False'. Defaults to 'True'
        
        Returns
        ----------
        main: squence of booleans
            True if the discontinuity is in the main flexural toppling zone
        secondary: squence of booleans
            True if the discontinuity is in the secondary flexural toppling zone
            Note: This is not normally considered
        """    

        strikes = (strikes-self.strike)%360
        dipdirs = (strikes+90)%360
        
        lons, lats = stereonet_math.pole(strikes, dips)
        lats = np.degrees(lats)
        lons = np.degrees(lons)

        if curved_lateral_limits:
            within_lat = ((lats >= -self.latlim-1e-8) & # with tolerance
                          (lats <= self.latlim+1e-8))
        else:
            within_lat = ((dipdirs >= 270-self.latlim) &
                          (dipdirs <= 270+self.latlim))
      
        fric_slip = lons >= 90-self.dip+self.fric_angle-1e-8 # with tolerance
        
        main = within_lat & fric_slip
        secondary = ~within_lat & fric_slip
        
        return main, secondary
    
    def plot_kinematic(self, secondary_zone=False, construction_lines=True, 
                       slopeface=True, curved_lateral_limits=True,
                       main_kws=None, secondary_kws=None, lateral_kws=None,
                       slip_kws=None, slope_kws=None, 
                       ax=None):
        
        """
        Generate the flexural toppling kinematic analysis plot for pole vectors. 
        (Note: The discontinuity data to be used in conjunction with this plot 
        should be displayed as POLES)
        
        This function plots the following elements on a StereonetAxes: 
        (1) main flexural toppling zone
        (2) secondary flexural toppling zones (not normally considered)
        (3) construction lines, i.e. slip limit and lateral limits
        (4) slope face
        
        (2)-(4) are optioanl. The style of the elements above can be specified 
        with their kwargs, or on the artists returned by this function later.
        
        Parameters
        ----------
        secondary_zone : boolean
            Plot the secondary zones if set to True. This is not normally 
            considered. I just leave this option in case some users find it 
            useful. Defaults to 'False'.
        construction_lines : boolean
            Plot the construction lines if set to True. Defaults to 'True'.
        slopeface : boolean
            Plot the slope face as a great-circle plane on stereonet. Defaults
            to 'True'.
        curved_lateral_limits : boolean
            Plot curved lateral limits (align with small circles) if set to 
            True, or else will be plotted as straight lines through the 
            stereonet center. Defaults to 'True'
        main_kws : dictionary
            kwargs for the main flexural toppling zone 
            (matplotlib.patches.Polygon)
        secondary_kws : dictionary
            kwargs for the secondary flexural toppling zones 
            (matplotlib.patches.Polygon)
        lateral_kws : dictionary
            kwargs for the lateral limits (matplotlib.lines.Line2D)
        slip_kws : dictionary
            kwargs for the slip limit (matplotlib.lines.Line2D)
        slope_kws : dictionary
            kwargs for the slope face (matplotlib.lines.Line2D)
        ax : StereonetAxes
            The StereonetAxes to plot on. A new StereonetAxes will be generated
            if set to 'None'. Defaults to 'None'.
        
        Returns
        -------
        result : dictionary
            A dictionary mapping each element of the kinematic analysis plot to
            a list of the artists created. The dictionary has the following 
            keys:
            - `main` : the main flexural toppling zone
            - `secondary` : the two secondary flexural toppling zones
            - `slope` : the slope face
            - `slip` : the slip limit
            - `lateral` : the two lateral limits
        """

        # Convert the construction lines into shapely linestrings / polygons    
        envelope = _shape('flexural_envelope', strike=0, dip=self.dip, 
                                  angle=self.fric_angle)
        if curved_lateral_limits:
            lat_lim1, lat_lim2 = _shape('curved_latlims', angle=self.latlim)
        else:
            lat_lim1 = _shape('plane', strike=90+self.latlim, dip=90)
            lat_lim2 = _shape('plane', strike=90-self.latlim, dip=90)
        
        # Get the failure zones (as shapely polygons) from geometry interaction
        sec_zone1, toppling_zone = ops.split(envelope, lat_lim1)
        toppling_zone, sec_zone2 = ops.split(toppling_zone, lat_lim2)
        
        # Plotting
        if ax==None:
            figure, axes = subplots(figsize=(8, 8))
        else:
            axes = ax
        
        # List of artists to be output
        main = []
        secondary = []
        slope = []
        slip = []
        lateral = []

        # Plot the main flexural toppling sliding zone
        main_kws = _set_kws(main_kws, polygon=True,
                            color='r', alpha=0.3,
                            label='Potential Flexural Toppling Zone')
        main.extend(axes.fill(
            *_rotate_shape(toppling_zone, self.strike), **main_kws))
        
        # Plot the secondary flexural toppling zones
        if secondary_zone:
            secondary_kws = _set_kws(secondary_kws, polygon=True,
                                     color='yellow', alpha=0.3,
                                     label='Secondary Flexural Toppling Zone')
            secondary_kws2 = secondary_kws.copy()
            secondary_kws2.pop('label')
            secondary.extend(axes.fill(
                *_rotate_shape(sec_zone1, self.strike), **secondary_kws))
            secondary.extend(axes.fill(
                *_rotate_shape(sec_zone2, self.strike), **secondary_kws2))
        
        # Plot the slope face
        if slopeface:
            slope_kws = _set_kws(slope_kws, color='k', label='Slope Face')
            slope.extend(axes.plane(self.strike, self.dip, **slope_kws))

        # Plot the construction lines (friction cone and slip limit)
        if construction_lines:
            slip_kws = _set_kws(slip_kws, color='r')
            lateral_kws = _set_kws(lateral_kws, color='r')
            lateral_kws2 = lateral_kws.copy()
            lateral_kws2.pop('label')
            slip.extend(axes.plane(
                self.strike, self.dip-self.fric_angle, **slip_kws))
            lateral.extend(axes.plot(
                *_rotate_shape(lat_lim1, self.strike), **lateral_kws))
            lateral.extend(axes.plot(
                *_rotate_shape(lat_lim2, self.strike), **lateral_kws2))
        
        return dict(main=main, secondary=secondary, slope=slope,
                    slip=slip, lateral=lateral)
