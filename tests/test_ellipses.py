import unittest
from collections import Counter
import numpy as np
from mesh2d.core import generate
from mesh2d.export import topology


class EllipseTest(unittest.TestCase):
    def test_offset_center(self):
        grid, _, report = generate({'shape': 'ellipse_ring', 'inner_axes': [1, .5],
                                    'outer_axes': [2, 1.3], 'inner_center': [.55, .2],
                                    'cells': [120, 24]}, 'radial')
        np.testing.assert_allclose(np.mean(grid[0, :-1], axis=0), [.55, .2], atol=1e-14)
        np.testing.assert_allclose(np.mean(grid[-1, :-1], axis=0), [0, 0], atol=1e-14)
        self.assertGreater(report['min_scaled_jacobian'], 0)

    def test_ring_and_closed_seam(self):
        grid, patches, report = generate({'shape': 'ellipse_ring', 'inner_axes': [1, .5],
                                          'outer_axes': [2, 1.3], 'cells': [120, 24]}, 'radial')
        self.assertEqual(report['cells'], 2880)
        for boundary, axes in [(grid[0], [1, .5]), (grid[-1], [2, 1.3])]:
            np.testing.assert_allclose(np.sum((boundary/axes)**2, axis=1), 1)
        cells, markers = topology(grid, patches)
        edges = Counter(tuple(sorted((int(cell[index]), int(cell[(index+1) % 4]))))
                        for cell in cells for index in range(4))
        marked = {tuple(sorted(edge)) for lines in markers.values() for edge in lines}
        self.assertEqual({edge for edge, count in edges.items() if count == 1}, marked)
        self.assertTrue(all(count in (1, 2) for count in edges.values()))
        self.assertEqual(len(marked), 240)
