"""
demonstration and sample problem for slope stability using kinematic analysis

"""

import numpy as np
import mplstereonet as st
import matplotlib.pyplot as plt
import envelopes as env

"""
DEMONSTRATIONS AND EXERCISE
"""

def demo_planar():
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
    env.planar_daylight(strike-60,dip)
    env.planar_friction(friction)
    plt.title('Rotate, plot\n daylight and friction\nenvelopes\n')
    
    
    jstr=np.random.randint(0,361,4)
    jdip=np.random.randint(0,91,4)
    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].plane(strike,dip,'k--',alpha=0.5,lw=5)
    env.planar_daylight(strike,dip)
    env.planar_friction(friction)
    ax[2].plane(jstr,jdip,c='k')
    plt.title('Rotate back,\nplot discontinuity planes\n')
    
    plt.sca(ax[3])
    ax[3].grid(True)
    ax[3].plane(strike,dip,'k--',alpha=0.5,lw=5)
    env.planar_daylight(strike,dip)
    env.planar_friction(friction)
    ax[3].plane(jstr,jdip,c='k')
    ax[3].pole(jstr,jdip)
    plt.title('Plot poles, evaluate results\n')
    fig.suptitle('Planar failure\n\n')
    
    
def demo_toppling():
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
    env.toppling_slipLimits(strike-strike,dip)
    env.toppling_friction(strike-strike,dip,friction)
    plt.title('Rotate, plot\n daylight and friction\nenvelopes\n')
    
    jstr=np.random.randint(0,361,4)#np.random.random_integers(0,360,4)
    jdip=np.random.randint(0,91,4)
    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].plane(strike,dip,'k--',alpha=0.5,lw=5)
    env.toppling_slipLimits(strike,dip)
    env.toppling_friction(strike,dip,friction)
    ax[2].plane(jstr,jdip,c='k')
    plt.title('Rotate back,\nplot discontinuity planes\n')
    
    plt.sca(ax[3])
    ax[3].grid(True)
    ax[3].plane(strike,dip,'k--',alpha=0.5,lw=5)
    env.toppling_slipLimits(strike,dip)
    env.toppling_friction(strike,dip,friction)
    ax[3].plane(jstr,jdip,c='k')
    ax[3].pole(jstr,jdip)
    plt.title('Plot poles, evaluate results\n')
    fig.suptitle('Toppling failure')
    
    
def demo_wedge():
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
    env.wedge_daylight(strike,dip)
    env.wedge_friction(friction)
    plt.title('Plot\n daylight and friction\nenvelopes\n')
    
    
    jstr=np.random.randint(0,361,4)
    jdip=np.random.randint(0,91,4)
    
    plt.sca(ax[2])
    ax[2].grid(True)
    ax[2].plane(strike,dip,'k--',alpha=0.5,lw=5)
    env.wedge_daylight(strike,dip)
    env.wedge_friction(friction)
    ax[2].plane(jstr,jdip,c='k')
    plt.title('Plot discontinuity\nplanes\n')
    
    plt.sca(ax[3])
    ax[3].grid(True)
    ax[3].plane(strike,dip,'k--',alpha=0.5,lw=5)
    env.wedge_daylight(strike,dip)
    env.wedge_friction(friction)
    ax[3].plane(jstr,jdip,c='k')
    
    curax=ax[3]
    for j in range(len(jstr)-1):
        for k in range(j+1,len(jstr)):
            wl_plunge,wl_bearing=st.plane_intersection(jstr[j], jdip[j], jstr[k], jdip[k])
            curax.line(wl_plunge,wl_bearing,'b^',label=str(j+1)+'x'+str(k+1))
    plt.title('Plot plane intersections,\n evaluate results\n')
    fig.suptitle('Wedge failure')

def kinematic_analysis_demo():
    demo_planar()
    demo_wedge()
    demo_toppling()
    plt.show()
    
def exercise(plotfig=False):
#   slope face
    strike=320
    dip=70
    if strike+90>=360:ddr=strike+90-360
    else:ddr=strike+90
#   discontinuities
    friction=30
    jstr=[330,295,180,135,340]      #np.random.random_integers(0,360,3)
    jdip=[20,50,80,65,55]           #np.random.random_integers(0,90,3)
    jddr=[]
    for j in range(len(jstr)):
        if jstr[j]+90>=360:
            ddr=jstr[j]+90-360
        else:
            ddr=jstr[j]+90
        jddr.append(ddr)

#    printing exercise title, problem, and input data
    print "\n\nKINEMATIC ANALYSIS FOR SLOPE FAILURES"
    print "\nProblem: Given a slope face and a set of planar rock discontinuities, determine the discontinuities which will facilitate planar, toppling, and wedge failures."
    print "\n1) Slope face data\n--------"
    print 'Strike - dip (RHR) / DipDir - dip'    
    print strike, dip, ' / ', ddr, dip
    print "\n2) Discontinuity data\n--------"
    print "Friction angle, in degrees (for all): ",friction
    print '\nStrike - dip (RHR) / DipDir - dip'    
    for j in range(len(jstr)):
        print j+1,jstr[j],jdip[j], ' / ', jddr[j],jdip[j]
        
    if plotfig:
        
#       kinematic analysis axes
        fig,ax=env.setup_axes(strike,dip,friction,True)
    
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


kinematic_analysis_demo()
    
exercise(plotfig=True)
