import unittest
import numpy as np
from mesh2d.core import generate


class ShapesTest(unittest.TestCase):
    def test_circle_boundary(self):
        grid, _, report = generate({'shape': 'circle', 'cells': [40, 40]}, 'radial')
        boundary = np.concatenate([grid[0], grid[-1], grid[:, 0], grid[:, -1]])
        np.testing.assert_allclose(np.linalg.norm(boundary, axis=1), 1)
        self.assertGreater(report['min_scaled_jacobian'], 0)

    def test_star_area(self):
        grid, _, report = generate({'shape': 'star', 'cells': [60, 60]}, 'radial')
        boundary = np.concatenate([grid[0, :-1], grid[:-1, -1], grid[-1, :0:-1], grid[:0:-1, 0]])
        following = np.roll(boundary, -1, axis=0)
        area = np.sum(boundary[:, 0]*following[:, 1]-boundary[:, 1]*following[:, 0])/2
        self.assertAlmostEqual(area, 5*0.6*np.sin(np.pi/5))
        self.assertGreater(report['min_scaled_jacobian'], 0.2)

    def test_invalid_resolution(self):
        with self.assertRaises(ValueError):
            generate({'shape': 'star', 'cells': [51, 51]}, 'radial')
