# -*- coding: utf-8 -*-
# r934 bm-c: W223 editor derive preflight ROUND 2 -- full context dumps of
# narrative anchors (r909 physical-byte law). Zero writes.
import io, json, re

SRC = r"results\_w222bmc_freeze_edits.py"
t = io.open(SRC, encoding="utf-8").read()

def dump_all(tag, s, ctx=170):
    out = []
    start = 0
    while True:
        i = t.find(s, start)
        if i < 0:
            break
        out.append(t[max(0, i-60):i+len(s)+ctx].replace("\n", "\\n"))
        start = i + 1
    print(f"=== {tag} ({len(out)} hits) ===")
    for o in out:
        print(repr(o)[:480])
    print()

dump_all("r931_freeze_window", "r931 freeze window")
dump_all("r927_freeze_window", "r927 freeze window")
dump_all("r927_window_editor", "r927 window editor")
dump_all("msg_1225", "MSG-20261012-1225")
dump_all("fin_time_141x", "14:1x", 80)
dump_all("chain_honest", "dead-window splice + POST-HOC six-gate heal chain, honest note", 60)
dump_all("prereg_bundle", "in the r930 window", 400)
dump_all("repair_note", "r927 splice (dead-window continuation)", 260)
dump_all("r925_line", "r930 prereg derived + r931 freeze-window bundle", 120)
dump_all("r927_bundle", "r931 freeze-window bundle", 120)
dump_all("hdr_lines", "2026-10-12 15:2x bm-c r931 freeze window", 300)
dump_all("upstream_landed_note", "W221 finalize one-pass", 200)
dump_all("eleventh", "eleventh consecutive", 120)
dump_all("ord_third", "EIGHTY-THIRD", 120)
dump_all("w223p", "W223p", 100)
dump_all("trans_chain", "ledger 907,789", 200)
dump_all("below221", "below 221", 120)
dump_all("selftest_cmt", "range(17, 222) at selftest time", 120)
dump_all("arith_a222", "arith_a222", 60)

w222 = json.load(open(r"results\perpetual_faces\n1_w222_results.json", encoding="utf-8"))
print("w222 finalize keys:", {k: w222.get(k) for k in ("generated", "wave", "asof", "ts", "timestamp", "cutoff") if k in w222})
lg = (w222.get("science_gates") or {})
print("w222 science_gates keys:", list(lg.keys())[:10])
fr = json.load(open(r"results\_w222bmc_freeze_receipt.json", encoding="utf-8"))
print("w222 freeze receipt top keys:", list(fr.keys())[:20])
