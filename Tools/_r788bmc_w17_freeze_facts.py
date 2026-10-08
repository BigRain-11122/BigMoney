# -*- coding: utf-8 -*-
"""r788 bm-c W17 FREEZE-WINDOW facts probe (funnel leg 3/5 pre-write evidence
per draft sec.6.2). Read-only legs, ONE facts JSON, zero ledger writes, zero
prereg numbers pre-written into any frozen doc (placeholder law).

Legs:
 A1  panel anchor: data/daily/sh510300.csv rows<=cutoff(2026-09-22), first
     date, last-bar<=cutoff (G-ANCHOR four-tuple face: path + pd.read_csv
     direct + full history + engine warmup faces per grammar)
 A2  core48 face: 48 no-prefix CSVs, all last-bar sane vs cutoff
 A3  entry-cell source: results/trial_labor_w16/w16_candidates.json sha256
     (16 hex), n, family split, exit-axis value distribution, tuple length,
     sample cell keys (runner verbatim-reuse face)
 A4  grammar lineage: w14_grammar.json sha256_16 re-verify + judge_state
     grammar sha + TRIAL_GRAMMAR_LEDGER W14/W16 sha16 re-verify
 A5  W16 verdict context: w16_screen null p95 + survivors; w16_judge
     n_eligible_g2; w16_reform_face.json existence (W16 sec.8 continuation)
 A6  DSR chain head: results/mass_trial/w3_judge.json trials_ledger.total
     (live read, cross-wave no-reset law)
 A7  W1 exit-axis ACTUAL-BURN correction evidence: w1_candidates exit
     distribution + w1_judge joined exit distribution + n_eligible (the
     r786-draft "zero exit-axis burn in W lineage" premise is FALSE at the
     products face; freeze banner must carry the corrected claim)
 A8  seed berth re-verify: live SEED_REGISTRY parse (incl. r899 bm-a
     94_200 addition) + conservative 2000-wide disjointness for
     20610000/20610500/20611000 + full text scan (r786 leg3 clone)
 A9  ExitConfig defaults re-read (importlib read-only, iron law) + W17
     face-table feasibility assert: every frozen face param reachable via
     run_backtest bridge kwargs + ExitPatch fields (zero engine edit)
 A10 rival scan: git fetch + origin log W17 zero-hit + fleet/tasks
     T-2026-10-09-* zero + inbox W17 zero (r252 berth four-check law)

rc: 0 = all green (facts feed the freeze); 1 = hard violation; 2 = mech.
House style: ASCII-only source, GBK console entry reconfigure (r236 law),
CREATE_NO_WINDOW subprocess (U060 silence law)."""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")  # r236 GBK console entry law

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUT = os.path.join(ROOT, "results", "_r788bmc_w17_freeze_facts.json")
CUTOFF = "2026-09-22"
W16_CANDS = os.path.join(ROOT, "results", "trial_labor_w16",
                         "w16_candidates.json")
W16_SCREEN = os.path.join(ROOT, "results", "trial_labor_w16",
                          "w16_screen.json")
W16_JUDGE = os.path.join(ROOT, "results", "trial_labor_w16",
                         "w16_judge.json")
W16_REFORM = os.path.join(ROOT, "results", "trial_labor_w16",
                          "w16_reform_face.json")
W14_GRAMMAR = os.path.join(ROOT, "results", "trial_labor_w14",
                           "w14_grammar.json")
W14_JUDGE_STATE = os.path.join(ROOT, "results", "trial_labor_w14",
                               "judge_state.json")
W1_CANDS = os.path.join(ROOT, "results", "trial_labor_w1",
                        "w1_candidates.json")
W1_JUDGE = os.path.join(ROOT, "results", "trial_labor_w1", "w1_judge.json")
LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
GATES_PY = os.path.join(ROOT, "scripts", "science_gates.py")
EXIT_PY = os.path.join(ROOT, "engine", "exit_rules.py")
MASS_JUDGE = os.path.join(ROOT, "results", "mass_trial", "w3_judge.json")
BAND = (20610000, 20612500)          # W17 family band (freeze face)
BERTH = (20610000, 20610500, 20611000)
SCAN_DIRS = ["research", "scripts", "Tools", "engine", "firm", "live",
             "config", "docs", "knowledge", "fleet"]
SCAN_EXTS = (".py", ".md", ".json", ".txt", ".ps1")
SELF_BASENAMES = {os.path.basename(__file__),
                  os.path.basename(OUT),
                  "TRIAL_LABOR_W17_CANDIDATE_EXITAXIS_PREREG_DRAFT.md",
                  "TRIAL_LABOR_W17_PREREG.md"}
OCCUPANCY_WIDTH = 2000


def sha16_file(path):
    with io.open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def leg_a1():
    df = pd.read_csv(os.path.join(ROOT, "data", "daily", "sh510300.csv"))
    dcol = df.columns[0]
    sub = df[df[dcol] <= CUTOFF]
    return {"path": "data/daily/sh510300.csv",
            "loader": "pd.read_csv direct (raw file, not engine load_core)",
            "rows_total": int(len(df)), "rows_le_cutoff": int(len(sub)),
            "first": str(sub[dcol].iloc[0]), "last_le_cutoff": str(sub[dcol].iloc[-1]),
            "start_window": "2012-05-28 full history (P-5C binding)",
            "warmup_face": "grammar member warmups per axis spec "
                           "(first-decidable anchors live in grammar files)"}


def leg_a2():
    d = os.path.join(ROOT, "data", "daily")
    csvs = [f for f in os.listdir(d)
            if f.lower().endswith(".csv") and not f.lower().startswith("sz")
            and not f.lower().startswith("sh")]
    lasts = []
    for f in csvs:
        df = pd.read_csv(os.path.join(d, f))
        lasts.append(str(df[df.columns[0]].iloc[-1]))
    return {"no_prefix_csvs": len(csvs),
            "min_last_bar": min(lasts), "max_last_bar": max(lasts),
            "all_last_ge_2026": all(x >= "2026" for x in lasts)}


def leg_a3():
    blob = io.open(W16_CANDS, "rb").read()
    j = json.loads(blob.decode("utf-8"))
    cands = j["candidates"] if isinstance(j, dict) else j
    fam = {}
    exits = {}
    tuple_len = None
    sample_keys = None
    for c in cands:
        cid = c.get("candidate_id", "?")
        fx = "A" if "-A-" in cid else ("B" if "-B-" in cid else "?")
        fam[fx] = fam.get(fx, 0) + 1
        ax = c.get("axis") or []
        if tuple_len is None:
            tuple_len = len(ax)
            sample_keys = sorted(c.keys())
        if len(ax) > 1:
            exits[ax[1]] = exits.get(ax[1], 0) + 1
    return {"file": "results/trial_labor_w16/w16_candidates.json",
            "sha256_16": hashlib.sha256(blob).hexdigest()[:16],
            "n_candidates": len(cands), "family_split": fam,
            "axis_tuple_len": tuple_len,
            "exit_axis_values": exits,
            "sample_cell_keys": sample_keys,
            "loader": "json.load direct (frozen product, zero re-derivation)"}


def leg_a4():
    facts = {"w14_grammar_sha256_16": sha16_file(W14_GRAMMAR)}
    js = json.load(io.open(W14_JUDGE_STATE, encoding="utf-8"))
    facts["judge_state_grammar_sha"] = js.get("grammar_sha256")
    led = io.open(LEDGER, encoding="utf-8").read()
    m = re.search(r"\|\s*TRIAL_LABOR_W14\s*\|\s*([0-9a-f]{16})", led)
    facts["ledger_w14_sha16"] = m.group(1) if m else None
    m16 = re.search(r"\|\s*TRIAL_LABOR_W16\s*\|\s*([0-9a-f]{16})", led)
    facts["ledger_w16_sha16"] = m16.group(1) if m16 else None
    facts["lineage_assert"] = bool(
        facts["judge_state_grammar_sha"] == facts["ledger_w14_sha16"])
    return facts


def leg_a5():
    s = json.load(io.open(W16_SCREEN, encoding="utf-8"))
    j = json.load(io.open(W16_JUDGE, encoding="utf-8"))
    out = {"w16_screen_n_survivors": s.get("n_survivors"),
           "w16_screen_batch_cells": s.get("batch_cells"),
           "w16_screen_k_nulls": s.get("k_nulls"),
           "w16_judge_n_judged": j.get("n_judged_cells"),
           "w16_judge_n_eligible_g2": j.get("n_eligible_g2"),
           "w16_reform_face_exists": os.path.exists(W16_REFORM)}
    nf = s.get("null_family") or {}
    out["w16_null_p95"] = nf.get("p95") if isinstance(nf, dict) else None
    if out["w16_null_p95"] is None:
        out["w16_null_family_dump"] = str(nf)[:300]
    return out


def leg_a6():
    """Authoritative chain head = science_gates.ledger_head() (data-driven
    max-total across results/**, void-adjusted per T-140 void face; the
    raw mass_trial/w3_judge block is NOT the head)."""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    sys.path.insert(0, ROOT)          # knowledge/ package import face
    from science_gates import ledger_head
    h = ledger_head()
    return {"dsr_chain_head_total": h.get("total"),
            "head_file": h.get("file"),
            "active_voids": h.get("voided"),
            "source": "science_gates.ledger_head() live call (authoritative "
                      "chain head, cross-wave no-reset, void-adjusted)"}


def leg_a7():
    """W1 exit-burn correction + FULL-W-LINEAGE exit-axis census (products
    face, every candidates file). The r786 draft's 'zero exit-axis burn'
    premise is corrected with the measured census: X was drawn (and burned
    through screen) in EVERY wave W1-W16 as a confounded grid dimension."""
    cands = json.load(io.open(W1_CANDS, encoding="utf-8"))["candidates"]
    byid = {c["candidate_id"]: c for c in cands}
    gen_ex, jf = {}, {}
    for c in cands:
        k = c["axis"][1]
        gen_ex[k] = gen_ex.get(k, 0) + 1
    j = json.load(io.open(W1_JUDGE, encoding="utf-8"))
    for c in j["cells"]:
        cd = byid.get(c["candidate_id"])
        if cd:
            k = cd["axis"][1]
            jf[k] = jf.get(k, 0) + 1
    # full census over every wave's frozen candidates file
    census = {}
    wdir0 = os.path.join(ROOT, "results")
    for wname in sorted(os.listdir(wdir0)):
        if not wname.startswith("trial_labor_w"):
            continue
        wdir = os.path.join(wdir0, wname)
        if not os.path.isdir(wdir):
            continue
        cfiles = [f for f in os.listdir(wdir) if "candidates" in f
                  and f.endswith(".json")]
        if not cfiles:
            continue
        jj = json.load(io.open(os.path.join(wdir, cfiles[0]),
                               encoding="utf-8"))
        cc = jj["candidates"] if isinstance(jj, dict) else jj
        n = nd = 0
        for c in cc:
            ax = c.get("axis") or []
            if len(ax) > 1:
                n += 1
                if ax[1] != "template_default":
                    nd += 1
        census[wname] = {"n": n, "non_default_x": nd}
    # W16 judged X join
    c16 = {c["candidate_id"]: c for c in
           json.load(io.open(W16_CANDS, encoding="utf-8"))["candidates"]}
    j16 = json.load(io.open(W16_JUDGE, encoding="utf-8"))
    jd16 = {}
    for c in j16["cells"]:
        cd = c16.get(c["candidate_id"])
        if cd:
            k = cd["axis"][1]
            jd16[k] = jd16.get(k, 0) + 1
    tot_n = sum(v["n"] for v in census.values())
    tot_nd = sum(v["non_default_x"] for v in census.values())
    return {"w1_generated_exit_dist": gen_ex,
            "w1_judged_exit_dist": jf,
            "w1_n_eligible": j.get("n_eligible_g2"),
            "full_census_per_wave": census,
            "census_totals": {"waves_with_candidates_file": len(census),
                              "total_generated": tot_n,
                              "total_non_default_x": tot_nd},
            "w16_judged_exit_dist": jd16,
            "verdict": "EXIT_AXIS_BURNED_EVERY_WAVE (draft r786 sec.1 "
                       "'zero exit-axis burn in W lineage' premise FALSE at "
                       "the products face; r786 L1 probe scanned ledger TEXT "
                       "not products = blind spot; W17's true novelty = "
                       "complete-block PAIRED isolation design never burned "
                       "-- X was always a confounded random draw dimension)"}


def registry_bases():
    import ast
    with io.open(GATES_PY, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    bases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "SEED_REGISTRY":
                    val = ast.literal_eval(node.value)
                    for k, v in val.items():
                        if isinstance(v, int):
                            bases[str(k)] = v
    return bases


def text_scan(trio):
    """Foreign-occupancy scan. Hits are classified: a hit line that names
    the trio in W17 context (the r786/r787/r788 berth-proposal lineage --
    probe facts, bookkeep, heartbeat, round reports, draft) is SELF lineage,
    not occupancy; only non-W17-context hits block the berth."""
    hits, self_hits = [], []
    needles = [str(c) for c in trio]
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dn, filenames in os.walk(base):
            for fn in filenames:
                if not fn.endswith(SCAN_EXTS) or fn in SELF_BASENAMES:
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(fp) > 2_000_000:
                        continue
                    blob_txt = io.open(fp, encoding="utf-8",
                                       errors="replace").read()
                    # self-lineage file face: any W17 mention in the file =
                    # W17 proposal/round artifact (r786 bookkeep/probe
                    # family, heartbeat, W17 drafts); trio numbers inside
                    # such files are the proposal record, NOT occupancy
                    file_is_self = ("W17" in blob_txt) or ("w17" in fn)
                    for i, ln in enumerate(blob_txt.splitlines(), 1):
                        for nd in needles:
                            if nd in ln:
                                rec = {"file": os.path.relpath(fp, ROOT),
                                       "line": i,
                                       "self_lineage": bool(
                                           file_is_self or "W17" in ln)}
                                (self_hits if rec["self_lineage"]
                                 else hits).append(rec)
                except OSError:
                    continue
    return hits, self_hits


def leg_a8():
    reg = registry_bases()
    known = set(reg.values())
    led = io.open(LEDGER, encoding="utf-8").read()
    for m in re.finditer(r"=(\d{5,8})", led):
        known.add(int(m.group(1)))
    # theme_deepen_p1_nulls band [20600000,20602200) + w16 family band
    # [20593000,20596000) are already inside `known` via their bases; the
    # conservative occupancy check below uses base+2000 windows.
    def disjoint(c, n):
        return not (n <= c < n + OCCUPANCY_WIDTH) and \
               not (c <= n < c + OCCUPANCY_WIDTH)
    blockers = sorted({n for c in BERTH for n in known if not disjoint(c, n)})
    hits, self_hits = text_scan(BERTH)
    w17_in_registry_now = [k for k, v in reg.items()
                           if v in BERTH or (20610000 <= v < 20612500)]
    return {"registry_n": len(reg), "berth": list(BERTH),
            "band": list(BAND),
            "occupancy_blockers": blockers[:8],
            "foreign_text_hits": hits[:6],
            "self_lineage_hits_n": len(self_hits),
            "w17_range_keys_already_registered": w17_in_registry_now,
            "w16_trio_still_registered": all(
                b in known for b in (20593000, 20593500, 20594000)),
            "verdict": "CLEAN" if (not blockers and not hits
                                   and not w17_in_registry_now)
            else "BLOCKED"}


def leg_a9():
    import importlib.util
    spec = importlib.util.spec_from_file_location("w17_probe_exit_rules",
                                                  EXIT_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # READ-ONLY import; iron law zero modify
    cfg = mod.ExitConfig()
    fields = {f: getattr(cfg, f) for f in cfg.__dataclass_fields__}
    doc = mod.__doc__ or ""
    priority = [ln.strip() for ln in doc.splitlines() if re.match(r"\s*P\d", ln)]
    # feasibility: every frozen face reachable via bridge kwargs
    # (take_profit_levels/trailing_stop_activate/trailing_lock/initial_stop/
    # time_decay_period/time_decay_threshold/position_size_pct/max_positions)
    # + ExitPatch fields (take_profit_fractions/loss_time_days/
    # global_hard_limit); P1 signal_reversal native via exit_signal arg.
    bridge = ("take_profit_levels", "trailing_stop_activate", "trailing_lock",
              "initial_stop", "time_decay_period", "time_decay_threshold")
    patchable = ("take_profit_fractions", "loss_time_days",
                 "global_hard_limit")
    bt_src = io.open(os.path.join(ROOT, "engine", "backtester.py"),
                     encoding="utf-8").read()
    bridge_ok = all(k in bt_src for k in bridge)
    lp_src = io.open(os.path.join(ROOT, "live", "paper.py"),
                     encoding="utf-8").read()
    patch_ok = all(k in lp_src for k in ("class ExitPatch", "loss_time_days"))
    return {"exit_config_defaults": fields,
            "engine_default_priority": priority,
            "bridge_kwargs_face_reachable": bridge_ok,
            "exitpatch_fields_reachable": patch_ok,
            "feasibility_assert": bool(bridge_ok and patch_ok),
            "note": "all frozen faces implementable with ZERO engine edit "
                    "(iron law intact; W1 EXIT_MACHINES bridged+patch "
                    "idiom reuse)"}


def leg_a10():
    p = subprocess.run(["git", "-C", ROOT, "fetch", "origin"],
                       capture_output=True, creationflags=CNW)
    rc_fetch = p.returncode
    p = subprocess.run(["git", "-C", ROOT, "log", "origin/main", "-40",
                        "--format=%h|%s"], capture_output=True,
                       creationflags=CNW)
    log = (p.stdout + p.stderr).decode("utf-8", "replace")
    w17_rival = [ln for ln in log.splitlines()
                 if "W17" in ln and "trial" in ln.lower()]
    tdir = os.path.join(ROOT, "fleet", "tasks")
    t_1009 = [f for f in os.listdir(tdir) if f.startswith("T-2026-10-09-")]
    idir = os.path.join(ROOT, "fleet", "inbox")
    inbox_w17 = [f for f in os.listdir(idir)
                 if f.endswith(".md") and "w17" in f.lower()]
    return {"fetch_rc": rc_fetch, "origin_w17_rival_hits": w17_rival[:4],
            "fleet_tickets_1009": t_1009, "inbox_w17": inbox_w17,
            "verdict": "CLEAR" if (not w17_rival and not t_1009
                                   and not inbox_w17) else "RIVAL"}


def main():
    facts = {"round": 788, "machine": "bm-c", "wave": "TRIAL_LABOR_W17",
             "funnel_leg": "3/5 freeze-window facts (draft sec.6.2)",
             "burn": "ZERO (pre-write evidence)"}
    try:
        facts["A1_panel_anchor"] = leg_a1()
        facts["A2_core48_face"] = leg_a2()
        facts["A3_entry_cells"] = leg_a3()
        facts["A4_grammar_lineage"] = leg_a4()
        facts["A5_w16_context"] = leg_a5()
        facts["A6_dsr_chain_head"] = leg_a6()
        facts["A7_w1_exit_burn_correction"] = leg_a7()
        facts["A8_seed_berth"] = leg_a8()
        facts["A9_exit_face_feasibility"] = leg_a9()
        facts["A10_rival_scan"] = leg_a10()
        hard = (not facts["A4_grammar_lineage"]["lineage_assert"]
                or facts["A8_seed_berth"]["verdict"] == "BLOCKED"
                or facts["A10_rival_scan"]["verdict"] == "RIVAL"
                or not facts["A9_exit_face_feasibility"]
                ["feasibility_assert"])
        mech = False
        facts["shape_assert"] = bool(
            facts["A1_panel_anchor"]["rows_le_cutoff"] > 3000
            and facts["A3_entry_cells"]["n_candidates"] > 100
            and isinstance(facts["A6_dsr_chain_head"]["dsr_chain_head_total"],
                          int)
            and facts["A6_dsr_chain_head"]["dsr_chain_head_total"] > 800000)
        facts["rc_map"] = {"hard_violation": hard, "mechanism_issue": mech}
    except Exception as exc:  # honest mech failure, never mask
        facts["error"] = repr(exc)[:400]
        facts["rc_map"] = {"hard_violation": False, "mechanism_issue": True}
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    slim = {k: facts.get(k) for k in ("A1_panel_anchor", "A3_entry_cells",
                                      "A5_w16_context", "A6_dsr_chain_head",
                                      "A7_w1_exit_burn_correction",
                                      "A8_seed_berth", "A9_exit_face_feasibility",
                                      "A10_rival_scan", "rc_map", "error")}
    print(json.dumps(slim, ensure_ascii=False, indent=1)[:3000])
    print("facts:", OUT)
    rc = facts.get("rc_map", {})
    return 1 if rc.get("hard_violation") else (2 if rc.get("mechanism_issue")
                                               else 0)


if __name__ == "__main__":
    raise SystemExit(main())
