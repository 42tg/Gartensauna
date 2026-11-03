"""Mesh, field reader, and independent physical balance prerequisites."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from thermal_case import mesh
from thermal_results import value,weighted_percentile
from simulate_ventilation import geometry,ROOT

class ThermalTests(unittest.TestCase):
    def test_exact_cad_volume_and_ports(self):
        g=geometry();cfg=json.loads((ROOT/'simulation/thermal/config.json').read_text())['base']
        with tempfile.TemporaryDirectory() as td:
            report=mesh(g,cfg,Path(td))
            lo=np.array(g['room'][0])/1000;hi=np.array(g['room'][1])/1000
            expected=np.prod(hi-lo)-(g['room'][2]/1000-lo[0])*hi[1]*hi[2]
            expected-=sum(np.prod(np.array(g[k][1])/1000) for k in ('heater','upper','lower'))
            self.assertAlmostEqual(report['air_volume_m3'],expected,places=8)
            self.assertAlmostEqual(report['patches']['supply']['area_m2'],.012,places=9)
            self.assertAlmostEqual(report['patches']['exhaust']['area_m2'],.048,places=9)
            data=np.load(Path(td)/'mesh_arrays.npz');owners=data['owner'];neighbours=data['neighbour'];n=len(neighbours)
            # Discrete divergence theorem: each cell's oriented face areas close.
            surface=data['face_area'][:,None]*data['face_normal'];balance=np.zeros((report['n_cells'],3))
            np.add.at(balance,owners,surface);np.add.at(balance,neighbours,-surface[:n])
            np.testing.assert_allclose(balance,0,atol=1e-12)
            self.assertTrue(np.all(owners[:n]<neighbours))

    def test_field_reader_rejects_truncation(self):
        np.testing.assert_allclose(value('internalField uniform (1 2 3);','internalField',2,True),[[1,2,3],[1,2,3]])
        np.testing.assert_allclose(value('value nonuniform List<scalar> 3 (1 2 3);','value',3),[1,2,3])
        with self.assertRaises(ValueError):value('value nonuniform List<scalar> 3 (1 2);','value',3)
        self.assertAlmostEqual(weighted_percentile(np.array([1,2,3]),np.array([1,1,100]),95),2.949)

if __name__=='__main__':unittest.main()
