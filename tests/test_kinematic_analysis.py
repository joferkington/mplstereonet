import mplstereonet.kinematic_analysis as kinematic
import mplstereonet.stereonet_math as smath
import numpy as np

class TestCheckFailures:
    def test_planar_sliding(self):
        planar_analysis = kinematic.PlanarSliding(0, 75)
        pole1 = smath.geographic2pole(np.radians(-70), np.radians(20))        
        data = [
        # Strike, dip     main, sec
            [(0, 45),    (True, False)],
            [pole1,      (True, False)], # just at lateral limit
            [(30, 35),   (True, False)], # just at friction cone
            [(0, 75),    (True, False)], # just daylights
            [(315, 35),  (False, True)], # just at friction cone
            [(45, 35),   (False, True)], # just at friction cone
            [(50, 60),   (False, True)],
            [(0, 20),    (False, False)],
            [(0, 80),    (False, False)],
            [(270, 60),  (False, False)],
        ]
        
        for strike_dip, correct in data:
            results = planar_analysis.check_failure(*strike_dip)
            assert results == correct
            
    def test_wedge_sliding(self):
        wedge_analysis = kinematic.WedgeSliding(0, 75)
        line1 = smath.geographic2plunge_bearing(np.radians(55), np.radians(40))
        data = [
        # plunge, bearing   main, sec
            [(75, 90),   (True, False)], # just daylights
            [(35, 60),   (True, False)], # just at friction cone
            [(45, 120),  (True, False)],
            [line1,      (False, True)], # just at "friction plane"
            [(30, 150),  (False, True)],
            [(30, 30),   (False, True)],
            [(80, 90),   (False, False)],
            [(0, 90),    (False, False)],
            [(20, 280),  (False, False)],
        ]
        
        for plunge_bearing, correct in data:
            p, b = plunge_bearing
            results = wedge_analysis.check_failure(b, p)
            assert results == correct
            
    def test_flexural_toppling(self):
        toppling_analysis = kinematic.FlexuralToppling(0, 75)
        pole1 = smath.geographic2pole(np.radians(70), np.radians(20))
        data = [
        # Strike, dip     main, sec
            [(180, 50),  (True, False)], # just at slip limit
            [pole1,      (True, False)], # just at lateral limit
            [(170, 90),  (True, False)], # at 90 degrees
            [(190, 60),  (True, False)],
            [(135, 70),  (False, True)],
            [(210, 70),  (False, True)],
            [(260, 85),  (False, True)],
            [(0, 20),    (False, False)],
            [(300, 80),  (False, False)],
            [(180, 30),  (False, False)],
        ]
        
        for strike_dip, correct in data:
            results = toppling_analysis.check_failure(*strike_dip)
            assert results == correct
            