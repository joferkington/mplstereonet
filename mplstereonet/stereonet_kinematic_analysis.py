"""
Utilities to analyze slope stability using kinematic analysis

"""
import numpy as np
import mplstereonet as st
import matplotlib.pyplot as plt

def planar_daylight_envelope(strike,dip,facecolor='none',edgecolor='b',segments=100):
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
    c_plunge, c_bearing, c_angle: arrays
        Arrays of plunges, bearings, and angles of the planar daylight envelopes.
    """
    ax=plt.gca()
    strikes, dips = np.atleast_1d(strike, dip)
    
    
#    calculating plunge and bearing of pole to plane
    p_plunge, p_bearing=st.pole2plunge_bearing(strikes, dips)
#    calculating plunge, bearing, and angle of cone
    c_plunge=45+p_plunge/2.
    c_bearing=p_bearing
    c_angle=(90-p_plunge)/2.-0.000000001
    
#    plotting plane, pole to plane, and daylight envelope
    ax.cone(c_plunge,c_bearing, c_angle,facecolor=facecolor,edgecolor=edgecolor)
#    ax.line(p_plunge, p_bearing,c='k')
    
    return c_plunge,c_bearing,c_angle



def planar_friction_envelope(friction=30,facecolor='r',segments=100):
    """
    Draws the planar friction envelope (cone) with given friction angle of sliding plane
    
    Parameters
    ----------
    
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
        
    Returns
    -------
    c_plunge, c_bearing, c_angle: arrays
        Arrays of plunges, bearings, and angles of the planar daylight envelopes.
    """
    ax=plt.gca()
    frictions = np.atleast_1d(friction)

#    computing plunge, bearing, and angle of friction cones
    c_plunge=90*np.ones(len(frictions))
    c_bearing=np.zeros(len(frictions))
    c_angle=frictions
    
#    plotting
    ax.cone(c_plunge,c_bearing, c_angle,alpha=0.5,facecolor=facecolor)
    
    
    return c_plunge,c_bearing,c_angle


def toppling_slip_limits(strike,dip,linecolor='b',segments=100):
    """
    Draws the toppling friction envelope (cone) with given friction angle of sliding plane
    and slope face with a given strike and dip.
    
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
    f_strike,f_dip: arrays
        Arrays of strike and dip of the toppling friction envelopes.
    """
    ax=plt.gca()
    strikes,dips = np.atleast_1d(strike,dip)
    
    ax.cone(0,strikes,60,facecolor='none',edgecolor='b')
    ax.cone(0,strikes+180,60,facecolor='none',edgecolor='b')
    
    return






def toppling_friction_envelope(strike,dip,friction=30,linecolor='r',segments=100):
    """
    Draws the toppling friction envelope (cone) with given friction angle of sliding plane
    and slope face with a given strike and dip.
    
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
    f_strike,f_dip: arrays
        Arrays of strike and dip of the toppling friction envelopes.
    """
    ax=plt.gca()
    frictions,strikes,dips = np.atleast_1d(friction,strike,dip)

#    computing plunge, bearing, and angle of friction cones
    c_plunge=90*np.ones(len(frictions))
    c_bearing=np.zeros(len(frictions))
    c_angle=frictions
    
#    plotting
    if dips-frictions>0:
        ax.plane(strikes,dips-frictions,c='r')
        return strikes, dips-frictions
    else:
        ax.plane(strikes,np.zeros(len(strikes)),c=linecolor)
        return strikes, np.zeros(len(strikes))
    
    
def setup_kinematic_analysis_ax(strike,dip,friction):

    # Make a figure with a single stereonet axes
    fig, ax = st.subplots(ncols=3,projection='equal_angle_stereonet')
   
    
    plt.sca(ax[0])
    ax[0].set_title('planar')
    ax[0].grid(True)
#    ax[0].set_azimuth_ticklabels(np.round(np.degrees(ax[0].get_azimuth_ticks())),fontsize='x-small')
    planar_friction_envelope(friction)
    ax[0].plane(strike,dip,'k--',lw=5)
    planar_daylight_envelope(strike,dip)
    
    
    plt.sca(ax[1])
    ax[1].grid(True)
    ax[1].set_title('wedge')
    planar_friction_envelope(friction)
    ax[1].plane(strike,dip,'k--',lw=5)
    ax[1].plane(strike,dip,c='b',lw=1)

    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].set_title('toppling')
    toppling_friction_envelope(strike,dip,friction)
    toppling_slip_limits(strike,dip)
    ax[2].plane(strike,dip,'k--',lw=5)
    
    

strike=[320]#,0,210]
dip=[70]#,45,75]
friction=25

setup_kinematic_analysis_ax(strike,dip,friction)









fig.tight_layout()
plt.show()

