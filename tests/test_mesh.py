import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from mesh2d.core import generate
from mesh2d.export import topology, write_mesh


class MeshTest(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((Path(__file__).resolve().parents[1]/'examples/channel.json').read_text())

    def test_rectangle(self):
        self.case.update(controls={},grading=[1,1],cells=[8,4])
        for method in ['ai','tfi']:
            grid,patches,report = generate(self.case,method)
            self.assertEqual(grid.shape,(5,9,2))
            self.assertAlmostEqual(report['min_area'],0.125)
            self.assertAlmostEqual(report['min_scaled_jacobian'],1)
            quads,edges = topology(grid,patches)
            self.assertEqual(len(quads),32)
            self.assertEqual(len(edges['wall']),16)

    def test_curved(self):
        grid,patches,report = generate(self.case)
        classical = generate(self.case,'tfi')[0]
        np.testing.assert_allclose(grid[0,32],[2,0.325])
        self.assertGreater(np.abs(grid-classical).max(),0.001)
        self.assertGreater(report['min_scaled_jacobian'],0.5)
        widths = np.diff(grid[:,0,1])
        self.assertAlmostEqual(widths[-1]/widths[0],3)
        with tempfile.TemporaryDirectory() as directory:
            for fmt,token in [('foam','type empty;'),('vtk','DIMENSIONS 65 25 1'),('su2','NELEM= 1536')]:
                target = Path(directory)/fmt
                write_mesh(target,grid,patches,fmt)
                self.assertIn(token,target.read_text())

    def test_folded(self):
        self.case['controls']['bottom']=[2,4]
        for method in ['ai','tfi']:
            with self.assertRaises(ValueError):
                generate(self.case,method)
