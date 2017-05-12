"""
Module description:
-------------------
    
Analysis of slope stability using kinematic analysis.
This module provides great circle and cone envelopes for
the kinematic analysis of planar, wedge, and toppling failures. 

Outputs can be plotted on stereonet axes provided by the mplstereonet package: 
https://github.com/joferkington/mplstereonet


References:
-----------
Goodman, R.E. 1980. Introduction to Rock Mechanics (Chapter 8), Toronto: John Wiley, pp 254-287
Hoek, E. and Bray, J.W. 1981. Rock Slope Engineering. Institution of Mining and Metallurgy, London.
Rocscience. 2000. DIPS (5.00) - Windows, Rocscience, Inc., Totonto, Ontario.

"""

import numpy as np
import mplstereonet as st
import matplotlib.pyplot as plt

def planar_daylight(strike,dip,to_plot=True,facecolor='none',edgecolor='b',segments=100):
    """
    Draws the planar daylight envelope (cone) with respect to a 
    slope face with a given strike and dip.
    
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
    pde_plunge, pde_bearing, pde_angle: arrays
        Arrays of plunges, bearings, and angles of the planar daylight envelopes (cones).
    """

    strikes, dips = np.atleast_1d(strike, dip)
#    calculating plunge and bearing of pole to plane
    p_plunge, p_bearing=st.pole2plunge_bearing(strikes, dips)
#    calculating plunge, bearing, and angle of planar daylight envelope (cone)
    pde_plunge=45+p_plunge/2.
    pde_bearing=p_bearing
    pde_angle=45-p_plunge/2.-10**-9
#    plotting daylight envelope
    if to_plot:
        ax=plt.gca()
        ax.cone(pde_plunge,pde_bearing, pde_angle,facecolor=facecolor,edgecolor=edgecolor)#,label='pDE')
    return pde_plunge,pde_bearing,pde_angle

def planar_friction(friction=30,to_plot=True,facecolor='none',edgecolor='r',segments=100):
    """
    Draws the planar friction envelope (cone) given friction angle of the sliding plane
    
    Parameters
    ----------
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
        
    Returns
    -------
    pfe_plunge, pfe_bearing, pfe_angle: arrays
        Arrays of plunges, bearings, and angles of the planar friction envelopes (cones).
    """
    frictions = np.atleast_1d(friction)
#    computing plunge, bearing, and angle of planar friction envelope (cone)
    pfe_plunge=90*np.ones(len(frictions))
    pfe_bearing=np.zeros(len(frictions))
    pfe_angle=frictions
#    plotting
    if to_plot:
        ax=plt.gca()
        ax.cone(pfe_plunge,pfe_bearing, pfe_angle,facecolor=facecolor,edgecolor=edgecolor)#,label='pFE')
    return pfe_plunge, pfe_bearing, pfe_angle

def wedge_daylight(strike,dip,to_plot=True,linecolor='b',segments=100):
    """
    Draws the wedge daylight envelope (great circle) with respect to a 
    slope face with a given strike and dip.
    
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
    wde_strikes, wde_dips: arrays
        Arrays of strike and dip of the wedge daylight envelopes (great circles).
    """
#    wedge daylight envelope is the same as the slope face orientation
    wde_strikes, wde_dips = np.atleast_1d(strike, dip)
#    plotting daylight envelope
    if to_plot:
        ax=plt.gca()
        ax.plane(wde_strikes,wde_dips,c=linecolor)#,label='wDE')
    return wde_strikes,wde_dips

def wedge_friction(friction=30,to_plot=True,facecolor='none',edgecolor='r',segments=100):
    """
    Draws the wedge friction envelope (cone) given friction angle of the sliding plane
    
    Parameters
    ----------
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
        
    Returns
    -------
    wfe_plunge, wfe_bearing, wfe_angle: arrays
        Arrays of plunges, bearings, and angles of the planar daylight envelopes (cones).
    """
    frictions = np.atleast_1d(friction)
#    computing plunge, bearing, and angle of planar friction envelope (cone)
    wfe_plunge=90*np.ones(len(frictions))
    wfe_bearing=np.zeros(len(frictions))
    wfe_angle=90-frictions
#    plotting
    if to_plot:
        ax=plt.gca()
        ax.cone(wfe_plunge,wfe_bearing, wfe_angle,facecolor=facecolor,edgecolor=edgecolor)#,label='wFE')
    return wfe_plunge, wfe_bearing, wfe_angle


def toppling_slipLimits(strike,dip,to_plot=True,linecolor='b',segments=100):
    """
    Draws the toppling friction envelope (cone) with given friction angle of sliding plane
    and slope face with a given strike and dip.
    
    for slip to be viable, discontinuity plane strike should be +/- 30 degrees 
    of slope strike (Goodman,1980)
    
    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) in degrees, with dip direction indicated by
        the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.
        
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
    
    Returns
    -------
    tsl1_plunge,tsl1_bearing,tsl1_angle, tsl2_plunge,tsl2_bearing,tsl2_angle: arrays
        Arrays of plunge, bearing, and angle of the toppling slip limits (cones).
    """
    strikes,dips = np.atleast_1d(strike,dip)
#    computing toppling slip limits (cones); assumes bidirectional cone plotting    
    tsl_plunge=0
    tsl_bearing=strikes
    tsl_angle=60
#    plotting toppling slip limits    
    if to_plot:
        ax=plt.gca()
        ax.cone(tsl_plunge,tsl_bearing,tsl_angle,facecolor='none',edgecolor='b')
    return tsl_plunge,tsl_bearing,tsl_angle

def toppling_friction(strike,dip,friction=30,to_plot=True,linecolor='r',segments=100):
    """
    Draws the toppling friction envelope (great circle) given sliding plane with friction angle, 
    and slope face with a strike and dip.
    
    Parameters
    ----------
    strike : number or sequence of numbers
        The strike of the plane(s) in degrees, with dip direction indicated by
        the azimuth (e.g. 315 vs. 135) specified following the "right hand
        rule".
    dip : number or sequence of numbers
        The dip of the plane(s) in degrees.
        
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
    
    Returns
    -------
    tfe_strikes,tfe_dips: arrays
        Arrays of strike and dip of the toppling friction envelopes.
    """
    frictions,strikes,dips = np.atleast_1d(friction,strike,dip)
#    computing toppling friction envelopes    
    tfe_strikes=strikes
    if dips-frictions>0:
        tfe_dips=dips-frictions
    else:
        tfe_dips=np.zeros(len(strikes))
#    plotting toppling friction envelopes
    if to_plot:
        ax=plt.gca()
        ax.plane(strikes,dips-frictions,c=linecolor)
    return tfe_strikes, tfe_dips
    
def setup_axes(strike,dip,friction,to_plot):

    # Make a figure with a single stereonet axes
    fig, ax = st.subplots(ncols=3,projection='equal_angle_stereonet')

    for a in range(3):
        ax[a].plane(strike,dip,'k--',alpha=0.5,lw=5)#,label='SF')
#   planar failure
    plt.sca(ax[0])
    ax[0].set_title('planar\n')
    ax[0].grid(True)
    planar_friction(friction,to_plot)
    planar_daylight(strike,dip,to_plot)    
#    wedge failure    
    plt.sca(ax[1])
    ax[1].set_title('wedge\n')
    ax[1].grid(True)
    wedge_friction(friction,to_plot)
    wedge_daylight(strike,dip,to_plot)    
#    toppling failure
    plt.sca(ax[2])
    ax[2].set_title('toppling\n')
    ax[2].grid(True)
    toppling_friction(strike,dip,friction,to_plot)
    toppling_slipLimits(strike,dip,to_plot)
    
    return fig,ax
 
