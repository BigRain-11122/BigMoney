# -*- coding: utf-8 -*-
"""CENSUS_FUS_S2_W2B runner -- T-86 s2 cross-wave fusion census (wave-2 W2-B).

Prereg (FROZEN R344 precedes this build, R99): research/CENSUS_FUSION_S2_PREREG.md
sec.9.4 + roster results/census_fusion_s2/w2b_roster.json (freeze commit
f084c8e2; roster anchors w2_roster.json 797ff916fe97 / sina_construct_p1.json
513f96deae8f / SINA_MF_PREREG.md 11d0610e3136 / HEATT spec 47eec1ffe490 are
re-verified at load, fail-closed). EXPLORATION FACE: zero judgment claims /
zero paper eligibility; sole output = frozen-rules family aggregation feeding
the T-23 intake funnel (judged consumers carry their own prereg + gates).
D-family standalone REJECT (R338 V1/V2, OOS IC negative) is disclosed with
the batch -- exploration face, no admission gate.

Universe: IDENTICAL to W2-A sec.9.3 (frozen reading): astock qfq panel x
data/fundamental/b_layer_mask.csv CODE set, >=5,000 join gate; ok_static
subset DISCLOSED not gated. The 32 A-faces + rets/fwd5/adv20 + z/t sidecars
are REUSED READ-ONLY from the W2-A state dir Money02/data/cache/census_w2/
(gitignored, deterministic-regenerable; validated against w2_roster.json at
prep; absent -> W2A.prep_state() rebuild fallback, fail-closed exit 2).

D-face input (roster lane): bm-a small-artifact export
data/census_w2b/w2b_d8_faces.npz (raw faces; 4 net verbatim + 4 ratio
rX_net/turnover with the judged turnover>0 guard) + git-tracked manifest
results/census_fusion_s2/w2b_d8_manifest.json. IN-RUNNER FAIL-CLOSED SHA256
GATE: recomputed artifact hash must equal manifest sha256, else exit 2.
Z-scoring happens here (W1._zscore, wave-1 convention -- the artifact is raw
by design). D-face cross-section = the W2-A universe reading (wider than the
judged construct universe 3,498 -- sign anchors only, disclosed).
Coverage window: the D-covered window (~1y, 250 artifact dates ending at
cutoff); the weekly REB=5 grid anchors at the first date where ALL 40 faces
have >=TOP_K valid -> ~47 signal days (roster sec.9.4 disclosure). The
~116k collapse-law-rejected panel rows travel as NaN in the artifact
(%.10g write-rounding latent defect, known + disclosed in the manifest).

Enumeration (sec.9.4 frozen, itertools-verified): 40 faces = 8 D + 32 A;
combos each forced >=1 D face: pairs 284 (D-D 28 + D-A 256) + triples 4,920
(3D 56 + 2D1A 896 + 1D2A 3,968) = 5,204 candidates + controls 16 (D x
rs_20/rs_60) + nulls 400 (200 pairs + 200 triples, rejection-redraw forced
>=1 D -- divergence from W2-A unconditional draw, disclosed sec.9.4) =
ledger N 5,620. Seeds: null base 20282500 band 20282500..20282899
(SEED_REGISTRY census_fusion_s2_w2b, R344 same-commit registration).

Methodology: IDENTICAL machinery to W2-A sec.9.3 -- blend long leg combo-score
TOP-50 equal weight, weekly REB=5 grid, signal t / exec t+1 close conservative
T+1 proxy, V2 + x2 costs, 1% ADV20 entry cap (adv20 RAW amount, no ffill),
IC face = fwd-5d rank-IC, dual-sort tercile matrices, deltas vs EW-universe
benchmark over the W2-B grid. Wave-1 machinery IMPORTED and reused, not
rewritten (W1._score_matrix / blend_top16 / _ic_stats / _dual_sort_* /
_zscore / _tercile_labels / _jsonable; W2A.eval_spec / block_worker row
schema). Ledger: append_ledger("CENSUS_FUS_S2_W2B", 5620, ...) at finalize
only (r252 embed key). Checkpoint every 200 combos (JSONL, cross-kill
resume; prep re-runs on resume). Deterministic: byte-stable rerun.

LANE: bm-b (astock panel + A sidecars locality; R31 lane_owner; the D8 npz
arrives via TRANSFER plan-A transfer branch per fleet/TRANSFER.md sec.2 --
receiving SOP: git checkout <branch> -- data/census_w2b/w2b_d8_faces.npz
then git restore --staged that path (r90 law), verify against manifest).

Usage: python scripts/census_fusion_s2_w2b.py run | probe | selftest [--workers N]
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "research", "shortline", "screening"))

import numpy as np
import pandas as pd

from science_gates import SEED_REGISTRY, append_ledger, cutoff_meta

import census_fusion_s2 as W1          # frozen wave-1 machinery (import-only)
import census_fusion_s2_w2 as W2A      # frozen W2-A prep/row machinery (import-only)

BATCH = "CENSUS_FUS_S2_W2B"
TICKET = "T-2026-09-26-86-P1 s2 wave-2 W2-B (CEO O-20260926-2320)"
PREREG = ("research/CENSUS_FUSION_S2_PREREG.md sec.9.4 + w2b_roster.json "
          "FROZEN commit f084c8e2 precedes runner build precedes ANY run (R99)")
CUTOFF = "2026-09-24"                   # evidence_cutoff (roster sec.9.4)
TOP_K = 50                              # blend long leg (sec.9.3 mechanics)
REB = 5                                # weekly grid
N_NULLS = 400                           # 200 pairs + 200 triples, >=1 D forced
BLOCK = 200                             # checkpoint cadence (wave-1 parity)
LEDGER_N = 5620                         # frozen enumeration total (sec.9.4)
MIN_JOIN = W2A.MIN_JOIN                 # frozen universe gate (sec.9.3)
MIN_FREE_RAM_GB = W2A.MIN_FREE_RAM_GB   # prep guard (a158 family)
SEED_W2B = SEED_REGISTRY["census_fusion_s2_w2b"]   # 20282500 (R344)
BENCH_FACES = W2A.BENCH_FACES           # rs_20_csi300 / rs_60_csi300

OUT_DIR = os.path.join(ROOT, "results", "census_fusion_s2")
ROSTER_JSON = os.path.join(OUT_DIR, "w2b_roster.json")
MANIFEST_JSON = os.path.join(OUT_DIR, "w2b_d8_manifest.json")
ARTIFACT_NPZ = os.path.join(ROOT, "data", "census_w2b", "w2b_d8_faces.npz")
SIDE_DIR_A = W2A.SIDE_DIR               # Money02/data/cache/census_w2 (W2-A)
SIDE_DIR_D = os.path.join(ROOT, "Money02", "data", "cache", "census_w2b")
CKPT = os.path.join(OUT_DIR, "w2b_checkpoint.jsonl")
FAM_D = "D_sina_mf"


# ---------------------------------------------------------------- roster

def _sha256_12(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


# roster anchor basenames -> repo paths (w2b_roster.json stores basenames)
ANCHOR_PATHS = {
    "w2_roster.json": os.path.join(OUT_DIR, "w2_roster.json"),
    "sina_construct_p1.json": os.path.join(ROOT, "results", "shortline",
                                           "sina_construct_p1.json"),
    "SINA_MF_PREREG.md": os.path.join(ROOT, "research", "shortline",
                                      "SINA_MF_PREREG.md"),
    "HEAT_ATTENTION_SPEC.md": os.path.join(ROOT, "research", "shortline",
                                           "HEAT_ATTENTION_SPEC.md"),
}


def load_roster_w2b():
    """Frozen W2-B roster: 8 D faces + signs + enumeration asserts + anchor
    re-verification (fail-closed). Zero invention: consume w2b_roster.json."""
    with open(ROSTER_JSON, encoding="utf-8") as fh:
        r = json.load(fh)
    anchors = r["artifact_anchors"]
    for rel, spec in anchors.items():
        p = ANCHOR_PATHS[rel]
        if not os.path.exists(p):
            raise FileNotFoundError(f"roster anchor absent: {rel} -> {p}")
        got = _sha256_12(p)
        if got != spec["sha256_12"]:
            raise AssertionError(
                f"roster anchor drift: {rel} sha12 {got} != "
                f"frozen {spec['sha256_12']}")
    enum = r["w2b"]["enumeration"]
    assert (enum["pairs"], enum["triples"], enum["candidates"],
            enum["controls_rs_pairs"], enum["nulls"],
            enum["ledger_N"]) == (284, 4920, 5204, 16, 400, 5620), enum
    assert r["w2b"]["seeds"]["null_base"] == SEED_W2B, "roster seed mismatch"
    assert SEED_REGISTRY["census_fusion_s2_w2b"] == 20282500
    assert r["gates"]["sina_mf_panel"]["state"] == "OPEN"
    d_faces = r["w2b"]["faces"]
    assert len(d_faces) == 8, f"roster w2b faces {len(d_faces)} != 8"
    d_names = [f["face"] for f in d_faces]
    d_signs = {f["face"]: float(f["sign"]) for f in d_faces}
    return r, d_names, d_signs


def combined_faces(d_names, a_faces):
    """40-face combined list: D8 first (roster order), then A32 (W2-A roster
    order) -- deterministic enumeration input."""
    return list(d_names) + list(a_faces)


# ---------------------------------------------------------------- D8 gate

def load_d8_artifact():
    """Fail-closed D8 artifact load: manifest sha256 must equal the
    recomputed npz hash; roster face names must all be present."""
    if not os.path.exists(MANIFEST_JSON):
        print(f"D8 GATE FAIL: manifest absent ({MANIFEST_JSON}) -> exit 2")
        return None, None
    if not os.path.exists(ARTIFACT_NPZ):
        print(f"D8 GATE FAIL: artifact absent ({ARTIFACT_NPZ}; TRANSFER "
              f"plan-A receiving SOP: git checkout <transfer-branch> -- "
              f"data/census_w2b/w2b_d8_faces.npz + git restore --staged "
              f"that path) -> exit 2")
        return None, None
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        mf = json.load(fh)
    h = hashlib.sha256()
    with open(ARTIFACT_NPZ, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != mf["sha256"]:
        print(f"D8 GATE FAIL: artifact sha256 {got[:16]}... != manifest "
              f"{str(mf['sha256'])[:16]}... -> exit 2 (re-transfer)")
        return None, None
    with np.load(ARTIFACT_NPZ) as z:
        dates = pd.DatetimeIndex(pd.to_datetime([str(x) for x in z["dates_iso"]]))
        syms = [str(s) for s in z["syms"]]
        faces = {k: np.asarray(z[k], dtype=np.float64)
                 for k in z.files if k not in ("dates_iso", "syms")}
    roster, _, _ = load_roster_w2b()
    want = [f["face"] for f in roster["w2b"]["faces"]]
    missing = [w for w in want if w not in faces]
    if missing:
        print(f"D8 GATE FAIL: artifact missing faces {missing} -> exit 2")
        return None, None
    if str(dates.max().date()) > CUTOFF:
        print(f"D8 GATE FAIL: artifact dates past cutoff {CUTOFF} -> exit 2")
        return None, None
    rep = {"sha256": got, "n_dates": len(dates), "n_syms": len(syms),
           "date_start": str(dates.min().date()),
           "date_end": str(dates.max().date()),
           "manifest_panel_report": mf.get("panel_report"),
           "manifest_bytes": mf.get("bytes")}
    return {"dates": dates, "syms": syms, "faces": faces}, rep


# ---------------------------------------------------------------- A sidecars

def validate_a_sidecars():
    """Read-only reuse of the W2-A state dir: meta.json + 32 z_/t_ sidecars +
    rets/fwd5/adv20, all consistent with the frozen w2_roster. Returns meta
    or None (caller falls back to W2A.prep_state rebuild)."""
    meta_p = os.path.join(SIDE_DIR_A, "meta.json")
    if not os.path.exists(meta_p):
        return None
    with open(meta_p, encoding="utf-8") as fh:
        meta = json.load(fh)
    if meta.get("cutoff_real") != CUTOFF:
        return None
    try:
        a_faces, a_signs, a_fam = W2A.load_roster()
    except Exception:
        return None
    if meta.get("faces") != [f["face"] for f in a_faces]:
        return None
    for nm in meta["faces"] + BENCH_FACES:
        for pre in ("z_", "t_"):
            if not os.path.exists(os.path.join(SIDE_DIR_A, f"{pre}{nm}.npy")):
                return None
    for nm in ("rets.npy", "fwd5.npy", "adv20.npy"):
        if not os.path.exists(os.path.join(SIDE_DIR_A, nm)):
            return None
    if not meta.get("gate", {}).get("ok"):
        return None
    return meta


def ensure_a_state():
    """A-side state: reuse validated W2-A sidecars (read-only) or rebuild via
    W2A.prep_state() (deterministic same dir). Returns (meta, gate, lhb_rep)
    or (None, gate, None) on gate failure (fail-closed)."""
    meta = validate_a_sidecars()
    if meta is not None:
        print("[a-state] REUSED validated W2-A sidecars (read-only)")
        return meta, meta["gate"], meta.get("lhb", {})
    print("[a-state] W2-A sidecars absent/invalid -> W2A.prep_state() rebuild")
    meta2, _side, gate, lhb_rep = W2A.prep_state()
    if meta2 is None:
        return None, gate, lhb_rep
    return meta2, gate, lhb_rep


# ---------------------------------------------------------------- D prep

def prep_d_sidecars(d8, meta_a, ram_guard=True):
    """Reindex the 8 raw D faces to the A panel (idx x syms), z-score (W1
    convention), write z_/t_ sidecars into SIDE_DIR_D. Returns rep or None
    (free-RAM guard refused; ram_guard=False for hermetic selftest)."""
    if ram_guard:
        free = W2A._free_ram_gb()
        if free is not None and free < MIN_FREE_RAM_GB:
            print(f"REFUSED: free RAM {free:.1f}GB < {MIN_FREE_RAM_GB}GB "
                  f"(prep guard)")
            return None
    idx = pd.DatetimeIndex(pd.to_datetime(meta_a["idx_iso"]))
    syms = list(meta_a["syms"])
    art_dates, art_syms = d8["dates"], d8["syms"]
    d_roster, d_names, d_signs = load_roster_w2b()
    n_offcal = int((~art_dates.isin(idx)).sum())
    sym_set = set(syms)
    n_syms_dropped = len([s for s in art_syms if s not in sym_set])
    frames = {}
    for nm in d_names:
        f = pd.DataFrame(d8["faces"][nm], index=art_dates, columns=art_syms)
        frames[nm] = f.reindex(index=idx, columns=syms)
    os.makedirs(SIDE_DIR_D, exist_ok=True)
    zed, terc = {}, {}
    for nm in d_names:
        Z = W1._zscore(frames[nm])
        zed[nm] = np.ascontiguousarray(Z.values, dtype=np.float64)
        terc[nm] = W1._tercile_labels(Z)
        np.save(os.path.join(SIDE_DIR_D, f"z_{nm}.npy"), zed[nm])
        np.save(os.path.join(SIDE_DIR_D, f"t_{nm}.npy"),
                np.ascontiguousarray(terc[nm], dtype=np.int8))
        frames[nm] = zed[nm] = None      # free as we go
    # coverage disclosure: valid counts per D face inside the D window
    cover = {}
    in_win = (idx >= art_dates.min()) & (idx <= art_dates.max())
    for nm in d_names:
        z = np.load(os.path.join(SIDE_DIR_D, f"z_{nm}.npy"), mmap_mode="r")
        cover[nm] = int(np.isfinite(np.asarray(z[in_win])).sum())
        z = None
    rep = {"artifact_dates": len(art_dates),
           "artifact_dates_off_panel_calendar": n_offcal,
           "artifact_syms_dropped_not_in_universe": n_syms_dropped,
           "d_window": [str(art_dates.min().date()), str(art_dates.max().date())],
           "d_valid_in_window": cover,
           "zscore_cross_section": "W2-A universe reading (panel x mask CODE "
                                   "set; wider than judged construct 3,498 "
                                   "-- sign anchors only, disclosed)"}
    return rep


# ---------------------------------------------------------------- grid + ew

def build_grid(meta_a, d_names):
    """Weekly grid anchored at the first date where ALL 40 faces have >=TOP_K
    valid (lands inside the D-window; ~47 signal days at 250 artifact dates)."""
    idx = pd.DatetimeIndex(pd.to_datetime(meta_a["idx_iso"]))
    n_days = len(idx)
    valid_min = None
    for nm in meta_a["faces"] + BENCH_FACES:
        z = np.load(os.path.join(SIDE_DIR_A, f"z_{nm}.npy"), mmap_mode="r")
        cnt = np.isfinite(np.asarray(z)).sum(axis=1)
        z = None
        valid_min = cnt if valid_min is None else np.minimum(valid_min, cnt)
    for nm in d_names:
        z = np.load(os.path.join(SIDE_DIR_D, f"z_{nm}.npy"), mmap_mode="r")
        cnt = np.isfinite(np.asarray(z)).sum(axis=1)
        z = None
        valid_min = cnt if valid_min is None else np.minimum(valid_min, cnt)
    feasible = np.asarray(valid_min) >= TOP_K
    anchor = int(np.argmax(feasible)) if feasible.any() else -1
    if anchor < 0:
        return None, None, -1
    grid_sig = list(range(anchor, n_days - 1, REB))
    grid_exec = [g + 1 for g in grid_sig if g + 1 < n_days]
    return grid_sig, grid_exec, anchor


def _ew_univ(state):
    """EW all-members benchmark over the W2-B grid (fixed_all mirror)."""
    return (W1.blend_top16(state, None, x2=False, fixed_all=True),
            W1.blend_top16(state, None, x2=True, fixed_all=True))


# ---------------------------------------------------------------- state/meta

def build_meta(meta_a, d_names, d_signs, d8_rep, d_prep_rep,
               grid_sig, grid_exec, gate):
    idx = pd.DatetimeIndex(pd.to_datetime(meta_a["idx_iso"]))
    meta = {
        "batch": BATCH, "cutoff_real": CUTOFF,
        "n_days": meta_a["n_days"], "n_syms": meta_a["n_syms"],
        "faces_a": meta_a["faces"], "signs_a": meta_a["signs"],
        "fam_a": meta_a["fam"], "fam_d": FAM_D,
        "faces_d": list(d_names), "signs_d": dict(d_signs),
        "grid_sig": grid_sig, "grid_exec": grid_exec,
        "idx_iso": meta_a["idx_iso"], "syms": meta_a["syms"],
        "d8_gate": d8_rep, "d_prep": d_prep_rep,
        "gate": W1._jsonable(gate),
    }
    meta["anchor_first_signal"] = str(idx[grid_sig[0]].date())
    return meta


# ---------------------------------------------------------------- enumeration

def enumerate_specs(meta):
    """5,204 candidates (>=1 D) + 16 D-controls + 400 nulls (>=1 D forced) =
    5,620 (sec.9.4 frozen; rejection-redraw null divergence disclosed)."""
    from itertools import combinations
    d_set = set(meta["faces_d"])
    faces = list(meta["faces_d"]) + list(meta["faces_a"])
    sign = {**meta["signs_d"], **meta["signs_a"]}
    specs = []
    for f1, f2 in combinations(faces, 2):
        if d_set & {f1, f2}:
            specs.append({"kind": "pair", "id": f"P:{f1}|{f2}",
                          "faces": [f1, f2],
                          "signs": [sign[f1], sign[f2]]})
    for f1, f2, f3 in combinations(faces, 3):
        if d_set & {f1, f2, f3}:
            specs.append({"kind": "triple", "id": f"T:{f1}|{f2}|{f3}",
                          "faces": [f1, f2, f3],
                          "signs": [sign[f1], sign[f2], sign[f3]]})
    for f in meta["faces_d"]:
        for b in BENCH_FACES:
            specs.append({"kind": "control", "id": f"C:{f}|{b}",
                          "faces": [f, b], "signs": [sign[f], 1.0]})
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED_W2B + k)
        n = 2 if k < 200 else 3
        while True:                      # rejection redraw until >=1 D face
            sel = rng.choice(len(faces), size=n, replace=False)
            if d_set & {faces[i] for i in sel}:
                break
        sgn = rng.choice([-1.0, 1.0], size=n)
        specs.append({"kind": "null", "id": f"N{k}",
                      "faces": [faces[i] for i in sel],
                      "signs": [float(x) for x in sgn]})
    assert len(specs) == LEDGER_N, len(specs)
    assert (sum(1 for s in specs if s["kind"] == "pair") == 284
            and sum(1 for s in specs if s["kind"] == "triple") == 4920
            and sum(1 for s in specs if s["kind"] == "control") == 16
            and sum(1 for s in specs if s["kind"] == "null") == 400)
    return specs


# ---------------------------------------------------------------- workers

_G = {}


def _init_worker(side_dir_a, side_dir_d, ew_x1, ew_x2, specs, meta):
    """Worker state from BOTH sidecar dirs (A: W2-A read-only reuse; D: own).
    Specs built once in the parent, pickled via initargs."""
    idx = pd.DatetimeIndex(pd.to_datetime(meta["idx_iso"]))
    syms = meta["syms"]
    zed, terc = {}, {}
    for nm in meta["faces_a"] + BENCH_FACES:
        zed[nm] = np.load(os.path.join(side_dir_a, f"z_{nm}.npy"),
                          mmap_mode="r")
        terc[nm] = np.load(os.path.join(side_dir_a, f"t_{nm}.npy"),
                           mmap_mode="r")
    for nm in meta["faces_d"]:
        zed[nm] = np.load(os.path.join(side_dir_d, f"z_{nm}.npy"),
                          mmap_mode="r")
        terc[nm] = np.load(os.path.join(side_dir_d, f"t_{nm}.npy"),
                           mmap_mode="r")
    fwd5_arr = np.load(os.path.join(side_dir_a, "fwd5.npy"), mmap_mode="r")
    _G["state"] = {
        "idx": idx, "syms": syms, "faces": meta["faces_d"] + meta["faces_a"],
        "sign": {**meta["signs_d"], **meta["signs_a"]},
        "zed": zed, "terc": terc,
        "rets": np.load(os.path.join(side_dir_a, "rets.npy"), mmap_mode="r"),
        "fwd5": pd.DataFrame(fwd5_arr, index=idx, columns=syms),
        "adv20": np.load(os.path.join(side_dir_a, "adv20.npy"), mmap_mode="r"),
        "grid_sig": meta["grid_sig"], "grid_exec": meta["grid_exec"],
        "n_days": meta["n_days"],
        "specs": specs,
    }
    _G["ew_x1"] = ew_x1
    _G["ew_x2"] = ew_x2


def eval_spec(state, spec, ew_x1, ew_x2):
    """One combo -> full stat row. W2A.eval_spec row schema reused verbatim
    (import-only; single definition, no rewrite)."""
    return W2A.eval_spec(state, spec, ew_x1, ew_x2)


def block_worker(start, end):
    """Top-level picklable: evaluate specs[start:end], return {i: row}."""
    state = _G["state"]
    specs = state["specs"]
    return {i: eval_spec(state, specs[i], _G["ew_x1"], _G["ew_x2"])
            for i in range(start, end)}


# ---------------------------------------------------------------- checkpoints

def _load_checkpoint():
    done = set()
    if os.path.exists(CKPT):
        with open(CKPT, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        done.add(json.loads(line)["i"])
                    except (ValueError, KeyError):
                        continue
    return done


def _append_ckpt(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CKPT, "a", encoding="utf-8") as fh:
        for i, row in rows.items():
            fh.write(json.dumps({"i": int(i), "row": W1._jsonable(row)},
                                ensure_ascii=False, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------- run

def run(probe=False, workers=None):
    t0 = time.time()
    from parallel_runner import run_cells_parallel

    roster, d_names, d_signs = load_roster_w2b()
    d8, d8_rep = load_d8_artifact()
    if d8 is None:
        print("D8 GATE FAIL (fail-closed, exit 2)")
        return 2
    meta_a, gate, lhb_rep = ensure_a_state()
    if meta_a is None:
        print("A-STATE GATE FAIL (fail-closed, exit 2)")
        return 2
    a_roster_faces, a_signs, a_fam = W2A.load_roster()
    a_names = [f["face"] for f in a_roster_faces]
    if meta_a["faces"] != a_names:
        print("A-STATE FACE DRIFT vs w2_roster (fail-closed, exit 2)")
        return 2

    d_prep_rep = prep_d_sidecars(d8, meta_a)
    if d_prep_rep is None:
        print("D-PREP REFUSED (free-RAM guard, exit 2)")
        return 2
    grid_sig, grid_exec, anchor = build_grid(meta_a, d_names)
    if grid_sig is None:
        print("GRID INFEASIBLE (no date with all-40-faces >=50 valid) "
              "-> exit 2")
        return 2
    idx = pd.DatetimeIndex(pd.to_datetime(meta_a["idx_iso"]))
    print(f"[grid] anchor={str(idx[anchor].date())} signals={len(grid_sig)} "
          f"execs={len(grid_exec)} d_window={d_prep_rep['d_window']}")

    meta = build_meta(meta_a, d_names, d_signs, d8_rep, d_prep_rep,
                      grid_sig, grid_exec, gate)
    ew_state = {
        "idx": idx, "syms": meta["syms"],
        "faces": meta["faces_d"] + meta["faces_a"],
        "sign": {**meta["signs_d"], **meta["signs_a"]},
        "rets": np.load(os.path.join(SIDE_DIR_A, "rets.npy"), mmap_mode="r"),
        "fwd5": pd.DataFrame(
            np.load(os.path.join(SIDE_DIR_A, "fwd5.npy"), mmap_mode="r"),
            index=idx, columns=meta["syms"]),
        "adv20": np.load(os.path.join(SIDE_DIR_A, "adv20.npy"), mmap_mode="r"),
        "grid_sig": grid_sig, "grid_exec": grid_exec,
        "n_days": meta_a["n_days"],
    }
    ew_x1, ew_x2 = _ew_univ(ew_state)
    meta["ew_univ"] = {"x1": W1._jsonable(ew_x1), "x2": W1._jsonable(ew_x2)}
    print(f"[ew_univ] x1 sharpe={ew_x1['sharpe']} | x2 sharpe={ew_x2['sharpe']}")
    del ew_state

    specs = enumerate_specs(meta)
    n_total = len(specs)
    n = min(n_total, 4) if probe else n_total

    done = set() if probe else _load_checkpoint()
    jobs = []
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        if all(i in done for i in range(s, e)):
            continue
        jobs.append((f"blk{s // BLOCK:02d}", block_worker, (s, e)))
    print(f"[plan] specs={n} blocks_todo={len(jobs)} ckpt_done={len(done)}")

    results = {}
    if jobs:
        res = run_cells_parallel(
            jobs, workers=workers or 4, desc="census-w2b",
            initializer=_init_worker,
            initargs=(SIDE_DIR_A, SIDE_DIR_D, meta["ew_univ"]["x1"],
                      meta["ew_univ"]["x2"], specs, meta))
        w = res.pop("__workers__", 1)
        for _blk, rows in res.items():
            results.update(rows)
            if not probe:
                _append_ckpt(rows)
    else:
        w = 0
        with open(CKPT, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    d = json.loads(line)
                    results[d["i"]] = d["row"]

    if probe:
        payload = W1._jsonable({
            "batch": BATCH, "mode": "probe", "d8_gate": d8_rep,
            "d_prep": d_prep_rep, "gate": gate, "lhb": lhb_rep,
            "n_days": meta_a["n_days"], "cutoff_real": CUTOFF,
            "grid_first_signal": meta["anchor_first_signal"],
            "n_grid_signals": len(grid_sig),
            "n_grid_execs": len(grid_exec),
            "ew_univ": meta["ew_univ"], "rows": list(results.values()),
        })
        s = json.dumps(payload, ensure_ascii=False)
        json.loads(s)
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "probe_w2b.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(s)
        print(f"[probe] OK rows={len(results)} grid={len(grid_exec)} "
              f"first_sig={payload['grid_first_signal']}")
        return 0

    # ---- finalize ----
    missing = [i for i in range(n_total) if i not in results]
    if missing:
        print(f"INCOMPLETE: {len(missing)} specs missing -> exit 2 "
              f"(checkpoint retained)")
        return 2
    cand_rows = [results[i] for i in range(n_total)
                 if results[i]["kind"] != "null"]
    nulls = [results[i] for i in range(n_total) if results[i]["kind"] == "null"]

    import csv as _csv
    cols = ["id", "kind", "faces", "signs", "ic_mean", "ic_ir", "ic_pos_pct",
            "ic_n", "x1_ann", "x1_vol", "x1_sharpe", "x1_maxdd",
            "x1_monthly_win", "x1_capped", "x2_ann", "x2_vol", "x2_sharpe",
            "x2_maxdd", "x2_monthly_win", "x2_capped",
            "delta_x1_ann_vs_ew_univ", "delta_x2_sharpe_vs_ew_univ"]
    ycols = sorted({c for r in cand_rows + nulls
                    for c in r if c.startswith("ic_y")})
    with open(os.path.join(OUT_DIR, "w2b_cells.csv"), "w", encoding="utf-8",
              newline="") as fh:
        wr = _csv.DictWriter(fh, fieldnames=cols + ycols, extrasaction="ignore")
        wr.writeheader()
        for r in cand_rows:
            wr.writerow({k: ("" if r.get(k) is None else r.get(k))
                         for k in cols + ycols})
    with open(os.path.join(OUT_DIR, "w2b_nulls.json"), "w",
              encoding="utf-8") as fh:
        json.dump(W1._jsonable({"batch": BATCH, "n": len(nulls),
                                 "seed_base": int(SEED_W2B),
                                 "nulls": nulls}),
                  fh, ensure_ascii=False, indent=1)

    ranked = sorted((r for r in cand_rows if r["ic_mean"] is not None),
                    key=lambda r: -abs(r["ic_mean"]))[:50]
    with open(os.path.join(OUT_DIR, "w2b_top_matrices.json"), "w",
              encoding="utf-8") as fh:
        json.dump(W1._jsonable({"batch": BATCH,
                                 "top_rule": "|ic_mean| top-50 (wave-1 rule)",
                                 "n": len(ranked),
                                 "items": [{"id": r["id"], "kind": r["kind"],
                                            "ic_mean": r["ic_mean"],
                                            "matrix": r["matrix"]}
                                           for r in ranked]}),
                  fh, ensure_ascii=False, indent=1)

    fam = {**meta_a["fam"], **{f: FAM_D for f in meta["faces_d"]}}
    fam_stats = {}
    for fam_name in sorted(set(fam.values())):
        members = [r for r in cand_rows if r["kind"] in ("pair", "triple")
                   and any(fam.get(f) == fam_name for f in r["faces"].split("|"))]
        xs = sorted(r["x2_sharpe"] for r in members
                    if r["x2_sharpe"] is not None)
        fam_stats[fam_name] = {
            "n_combos": len(members),
            "median_x2_sharpe": round(float(np.median(xs)), 4) if xs else None}
    cross_top10 = sorted((r for r in cand_rows
                          if r["kind"] in ("pair", "triple")
                          and r["x2_sharpe"] is not None),
                         key=lambda r: -r["x2_sharpe"])[:10]
    null_x2 = sorted(r["x2_sharpe"] for r in nulls
                     if r["x2_sharpe"] is not None)
    cand_x2 = [r["x2_sharpe"] for r in cand_rows
               if r["x2_sharpe"] is not None]
    summary = W1._jsonable({
        "batch": BATCH,
        "family_rule": ("sec.9.4: per roster family (5 A families + D_sina_mf), "
                        "median x2 blend Sharpe of combos containing >=1 "
                        "family face + coverage count; cross-family top-10 by "
                        "x2 Sharpe; EXPLORATION ONLY (zero registration effect)"),
        "families": fam_stats,
        "cross_family_top10": [{"id": r["id"], "faces": r["faces"],
                                 "signs": r["signs"],
                                 "x2_sharpe": r["x2_sharpe"],
                                 "x1_sharpe": r["x1_sharpe"],
                                 "ic_mean": r["ic_mean"]} for r in cross_top10],
        "ew_univ_benchmark": meta["ew_univ"],
        "null_x2_sharpe": {"n": len(null_x2),
                            "median": round(float(np.median(null_x2)), 4)
                            if null_x2 else None,
                            "p95": round(float(np.quantile(null_x2, 0.95)), 4)
                            if null_x2 else None},
        "cand_x2_p95": round(float(np.quantile(cand_x2, 0.95)), 4)
        if cand_x2 else None,
    })
    with open(os.path.join(OUT_DIR, "w2b_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)

    ledger = append_ledger(BATCH, n_total, "census_fusion_s2/w2b_results.json",
                           evidence_cutoff=CUTOFF,
                           note="exploration face: 5,204 cross-wave D>=1 "
                                "combos + 16 D rs-controls + 400 nulls "
                                "(sec.9.4 frozen N=5,620)")
    payload = {
        **cutoff_meta(CUTOFF),
        "batch": BATCH, "ticket": TICKET, "prereg_ref": PREREG,
        "face": "EXPLORATION (zero judgment claims / zero paper eligibility)",
        "n_candidates": sum(1 for r in cand_rows
                            if r["kind"] in ("pair", "triple")),
        "n_controls": sum(1 for r in cand_rows if r["kind"] == "control"),
        "n_nulls": len(nulls),
        "data_gate": W1._jsonable({"universe": gate, "d8": d8_rep,
                                    "d_prep": d_prep_rep,
                                    "lhb_events": lhb_rep}),
        "d_family_disclosure": {
            "standalone": "REJECT (R338 V1/V2 judged; OOS IC negative) -- "
                          "disclosed with the batch, exploration face only",
            "sign_anchor": "sina_construct_p1.json h10 IS IC (r0/r1 +, "
                           "r2/r3 -); intra-D corr pre-evidence: TIER_r0|"
                           "TIER_r1 0.4877, TIER_r0|MAIN 0.8636 "
                           "(family_by_construction, roster honest_notes)"},
        "grid": {"anchor_first_signal": meta["anchor_first_signal"],
                 "n_signals": len(grid_sig), "n_execs": len(grid_exec),
                 "cadence": f"{REB} trading days", "top_k": TOP_K,
                 "panel_days": meta_a["n_days"],
                 "cutoff_real": CUTOFF, "n_syms": meta_a["n_syms"],
                 "d_window": d_prep_rep["d_window"],
                 "coverage_window_note": "D-combo stats run on the "
                          "D-covered window (~1y) vs W2-A full-window "
                          "(roster sec.9.4 disclosure)"},
        "products": ["w2b_cells.csv", "w2b_nulls.json",
                     "w2b_top_matrices.json", "w2b_summary.json"],
        "audit": {"workers": int(w),
                   "purpose": "exploration census (no selection gate)",
                   "ledger_trials_added": int(n_total),
                   "elapsed_sec": round(time.time() - t0, 1),
                   "null_seed_band": f"{SEED_W2B}..{SEED_W2B + N_NULLS - 1}",
                   "checkpoint": "w2b_checkpoint.jsonl (200-combo cadence)",
                   "sidecars": (SIDE_DIR_A + " (W2-A read-only reuse) + "
                                + SIDE_DIR_D + " (own; gitignored, "
                                "regenerable)"),
                   "methodology_divergences": [
                       "D-window restriction: grid anchors inside the D-"
                       "covered window (~250 artifact dates, ~47 weekly "
                       "signals) vs W2-A full-window (roster sec.9.4)",
                       "D-face z-score cross-section = W2-A universe reading "
                       "(panel x mask CODE set) -- wider than the judged "
                       "construct universe (3,498); sign anchors only",
                       "nulls: rejection-redraw forced >=1 D face (sec.9.4 "
                       "divergence from W2-A unconditional draw)",
                       "controls = D-faces x rs bench only (16) vs W2-A "
                       "all-face x bench (64)",
                       "D8 artifact carries ~116k collapse-law-rejected "
                       "panel rows as NaN (%.10g write-rounding latent "
                       "defect, known + disclosed in the manifest)",
                       "A-sidecar read-only reuse dependency (validated vs "
                       "w2_roster; W2A.prep_state() rebuild fallback)"]},
        "trials_ledger": ledger,   # r252 law: canonical embed key
    }
    out = os.path.join(OUT_DIR, "w2b_results.json")
    s = json.dumps(W1._jsonable(payload), ensure_ascii=False, indent=1)
    json.loads(s)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(f"[done] cells={len(cand_rows)} nulls={len(nulls)} workers={w} "
          f"elapsed={payload['audit']['elapsed_sec']}s "
          f"ledger={ledger['total']}")
    return 0


# ---------------------------------------------------------------- selftest

def selftest():
    """Hermetic selftest (no real panel, no real npz, no network). r263 law."""
    import tempfile
    ok = True

    def t(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and bool(cond)

    # [1] frozen roster load + anchor sha re-verification + enumeration math
    roster, d_names, d_signs = load_roster_w2b()
    t("[1] roster 8 D faces + anchors verified + seed registry",
      len(d_names) == 8 and all(f in d_signs for f in d_names)
      and SEED_W2B == 20282500
      and SEED_REGISTRY["census_fusion_s2_w2b"] == 20282500)
    a_faces, a_signs, a_fam = W2A.load_roster()
    mini_meta = {"faces_d": d_names, "faces_a": [f["face"] for f in a_faces],
                 "signs_d": d_signs,
                 "signs_a": {f["face"]: float(f["sign"]) for f in a_faces}}
    specs = enumerate_specs(mini_meta)
    n_pair = sum(1 for s in specs if s["kind"] == "pair")
    n_trip = sum(1 for s in specs if s["kind"] == "triple")
    n_ctrl = sum(1 for s in specs if s["kind"] == "control")
    n_null = sum(1 for s in specs if s["kind"] == "null")
    d_set = set(d_names)
    t("[1b] enumeration 284/4920/16/400 = 5620, every combo >=1 D",
      len(specs) == 5620 and n_pair == 284 and n_trip == 4920
      and n_ctrl == 16 and n_null == 400
      and all(d_set & set(s["faces"]) for s in specs))

    # [2] null determinism + forced->=1D under rejection redraw
    s0 = enumerate_specs(mini_meta)
    s1 = enumerate_specs(mini_meta)
    nulls0 = [s for s in s0 if s["kind"] == "null"]
    nulls1 = [s for s in s1 if s["kind"] == "null"]
    t("[2] null seed determinism + all nulls >=1 D + sign +/-",
      nulls0 == nulls1
      and all(d_set & set(n["faces"]) for n in nulls0)
      and all(s in (-1.0, 1.0) for n in nulls0 for s in n["signs"])
      and all(len(n["faces"]) == (2 if i < 200 else 3)
              for i, n in enumerate(nulls0)))

    # [3] D8 gate fail-closed: wrong sha + missing faces (synthetic artifact)
    with tempfile.TemporaryDirectory() as td:
        global ARTIFACT_NPZ, MANIFEST_JSON, SIDE_DIR_D
        saved = (ARTIFACT_NPZ, MANIFEST_JSON, SIDE_DIR_D)
        try:
            SIDE_DIR_D = os.path.join(td, "side_d")
            ARTIFACT_NPZ = os.path.join(td, "d8.npz")
            MANIFEST_JSON = os.path.join(td, "manifest.json")
            rng = np.random.default_rng(3)
            fake = {n: rng.normal(0, 1, (30, 20)) for n in d_names}
            np.savez(ARTIFACT_NPZ,
                     dates_iso=np.array([f"2026-08-{d:02d}" for d in
                                         range(1, 31)]),
                     syms=np.array([f"s{i:02d}" for i in range(20)]), **fake)
            mf = {"sha256": "0" * 64, "faces": d_names}
            with open(MANIFEST_JSON, "w", encoding="utf-8") as fh:
                json.dump(mf, fh)
            d8, rep = load_d8_artifact()
            t("[3] D8 gate fail-closed on sha mismatch",
              d8 is None and rep is None)
            # correct sha -> loads; then drop a face member -> fail
            h = hashlib.sha256(open(ARTIFACT_NPZ, "rb").read()).hexdigest()
            mf["sha256"] = h
            with open(MANIFEST_JSON, "w", encoding="utf-8") as fh:
                json.dump(mf, fh)
            d8b, repb = load_d8_artifact()
            t("[3b] D8 gate passes on sha match + shape/meta report",
              d8b is not None and repb["n_dates"] == 30
              and repb["n_syms"] == 20)
            with np.load(ARTIFACT_NPZ) as z:
                keep = {k: z[k] for k in z.files if k != d_names[0]}
            np.savez(ARTIFACT_NPZ, **keep)
            h2 = hashlib.sha256(open(ARTIFACT_NPZ, "rb").read()).hexdigest()
            mf["sha256"] = h2
            with open(MANIFEST_JSON, "w", encoding="utf-8") as fh:
                json.dump(mf, fh)
            d8c, repc = load_d8_artifact()
            t("[3c] D8 gate fail-closed on missing roster face",
              d8c is None)

            # [4] D prep + z semantics on synthetic A meta
            idx = pd.bdate_range("2026-07-01", periods=60)
            meta_a = {"idx_iso": [str(x.date()) for x in idx],
                      "syms": [f"s{i:02d}" for i in range(20)],
                      "faces": [f["face"] for f in a_faces][:4],
                      "signs": {}, "n_days": 60, "n_syms": 20}
            rep_d = prep_d_sidecars(d8b, meta_a, ram_guard=False)
            t("[4] D sidecars written + off-cal/sym-drop disclosed",
              rep_d is not None
              and rep_d["artifact_dates_off_panel_calendar"] >= 0
              and all(os.path.exists(os.path.join(SIDE_DIR_D, f"z_{n}.npy"))
                      for n in d_names))
            z0 = np.load(os.path.join(SIDE_DIR_D, f"z_{d_names[0]}.npy"))
            t("[4b] D z: NaN outside D-window, finite within",
              z0.shape == (60, 20)
              and np.isnan(z0[:20]).all() and np.isfinite(z0[25]).any())
        finally:
            ARTIFACT_NPZ, MANIFEST_JSON, SIDE_DIR_D = saved

    # [5] worker glue: mini A+D sidecars -> block eval + json round-trip
    with tempfile.TemporaryDirectory() as td:
        side_a = os.path.join(td, "side_a")
        side_d = os.path.join(td, "side_d")
        os.makedirs(side_a); os.makedirs(side_d)
        rng = np.random.default_rng(11)
        idx = pd.bdate_range("2026-01-01", periods=200)
        syms = [f"s{i:02d}" for i in range(40)]
        T, N = len(idx), len(syms)
        fa = ["a_face_1", "a_face_2"]
        fd = list(d_names[:2])
        for nm in fa + BENCH_FACES:
            arr = rng.normal(0, 1, (T, N))
            np.save(os.path.join(side_a, f"z_{nm}.npy"), arr)
            np.save(os.path.join(side_a, f"t_{nm}.npy"),
                    W1._tercile_labels(pd.DataFrame(arr, index=idx,
                                                    columns=syms)))
        close = pd.DataFrame(100 + np.cumsum(rng.normal(0, 1, (T, N)), axis=0),
                             index=idx, columns=syms)
        np.save(os.path.join(side_a, "rets.npy"),
                np.asarray(close.pct_change(), dtype=float))
        np.save(os.path.join(side_a, "fwd5.npy"),
                np.asarray(close.shift(-5) / close - 1, dtype=float))
        np.save(os.path.join(side_a, "adv20.npy"),
                np.asarray(pd.DataFrame(rng.uniform(1e6, 5e6, (T, N)),
                                        index=idx, columns=syms)
                           .rolling(20).mean(), dtype=float))
        for nm in fd:
            arr = rng.normal(0, 1, (T, N))
            np.save(os.path.join(side_d, f"z_{nm}.npy"), arr)
            np.save(os.path.join(side_d, f"t_{nm}.npy"),
                    W1._tercile_labels(pd.DataFrame(arr, index=idx,
                                                    columns=syms)))
        grid_sig = list(range(60, T - 1, REB))
        mini_meta = {
            "idx_iso": [str(x.date()) for x in idx], "syms": syms,
            "faces_a": fa, "faces_d": fd,
            "signs_a": {"a_face_1": 1.0, "a_face_2": -1.0},
            "signs_d": {n: d_signs[n] for n in fd},
            "grid_sig": grid_sig, "grid_exec": [g + 1 for g in grid_sig],
            "n_days": T,
        }
        mini_specs = [{"kind": "pair", "id": f"P:{fd[0]}|a_face_1",
                       "faces": [fd[0], "a_face_1"],
                       "signs": [d_signs[fd[0]], 1.0]},
                      {"kind": "control", "id": f"C:{fd[1]}|rs_20_csi300",
                       "faces": [fd[1], "rs_20_csi300"], "signs": [-1.0, 1.0]}]
        _init_worker(side_a, side_d, {"ann": 0.1, "sharpe": 0.5},
                     {"ann": 0.05, "sharpe": 0.2}, mini_specs, mini_meta)
        rows = block_worker(0, 2)
        json.loads(json.dumps({"r": W1._jsonable(rows[0])},
                              ensure_ascii=False))
        t("[5] two-dir worker glue, D-A pair + control rows, json round-trip",
          rows[0]["id"] == f"P:{fd[0]}|a_face_1"
          and rows[0]["x2_sharpe"] is not None
          and rows[1]["kind"] == "control"
          and isinstance(W1._jsonable(rows[0])["x2_capped"], int))
        _G.clear()
        import gc
        gc.collect()

    # [6] ledger pure fn + cutoff_meta (C2 face)
    led = append_ledger(BATCH, LEDGER_N, "census_fusion_s2/w2b_results.json",
                        evidence_cutoff=CUTOFF)
    t("[6] ledger dict + cutoff keys",
      {"prev_total", "batch_trials", "total", "batch"} <= set(led)
      and led["total"] == led["prev_total"] + LEDGER_N
      and cutoff_meta(CUTOFF) == {"evidence_cutoff": CUTOFF})

    # [7] np-native coercion (r286 law) via wave-1 _jsonable
    dirty = {"a": np.int64(5), "b": np.float32(1.5), "c": np.bool_(True),
             "d": np.float64(np.nan)}
    clean = W1._jsonable(dirty)
    json.dumps(clean)
    t("[7] np-native coercion + NaN->None",
      isinstance(clean["a"], int) and isinstance(clean["b"], float)
      and isinstance(clean["c"], bool) and clean["d"] is None)

    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "probe", "selftest"])
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "probe":
        return run(probe=True, workers=a.workers or 4)
    return run(workers=a.workers or 4)


if __name__ == "__main__":
    sys.exit(main())
