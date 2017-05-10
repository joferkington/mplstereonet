"""
Utilities to analyze slope stability using kinematic analysis

References:
-----------
Goodman, R.E. 1980. Introduction to Rock Mechanics (Chapter 8), Toronto: John Wiley, pp 254-287
Hoek, E. and Bray, J.W. 1981. Rock Slope Engineering. Institution of Mining and Metallurgy, London.
Rocscience. 2000. DIPS (5.00) - Windows, Rocscience, Inc., Totonto, Ontario.

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

    strikes, dips = np.atleast_1d(strike, dip)
#    calculating plunge and bearing of pole to plane
    p_plunge, p_bearing=st.pole2plunge_bearing(strikes, dips)
#    calculating plunge, bearing, and angle of planar daylight envelope (cone)
    pde_plunge=45+p_plunge/2.
    pde_bearing=p_bearing
    pde_angle=45-p_plunge/2.-10**-9
#    plotting daylight envelope
    ax=plt.gca()
    ax.cone(pde_plunge,pde_bearing, pde_angle,facecolor=facecolor,edgecolor=edgecolor)#,label='pDE')
#    ax.legend(fontsize='x-small')
    return pde_plunge,pde_bearing,pde_angle

def planar_friction_envelope(friction=30,facecolor='none',edgecolor='r',segments=100):
    """
    Draws the planar friction envelope (cone) given friction angle of the sliding plane
    
    Parameters
    ----------
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
        
    Returns
    -------
    pfe_plunge, pfe_bearing, pfe_angle: arrays
        Arrays of plunges, bearings, and angles of the planar friction envelopes.
    """
    frictions = np.atleast_1d(friction)
#    computing plunge, bearing, and angle of planar friction envelope (cone)
    pfe_plunge=90*np.ones(len(frictions))
    pfe_bearing=np.zeros(len(frictions))
    pfe_angle=frictions
#    plotting
    ax=plt.gca()
    ax.cone(pfe_plunge,pfe_bearing, pfe_angle,facecolor=facecolor,edgecolor=edgecolor)#,label='pFE')
#    ax.legend(fontsize='x-small')
    return pfe_plunge, pfe_bearing, pfe_angle

def wedge_daylight_envelope(strike,dip,linecolor='b',segments=100):
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
        Arrays of strike and dip of the wedge daylight envelopes.
    """
#    wedge daylight envelope is the same as the slope face orientation
    wde_strikes, wde_dips = np.atleast_1d(strike, dip)
#    plotting daylight envelope
    ax=plt.gca()
    ax.plane(wde_strikes,wde_dips,c=linecolor)#,label='wDE')
#    ax.legend(fontsize='x-small')
    return wde_strikes,wde_dips

def wedge_friction_envelope(friction=30,facecolor='none',edgecolor='r',segments=100):
    """
    Draws the wedge friction envelope (cone) given friction angle of the sliding plane
    
    Parameters
    ----------
    friction : number or sequence of numbers
        The friction angle of the sliding plane in degrees.
        
    Returns
    -------
    c_plunge, c_bearing, c_angle: arrays
        Arrays of plunges, bearings, and angles of the planar daylight envelopes.
    """
    frictions = np.atleast_1d(friction)
#    computing plunge, bearing, and angle of planar friction envelope (cone)
    wfe_plunge=90*np.ones(len(frictions))
    wfe_bearing=np.zeros(len(frictions))
    wfe_angle=90-frictions
#    plotting
    ax=plt.gca()
    ax.cone(wfe_plunge,wfe_bearing, wfe_angle,facecolor=facecolor,edgecolor=edgecolor)#,label='wFE')
#    ax.legend(fontsize='x-small')
    return wfe_plunge, wfe_bearing, wfe_angle


def toppling_slip_limits(strike,dip,linecolor='b',segments=100):
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
        Arrays of plunge, bearing, and angle of the toppling slip limits.
    """
    strikes,dips = np.atleast_1d(strike,dip)
#    computing toppling slip limits (cones)    
    tsl1_plunge=0
    tsl1_bearing=strikes
    tsl1_angle=60
    tsl2_plunge=0
    tsl2_bearing=strikes+180
    tsl2_angle=60
#    plotting toppling slip limits    
    ax=plt.gca()
    ax.cone(tsl1_plunge,tsl1_bearing,tsl1_angle,facecolor='none',edgecolor='b')#,label='tSL')
    ax.cone(tsl2_plunge,tsl2_bearing,tsl2_angle,facecolor='none',edgecolor='b')
#    ax.legend(fontsize='x-small')
    return tsl1_plunge,tsl1_bearing,tsl1_angle, tsl2_plunge,tsl2_bearing,tsl2_angle

def toppling_friction_envelope(strike,dip,friction=30,linecolor='r',segments=100):
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
    ax=plt.gca()
    ax.plane(strikes,dips-frictions,c=linecolor)#,label='tFE')
#    ax.legend(fontsize='x-small')
    return tfe_strikes, tfe_dips
    
    
    
def setup_kinematic_analysis_axes(strike,dip,friction):

    # Make a figure with a single stereonet axes
    fig, ax = st.subplots(ncols=3,projection='equal_angle_stereonet')

    for a in range(3):
        ax[a].plane(strike,dip,'k--',alpha=0.5,lw=5)#,label='SF')
#   planar failure
    plt.sca(ax[0])
    ax[0].set_title('planar\n')
    ax[0].grid(True)
    planar_friction_envelope(friction)
    planar_daylight_envelope(strike,dip)    
#    wedge failure    
    plt.sca(ax[1])
    ax[1].set_title('wedge\n')
    ax[1].grid(True)
    wedge_friction_envelope(friction)
    wedge_daylight_envelope(strike,dip)    
#    toppling failure
    plt.sca(ax[2])
    ax[2].set_title('toppling\n')
    ax[2].grid(True)
    toppling_friction_envelope(strike,dip,friction)
    toppling_slip_limits(strike,dip)
    
    fig.tight_layout()
    
    return fig,ax
    




def steps_planar():
#    slope face
    strike=60
    dip=55
#    generalized friction angle of slip planes
    friction=25
    
    fig, ax = st.subplots(ncols=4,projection='equal_angle_stereonet')
    plt.sca(ax[0])
    ax[0].grid(True)
    ax[0].plane(strike,dip,'k--',alpha=0.5,lw=5)
    plt.title('Plot slope face\n')
    
    
    plt.sca(ax[1])
    ax[1].grid(True)
    ax[1].plane(strike-strike,dip,'k--',alpha=0.5,lw=5)
    ax[1].set_azimuth_ticks([])
    planar_daylight_envelope(strike-60,dip)
    planar_friction_envelope(friction)
    plt.title('Rotate, plot\n daylight and friction\nenvelopes\n')
    
    
    jstr=np.random.random_integers(0,360,4)
    jdip=np.random.random_integers(0,90,4)
    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].plane(strike,dip,'k--',alpha=0.5,lw=5)
    planar_daylight_envelope(strike,dip)
    planar_friction_envelope(friction)
    ax[2].plane(jstr,jdip,c='k')
    plt.title('Rotate back,\nplot discontinuity planes\n')
    
    plt.sca(ax[3])
    ax[3].grid(True)
    ax[3].plane(strike,dip,'k--',alpha=0.5,lw=5)
    planar_daylight_envelope(strike,dip)
    planar_friction_envelope(friction)
    ax[3].plane(jstr,jdip,c='k')
    ax[3].pole(jstr,jdip)
    plt.title('Plot poles, evaluate results\n')
    fig.suptitle('Planar failure\n\n')
    
    
def steps_toppling():
#    slope face
    strike=60
    dip=55
#    generalized friction angle of slip planes
    friction=25
    
    fig, ax = st.subplots(ncols=4,projection='equal_angle_stereonet')
    plt.sca(ax[0])
    ax[0].grid(True)
    ax[0].plane(strike,dip,'k--',alpha=0.5,lw=5)
    plt.title('Plot slope face\n')
    
    plt.sca(ax[1])
    ax[1].grid(True)
    ax[1].plane(strike-strike,dip,'k--',alpha=0.5,lw=5)
    ax[1].set_azimuth_ticks([])
    toppling_slip_limits(strike-strike,dip)
    toppling_friction_envelope(strike-strike,dip,friction)
    plt.title('Rotate, plot\n daylight and friction\nenvelopes\n')
    
    jstr=np.random.random_integers(0,360,4)
    jdip=np.random.random_integers(0,90,4)
    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].plane(strike,dip,'k--',alpha=0.5,lw=5)
    toppling_slip_limits(strike,dip)
    toppling_friction_envelope(strike,dip,friction)
    ax[2].plane(jstr,jdip,c='k')
    plt.title('Rotate back,\nplot discontinuity planes\n')
    
    plt.sca(ax[3])
    ax[3].grid(True)
    ax[3].plane(strike,dip,'k--',alpha=0.5,lw=5)
    toppling_slip_limits(strike,dip)
    toppling_friction_envelope(strike,dip,friction)
    ax[3].plane(jstr,jdip,c='k')
    ax[3].pole(jstr,jdip)
    plt.title('Plot poles, evaluate results\n')
    fig.suptitle('Toppling failure')
    
    
def steps_wedge():
#    slope face
    strike=60
    dip=55
#    generalized friction angle of slip planes
    friction=25
    
    fig, ax = st.subplots(ncols=4,projection='equal_angle_stereonet')
    plt.sca(ax[0])
    ax[0].grid(True)
    ax[0].plane(strike,dip,'k--',alpha=0.5,lw=5)
    plt.title('Plot slope face\n')
    
    plt.sca(ax[1])
    ax[1].grid(True)
    ax[1].plane(strike,dip,'k--',alpha=0.5,lw=5)
    wedge_daylight_envelope(strike,dip)
    wedge_friction_envelope(friction)
    plt.title('Plot\n daylight and friction\nenvelopes\n')
    
    
    jstr=np.random.random_integers(0,360,4)
    jdip=np.random.random_integers(0,90,4)
    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].plane(strike,dip,'k--',alpha=0.5,lw=5)
    wedge_daylight_envelope(strike,dip)
    wedge_friction_envelope(friction)
    ax[2].plane(jstr,jdip,c='k')
    plt.title('Plot discontinuity\nplanes\n')
    
    plt.sca(ax[3])
    ax[3].grid(True)
    ax[3].plane(strike,dip,'k--',alpha=0.5,lw=5)
    wedge_daylight_envelope(strike,dip)
    wedge_friction_envelope(friction)
    ax[3].plane(jstr,jdip,c='k')
    
    curax=ax[3]
    for j in range(len(jstr)-1):
        for k in range(j+1,len(jstr)):
            wl_plunge,wl_bearing=st.plane_intersection(jstr[j], jdip[j], jstr[k], jdip[k])
            curax.line(wl_plunge,wl_bearing,'b^',label=str(j+1)+'x'+str(k+1))
    plt.title('Plot plane intersections,\n evaluate results\n')
    fig.suptitle('Wedge failure')

def kinematic_analysis_demo():
    steps_planar()
    steps_wedge()
    steps_toppling()
    plt.show()
    
def exercise(plotfig=False):
#    slope face
    strike=320
    dip=70
#    generalized friction angle of slip planes
    friction=30
    
#    discontinuity sets
    jstr=[330,295,180,135,340]      #np.random.random_integers(0,360,3)
    jdip=[20,50,80,65,55]           #np.random.random_integers(0,90,3)
    jddr=[]
    for j in range(len(jstr)):
        if jstr[j]+90>=360:
            ddr=jstr[j]+90-360
        else:
            ddr=jstr[j]+90
        jddr.append(ddr)
    

    print '\n\n\nStrike - dip (RHR) / DipDir - dip'    
    for j in range(len(jstr)):
        print j+1,jstr[j],jdip[j], ' / ', jddr[j],jdip[j]
        
    if plotfig:
        
#       kinematic analysis axes
        fig,ax=setup_kinematic_analysis_axes(strike,dip,friction)
    
#       evaluate planar and toppling failures
        for j in range(len(jstr)):
            curax=ax[0]
            curax.pole(jstr[j],jdip[j],label=str(j+1))
            curax.legend(fontsize='x-small')
            
            curax=ax[2]
            curax.pole(jstr[j],jdip[j],label=str(j+1))
            curax.legend(fontsize='x-small')
            
            print j+1,jstr[j],jdip[j], ' / ', jddr[j],jdip[j]
        
    #    evaluate wedge failures
        curax=ax[1]
        curax.plane(jstr, jdip,'k',alpha=0.2)
        curax.plane(jstr, jdip,'k',alpha=0.2)
        for j in range(len(jstr)-1):
            for k in range(j+1,len(jstr)):
                wl_plunge,wl_bearing=st.plane_intersection(jstr[j], jdip[j], jstr[k], jdip[k])
                curax.line(wl_plunge,wl_bearing,marker='^',label=str(j+1)+'x'+str(k+1))
                curax.legend(fontsize='x-small')
        
        plt.show()
    else:
        return

#kinematic_analysis_demo()
    
exercise(plotfig=False)

