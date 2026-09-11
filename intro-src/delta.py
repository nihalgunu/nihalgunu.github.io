"""Swept-wing delta from a SQUARE sheet in nine folds.

Steps 1-6 are seen from above, nose up: 1 fold in half vertically (the valley
fold is shown; the sheet is open again with a faint centre seam from step 2
on), 2 top-left corner to the centre line, 3 top-right corner to the centre
line (kite), 4 the tip folds down to the centre point where the two corners
meet (blunt nose), 5 the left slanted edge folds to the centre line over the
folded tip, 6 the right slanted edge likewise (long narrow kite; the flaps
lock the nose down). On a square these last two creases run off the bottom
edge, so the bottom corners fold over too and a sliver pokes past the old
bottom edge, exactly as on real paper.

Step 7 folds the model in half along the seam, right over left, and as it
closes the model turns 90 degrees clockwise so the nose points RIGHT. From
here on it is a side view: a thin wedge lying horizontally, the spine (the
fold) along its bottom edge and the wing stack above it. 8 the near wing folds
down along a shallow diagonal from just behind the nose to the tail, so the
trailing edge flares wide below the spine, 9 the far wing folds the same way
and both wings open to a slightly raised V: the same pieces are drawn in a
three-quarter view from a little above (near wing foreshortened, far wing
rising behind the keel and showing its swept planform) and the finished delta
grows a little for the finale.

Steps 1-6 draw every layer as one sheet (n=1) and let overlap make the
thickness; once the model is closed (7-8) the stacks are drawn two sheets
thick and the finale three, so the paper brightens in steps rather than
popping at the last cut. Every fold is a literal reflection of the moving
pieces across the crease line; the only paper not carried through is the
4-unit bottom-corner slivers of steps 5/6, tucked at the tail when the model
turns side-on in step 7.
"""
import math
import sys

from engine import bbox, dump, layer, recenter, reflect, rotate, scale

# --- sheet: a square, side 70, centred on the view
SIDE = 70.0
X0, X1, Y0, Y1 = 50 - SIDE / 2, 50 + SIDE / 2, 50 - SIDE / 2, 50 + SIDE / 2
CX = 50.0
W2 = SIDE / 2
TL, TR, BL, BR = (X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)
N, S = (CX, Y0), (CX, Y1)                    # nose and tail on the centre line

RC = (CX, 50.0)                              # step 7 turns the model about this point
SPINE_Y = RC[1]                              # after the turn the spine lies along this line
NOSE_X = RC[0] + (SPINE_Y - Y0) - W2 / 2     # the blunt nose's front edge after the turn (see step 4)
KEEL_NOSE = 0.8                              # wing crease height above the spine, just behind the nose
KEEL_TAIL = 4.0                              # ... and at the tail: the crease is a shallow diagonal
VIEW_ELEV = 30.0                             # finale: camera looks down at the delta by this many degrees
DIHEDRAL = 4.0                               # finale: the opened wings are raised this much above level
#   VIEW_ELEV > DIHEDRAL: the near wing, tilted toward the camera, projects BELOW the spine
#   on screen and the far wing above it, so the swept planform reads on both sides.
#   far wing sin(34) = 0.56 (it visibly sweeps down from standing), near wing sin(-26) = -0.44,
#   keel cos(30) = 0.87: the V is close to symmetric and the near wing's tail flare (~11 below
#   the hinge) clears the keel bottom (~3.5 below it).
FINALE_SCALE = 1.25
FINALE_N = 3                                 # solidity boost so the finished delta holds over bright photos
STACK_N = 2                                  # steps 7-8: the closed model is two sheets thick (opacity ramp to the finale)


def mirror(pts):
    return [(2 * CX - x, y) for x, y in pts]


def clip(poly, a, b, side):
    """Sutherland-Hodgman clip of `poly` against the line a-b.
    side='left' keeps points on the left of a->b (y down), 'right' the other side."""
    ux, uy = b[0] - a[0], b[1] - a[1]

    def d(p):
        return (p[0] - a[0]) * uy - (p[1] - a[1]) * ux    # > 0 on the right of a->b

    def inside(p):
        return d(p) <= 1e-9 if side == 'left' else d(p) >= -1e-9

    def cross(p, q):
        dp, dq = d(p), d(q)
        t = dp / (dp - dq)
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)

    out = []
    for i, cur in enumerate(poly):
        prev = poly[i - 1]
        if inside(cur):
            if not inside(prev):
                out.append(cross(prev, cur))
            out.append(cur)
        elif inside(prev):
            out.append(cross(prev, cur))
    res = []
    for p in out:
        if not res or math.dist(res[-1], p) > 1e-6:
            res.append(p)
    if len(res) > 1 and math.dist(res[0], res[-1]) < 1e-6:
        res.pop()
    return res if len(res) >= 3 else None


def split(pieces, a, b):
    """Split pieces along the crease a-b: (parts left of a->b, parts right of it)."""
    left, right = [], []
    for p in pieces:
        l, r = clip(p, a, b, 'left'), clip(p, a, b, 'right')
        if l:
            left.append(l)
        if r:
            right.append(r)
    return left, right


def fold(pieces, a, b):
    return [reflect(p, a, b) for p in pieces]


def static(pieces, n=1):
    return [layer(p, n) for p in pieces]


def moving(to_pieces, from_pieces, n=1):
    return [layer(p, n, frm=f) for p, f in zip(to_pieces, from_pieces)]


def extend(a, b, k=40.0):
    """The segment a-b stretched by k units past both ends (a crease line that clears the model)."""
    length = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    return (a[0] - ux * k, a[1] - uy * k), (b[0] + ux * k, b[1] + uy * k)


sheet = [TL, TR, BR, BL]
left_half = [TL, N, S, BL]
right_half = [N, TR, BR, S]

# --- step 1: fold in half vertically (left half over onto the right). The sheet
# is opened again at the cut into step 2, where the two halves meet at the seam.
s1 = [
    layer(right_half, 1),
    layer(mirror(left_half), 1, frm=left_half),
]

# --- step 2: top-left corner to the centre line. Crease N-E_L at 45 degrees;
# the corner lands on the seam at P, the sheet centre. The step starts from the
# folded half of step 1 (same frame, no paper reappearing at the cut): the left
# half glides open across the seam while its corner swings on round to P.
E_L, E_R = (X0, Y0 + W2), (X1, Y0 + W2)
P = (CX, Y0 + W2)
cornerL, cornerR = [N, TL, E_L], [N, TR, E_R]
flapL, flapR = reflect(cornerL, N, E_L), reflect(cornerR, N, E_R)     # [N, P, E]
baseL = [N, S, BL, E_L]                    # left half minus the corner
baseR = [N, E_R, BR, S]                    # right half minus the corner
s2 = [
    layer(right_half, 1),
    layer(baseL, 1, frm=mirror(baseL)),
    layer(flapL, 1, frm=mirror(cornerL)),
]
# --- step 3: top-right corner to the centre line -> kite
s3 = [
    layer(baseL, 1),
    layer(flapL, 1),
    layer(baseR, 1),
    layer(flapR, 1, frm=cornerR),
]

# --- step 4: the tip folds down to P, where the two corners meet: a horizontal
# crease halfway between N and P cuts the base sheet and both flaps; the three
# tip pieces flip down over the flaps and make the blunt nose.
TIP_Y = (Y0 + P[1]) / 2
TA, TB = (X0 - 20, TIP_Y), (X1 + 20, TIP_Y)
model3 = [baseL, baseR, flapL, flapR]
low4, tip4 = split(model3, TA, TB)                             # crease left -> right: above it is the tip
assert all(y >= TIP_Y - 1e-6 for p in low4 for _, y in p)
assert all(y <= TIP_Y + 1e-6 for p in tip4 for _, y in p)
tip4f = fold(tip4, TA, TB)
assert abs(reflect([N], TA, TB)[0][1] - P[1]) < 1e-6           # the tip lands on P
s4 = static(low4) + moving(tip4f, tip4)
model4 = low4 + tip4f

# --- step 5: the left slanted edge to the centre line, over the folded tip.
# The slanted edge and the centre line meet at N (now off the paper, above the
# blunt nose), so the crease is their bisector from N at 22.5 degrees: it
# enters the paper on the nose's top edge and, on a square, runs off the
# BOTTOM edge, so the bottom-left corner folds over too and pokes past the old
# bottom edge. The flap lands exactly on the seam and locks the tip down.
tan225 = math.tan(math.radians(22.5))
Q_L = (CX - SIDE * tan225, Y1)
Q_R = (CX + SIDE * tan225, Y1)
assert abs(reflect([E_L], N, Q_L)[0][0] - CX) < 1e-6           # E_L lands on the centre line
move5, stay5 = split(model4, N, Q_L)                           # crease N -> Q_L (downwards): left of it moves
move5f = fold(move5, N, Q_L)
s5 = static(stay5) + moving(move5f, move5)
model5 = stay5 + move5f

# --- step 6: the right slanted edge to the centre line (long narrow kite).
stay6, move6 = split(model5, N, Q_R)                           # crease N -> Q_R: right of it moves
move6f = fold(move6, N, Q_R)
s6 = static(stay6) + moving(move6f, move6)
model6 = stay6 + move6f

# --- step 7: fold in half along the centre seam, right over left, and turn
# the model 90 degrees clockwise as it closes so the nose points right. Every
# piece is cut at the seam; the parts on the right flip across it onto the
# left parts, then everything turns: the frm polygons are the step-6 geometry,
# the to polygons the folded profile rotated about RC. With y down, +90 takes
# the top (nose) to the right and the left half (now the whole folded stack)
# to the top, so the spine is the bottom edge of the wedge and the wings stand
# above it.
# The bottom-corner slivers that poked past the old bottom edge in steps 5/6
# are tucked here (clipped at the tail line, y = Y1, in both the frm and the to
# geometry so every vertex still has its partner): in the side view they would
# read as a spike at the tail, and the honest silhouette is a clean trailing
# edge. The paper lost is a 4-unit sliver.
far7, near7 = split(model6, N, S)                              # crease N -> S: right of it moves
TAIL_A, TAIL_B = (X0 - 20, Y1), (X1 + 20, Y1)
_, far7 = split(far7, TAIL_A, TAIL_B)                          # right of left -> right is above the line
_, near7 = split(near7, TAIL_A, TAIL_B)
near7_flat = fold(near7, N, S)                                 # right side reflected onto the left


def turn(pieces):
    return [rotate(p, RC, 90) for p in pieces]


far_stack = turn(far7)                                         # the half that stayed: far side of the delta
near_stack = turn(near7_flat)                                  # the half that flipped over: near side, on top
# The far stack is drawn two sheets thick from here (the closed model is), so
# it carries the silhouette through the turn while the near stack, which is
# edge-on mid-fold, stays one sheet until it has landed.
s7 = moving(far_stack, far7, STACK_N) + moving(near_stack, near7, 1)
px0, py0, px1, py1 = bbox([static(far_stack + near_stack)])
assert abs(py1 - SPINE_Y) < 1e-6                               # the spine is the bottom edge of the profile
assert abs(px1 - NOSE_X) < 1e-6                                # the nose points right
assert abs(px0 - X0) < 1e-6                                    # clean vertical trailing edge at the tail

# --- step 8: fold the near wing down. The crease is a shallow diagonal from
# just behind the nose (KEEL_NOSE above the spine) back to the tail (KEEL_TAIL
# above it); everything of the near stack above it reflects across, sweeps
# past the spine and hangs below the model, flaring wide at the tail. The far
# stack's wing is still up behind it.
TAIL_X = px0
HA, HB = extend((TAIL_X, SPINE_Y - KEEL_TAIL), (NOSE_X, SPINE_Y - KEEL_NOSE))   # tail -> nose: above it is the wing
near_keel, near_wing = split(near_stack, HA, HB)
near_wing_f = fold(near_wing, HA, HB)
s8 = static(far_stack, STACK_N) + static(near_keel, STACK_N) + moving(near_wing_f, near_wing, STACK_N)

# --- step 9: fold the far wing the same way and open both wings. Both wings
# hinge around the crease to a slightly raised V. The finished delta is drawn
# in a three-quarter view from a little above: with the camera looking down by
# VIEW_ELEV and the wings raised by DIHEDRAL, a point w from the hinge on the
# near wing sits w*sin(DIHEDRAL - VIEW_ELEV) above the crease line, one on the
# far wing w*sin(DIHEDRAL + VIEW_ELEV) above it (it rises behind the keel and
# shows the swept planform), and the keel is foreshortened by cos(VIEW_ELEV).
# Every piece is the same polygon as in step 8, just mapped by that projection
# (the far wing goes straight from standing to open: its fold-and-lift is one
# sweep), then the delta grows for the finale.
far_keel, far_wing = split(far_stack, HA, HB)
_e, _a = math.radians(VIEW_ELEV), math.radians(DIHEDRAL)
NEAR_K, FAR_K, KEEL_K = math.sin(_a - _e), math.sin(_a + _e), math.cos(_e)


def project(pieces, k):
    """Scale each point's distance from the hinge line by k (the wing's opening angle, seen from the camera)."""
    ax, ay = HA
    ux, uy = HB[0] - ax, HB[1] - ay
    d2 = ux * ux + uy * uy
    out = []
    for p in pieces:
        q = []
        for x, y in p:
            t = ((x - ax) * ux + (y - ay) * uy) / d2
            fx, fy = ax + t * ux, ay + t * uy
            q.append((fx + (x - fx) * k, fy + (y - fy) * k))
        out.append(q)
    return out


near_wing_open = project(near_wing, NEAR_K)
far_wing_open = project(far_wing, FAR_K)
keel_pieces = far_keel + near_keel
keel_open = project(keel_pieces, KEEL_K)
open_all = far_wing_open + keel_open + near_wing_open
lx0, ly0, lx1, ly1 = bbox([static(open_all)])
lc = ((lx0 + lx1) / 2, (ly0 + ly1) / 2)


def grow(pieces):
    return [scale(p, lc, FINALE_SCALE) for p in pieces]


s9 = moving(grow(far_wing_open), far_wing, FINALE_N) + \
     moving(grow(keel_open), keel_pieces, FINALE_N) + \
     moving(grow(near_wing_open), near_wing_f, FINALE_N)

STEPS = recenter([[layer(sheet, 1)], s1, s2, s3, s4, s5, s6, s7, s8, s9])

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'delta.json'
    dump('delta', STEPS, out)
    for k, st in enumerate(STEPS):
        x0, y0, x1, y1 = bbox([st])
        print('step %d: %d layers, bbox w %.1f h %.1f' % (k, len(st), x1 - x0, y1 - y0))
    print('delta: %d steps, bbox %s -> %s' % (len(STEPS) - 1, tuple(round(v, 1) for v in bbox(STEPS)), out))
