import numpy as np


def ellipse_ring(case):
    if set(case)-{'shape', 'cells', 'inner_axes', 'outer_axes', 'center', 'inner_center', 'inner_shape'}:
        raise ValueError('Unknown ellipse ring fields')
    counts = case['cells']
    if len(counts) != 2 or any(type(count) is not int for count in counts):
        raise ValueError('cells must contain two integers')
    angular, radial = counts
    if angular < 8 or radial < 1 or (angular+1)*(radial+1) > 1000000:
        raise ValueError('Expected >= 8 angular and >= 1 radial cells; maximum one million nodes')
    inner = np.asarray(case['inner_axes'], dtype=float)
    outer = np.asarray(case['outer_axes'], dtype=float)
    center = np.asarray(case.get('center', [0, 0]), dtype=float)
    inner_center = np.asarray(case.get('inner_center', center), dtype=float)
    if any(values.shape != (2,) or not np.isfinite(values).all() for values in (inner, outer, center, inner_center)):
        raise ValueError('Expected finite pairs for axes and center')
    if np.any(inner <= 0) or np.any(outer <= inner):
        raise ValueError('Outer semiaxes must be greater than positive inner semiaxes')
    angle = np.linspace(0, -2*np.pi, angular+1)
    fraction = np.linspace(0, 1, radial+1)[:, None]
    axes = inner + fraction*(outer-inner)
    centers = inner_center + fraction*(center-inner_center)
    grid = centers[:, None, :] + axes[:, None, :]*np.stack([np.cos(angle), np.sin(angle)], axis=-1)
    if case.get('inner_shape', 'ellipse') == 'quadrilateral':
        if angular % 4:
            raise ValueError('Quadrilateral requires angular cells divisible by four')
        position = np.linspace(0, 4, angular+1)
        index = np.floor(position).astype(int)
        weight = (position-index)[:, None]
        vertices = inner_center + np.array([[1, 1], [1, -1], [-1, -1], [-1, 1]])*inner
        boundary = (1-weight)*vertices[index % 4] + weight*vertices[(index+1) % 4]
        outer_angle = np.pi/4 + angle
        outer_boundary = center + outer*np.stack([np.cos(outer_angle), np.sin(outer_angle)], axis=-1)
        grid = (1-fraction[:, :, None])*boundary + fraction[:, :, None]*outer_boundary
    elif case.get('inner_shape', 'ellipse') != 'ellipse':
        raise ValueError('inner_shape must be ellipse or quadrilateral')
    grid[:, -1] = grid[:, 0]
    return grid
