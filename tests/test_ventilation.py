"""Numerical conservation and CAD-driven boundary-condition regression tests."""
import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import spsolve
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from simulate_ventilation import geometry,solve,transport_matrix,laplacian

class VentilationTests(unittest.TestCase):
    def test_plug_flow_age_and_conservation(self):
        # Independent exact discrete 1-D duct: 8 equal cells, 2 m3/s.
        n=8;a=np.arange(n-1);b=a+1;q=2.;vol=0.5
        inlet=np.zeros(n);inlet[0]=q;outlet=np.zeros(n);outlet[-1]=q
        T=transport_matrix(n,a,b,np.full(n-1,q),np.zeros(n-1),inlet,outlet)
        age=spsolve(T,np.full(n,vol))
        np.testing.assert_allclose(age,np.arange(1,n+1)*vol/q)
        self.assertAlmostEqual(outlet@age/q,n*vol/q)
        L=laplacian(n,a,b,np.ones(n-1));p=np.zeros(n);p[1:]=spsolve(L[1:,1:],(inlet-outlet)[1:])
        np.testing.assert_allclose(p[a]-p[b],q)

    def test_cad_ports_and_flow_scaling(self):
        g=geometry();cfg=dict(name='test',grid_m=.2,flow_m3h=80,mixing_diffusivity_m2s=.003,exhaust='exhaust')
        first,_=solve(g,cfg)
        second,_=solve(g,{**cfg,'flow_m3h':160,'mixing_diffusivity_m2s':.006})
        self.assertAlmostEqual(first['occupied_mean_age_min']/2,second['occupied_mean_age_min'],places=7)
        self.assertAlmostEqual(first['occupied_age_factor'],second['occupied_age_factor'],places=7)
        self.assertLess(first['max_cell_mass_error_relative_to_Q'],1e-7)
        self.assertLess(g['exhaust'][0][2]+g['exhaust'][1][2],600)
        self.assertGreater(g['supply'][0][2],g['heater'][0][2]+g['heater'][1][2])
        with self.assertRaises(ValueError):solve(g,{**cfg,'exhaust_y_m':5})

if __name__=='__main__':unittest.main()
