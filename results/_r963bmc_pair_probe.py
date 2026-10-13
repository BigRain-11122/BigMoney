# -*- coding: utf-8 -*-
# r963 bm-c continuation pair probe: dump exact template regions from the
# committed _w229bmc_freeze_edits.py (48,884B) so the W230 editor pairs are
# authored from ACTUAL template bytes (E63 live-import law, zero transcription).
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w229bmc_freeze_edits.py")
t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 48884, f"template length drift: {len(t)} != 48884"
lines = t.split("\n")

def find_all(pat):
    return [i for i, l in enumerate(lines) if re.search(pat, l)]

def dump(name, pat, before=2, after=6, maxhits=4):
    hits = find_all(pat)
    out = {"name": name, "pattern": pat, "hits": len(hits), "blocks": []}
    for h in hits[:maxhits]:
        lo = max(0, h - before); hi = min(len(lines), h + after + 1)
        out["blocks"].append({"line": h + 1, "text": "\n".join(lines[lo:hi])})
    return out

probes = [
 dump("header", r"freeze window \(upstream W1", 1, 10, 1),
 dump("present_prose", r"# present \(W2", 1, 8, 1),
 dump("lineage", r"# Lineage: _w229bmc_freeze_edits", 0, 4, 1),
 dump("atomic_triple", r"ATOMIC TRIPLE absorbed", 1, 5, 1),
 dump("struct_choice_a", r"STRUCTURAL CHOICE \(vs the W228 editor\)", 0, 10, 1),
 dump("struct_choice_b", r"STRUCTURAL CHOICE: extract the estate", 0, 8, 1),
 dump("gate05", r'w227_out_path = os\.path\.join', 0, 3, 1),
 dump("gate05_present", r'finalize products present', 0, 1, 2),
 dump("kept_first_last", r"--- W228 materializer face", 0, 1, 2),
 dump("kept_w209", r"--- W209 materializer face", 0, 1, 1),
 dump("liveness", r"liveness_anchors", 0, 3, 1),
 dump("legdefs", r"w226_leg = \[", 0, 6, 1),
 dump("leg227", r"w227_leg = \[", 0, 6, 1),
 dump("leg228", r"w228_leg = \[", 0, 6, 1),
 dump("asm", r"block = EOL\.join\(hdr\)", 0, 2, 1),
 dump("receipt_upstream", r'"w228_upstream"', 0, 6, 1),
 dump("receipt_transitive", r'"w227_transitive"', 0, 3, 1),
 dump("receipt_note", r'"note": "prereg derived\+committed', 0, 3, 1),
 dump("receipt_parity", r"full-span estate W138\.\.W206 \(69 rows, r858 absorb generation\) \+ W211", 0, 3, 1),
 dump("receipt_family6", r"family-6 gate carried forward", 0, 3, 1),
 dump("receipt_ordinal", r"probe_receipt_bmc_ordinal_face", 0, 2, 1),
 dump("rows_owned", r"59th owned", 1, 3, 1),
 dump("cfg_asserts", r'PERPETUAL-N1-W229', 0, 1, 6),
 dump("m_cut", r"row leg not found inside", 0, 2, 1),
 dump("par_sec", r"assert par_sec\.count", 0, 4, 1),
 dump("estate_ws", r"_estate_ws\[", 0, 4, 1),
 dump("par_full", r"assert par_full\.count", 0, 3, 2),
 dump("post_edit_gate", r"post-edit gate", 0, 3, 1),
 dump("seat_prose_inline", r"MSG-20261013-0855-bmc, executed", 0, 3, 1),
 dump("seat_prose_block", r"MSG-20261013-0720-bmc, executed bm-c r957", 0, 7, 2),
 dump("probe_window_faces", r"probe receipt @ r959 window", 0, 2, 3),
 dump("ordinal_faces", r"EIGHTY-NINTH per probe receipt|staircase EIGHTY-NINTH", 0, 1, 4),
 dump("wave_first_free", r"wave 229 = first free number", 0, 4, 1),
 dump("downstream_seat", r"downstream W230 seat", 0, 1, 3),
 dump("transitive_deps", r"finalize are transitive deps", 0, 1, 1),
]

outp = os.path.join(HERE, "_r963bmc_pair_probe.json")
open(outp, "w", encoding="utf-8").write(json.dumps(probes, indent=1, ensure_ascii=False))
print("WROTE", outp, "probes:", len(probes))
for p in probes:
    print(f"[{p['name']}] hits={p['hits']}")
