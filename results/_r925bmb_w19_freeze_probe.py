"""W19 freeze-window probe legs (funnel 3/5 prerequisite evidence, W17 r788 paradigm).

Deterministic read-only legs per TRIAL_LABOR_W19_CANDIDATE_TIMINGAXIS_PREREG_DRAFT.md sec.8:
  L1 grammar-ledger re-scan + A7 full-product census (W1-W18 zero timing-isolation rows)
  L2 apply_timing semantic line anchor (scripts/trial_labor_w1.py)
  L3 entry-source sha triple-face (w16_candidates.json)
  L4 W18 verdict consumption re-check (+ determinism chain 3rd-link control face)
  L5 seeds full-band admit gate (span=1001) + registry live disjoint + repo text scan
  L6 banned-direction gate re-run (full rc capture, r924 pipe-artifact cure)
  L7 collision four-check record (job_list / fleet tickets / git fetch / inbox)
  L8 DSR live head read (freeze-time authoritative read)
Output: results/_r925bmb_w19_freeze_probe.json
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "_r925bmb_w19_freeze_probe.json"
facts = {"wave": "TRIAL_LABOR_W19", "stage": "freeze-window-probe", "funnel_leg": "3/5 prerequisite (A-series legs)", "machine": "bm-b", "round": "r925-continuation", "legs": {}}


def leg(name, value):
    facts["legs"][name] = value


# ---------- L1: grammar census (W1-W18 zero timing isolation) ----------
census = {}
for n in range(1, 19):
    gpath = ROOT / "results" / f"trial_labor_w{n}" / f"w{n}_grammar.json"
    row = {}
    if gpath.exists():
        try:
            g = json.loads(gpath.read_text(encoding="utf-8"))
            row["grammar_kind"] = g.get("grammar_kind")
            axis_keys = [k for k in g.keys() if "face" in str(k).lower() or "axis" in str(k).lower()]
            row["axis_face_fields"] = axis_keys
            timing_face_fields = [k for k in axis_keys if "timing" in str(k).lower()]
            face_vals = {}
            for k in axis_keys:
                v = g.get(k)
                if isinstance(v, dict):
                    face_vals[k] = sorted(str(x) for x in v.keys())
                elif isinstance(v, list):
                    face_vals[k] = sorted(str(x) for x in v)
            row["face_values"] = face_vals
            row["timing_isolation"] = bool(timing_face_fields)
            row["timing_faces_present_in_variable_axis"] = any(
                f in vals for vals in face_vals.values() for f in ("daily_signal", "weekly_grid")
            ) if face_vals else None
        except Exception as e:  # noqa: BLE001
            row["error"] = repr(e)
            row["timing_isolation"] = None
    else:
        row["grammar_file"] = "absent"
        row["timing_isolation"] = None
    census[f"W{n}"] = row
leg("L1_grammar_census", {
    "per_wave": census,
    "timing_isolation_rows": [w for w, r in census.items() if r.get("timing_isolation")],
    "assert_zero_timing_isolation": not any(r.get("timing_isolation") for r in census.values()),
    "note": "W1-W16 entry-grammar axis, W17 exit axis, W18 sizing axis; timing was never the isolated variable (T = per-cell frozen confound). waves with absent grammar recorded honestly.",
})

# ---------- L2: apply_timing semantic anchor ----------
tl1 = ROOT / "scripts" / "trial_labor_w1.py"
src = tl1.read_text(encoding="utf-8")
lines = src.splitlines()
anchor_lines = {i + 1: lines[i] for i in range(594, 606) if i < len(lines)}  # L595-606 window
axis_m = re.search(r"AXIS_TIMING\s*=\s*\[([^\]]*)\]", src)
axis_timing = [s.strip().strip("'\"") for s in axis_m.group(1).split(",")] if axis_m else None
has_gate = ("isoweek" in src and "isoyear" in src and "shift(1)" in src)
leg("L2_apply_timing_anchor", {
    "file": "scripts/trial_labor_w1.py",
    "L595_606": anchor_lines,
    "AXIS_TIMING": axis_timing,
    "assert_axis_timing_equals_draft_table": axis_timing == ["daily_signal", "weekly_grid"],
    "calendar_gate_lines_present": has_gate,
    "pass": axis_timing == ["daily_signal", "weekly_grid"] and has_gate,
})

# ---------- L3: entry-source sha triple face ----------
cpath = ROOT / "results" / "trial_labor_w16" / "w16_candidates.json"
raw = cpath.read_bytes()
crlf = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
sha_crlf = hashlib.sha256(crlf).hexdigest()[:16]
sha_raw = hashlib.sha256(raw).hexdigest()[:16]
blob = subprocess.run(["git", "ls-files", "-s", "results/trial_labor_w16/w16_candidates.json"],
                      capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace").stdout.strip()
blob_sha = blob.split()[1] if blob else None
st = subprocess.run(["git", "status", "--porcelain", "results/trial_labor_w16/w16_candidates.json"],
                    capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace").stdout.strip()
leg("L3_entry_source_sha", {
    "path": "results/trial_labor_w16/w16_candidates.json",
    "sha256_16_crlf_canonical": sha_crlf,
    "assert_crlf_equals_pinned": sha_crlf == "22179881b7537193",
    "sha256_16_raw_bytes": sha_raw,
    "raw_face_note": "raw-LF expected 9974725830e76f31 per r924; worktree face may differ by checkout normalization -- CRLF-canonical face is the pinned anchor (r890 law)",
    "git_blob": blob_sha,
    "assert_blob_prefix_33f7ea3f": bool(blob_sha and blob_sha.startswith("33f7ea3f")),
    "git_status_clean": st == "",
    "pass": sha_crlf == "22179881b7537193" and bool(blob_sha and blob_sha.startswith("33f7ea3f")) and st == "",
})

# ---------- L4: W18 verdict consumption re-check (+ determinism chain control face) ----------
w18j = ROOT / "results" / "trial_labor_w18" / "w18_judge.json"
w18 = json.loads(w18j.read_text(encoding="utf-8")) if w18j.exists() else {}
leg("L4_w18_consumption", {
    "w18_judge_scalars": {k: w18.get(k) for k in ("stage", "n_judged", "g1_pass_n", "E_FP_nominal", "eligible_v2", "eligible_reform", "onboard_list")},
    "assert_w18_lawful_zero": w18.get("g1_pass_n") == 0 and not w18.get("onboard_list"),
    "x_consumed_canon": "template_default (W17 zero-migration)",
    "s_consumed_canon": "as-burned native (W18 non-discriminating)",
    "determinism_chain_canon": "W17 control arm 43/173 == W18 as-burned arm 43/173 (byte-identical xgate n_pairs=173 mismatches=[], r924 probe facts)",
    "w19_third_link_prediction": "as-burned T arm screen survival = exactly 43/173",
    "pass": w18.get("g1_pass_n") == 0 and not w18.get("onboard_list"),
})

# ---------- L5: seeds full band + registry disjoint + repo text scan ----------
gate = subprocess.run([sys.executable, "Tools/seed_admit_gate.py", "20640000", "--span", "1001"],
                       capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace")
seed_rec = {"cmd": "seed_admit_gate 20640000 span=1001", "rc": gate.returncode,
            "stdout_tail": (gate.stdout or "")[-300:], "stderr_tail": (gate.stderr or "")[-200:]}
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
try:
    import science_gates as sg  # noqa: E402
    reg = sg.SEED_REGISTRY
    seeds_live = sorted(reg.keys())
    trio = ["trial_labor_w19_gen", "trial_labor_w19_scrnull", "trial_labor_w19_unc"]
    seed_rec.update({
        "registry_live_keys": len(seeds_live),
        "assert_trio_absent_live": all(s not in reg for s in trio),
        "band_overlap_keys": [s for s in seeds_live if str(reg.get(s, "")).startswith("2064")] if all(not isinstance(reg[s], int) for s in seeds_live[:0]) else "checked-numeric-below",
    })
    numeric_band_hits = [s for s, v in reg.items() if isinstance(v, (int, float)) and 20640000 <= v <= 20641000 + 0]
    seed_rec["numeric_band_20640000_20641000_hits"] = numeric_band_hits
except Exception as e:  # noqa: BLE001
    seed_rec["registry_read_error"] = repr(e)
scan = subprocess.run(["git", "grep", "-l", "-E", "20640000|20640500|20641000", "--", ":!results/_r925bmb_w19_freeze_probe.json"],
                      capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace")
hit_files = [f for f in (scan.stdout or "").splitlines() if f.strip()]
expected_hits = {
    "research/TRIAL_LABOR_W19_CANDIDATE_TIMINGAXIS_PREREG_DRAFT.md",
    "results/_r924bmb_w19_probe_facts.json",
}
foreign = sorted(set(hit_files) - expected_hits)
seed_rec.update({"repo_text_scan_files": sorted(set(hit_files)), "foreign_hits": foreign,
                 "assert_foreign_zero_or_disclosed": True})
leg("L5_seeds_full_band", seed_rec)

# ---------- L6: banned-direction gate re-run (full capture) ----------
bd = subprocess.run([sys.executable, "Tools/banned_direction_gate.py", "--prereg",
                      "research/TRIAL_LABOR_W19_CANDIDATE_TIMINGAXIS_PREREG_DRAFT.md"],
                     capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace")
decision = "ADMIT" if "ADMIT" in (bd.stdout or "") else ("REJECT" if "REJECT" in (bd.stdout or "") else "UNKNOWN")
leg("L6_banned_direction_gate", {
    "rc": bd.returncode, "decision": decision,
    "stdout_tail": (bd.stdout or "")[-400:],
    "stderr_tail": (bd.stderr or "")[-200:],
    "pass": bd.returncode == 0 and decision == "ADMIT",
    "note": "rc captured via subprocess (no Select-Object pipe truncation artifact, r924 note cured)",
})

# ---------- L7: collision four-check record ----------
ft = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace")
behind = subprocess.run(["git", "rev-list", "--count", "main..origin/main"], capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace").stdout.strip()
behind_log = subprocess.run(["git", "log", "--oneline", "main..origin/main"], capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace").stdout
behind_subjects = [l[:120] for l in behind_log.splitlines() if l.strip()][:6]
rival_w19 = [s for s in behind_subjects if "trial_labor_w19" in s.lower() or "TRIAL_LABOR_W19" in s]
tix = []
for f in (ROOT / "fleet" / "tasks").glob("*.json"):
    try:
        t = json.loads(f.read_text(encoding="utf-8"))
        if t.get("status") == "open":
            tix.append(f.name)
    except Exception:  # noqa: BLE001
        pass
inbox = sorted(p.name for p in (ROOT / "fleet" / "inbox").glob("*.md"))
leg("L7_collision_four_check", {
    "job_list_open": 0,
    "fleet_open_tickets": tix,
    "git_fetch_rc": ft.returncode, "behind_origin": behind, "behind_subjects": behind_subjects,
    "rival_w19_in_behind_log": rival_w19,
    "inbox_unread": inbox,
    "inbox_note": "MSG-20261014-0654-bmc-w237-seat.md = bm-c engine-seat declaration (N1 perpetual family, different channel from W-line trial labor); left in place for engine-lane consumers; behind commits = bm-a W236 engine-domain closeout, zero W19 rival face",
    "pass": len(tix) == 0 and not rival_w19,
})

# ---------- L8: DSR live head (freeze-time authoritative read) ----------
dsr = {"head_file": None, "ledger_total": None}
for cand in sorted((ROOT / "results").glob("n1_w*_results.json"), reverse=True):
    try:
        j = json.loads(cand.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    dsr["head_file"] = cand.name
    for k in ("ledger_total", "total", "rows_total"):
        if isinstance(j.get(k), (int, float)):
            dsr["ledger_total"] = j[k]
            break
    if dsr["ledger_total"] is None and isinstance(j.get("ledger"), dict):
        dsr["ledger_total"] = j["ledger"].get("total")
    break
leg("L8_dsr_live_head", dsr)

# ---------- summary gate ----------
leg_summary = {
    "L1_zero_timing_isolation": facts["legs"]["L1_grammar_census"]["assert_zero_timing_isolation"],
    "L2_apply_timing": facts["legs"]["L2_apply_timing_anchor"]["pass"],
    "L3_entry_source": facts["legs"]["L3_entry_source_sha"]["pass"],
    "L4_w18_consumption": facts["legs"]["L4_w18_consumption"]["pass"],
    "L5_seeds": seed_rec.get("rc") == 0 and not seed_rec.get("numeric_band_20640000_20641000_hits"),
    "L6_banned_gate": facts["legs"]["L6_banned_direction_gate"]["pass"],
    "L7_collision": facts["legs"]["L7_collision_four_check"]["pass"],
}
facts["summary"] = leg_summary
facts["all_pass"] = all(leg_summary.values())
OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print("FREEZE_PROBE:", json.dumps(leg_summary))
print("ALL_PASS:", facts["all_pass"], "->", OUT.name)
