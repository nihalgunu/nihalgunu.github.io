"""Emit the finished model's silhouette as a small inline SVG for the nav logo.

Usage: python3 gen_logo.py dart.json  -> prints the <svg> markup
Takes the last step's `to` polygons, crops the viewBox to their bounds, and
boosts the layer opacities a little so the stack reads solid at ~20px.
"""
import json
import sys

data = json.load(open(sys.argv[1]))
step = data['steps'][-1]
xs = [x for L in step for x, _ in L['to']]
ys = [y for L in step for _, y in L['to']]
x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
pad = 1.0
vb = '%.1f %.1f %.1f %.1f' % (x0 - pad, y0 - pad, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad)
polys = ''.join(
    '<polygon points="%s" fill-opacity="%.2f"/>' % (
        ' '.join('%.1f,%.1f' % (x, y) for x, y in L['to']), min(1.0, L['op'] * 1.5))
    for L in step
)
print('<svg class="nav-logo-mark" viewBox="%s" aria-hidden="true">%s</svg>' % (vb, polys))
print('ratio %.2f' % ((x1 - x0) / (y1 - y0)), file=sys.stderr)
