# -*- coding: utf-8 -*-
# repair pass: machine-health.json (insert missing element separator) + d19_check (stashed side)
import io, json

p1 = "fleet/machine-health.json"
t = io.open(p1, encoding="utf-8").read()
try:
    json.loads(t)
    print("machine-health.json: already valid")
except json.JSONDecodeError:
    needle = '"ts":  "2026-10-14 13:11"\n        "@{name=qwen3.8:27b'
    fixed = t.replace(needle, '"ts":  "2026-10-14 13:11"\n    },\n    {\n        "@{name=qwen3.8:27b', 1)
    d1 = json.loads(fixed)
    io.open(p1, "w", encoding="utf-8", newline="").write(fixed)
    print("machine-health.json: element separator inserted, %d elements, JSON valid" % len(d1))

def split_conflict(text):
    a = text.find("<<<<<<< Updated upstream\n")
    b = text.find("||||||| Stash base\n", a)
    c = text.find("=======\n", b)
    d = text.find(">>>>>>> Stashed changes\n", c)
    assert -1 not in (a, b, c, d), "conflict markers not found"
    pre = text[:a]
    upstream = text[a + len("<<<<<<< Updated upstream\n"):b]
    stashed = text[c + len("=======\n"):d]
    post = text[d + len(">>>>>>> Stashed changes\n"):]
    return pre, upstream, stashed, post

p2 = "results/_r686bmb_d19_check.json"
t2 = io.open(p2, encoding="utf-8").read()
if "<<<<<<<" in t2:
    out = []
    rest = t2
    while "<<<<<<< Updated upstream" in rest:
        pre, up, st, post = split_conflict(rest)
        out.append(pre)
        out.append(st)  # stashed side = bm-c live face, ts-newer-wins
        rest = post
    out.append(rest)
    resolved2 = "".join(out)
    d = json.loads(resolved2)
    assert d["machine"] == "bm-c", "d19_check resolved side must be the bm-c face"
    io.open(p2, "w", encoding="utf-8", newline="").write(resolved2)
    print("d19_check: STASHED (bm-c) side kept, JSON valid, wm_dec", d["wm_decisions"][:8], "wm_ord", d["wm_orders"][:8])
else:
    d = json.loads(t2)
    print("d19_check: already resolved, machine =", d.get("machine"))
