import re
import numpy as np
from .model import predict


SIDES = ('bottom', 'top', 'left', 'right')


def axis_points(count, ratio):
    if not isinstance(ratio, (float, int)) or not np.isfinite(ratio) or ratio <= 0:
        raise ValueError('grading must be positive and finite')
    widths = np.geomspace(1.0, ratio, count)
    cumulative = np.r_[0.0, np.cumsum(widths / widths.max())]
    return cumulative / cumulative[-1]


def make_wall(start, end, control):
    def evaluate(values):
        fraction = values[:, None]
        return ((1-fraction)**2*start + 2*fraction*(1-fraction)*control + fraction**2*end)
    return evaluate


def quality(grid):
    corners = np.stack([grid[:-1,:-1], grid[:-1,1:], grid[1:,1:], grid[1:,:-1]])
    edges = np.roll(corners,-1,axis=0) - corners
    following = np.roll(edges,-1,axis=0)
    cross = edges[...,0]*following[...,1] - edges[...,1]*following[...,0]
    lengths = np.linalg.norm(edges,axis=-1)
    if not np.isfinite(cross).all() or np.any(cross <= 0):
        raise ValueError('Inverted, concave or degenerate cells; check geometry and grading')
    scaled = cross / (lengths*np.roll(lengths,-1,axis=0))
    if not np.isfinite(scaled).all() or scaled.min() < 1e-10:
        raise ValueError('Numerically degenerate mesh')
    return {'cells': int(cross[0].size), 'min_area': float(((cross[0]+cross[2])/2).min()),
            'min_scaled_jacobian': float(scaled.min()),
            'max_aspect_ratio': float((lengths.max(axis=0)/lengths.min(axis=0)).max())}


def generate(case, method='ai'):
    if isinstance(case, dict) and case.get('shape') == 'ellipse_ring':
        if method != 'radial':
            raise ValueError('Ellipse ring uses --method radial')
        from .ellipses import ellipse_ring
        grid = ellipse_ring(case)
        return grid, {'bottom': 'inner_wall', 'top': 'outer_wall'}, quality(grid)
    if isinstance(case, dict) and 'shape' in case:
        if method != 'radial':
            raise ValueError('Circle and star use --method radial')
        if set(case)-{'shape','cells','radius','inner_radius','center'}:
            raise ValueError('Unknown shape fields')
        from .shapes import radial_grid
        grid = radial_grid(case)
        return grid, {side: 'wall' for side in SIDES}, quality(grid)
    if not isinstance(case,dict) or set(case)-{'corners','controls','cells','grading','patches'}:
        raise ValueError('Unknown case fields or invalid case')
    corners = np.asarray(case['corners'],dtype=float)
    if corners.shape != (4,2) or not np.isfinite(corners).all():
        raise ValueError('Expected four finite planar corners')
    counts, ratios = case['cells'], case.get('grading',[1,1])
    if len(counts)!=2 or len(ratios)!=2 or any(type(count) is not int or count<1 for count in counts):
        raise ValueError('Expected two positive cell counts and two grading ratios')
    if (counts[0]+1)*(counts[1]+1)>1000000:
        raise ValueError('Maximum one million nodes')
    horizontal,vertical = (axis_points(count,ratio) for count,ratio in zip(counts,ratios))
    controls,patches = case.get('controls',{}),case.get('patches',{})
    if not all(isinstance(item,dict) and not set(item)-set(SIDES) for item in (controls,patches)):
        raise ValueError('Invalid side specification')
    if not all(isinstance(name,str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',name) for name in patches.values()):
        raise ValueError('Invalid patch name')
    walls = []
    for side,(start,end) in zip(SIDES,[(0,1),(3,2),(0,3),(1,2)]):
        first,last = corners[[start,end]]
        control = np.asarray(controls.get(side,(first+last)/2),dtype=float)
        if control.shape != (2,) or not np.isfinite(control).all():
            raise ValueError('Expected finite planar control point')
        walls.append(make_wall(first,last,control))
    bottom,top,left,right = [wall(values) for wall,values in zip(walls,[horizontal,horizontal,vertical,vertical])]
    across,up = horizontal[None,:,None],vertical[:,None,None]
    base = (1-up)*((1-across)*corners[0]+across*corners[1])+up*((1-across)*corners[3]+across*corners[2])
    if method=='ai':
        grid = base + predict(walls,horizontal,vertical)
    elif method=='tfi':
        grid = (1-up)*bottom+up*top+(1-across)*left[:,None]+across*right[:,None]-base
    else:
        raise ValueError('Unknown method')
    grid[0],grid[-1],grid[:,0],grid[:,-1] = bottom,top,left,right
    return grid,{side:patches.get(side,side) for side in SIDES},quality(grid)
