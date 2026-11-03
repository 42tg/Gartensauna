"""Geometry invariants and refusal to invent a ranking from failed/ambiguous runs."""
import sys,unittest,tempfile,copy
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from study_cases import settings,case
from study_report import evaluate,qualified
from thermal_case import mesh
from simulate_ventilation import geometry

def result(factor):
    return {'thermal_window_pass':True,'age_quality_pass':True,'window_start_s':3000,'window_end_s':3600,
            'regions':{k:{'age_factor':factor,'mean_temperature_C':70} for k in ('upper','lower')},
            'occupied_p95_mean_speed_m_s':.05,'occupied_p95_mean_age_min':12*factor}

class StudyTests(unittest.TestCase):
    def test_five_ports_preserve_area_volume_and_source_cad(self):
        g=geometry();original=copy.deepcopy(g);vol=[]
        for v in settings()['variants']:
            actual,c,_=case(v['name'],g=g)
            with tempfile.TemporaryDirectory() as td:
                m=mesh(actual,c,Path(td));vol.append(m['air_volume_m3'])
                self.assertAlmostEqual(m['patches']['supply']['area_m2'],.012)
                self.assertAlmostEqual(m['patches']['exhaust']['area_m2'],.048)
        np.testing.assert_allclose(vol,vol[0],atol=1e-9);self.assertEqual(g,original)
    def test_short_or_unsettled_age_cannot_rank(self):
        r=result(.5);r['age_quality_pass']=False;self.assertFalse(qualified(r))
        r=result(.5);r['window_end_s']=300;self.assertFalse(qualified(r))
        x=evaluate({('A_current','nominal'):r});self.assertEqual(x['nominal_freshness_order'],[]);self.assertFalse(x['complete'])
    def test_overlapping_nominal_bands_are_tied(self):
        x=evaluate({('A_current','nominal'):result(1),('B_far_exhaust','nominal'):result(1.05)})
        self.assertEqual(x['nominal_tiers'][0]['variants'],['A_current','B_far_exhaust']);self.assertIsNone(x['robust_finalist_winner'])
    def test_rank_reversal_blocks_robust_winner(self):
        data={(v['name'],'nominal'):result(i+1) for i,v in enumerate(settings()['variants'])}
        for sc in settings()['validation_scenarios']:
            data[('A_current',sc['name'])]=result(1);data[('B_far_exhaust',sc['name'])]=result(2)
        data[('A_current','flow_60')]=result(3)
        x=evaluate(data);self.assertTrue(x['complete']);self.assertIsNone(x['robust_finalist_winner'])
        data[('A_current','flow_60')]=result(1)
        self.assertEqual(evaluate(data)['robust_finalist_winner'],'A_current')
if __name__=='__main__':unittest.main()
