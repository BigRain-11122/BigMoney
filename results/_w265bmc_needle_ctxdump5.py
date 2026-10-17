# -*- coding: utf-8 -*-
# r1084 bm-c: W265 derive ctxdump5 (remaining unmeasured narrative faces)
import io
t = io.open("results/_w264bmc_freeze_edits.py", encoding="utf-8", newline="").read()
FACES = [
    "(R263: ", "(R264: ",
    "bm-a (upstream seat honored)", "owner=bm-a seat honored",
    "W263 bm-a own-wave full cycle r1038",
    "derived from the committed W263 freeze-edits template",
    "editor template",
    "bm-a splice generation r1038 window",
    "verified r1039/r1040",
    "the bm-a r1038 splice window",
    "(bm-a r1038",
    "cycle COMPLETE bm-a r1038+r1040 closeout 19:2x",
    "bm-a own seat executed at the bm-a r1038 splice window",
    "finalize one-pass bm-a r1039",
    "itself r1075; queue-head", "(r1075, queue-head",
    "r1075 BEFORE this freeze", "(r1075 MSG-", "dd5fd438e r1075,",
    "r1076 commit", "# r1076 window", "bm-c r1076 window", "authored 20:1x",
    "wave 264 engine_owner=bm-c", '"wave 264: "', "wave 264 = first free number",
    'N1_BANDS[") == 121,', "!= 121", 'N1_BANDS[") == 52', 'N1_BANDS[") == 34',
    "W261_W262_W263_bands_respected", "bm-a five-face freeze upstream seat",
    "row not landed as declared (bm-a seat owner expected)",
    '"machine": "bm-c"', "bm-c own-seat freeze window",
    "n1_w263_results", "n1_w264_results", "n1_w264", "n1_w263",
]
for k in FACES:
    print("FACE %-62r = %d" % (k[:62], t.count(k)))
lines = t.split("\n")
for i, l in enumerate(lines):
    if "repair_chain_note" in l or "(R26" in l:
        print("CTX L%d: %s" % (i + 1, l.strip()[:210]))
    if "verified r1039" in l or "derived from the committed" in l:
        print("CTX2 L%d: %s" % (i + 1, l.strip()[:210]))
    if "wave 264 engine_owner" in l or '"wave 264: "' in l:
        print("CTX3 L%d: %s" % (i + 1, l.strip()[:210]))
