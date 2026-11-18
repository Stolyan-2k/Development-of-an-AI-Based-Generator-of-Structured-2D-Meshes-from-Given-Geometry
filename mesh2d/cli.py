import argparse
import json
from pathlib import Path
from .core import generate
from .export import write_mesh


def main():
    parser = argparse.ArgumentParser(description='Generate a structured planar quadrilateral mesh')
    parser.add_argument('case',type=Path,help='JSON geometry file')
    parser.add_argument('--method',choices=['ai','tfi','radial'],default='ai')
    parser.add_argument('--format',choices=['su2','vtk','foam'],default='su2')
    parser.add_argument('-o','--output',type=Path,required=True)
    parser.add_argument('--plot',type=Path,help='Save a mesh image (PNG, SVG or PDF)')
    parser.add_argument('--show',action='store_true',help='Open an interactive mesh view')
    args = parser.parse_args()
    try:
        if args.case.resolve()==args.output.resolve():
            raise ValueError('Output must differ from input')
        if args.plot and args.plot.resolve() in {args.case.resolve(),args.output.resolve()}:
            raise ValueError('Image path must differ from input and mesh output')
        if args.plot and args.plot.suffix.lower() not in {'.png','.svg','.pdf'}:
            raise ValueError('Image extension must be PNG, SVG or PDF')
        grid,patches,report = generate(json.loads(args.case.read_text(encoding='utf-8-sig')),args.method)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        write_mesh(args.output,grid,patches,args.format)
        if args.plot or args.show:
            from .visualize import plot_mesh
            plot_mesh(grid,patches,report,args.plot,args.show)
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,f'mesh2d: {error}\n')
    print(json.dumps(report,indent=2))
