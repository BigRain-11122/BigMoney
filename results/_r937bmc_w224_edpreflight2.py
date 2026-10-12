# -*- coding: utf-8 -*-
# r937 bm-c: W224 editor derive preflight ROUND 2 -- corrected live scan (full protect
# needles) + full-context dumps of narrative anchors (r909 physical-byte law). Zero writes.
import io

t = io.open(r"results\_w223bmc_freeze_edits.py", encoding="utf-8").read()

P3 = "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg"
P2 = "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg"
P1 = "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220 legs"
P8 = "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220)"
P9 = "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg + own W221 leg"
P4 = "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78])"
P5 = "[211, 212, 213, 214, 215, 216, 217, 218, 219, 220]"
P7 = '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1'

def q(s):
    return "'" + s + "'"

keep = "    # --- W216 materializer face"
P6full = (
    "assert n1_t4.count(" + q(keep) + ") == 1  # prior block kept (W216 splice landed r914 window)\n"
    "assert n1_t4.count(" + q(keep.replace("W216", "W217")) + ") == 1  # prior block kept (W217 splice landed r916 window)\n"
    "assert n1_t4.count(" + q(keep.replace("W216", "W218")) + ") == 1  # prior block kept (W218 splice landed r918 window)\n"
    "assert n1_t4.count(" + q(keep.replace("W216", "W219")) + ") == 1  # prior block kept (W219 splice landed r920 window)\n"
    "assert n1_t4.count(" + q(keep.replace("W216", "W220")) + ") == 1  # prior block kept (W220 splice landed r923 window)\n"
    "assert n1_t4.count(" + q(keep.replace("W216", "W221")) + ") == 1  # prior block kept (W221 splice landed r927 window)\n"
    "assert n1_t4.count(" + q(keep.replace("W216", "W222")) + ") == 1  # prior block kept (W222 splice landed r931 window)"
)
print("P6full count:", t.count(P6full))

t2 = t
for s in [P3, P2, P1, P8, P9, P4, P5, P6full, P7]:
    t2 = t2.replace(s, "\x00PH\x00")
live = {}
for w in range(210, 227):
    live["W%d" % w] = t2.count("W%d" % w)
    live["w%d" % w] = t2.count("w%d" % w)
print("LIVE:", {k: v for k, v in live.items() if v})
print()

def dump(tag, s, ctx=200, maxn=4):
    print("=== %s ===" % tag)
    n = 0
    st = 0
    while True:
        i = t.find(s, st)
        if i < 0:
            break
        print(repr(t[max(0, i - 40):i + len(s) + ctx])[:430])
        n += 1
        st = i + 1
        if n >= maxn:
            break
    print()

dump("hdr_full", "2026-10-12 17:3x", 340)
dump("prereg_note", "in the r933 window", 420)
dump("W224p", "W224p", 150)
dump("w224_next_narr", "W224", 120)
dump("upstream_1430", "MSG-20261012-1430", 140)
dump("seat_origin", "8f2d79147", 150)
dump("chain_line", "six-gate POST-HOC", 160)
dump("below222", "below 222", 140)
dump("fin4_15x", "15:4x", 90)
dump("ws_tail", "_estate_ws[-10:]", 120)
dump("m221", "m221", 90)
dump("twelfth", "twelfth consecutive", 130)
dump("r929_seat", "r929 seat window", 150)
dump("selftest_cmt", "at selftest time", 160)
dump("get222", "get(222)", 110)
dump("wave223c", "wave 223: ", 110)
dump("wave223eq", "wave 223 = ", 110)
