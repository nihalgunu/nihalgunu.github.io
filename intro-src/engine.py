"""Flat-fold model for the intro mark: a sheet of paper folded step by step.

A model is a list of steps. Step 0 is the unfolded sheet; each later step is
the full set of visible paper layers after that fold. A layer is a polygon with
a thickness count `n` (how many sheets are stacked there, rendered as opacity)
and, if it moves during the step, the polygon it moves *from*. The runtime
interpolates from -> to, so a reflected flap sweeps through its crease line
exactly like the top-down view of paper turning over.
"""
import json
import math

BASE_OPACITY = 0.32  # one sheet of paper; n sheets = 1 - (1 - base)^n


def reflect(pts, a, b):
    """Reflect points across the line through a and b."""
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    d2 = dx * dx + dy * dy
    out = []
    for x, y in pts:
        t = ((x - ax) * dx + (y - ay) * dy) / d2
        px, py = ax + t * dx, ay + t * dy
        out.append((2 * px - x, 2 * py - y))
    return out


def rotate(pts, c, deg):
    s, co = math.sin(math.radians(deg)), math.cos(math.radians(deg))
    return [(c[0] + (x - c[0]) * co - (y - c[1]) * s, c[1] + (x - c[0]) * s + (y - c[1]) * co) for x, y in pts]


def scale(pts, c, k):
    return [(c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k) for x, y in pts]


def translate(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def mid(a, b):
    return lerp(a, b, 0.5)


def pad(pts, length):
    return list(pts) + [pts[-1]] * (length - len(pts))


def layer(to, n, frm=None):
    """A visible layer after a step; `frm` is where it moves from during the step."""
    if frm is not None:
        m = max(len(to), len(frm))
        to, frm = pad(to, m), pad(frm, m)
    return {'to': [list(p) for p in to], 'from': [list(p) for p in frm] if frm else None, 'n': n}


def opacity(n):
    return round(1 - (1 - BASE_OPACITY) ** n, 3)


def export(name, steps):
    return {
        'name': name,
        'steps': [[{'to': L['to'], 'from': L['from'], 'op': opacity(L['n'])} for L in step] for step in steps],
    }


def bbox(steps):
    xs = [x for step in steps for L in step for x, _ in L['to']]
    ys = [y for step in steps for L in step for _, y in L['to']]
    return min(xs), min(ys), max(xs), max(ys)


def recenter(steps, cx=50.0, cy=50.0):
    """Keep the paper centred: shift every step so its bounding box sits on (cx, cy).

    `to` polygons take the step's own shift; `from` polygons take the previous
    step's shift (they live in that step's frame), so a fold that moves the
    paper's centre of mass glides smoothly back to the middle as it folds.
    Static layers get a `from` too (their own outline, previous shift) so the
    whole model glides together instead of static parts jumping.
    """
    out, prev = [], (0.0, 0.0)
    for k, step in enumerate(steps):
        x0, y0, x1, y1 = bbox([step])
        d = (cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)
        shifted = []
        for L in step:
            frm = L['from'] if L['from'] else (L['to'] if k else None)
            shifted.append({
                'to': [[x + d[0], y + d[1]] for x, y in L['to']],
                'from': [[x + prev[0], y + prev[1]] for x, y in frm] if frm else None,
                'n': L['n'],
            })
        out.append(shifted)
        prev = d
    return out


def dump(name, steps, path):
    data = export(name, steps)
    with open(path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    return data
