"""Physical time quadrature and conservation tests, independent of the CFD solver."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from transient_results import time_mean,time_diagnostics

class TransientTests(unittest.TestCase):
    def test_irregular_linear_signal_and_clipped_endpoints(self):
        t=np.array([0.,.03,.4,1.7,3.]);a=2*t+7
        self.assertAlmostEqual(time_mean(t,a,.1,2.8),9.9)
        # Arithmetic sample averaging would bias this toward the smaller steps.
        self.assertNotAlmostEqual(np.mean(a),10.)
        np.testing.assert_allclose(time_mean(t,np.stack([a,3*a],axis=1),.1,2.8),[9.9,29.7])
    def test_storage_closes_unsteady_control_volume(self):
        # Mass = 2 + t^2, net outward flux = -2t; heat store 10+3t^2,
        # heat source 50 W and outgoing heat 50-6t W.
        t=np.array([0.,.1,.7,2.]);start=.1;end=2.
        mass_rate=((2+end**2)-(2+start**2))/(end-start)
        self.assertAlmostEqual(time_mean(t,-2*t,start,end)+mass_rate,0)
        energy_rate=((10+3*end**2)-(10+3*start**2))/(end-start)
        self.assertAlmostEqual(50-time_mean(t,50-6*t,start,end)-energy_rate,0)
    def test_initial_courant_is_not_an_integrated_step(self):
        log="""Build  : v1912
Courant Number mean: 1 max: 200
deltaT = 0.025
Time = 0.025
ExecutionTime = 1 s
Courant Number mean: .02 max: 5.01
Build  : v1912
Courant Number mean: .02 max: 5.02
deltaT = 0.024
Time = 85.024
ExecutionTime = 2 s
Courant Number mean: .02 max: 5.03
"""
        dt,co,initial=time_diagnostics(log)
        self.assertEqual(dt,[.025,.024]);self.assertEqual(co,[5.01,5.03]);self.assertEqual(initial,[200,5.02])
    def test_bad_windows_rejected(self):
        for start,end in [(-1,1),(0,4),(1,1),(2,1)]:
            with self.assertRaises(ValueError):time_mean([0,1,3],[1,2,4],start,end)
        with self.assertRaises(ValueError):time_mean([0,1,1],[0,1,2],0,1)
if __name__=='__main__':unittest.main()
