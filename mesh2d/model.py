"""Fit a linear boundary-to-interior operator on synthetic harmonic grids."""
from functools import lru_cache
import numpy as np


@lru_cache(maxsize=1)
def train():
    size = 17
    samples = np.random.default_rng(40).uniform(-1, 1, (96, size - 2))
    fields = np.zeros((len(samples), size, size))
    fields[:, 0, 1:-1] = samples
    for _ in range(320):
        fields[:, 1:-1, 1:-1] = 0.25 * (fields[:, :-2, 1:-1] + fields[:, 2:, 1:-1]
                                         + fields[:, 1:-1, :-2] + fields[:, 1:-1, 2:])
    weights = np.linalg.lstsq(samples, fields.reshape(len(samples), -1), rcond=None)[0]
    return weights.reshape(size - 2, size, size)


def predict(walls, horizontal, vertical):
    weights = train()
    size = weights.shape[1]
    axis = np.linspace(0, 1, size)
    fields = []
    for wall in walls:
        curve = wall(axis)
        chord = (1 - axis[:, None]) * curve[0] + axis[:, None] * curve[-1]
        fields.append(np.einsum('kij,kd->ijd', weights, (curve - chord)[1:-1]))
    bottom, top, left, right = fields
    field = bottom + top[::-1] + left.transpose(1,0,2) + right.transpose(1,0,2)[:,::-1]
    xcoord, ycoord = horizontal * (size-1), vertical * (size-1)
    cols = np.minimum(xcoord.astype(int), size-2)
    rows = np.minimum(ycoord.astype(int), size-2)
    across = (xcoord-cols)[None,:,None]
    up = (ycoord-rows)[:,None,None]
    rows = rows[:,None]
    return ((1-up)*((1-across)*field[rows,cols]+across*field[rows,cols+1])
            + up*((1-across)*field[rows+1,cols]+across*field[rows+1,cols+1]))
