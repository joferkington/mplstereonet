import mplstereonet
import numpy as np

class TestDensityGridding:
    def test_basic_values(self):
        #------------------ Test default results ------------------------------
        x, y, result = mplstereonet.density_grid(0, 0, gridsize=(10,10))
        expected = np.array(
          [[ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.49168947,  1.4740896 ,
             1.4740896 ,  0.49168947,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  1.4740896 ,  2.90125022,
             2.90125022,  1.4740896 ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  1.4740896 ,  2.90125022,
             2.90125022,  1.4740896 ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.49168947,  1.4740896 ,
             1.4740896 ,  0.49168947,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ]])
        assert np.allclose(result, expected)

        #--------------- Test exponential kamb results ------------------------
        # The default is "exponential_kamb", so this should be the same as the
        # "expected" array above.
        x, y, result = mplstereonet.density_grid(0, 0, gridsize=(10,10),
                                                method='exponential_kamb')
        assert np.allclose(result, expected)

        #----------------- Test linear kamb results ---------------------------
        x, y, result = mplstereonet.density_grid(0, 0, gridsize=(10,10),
                                                method='linear_kamb')
        expected = np.array(
          [[ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.08758584,
             0.08758584,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.6531549 ,  1.71607703,  2.28164609,
             2.28164609,  1.71607703,  0.6531549 ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  1.71607703,  3.14814815,  3.91013727,
             3.91013727,  3.14814815,  1.71607703,  0.        ,  0.        ],
           [ 0.        ,  0.08758584,  2.28164609,  3.91013727,  4.77663934,
             4.77663934,  3.91013727,  2.28164609,  0.08758584,  0.        ],
           [ 0.        ,  0.08758584,  2.28164609,  3.91013727,  4.77663934,
             4.77663934,  3.91013727,  2.28164609,  0.08758584,  0.        ],
           [ 0.        ,  0.        ,  1.71607703,  3.14814815,  3.91013727,
             3.91013727,  3.14814815,  1.71607703,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.6531549 ,  1.71607703,  2.28164609,
             2.28164609,  1.71607703,  0.6531549 ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.08758584,
             0.08758584,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ]])
        assert np.allclose(result, expected)

        #-------------- Test Traditional Kamb Results -------------------------
        x, y, result = mplstereonet.density_grid(0, 0, gridsize=(10,10),
                                                method='kamb')
        expected = np.array(
          [[ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  1.66666667,  1.66666667,  1.66666667,  1.66666667,
             1.66666667,  1.66666667,  1.66666667,  1.66666667,  0.        ],
           [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
             0.        ,  0.        ,  0.        ,  0.        ,  0.        ]])
        assert np.allclose(result, expected)

        #----------- Test Schmidt (a.k.a. 1%) Results -------------------------
        x, y, result = mplstereonet.density_grid(0, 0, gridsize=(5,5),
                                                 method='schmidt')
        expected = np.array([[   0.,    0.,    0.,    0.,    0.],
                             [   0.,    0.,    0.,    0.,    0.],
                             [   0.,    0.,  100.,    0.,    0.],
                             [   0.,    0.,    0.,    0.,    0.],
                             [   0.,    0.,    0.,    0.,    0.]])
        assert np.allclose(result, expected)

    def test_gridsize_shape(self):
        x, y, z = mplstereonet.density_grid(0, 0, gridsize=(10,10))
        assert z.shape == (10, 10)

    def test_equal_weights(self):
        x, y, result1 = mplstereonet.density_grid([0, 0], [0, 45])
        x, y, result2 = mplstereonet.density_grid([0, 0], [0, 45],
                                                  weights=[5, 5])
        np.testing.assert_array_equal(result1, result2)

    def test_weights_array_input(self):
        strike = np.array([0, 0])
        dip = np.array([0, 45])
        weights = np.array([5, 5])
        x, y, result1 = mplstereonet.density_grid(strike, dip)
        x, y, result2 = mplstereonet.density_grid(strike, dip, weights=weights)
        np.testing.assert_array_equal(result1, result2)

    def test_grid_extents(self):
        x, y, z = mplstereonet.density_grid(0, 0, gridsize=(10,10))
        assert x.min() == -np.pi/2
        assert y.min() == -np.pi/2
        assert x.max() == np.pi/2
        assert y.max() == np.pi/2
