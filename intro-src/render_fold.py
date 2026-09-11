"""Render a fold model's steps as a PNG sheet for visual QA.

Usage: python3 render_fold.py <model.json> <out.png>

Ten step cells (0-9) in two rows. Inside each cell, three phases of that step
stacked top to bottom: start of the fold (p=0), mid-fold (p=0.5), finished
(p=1). White paper on black, like the intro overlay.
"""
import json
import math
import pathlib
import subprocess
import sys
import tempfile

CELL, PHASE = 126, 100


def ease(p):
    return (1 - math.cos(p * math.pi)) / 2


def poly_at(L, p):
    if not L['from']:
        return L['to']
    return [[a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p] for a, b in zip(L['from'], L['to'])]


def polygons(step, p):
    out = []
    for L in step:
        pts = ' '.join('%.2f,%.2f' % (x, y) for x, y in poly_at(L, p))
        out.append('<polygon points="%s" fill="#fff" fill-opacity="%s" stroke="#fff" stroke-width="0.5" stroke-opacity="0.55" stroke-linejoin="round"/>' % (pts, L['op']))
    return ''.join(out)


def main(model_path, out_path):
    data = json.loads(pathlib.Path(model_path).read_text())
    steps = data['steps']
    W, Hh = 5 * (CELL + 4) + 4, 2 * (3 * PHASE + 14) + 4
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, Hh, W * 2, Hh * 2),
             '<rect width="%d" height="%d" fill="#151515"/>' % (W, Hh)]
    for k, step in enumerate(steps):
        col, row = k % 5, k // 5
        x = 4 + col * (CELL + 4)
        y = 4 + row * (3 * PHASE + 14)
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#000"/>' % (x, y, CELL, 3 * PHASE + 10))
        parts.append('<text x="%d" y="%d" fill="#ff0" font-size="7" font-family="sans-serif">step %d</text>' % (x + 3, y + 8, k))
        for i, p in enumerate((0.0, 0.5, 1.0)):
            parts.append('<svg x="%d" y="%d" width="%d" height="%d" viewBox="0 0 100 100" overflow="visible">%s</svg>'
                         % (x + 13, y + 8 + i * PHASE, PHASE, PHASE, polygons(step, ease(p))))
    parts.append('</svg>')
    out = pathlib.Path(out_path)
    with tempfile.TemporaryDirectory() as tmp:
        svg = pathlib.Path(tmp) / (out.stem + '.svg')
        svg.write_text(''.join(parts))
        subprocess.run(['qlmanage', '-t', '-s', str(W * 2), '-o', tmp, str(svg)], check=True, capture_output=True, timeout=60)
        out.write_bytes((pathlib.Path(tmp) / (svg.name + '.png')).read_bytes())
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
