from collections import defaultdict
import numpy as np


def topology(grid, patches):
    rows, columns = grid.shape[:2]
    nodes = np.arange(rows*columns).reshape(rows,columns)
    if 'left' not in patches and 'right' not in patches:
        nodes = np.column_stack([np.arange(rows*(columns-1)).reshape(rows,columns-1),
                                 np.arange(rows)*(columns-1)])
    quads = np.stack([nodes[:-1,:-1],nodes[:-1,1:],nodes[1:,1:],nodes[1:,:-1]],axis=-1).reshape(-1,4)
    markers = defaultdict(list)
    for side,line in [('bottom',nodes[0]),('right',nodes[:,-1]),('top',nodes[-1,::-1]),('left',nodes[::-1,0])]:
        if side not in patches:
            continue
        markers[patches[side]].extend(zip(line[:-1],line[1:]))
    return quads,markers


def write_mesh(path,grid,patches,fmt):
    coords = grid.reshape(-1,2)
    if fmt != 'vtk' and 'left' not in patches and 'right' not in patches:
        coords = grid[:, :-1].reshape(-1, 2)
    total = len(coords)
    quads,markers = topology(grid,patches)
    def labels(items):
        return ' '.join(map(str,items))
    with path.open('w',encoding='ascii',newline='\n') as stream:
        def line(value):
            print(value,file=stream)
        if fmt=='vtk':
            line('# vtk DataFile Version 3.0\nMesh2D\nASCII\nDATASET STRUCTURED_GRID')
            line(f'DIMENSIONS {grid.shape[1]} {grid.shape[0]} 1\nPOINTS {total} double')
            for xpos,ypos in coords:
                line(f'{xpos:.17g} {ypos:.17g} 0')
        elif fmt=='su2':
            line(f'NDIME= 2\nNELEM= {len(quads)}')
            for cell in quads:
                line('9 '+labels(cell))
            line(f'NPOIN= {total}')
            for xpos,ypos in coords:
                line(f'{xpos:.17g} {ypos:.17g}')
            line(f'NMARK= {len(markers)}')
            for name,edges in markers.items():
                line(f'MARKER_TAG= {name}\nMARKER_ELEMS= {len(edges)}')
                for edge in edges:
                    line('3 '+labels(edge))
        elif fmt=='foam':
            line('FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }')
            line('convertToMeters 1;\nvertices\n(')
            for height in (0,1):
                for xpos,ypos in coords:
                    line(f'({xpos:.17g} {ypos:.17g} {height})')
            line(');\nblocks\n(')
            for cell in quads:
                line('hex ('+labels([*cell,*(cell+total)])+') (1 1 1) simpleGrading (1 1 1)')
            line(');\nedges ();\nboundary\n(')
            for name,edges in markers.items():
                line(f'{name} {{ type patch; faces (')
                for first,last in edges:
                    line('('+labels([first,last,last+total,first+total])+')')
                line('); }')
            cap = 'frontAndBack'
            while cap in markers:
                cap += '_'
            line(f'{cap} {{ type empty; faces (')
            for cell in quads:
                line('('+labels(cell[::-1])+')\n('+labels(cell+total)+')')
            line('); }\n);\nmergePatchPairs ();')
