from pathlib import Path

def plot_mesh(grid, patches, report, output=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    figure, axes = plt.subplots(figsize=(12, 5), layout='constrained')
    figure.patch.set_facecolor('#f5f7fb')
    axes.set_facecolor('#ffffff')
    lines = list(grid) + list(grid.transpose(1, 0, 2))
    axes.add_collection(LineCollection(lines, colors='#4c6688', linewidths=0.55))
    boundaries = {'bottom': grid[0], 'top': grid[-1],
                  'left': grid[:, 0], 'right': grid[:, -1]}
    names = list(dict.fromkeys(patches.values()))
    colors = dict(zip(names, ['#db652b', '#188d83', '#7755bb', '#cf4368']))
    seen = set()
    for side, coordinates in boundaries.items():
        if side not in patches:
            continue
        name = patches[side]
        axes.plot(coordinates[:, 0], coordinates[:, 1], color=colors[name],
                  linewidth=2.3, label=name if name not in seen else '_nolegend_')
        seen.add(name)
    axes.autoscale()
    axes.set_aspect('equal', adjustable='box')
    axes.margins(0.04)
    axes.set_xlabel('x')
    axes.set_ylabel('y')
    axes.set_title(f"Mesh2D | {report['cells']:,} cells | "
                   f"min scaled Jacobian: {report['min_scaled_jacobian']:.3f}", pad=18)
    axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=len(names), frameon=False)
    for spine in axes.spines.values():
        spine.set_color('#c6ceda')
    try:
        if output is not None:
            target = Path(output)
            target.parent.mkdir(parents=True, exist_ok=True)
            figure.savefig(target, dpi=180)
        if show:
            plt.show()
    finally:
        plt.close(figure)
