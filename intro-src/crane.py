"""Traditional crane in nine folds, seen from above.

Sheet is a square set as a diamond. The open corners gather at T (top), the
sheet centre C is the closed point. Steps: 1 diagonal fold, 2 fold in half,
3 squash to the preliminary (square) base, 4 kite folds, 5 petal fold to the
bird base, 6 narrow the legs, 7 reverse-fold neck and tail, 8 fold the head,
9 spread the wings (the crane lifts and grows for the finale).
"""
import math
import sys

from engine import bbox, dump, layer, mid, recenter, reflect, rotate, scale

C = (50.0, 47.0)   # sheet centre (closed point of the bases)
H = 42.0           # half diagonal
T, R, B, L = (50.0, C[1] - H), (50.0 + H, C[1]), (50.0, C[1] + H), (50.0 - H, C[1])

# Preliminary base: diamond with T on top, C at the bottom, side points at the edge midpoints.
Rv, Lv = mid(R, T), mid(L, T)

# Kite fold from T: crease T–X_R meets the edge Rv–C at X_R; Rv lands on the centre line at M.
theta = math.radians(22.5)
t = H / (math.cos(theta) + math.sin(theta))  # distance from T along the crease to the edge Rv–C
X_R = (T[0] + math.sin(theta) * t, T[1] + math.cos(theta) * t)
X_L = (100 - X_R[0], X_R[1])
M = (50.0, X_R[1])
crease_y = X_R[1]

# Petal fold: T flips across the crease line to Tp.
Tp = (50.0, 2 * crease_y - T[1])

# Leg narrowing: edge Tp–X_R folds to the centre line; crease from Tp at 11.25°.
phi = math.radians(11.25)
Z_R = (50.0 + (Tp[1] - crease_y) * math.tan(phi), crease_y)
Z_L = (100 - Z_R[0], crease_y)
leg_len = math.dist(Tp, X_R)
X_Rp = (50.0, Tp[1] - leg_len)  # where X_R lands (just above the crease)

sheet = [T, R, B, L]

# --- step 1: fold B up to T across L–R
s1 = [
    layer([L, R, T], 1),
    layer([L, T, R], 1, frm=[L, B, R]),
]
# --- step 2: fold L to R across the centre line T–C
s2 = [
    layer([C, R, T], 2),
    layer([R, C, T], 2, frm=[L, C, T]),
]
# --- step 3: squash both flaps into the square base. Each flap opens: the
# double corner R travels to T, the raw edge folds in half at Rv (which stays
# put), and the flap's other sheet swings out to the left to become Lv.
# Seen from above the silhouette spreads from the triangle to the diamond.
D = [C, Rv, T, Lv]
s3 = [
    layer(D, 4, frm=[C, R, T, mid(T, C)]),
]
# --- step 4: kite folds on the front layer (edges T–Rv and T–Lv to the centre)
s4 = [
    layer(D, 3),
    layer([C, X_R, T, X_L], 1),
    layer([T, M, X_R], 1, frm=[T, Rv, X_R]),
    layer([T, M, X_L], 1, frm=[T, Lv, X_L]),
]
# --- step 5: petal fold, front and back -> bird base (a rhombus T, X_R, Tp, X_L).
# The wings are the kites [T, X_R, C, X_L]; the petals flip down across the crease line.
wing = [T, X_R, C, X_L]
body = [X_L, X_R, C]
s5 = [
    layer(wing, 2),
    layer(body, 8),
    # the base's side corners fold in along the kite creases as the petal lifts
    layer([T, M, X_R], 2, frm=[T, Rv, X_R]),
    layer([T, M, X_L], 2, frm=[T, Lv, X_L]),
    layer([X_L, X_R, Tp], 3, frm=[X_L, X_R, T]),
]
# --- step 6: narrow the legs (petal edges to the centre line)
leg = [Z_L, Z_R, Tp]
s6 = [
    layer(wing, 3),
    layer(body, 8),
    layer(leg, 6),
    layer([Tp, X_Rp, Z_R], 3, frm=[Tp, X_R, Z_R]),
    layer([Tp, X_Rp, Z_L], 3, frm=[Tp, X_L, Z_L]),
]
# --- step 7: inside reverse folds. The crease crosses each leg a quarter of the
# way down; the part beyond it flips up and out, so the neck emerges from the
# lower-left of the body and the tail from the lower-right. The leg stubs that
# stay form the belly. A reverse fold is a reflection across a line through the
# pivot point on the leg's outer edge.
def reverse_fold(pivot, other, tip, angle_deg):
    """Reflect [pivot, other, tip] so the tip points `angle_deg` above horizontal."""
    length = math.dist(pivot, tip)
    sign = -1 if pivot[0] < 50 else 1
    new_tip = (pivot[0] + sign * length * math.cos(math.radians(angle_deg)),
               pivot[1] - length * math.sin(math.radians(angle_deg)))
    u1 = ((tip[0] - pivot[0]) / length, (tip[1] - pivot[1]) / length)
    u2 = ((new_tip[0] - pivot[0]) / length, (new_tip[1] - pivot[1]) / length)
    bis = (pivot[0] + u1[0] + u2[0], pivot[1] + u1[1] + u2[1])
    return reflect([pivot, other, tip], pivot, bis)

def along(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)

def limb(base, angle_deg, length, sign, width):
    """A neck/tail flap: base corner on the spine, tip at angle_deg above
    horizontal, `width` measured across the flap (inner edge toward the body)."""
    a = math.radians(angle_deg)
    tip = (base[0] + sign * length * math.cos(a), base[1] - length * math.sin(a))
    perp = (-sign * math.sin(a), -math.cos(a))
    inner = (base[0] + width * perp[0], base[1] + width * perp[1])
    return [base, inner, tip]

# --- step 7: inside reverse folds. Each leg flips up and out about its base
# corner on the spine: the neck rises steeply from the left side point X_L,
# the tail a little lower from X_R. As they swing up the body gathers into
# one diamond (spine on top, side points X_L/X_R, a small belly point B), so
# wings, neck and tail all attach to the same shape, like the real crane.
B = (50.0, crease_y + 9)
body7 = [X_L, M, X_R, B]
belly7 = [X_L, X_R, B]
wing7 = [T, X_R, M, X_L]
leg_len = math.dist(Tp, Z_L) * 0.95
neck = limb(X_L, 74, leg_len, -1, 8)
tail = limb(X_R, 58, leg_len, +1, 7)
s7 = [
    layer(wing7, 3, frm=wing),
    layer(body7, 8, frm=[X_L, M, X_R, C]),
    layer(belly7, 6, frm=[Z_L, Z_R, Tp]),
    layer(neck, 6, frm=[Z_L, Z_R, Tp]),
    layer(tail, 6, frm=[Z_R, Z_L, Tp]),
]
# --- step 8: fold the head: the last 30% of the neck reverse-folds forward-down.
nb, no, nt = neck
a70 = (nb[0] + 0.62 * (nt[0] - nb[0]), nb[1] + 0.62 * (nt[1] - nb[1]))
b70 = (no[0] + 0.62 * (nt[0] - no[0]), no[1] + 0.62 * (nt[1] - no[1]))
head_len = math.dist(a70, nt) * 0.6
d = ((nt[0] - nb[0]) / math.dist(nb, nt), (nt[1] - nb[1]) / math.dist(nb, nt))
down = (-d[1], d[0])  # rotate the neck direction 90 degrees toward the ground
if down[1] < 0:
    down = (-down[0], -down[1])
hm = mid(a70, b70)
head_tip = (hm[0] + head_len * down[0], hm[1] + head_len * down[1])
neck_body = [nb, no, b70, a70]
head = [a70, b70, head_tip]
s8 = [
    layer(wing7, 3),
    layer(body7, 8),
    layer(belly7, 6),
    layer(neck_body, 6),
    layer(tail, 6),
    layer(head, 6, frm=[a70, b70, nt]),
]
# --- step 9: pull the wings apart. This is the last real fold. The wing flap
# splits along the centre line and each half swings out about the top of the
# body (M on the spine), opening into a V, while body, neck, tail and head
# stay exactly as folded in step 8. A scale-up gives the finale a lift.
WING_SPREAD = 15
k9 = 1.25
def up(pts):
    return scale(pts, C, k9)

M_L, M_R = X_L, X_R  # wings root along the whole spine, flush with neck and tail
back = [X_L, (50.0, crease_y - 3.5), X_R, B]  # the back rises between the opened wings
wing_l9 = rotate(scale([M_L, T, M], M, 1.15), M, -WING_SPREAD)
wing_r9 = rotate(scale([M_R, T, M], M, 1.15), M, WING_SPREAD)
s9 = [
    layer(up(wing_r9), 5, frm=[X_R, T, M]),
    layer(up(wing_l9), 5, frm=[X_L, T, M]),
    layer(up(back), 8, frm=body7),
    layer(up(belly7), 6, frm=belly7),
    layer(up(neck_body), 6, frm=neck_body),
    layer(up(tail), 6, frm=tail),
    layer(up(head), 6, frm=head),
]

STEPS = recenter([[layer(sheet, 1)], s1, s2, s3, s4, s5, s6, s7, s8, s9])

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'crane.json'
    dump('crane', STEPS, out)
    print('crane: %d steps, bbox %s -> %s' % (len(STEPS) - 1, tuple(round(v, 1) for v in bbox(STEPS)), out))
