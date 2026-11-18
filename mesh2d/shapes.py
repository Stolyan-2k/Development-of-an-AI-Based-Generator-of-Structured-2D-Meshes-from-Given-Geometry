import numpy as np


def radial_grid(case):
    counts = case['cells']
    if len(counts) != 2 or any(type(count) is not int or count < 2 for count in counts):
        raise ValueError('Expected two integer cell counts >= 2')
    if (counts[0]+1)*(counts[1]+1) > 1000000:
        raise ValueError('Maximum one million nodes')
    radius = float(case.get('radius', 1))
    center = np.asarray(case.get('center', [0, 0]), dtype=float)
    if not np.isfinite(radius) or radius <= 0 or center.shape != (2,) or not np.isfinite(center).all():
        raise ValueError('Invalid radius or center')
    across, up = np.meshgrid(np.linspace(-1, 1, counts[0]+1), np.linspace(-1, 1, counts[1]+1))
    distance = np.maximum(np.abs(across), np.abs(up))
    safe = np.where(distance == 0, 1, distance)
    xpos, ypos = across/safe, up/safe
    parameter = np.where(np.abs(across) >= np.abs(up),
                         np.where(across >= 0, 1+(ypos+1)/2, 3+(1-ypos)/2),
                         np.where(up >= 0, 2+(1-xpos)/2, (xpos+1)/2)) / 4
    if case['shape'] == 'circle':
        angle = -3*np.pi/4 + 2*np.pi*parameter
        boundary = np.stack([np.cos(angle), np.sin(angle)], axis=-1)
    elif case['shape'] == 'star':
        inner = float(case.get('inner_radius', 0.6*radius))
        if not np.isfinite(inner) or not 0 < inner < radius:
            raise ValueError('inner_radius must lie between zero and radius')
        if counts[0] != counts[1] or counts[0] % 20:
            raise ValueError('Star requires equal cell counts divisible by 20 to resolve every tip')
        angles = -7*np.pi/10 + np.arange(10)*np.pi/5
        radii = np.where(np.arange(10) % 2 == 0, 1, inner/radius)
        vertices = radii[:, None]*np.stack([np.cos(angles), np.sin(angles)], axis=-1)
        position = np.interp(parameter, [0, 0.25, 0.5, 0.75, 1], [0, 2, 4, 8, 10])
        index = np.floor(position).astype(int)
        fraction = (position-index)[..., None]
        boundary = (1-fraction)*vertices[index % 10]+fraction*vertices[(index+1) % 10]
    else:
        raise ValueError('shape must be circle or star')
    return center + radius*distance[..., None]*boundary
