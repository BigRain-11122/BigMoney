# -*- coding: utf-8 -*-
# r1102 post-build heals (both disclosed, same-window, fail-closed):
# H1 seat-MSG gate: W273 seat MSG swept to processed/ by r1101 closeout BEFORE this derive
#    window -- inbox path last-touch = sweep commit. New gate = seat commit 39e1bb32f1
#    carries the MSG name (machine-found by _r1102bmc_facts_gather.py, zero transcription).
# H2 floor-raise format: the clone's FLOOR FAIL raise lost its third format arg -- restored
#    verbatim ("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c, f)).
import io
p = r"results\_w273bmc_prereg_derive.py"
t = io.open(p, encoding="utf-8", newline="").read()
old1 = '_seat_log = git_out(["log", "-1", "--format=%h", "--", "fleet/inbox/MSG-20261018-211x-bmc-w273-seat.md"])\nassert _seat_log == "39e1bb32f1", "W273 seat MSG landed by unexpected commit: %s" % _seat_log'
new1 = '_seat_files = git_out(["show", "--name-only", "--format=", "39e1bb32f1"])\nassert "MSG-20261018-211x-bmc-w273-seat.md" in _seat_files, "W273 seat MSG not carried by seat commit 39e1bb32f1: %r" % _seat_files[:200]'
assert t.count(old1) == 1, "H1 anchor count=%d" % t.count(old1)
t = t.replace(old1, new1)
old2 = 'raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c))'
new2 = 'raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))'
assert t.count(old2) == 1, "H2 anchor count=%d" % t.count(old2)
t = t.replace(old2, new2)
# H3 se_mu-chain MUST entry: the general value needles + W-chain rolled the old MUST entry into
# the shifted-stale form; the authoritative true-history form is the S5 POST_LEG target
# (W267 0.000320 .. W272 0.000317 measured + W273 projection 0.000317) -- MUST aligned verbatim.
old3 = "→W267 **0.000321**→W268 **0.000320**→W269 **0.000320**→W270 **0.000318**→W271 **0.000318**→W272 **0.000317**→W273 投影 0.000317】"
new3 = "→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 投影 0.000317】"
assert t.count(old3) == 1, "H3 anchor count=%d" % t.count(old3)
t = t.replace(old3, new3)
io.open(p, "w", encoding="utf-8", newline="").write(t)
compile(t, p, "exec")
print("POSTHEALS-OK")
