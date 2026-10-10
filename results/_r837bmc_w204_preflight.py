# r837 bm-c W204 phase-2 preflight (zero-write) -- r787 E48 law: all
# anchor counts asserted BEFORE any live edit; r909 law: rolling-pair
# old sides extracted via find+repr bytes, never visual transcription.
# CRLF-aware: multi-line anchors built with the file's physical EOL.
import json, hashlib, os, sys

PF = r"scripts\perpetual_faces.py"
N1 = r"scripts\perpetual_faces_n1.py"
out = {}

def probe(path, name):
    b = open(path, "rb").read()
    t = b.decode("utf-8")
    d = {"bytes": len(b), "sha16": hashlib.sha256(b).hexdigest()[:16],
         "crlf_count": t.count("\r\n"),
         "lf_only_lines": t.count("\n") - t.count("\r\n")}
    out[name] = d
    return t

pf_t = probe(PF, "pf")
n1_t = probe(N1, "n1")
EOL = "\r\n" if out["n1"]["crlf_count"] > out["n1"]["lf_only_lines"] else "\n"
PF_EOL = "\r\n" if out["pf"]["crlf_count"] > out["pf"]["lf_only_lines"] else "\n"
out["n1_eol"] = EOL; out["pf_eol"] = PF_EOL

def cnt(t, s):
    return t.count(s)

checks = []
M = lambda s: s.replace("\n", EOL)          # n1 multi-line anchor
MP = lambda s: s.replace("\n", PF_EOL)      # pf multi-line anchor

# --- anchor 1: pf W203 row head (unique, single line) ---
a1 = '    203: {"a": (461_404, 463_403), "b_exit": (463_404, 463_603),'
checks.append(("pf_w203_row_head", cnt(pf_t, a1), 1))
# --- anchor 2: pf N1_BANDS closing right after W203 row (CRLF) ---
a2 = MP('         "engine_owner": "bm-a"},\n}\n# v1 + ext(wave-1) in-use bands')
checks.append(("pf_bands_close_after_w203", cnt(pf_t, a2), 1))
# --- anchor 3: n1 WAVE_CONFIGS closing (CRLF) ---
a3 = M('                       }\nPREREG = WAVE_CONFIGS[2]["prereg"]')
checks.append(("n1_cfg_close", cnt(n1_t, a3), 1))
# --- anchor 4: n1 T-141 lane face marker (4-space form, unique per r787) ---
a4 = '    # --- T-141 s2 lane face'
checks.append(("n1_t141_marker", cnt(n1_t, a4), 1))
# --- anchor 5: n1 print T-141 tail fragment (single physical line) ---
a5 = '          "+ T-141 s2 "'
checks.append(("n1_print_t141", cnt(n1_t, a5), 1))
# --- anchor 6: W203 materializer block start marker ---
a6 = '    # --- W203 materializer face'
checks.append(("n1_w203_block_marker", cnt(n1_t, a6), 1))
# --- anchor 7: W204 must not exist anywhere yet ---
checks.append(("pf_w204_absent", cnt(pf_t, '204: {"a"'), 0))
checks.append(("n1_cfg_w204_absent", cnt(n1_t, '"PERPETUAL-N1-W204"'), 0))
checks.append(("n1_block_w204_absent", cnt(n1_t, "W204 materializer face"), 0))
# --- extraction: W203 block parity section (recent estate rows) ---
w203_start = n1_t.find(a6)
t141_pos = n1_t.find(a4)
assert 0 < w203_start < t141_pos, "W203 block before T-141 marker"
blk = n1_t[w203_start:t141_pos]
par_start_marker = "        # registered row parity (r307 pinned constants, recent estate)"
par_pos = blk.find(par_start_marker)
disj_marker = "        # prior-wave disjointness W2..W202 (single state: all"
disj_pos = blk.find(disj_marker)
assert 0 <= par_pos < disj_pos, "parity section inside W203 block"
par_sec = blk[par_pos:disj_pos]
out["w203_parity_section_bytes"] = len(par_sec)
out["w203_parity_row_asserts"] = par_sec.count("assert pf.N1_BANDS[")
out["w203_parity_last_row"] = par_sec.rstrip().rsplit("N1_BANDS[", 1)[1].split("]")[0]
# --- extraction: W203 cfg entry close (CRLF) ---
w203_entry_close = M('"engine_owner": "bm-a"},\n                       }')
checks.append(("n1_w203_entry_close", cnt(n1_t, w203_entry_close), 1))
# --- W203 block final-fragment (single line) ---
frag_end = '            "W203 per-wave prereg missing (materializer requirement)"'
checks.append(("n1_w203_prereg_missing_frag", cnt(n1_t, frag_end), 1))
# --- pf row-to-close ordering ---
pf_row_pos = pf_t.find(a1)
pf_close_pos = pf_t.find(a2)
out["pf_row_pos"] = pf_row_pos; out["pf_close_pos"] = pf_close_pos
checks.append(("pf_row_before_close_order", 1 if 0 < pf_row_pos < pf_close_pos else 0, 1))
# --- dump physical fragments for the live editor (repr-safe) ---
out["anchor_reprs"] = {
    "a2_pf_close": repr(a2)[:400],
    "a3_n1_cfg_close": repr(a3)[:200],
    "w203_entry_close": repr(w203_entry_close)[:200],
}

out["checks"] = [{"name": n, "got": g, "want": w, "ok": g == w} for n, g, w in checks]
out["all_ok"] = all(c["ok"] for c in out["checks"])
print(json.dumps(out, indent=1))
sys.exit(0 if out["all_ok"] else 2)
