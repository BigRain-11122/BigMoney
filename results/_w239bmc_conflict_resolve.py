# -*- coding: utf-8 -*-
# r996-continuation bm-c: resolve the two orphaned stash-pop conflict faces
# (lineage-B r933 surgery leftover, zero active rebase on disk).
# machine-health.json = UNION (append-only snapshot array: keep upstream 13:11
#   entry AND stashed 13:36 entry, drop base + markers)
# _r686bmb_d19_check.json = STASHED side (bm-c live probe face, ts-newer-wins,
#   single rotating evidence face; upstream bm-b face preserved in git history)
import io, sys

def split_conflict(text):
    """Return (pre, upstream, base, stashed, post) for a single 3-way block."""
    a = text.find("<<<<<<< Updated upstream\n")
    b = text.find("||||||| Stash base\n", a)
    c = text.find("=======\n", b)
    d = text.find(">>>>>>> Stashed changes\n", c)
    assert -1 not in (a, b, c, d), "conflict markers not found"
    pre = text[:a]
    upstream = text[a + len("<<<<<<< Updated upstream\n"):b]
    base = text[b + len("||||||| Stash base\n"):c]
    stashed = text[c + len("=======\n"):d]
    post = text[d + len(">>>>>>> Stashed changes\n"):]
    return pre, upstream, base, stashed, post

# ---- machine-health.json: union (upstream + stashed as SEPARATE elements) ----
p1 = "fleet/machine-health.json"
t = io.open(p1, encoding="utf-8").read()
pre, up, base, st, post = split_conflict(t)
# conflict sits INSIDE one array element: pre ends with "    {\n", post = "    }\n]"
# union = two elements: {up body} }, { {st body} }
resolved1 = pre + up + "    },\n    {\n" + st + post
io.open(p1, "w", encoding="utf-8", newline="").write(resolved1)
import json
d1 = json.loads(resolved1)  # validity gate
print("machine-health.json: UNION resolved -> %d top-level elements, JSON valid" % len(d1))

# ---- _r686bmb_d19_check.json: stashed side (bm-c face, ts-newer-wins) ----
p2 = "results/_r686bmb_d19_check.json"
t2 = io.open(p2, encoding="utf-8").read()
out = []
rest = t2
while "<<<<<<< Updated upstream" in rest:
    pre, up, base, st, post = split_conflict(rest)
    out.append(pre)
    out.append(st)  # stashed side = bm-c live face
    rest = post
out.append(rest)
resolved2 = "".join(out)
d = json.loads(resolved2)  # validity gate
assert d["machine"] == "bm-c", "d19_check resolved side must be the bm-c face"
io.open(p2, "w", encoding="utf-8", newline="").write(resolved2)
print("_r686bmb_d19_check.json: STASHED (bm-c) side kept, JSON valid, wm_dec", d["wm_decisions"][:8], "wm_ord", d["wm_orders"][:8])
