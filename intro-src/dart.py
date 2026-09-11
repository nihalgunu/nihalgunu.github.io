"""Classic dart from a SQUARE sheet in nine folds.

Steps 1-5 are seen from above, nose up: 1 fold in half vertically (the valley
fold closes left over right; the sheet opens again DURING step 2, so the two
halves meet at a faint centre seam from then on), 2 top-left corner to the
centre line, 3 top-right corner to the centre line (kite), 4 left slanted edge
to the centre line, 5 right slanted edge (narrow kite - on a square the second
flaps cross below the centre and poke past the old bottom edge, as they do on
real paper).

Step 6 folds the model in half along the seam, right over left, and as it
closes the model turns 90 degrees clockwise so the nose points RIGHT. From
here on it is a side view: a thin wedge lying horizontally, the spine (the
fold) along its bottom edge and the wing stack above it. 7 the near wing folds
down along a crease parallel to the spine and hangs below it, 8 the far wing
folds down behind it on a crease a touch lower (as the second wing of a real
dart sits, one paper thickness off), so its edge peeks out below, 9 the wings
lift open to a raised V: the same pieces are drawn in a three-quarter view from
above (near wing foreshortened below the keel, far wing rising behind it) and
the finished dart grows a little for the finale.

Every layer is one sheet (n=1); thickness comes from layers overlapping, and
every fold is a literal reflection of the moving pieces across its crease line.
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

KEEL = 10.0                                  # keel depth: the near wing crease sits this far above the spine
FAR_DROP = 2.0                               # step 8: the far wing's crease sits this much lower (nearer the spine)
RC = (CX, 50.0)                              # step 6 turns the model about this point
SPINE_Y = RC[1]                              # after the turn the spine lies along this line
CREASE_Y = SPINE_Y - KEEL                    # near wing crease, parallel to the spine
FAR_CREASE_Y = CREASE_Y + FAR_DROP           # far wing crease, a little closer to the spine
VIEW_ELEV = 52.0                             # finale: camera looks down at the dart by this many degrees
VIEW_AZ = -4.0                               # finale: camera swung this far behind the dart (negative = behind)
DIHEDRAL = 44.0                              # finale: the opened wings are raised this much above level
FINALE_SCALE = 1.10


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


sheet = [TL, TR, BR, BL]
left_half = [TL, N, S, BL]
right_half = [N, TR, BR, S]

# --- step 1: fold in half vertically (left half over onto the right).
s1 = [
    layer(right_half, 1),
    layer(mirror(left_half), 1, frm=left_half),
]

# --- step 2: open the sheet again and fold the top-left corner to the centre
# line. Crease N-E_L at 45 degrees; the corner lands on the seam at P. The left
# half starts where step 1 left it (lying on the right half) and swings open
# while the corner folds, so photo 2 begins on exactly the frame photo 1 ended
# on and the sheet opens about its centre instead of popping.
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

# --- step 4: left slanted edge N-E_L to the centre line. Crease from N at 22.5
# degrees; on a square it reaches the BOTTOM edge at Q_L, so the bottom-left
# corner folds over too and pokes past the centre line and below the old bottom
# edge. The crease cuts the first flap at K_L (on the flap's lower edge), so the
# flap folds along with the base sheet.
tan225 = math.tan(math.radians(22.5))
Q_L = (CX - SIDE * tan225, Y1)
Q_R = (CX + SIDE * tan225, Y1)
assert abs(reflect([E_L], N, Q_L)[0][0] - CX) < 1e-6           # E_L lands on the centre line

moveL4, stayL4 = split([baseL, flapL], N, Q_L)                 # the crease runs N -> Q_L (downwards): left of it moves
moveL4f = fold(moveL4, N, Q_L)
s4 = [
    layer(baseR, 1),
    layer(flapR, 1),
] + static(stayL4) + moving(moveL4f, moveL4)

# --- step 5: the right slanted edge to the centre line (narrow kite). The right
# flap lands on top of the left one where they cross below the centre.
stayR4, moveR4 = split([baseR, flapR], N, Q_R)                 # crease N -> Q_R: right of it moves
moveR4f = fold(moveR4, N, Q_R)
left_side = stayL4 + moveL4f
s5 = static(stayR4) + static(left_side) + moving(moveR4f, moveR4)
right_side = stayR4 + moveR4f
model5 = left_side + right_side

# --- step 6: fold in half along the centre seam, right over left, and turn
# the model 90 degrees clockwise as it closes so the nose points right. Every
# piece is cut at the seam; the parts on the right flip across it (including
# the left flap's overhang) onto the left parts, then everything turns: the
# frm polygons are the step-5 geometry, the to polygons the folded profile
# rotated about RC. With y down, +90 takes the top (nose) to the right and the
# left half (now the whole folded stack) to the top, so the spine is the
# bottom edge of the wedge and the wings stand above it.
# (Known limit: the runtime blends frm -> to linearly, and the chord of a
# 90-degree turn passes through a 45-degree, 0.71-scale copy of the model at
# mid-step, so the wedge dips smaller for a few frames while it turns.)
far6_from, near6_from = split(model5, N, S)                    # crease N -> S: right of it moves
near6_flat = fold(near6_from, N, S)                            # right side reflected onto the left


def turn(pieces):
    return [rotate(p, RC, 90) for p in pieces]


far_stack = turn(far6_from)                                    # the half that stayed: far side of the dart
near_stack = turn(near6_flat)                                  # the half that flipped over: near side, on top
s6 = moving(far_stack, far6_from) + moving(near_stack, near6_from)

# --- step 7: fold the near wing down. The crease is the horizontal line
# y = CREASE_Y, parallel to the spine and KEEL above it; everything of the near
# stack above the crease reflects across it, sweeps past the spine and hangs
# below the model. The far stack's wing is still up behind it.
WA, WB = (X0 - 20, CREASE_Y), (X1 + 20, CREASE_Y)
near_keel, near_wing = split(near_stack, WA, WB)               # crease left -> right: above it is the wing
assert all(y >= CREASE_Y - 1e-6 for p in near_keel for _, y in p)
assert all(y <= CREASE_Y + 1e-6 for p in near_wing for _, y in p)
near_wing_f = fold(near_wing, WA, WB)
s7 = static(far_stack) + static(near_keel) + moving(near_wing_f, near_wing)

# --- step 8: fold the far wing down the same way, on its own crease a paper
# thickness nearer the spine (FAR_DROP). It lands behind the near wing, so it
# is drawn first (mostly covered); because its crease is lower it hangs
# 2*FAR_DROP further down and its edge peeks out below the near wing, as the
# second wing of a real dart does. Still an exact reflection about its crease.
FA, FB = (X0 - 20, FAR_CREASE_Y), (X1 + 20, FAR_CREASE_Y)
far_keel, far_wing = split(far_stack, FA, FB)
far_wing_f = fold(far_wing, FA, FB)
s8 = moving(far_wing_f, far_wing) + static(far_keel) + static(near_keel) + static(near_wing_f)

# --- step 9: open the wings. Both wings hinge back up around their creases to
# a raised V, and the finished dart is drawn in a three-quarter view: the
# camera sits on the near side, well above (VIEW_ELEV) and a little behind
# (VIEW_AZ), so the far wing rises behind the keel, the near wing lies
# foreshortened below it, the two trailing edges separate, and the nose lifts
# slightly as if climbing. In dart space x runs along the spine (nose +x), d
# toward the viewer, z up: a keel point is (x, 0, z<=0), a point w from its
# hinge on the near wing is (x, w cos a, w sin a), on the far wing
# (x, -w cos a, -FAR_DROP + w sin a). Every piece is the same polygon as in
# step 8 mapped by that projection; the dart then grows for the finale.
_e, _a, _z = math.radians(VIEW_ELEV), math.radians(DIHEDRAL), math.radians(VIEW_AZ)


def project(pieces, side):
    """Map plan-view pieces into the finale view. side: +1 near wing, -1 far wing, 0 keel."""
    out = []
    for piece in pieces:
        q = []
        for x, y in piece:
            X = x - CX
            if side == 0:
                d, z = 0.0, CREASE_Y - y                      # keel hangs below the near hinge
            elif side > 0:
                w = CREASE_Y - y                              # distance from the hinge (wing was above it)
                d, z = w * math.cos(_a), w * math.sin(_a)
            else:
                w = FAR_CREASE_Y - y
                d, z = -w * math.cos(_a), -FAR_DROP + w * math.sin(_a)
            sx = X * math.cos(_z) - d * math.sin(_z)
            sy = -X * math.sin(_z) * math.sin(_e) - d * math.cos(_z) * math.sin(_e) + z * math.cos(_e)
            q.append((CX + sx, CREASE_Y - sy))
        out.append(q)
    return out


near_wing_open = project(near_wing, +1)
far_wing_open = project(far_wing, -1)
keel_pieces = far_keel + near_keel
keel_open = project(keel_pieces, 0)
open_all = far_wing_open + keel_open + near_wing_open
lx0, ly0, lx1, ly1 = bbox([static(open_all)])
lc = ((lx0 + lx1) / 2, (ly0 + ly1) / 2)


def grow(pieces):
    return [scale(p, lc, FINALE_SCALE) for p in pieces]


s9 = moving(grow(far_wing_open), far_wing_f) + \
     moving(grow(keel_open), keel_pieces) + \
     moving(grow(near_wing_open), near_wing_f)

STEPS = recenter([[layer(sheet, 1)], s1, s2, s3, s4, s5, s6, s7, s8, s9])

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'dart.json'
    dump('dart', STEPS, out)
    for k, st in enumerate(STEPS):
        x0, y0, x1, y1 = bbox([st])
        print('step %d: %d layers, bbox w %.1f h %.1f' % (k, len(st), x1 - x0, y1 - y0))
    print('dart: %d steps, bbox %s -> %s' % (len(STEPS) - 1, tuple(round(v, 1) for v in bbox(STEPS)), out))
