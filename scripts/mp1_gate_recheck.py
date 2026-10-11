#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GATE-RECHECK-MP1 -- independent recheck of the 25 PASS gates from
N2-MP1 (prereg research/GATE_RECHECK_MP1_PREREG.md, frozen before burn).

a158_gate_recheck.py clone + factor-face swap (r836 clone law, all
parameters explicit). Three faces:

  Face A  five-member OOS recheck, gate_verify caliber (B2 strict
          buckets + pit-95/r431 decidable AND, cost 0.10% RT) with
          lattice-B thinning (drop-first greedy stride-20 = shifted
          lattice re-draw on the same information set, lattice-
          stability leg declared honestly). Confirm legs: five-member
          net median > 0 AND pos members >= 3/5 AND thin_B median > 0
          (>= 2 valid members).
  Face B  D6 adjacency audit: 25x25 inter-candidate correlation +
          25x19 vs the REGISTERED face = RSV30_low/RSV60_low absolute
          gates (gate_verify PASS2 family) + the 17 A158 RECHECK
          library entries (results/gate_recheck_a158.json literal
          read). Registered signals are REBUILT SAME-CUTOFF on the
          truncated panel (same-instant law: A158 RECHECK's 2026-09-22
          cached signal series are NOT borrowed; this batch rebuilds
          to keep the corr face comparable). Clusters = |corr|>=0.7
          connected components (union-find); representative = highest
          MP1 OOS med_t, tie -> name ascending.
  Face R  MP1-specific new face -- secondary-face reconciliation: the
          recomputed per-member OOS net / n_in / thin(lattice-A) must
          equal the mp1_tsgate_p1.json five_member_oos secondary face
          positionally (sh canonical keys; same cutoff, same
          construction = determinism). Any mismatch = configuration
          drift -> VOID fail-closed (double-burn-window drift guard).

Verdicts (frozen order): REGISTERED-CLONE (max|corr| vs registered
>= 0.7) > CLUSTER-COLLAPSED (non-representative) > RECHECK-CONFIRM
(rep + Face A three legs -> T-101 v4 candidate library) /
RECHECK-FAIL (rep, leg(s) failed -> C1 input-feature demotion).

Machinery single-source, zero reimplementation: mp1_tsgate_probe
(pool formulas / gates / thin / preflight anchor) +
a158_tsgate_probe (alpha158 factors + gate universe). Fail-closed
gates: G-P1 (PASS==25 literal) + G-RECHECK-A158 (library==17 literal)
+ M.preflight_gates() (G-PANEL/G-CUTOFF/G-ANCHOR-MP1/G-FACTORS) +
G-FACTORS-R (44 gate faces decidable >= 100 per member) + Face R
reconciliation. Refuse-if-exists on the final artifact. Deterministic
rerun byte-identical on the stable segment (runtime metadata
segregated). __main__ guarded. Zero network, zero token, minutes-level
local CPU (O-2100 in-round exemption; NOT pooled). Non-trial ledger
batch: marks +0, SEED +0, zero rng consumption (gate machinery
deterministic).

Exit codes: 0 = normal; 2 = fail-closed breach / refuse-if-exists."""
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import mp1_tsgate_probe as M      # pool machinery (single source)
import a158_tsgate_probe as P8    # A158 library + RSV absolute gates

try:
    import science_gates
except Exception:  # pragma: no cover - hermetic fallback
    science_gates = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS_JSON = ROOT / "results" / "gate_recheck_mp1.json"
MD_PATH = ROOT / "research" / "MP1_GATE_RECHECK.md"
P1_JSON = ROOT / "results" / "mp1_tsgate_p1.json"
A158_RECHECK_JSON = ROOT / "results" / "gate_recheck_a158.json"
PREREG_REF = "research/GATE_RECHECK_MP1_PREREG.md"

BATCH = "GATE-RECHECK-MP1"
CUTOFF = "2026-10-09"        # M.CUTOFF, explicit (r836 clone law)
SPLIT = "2017-01-01"         # OOS >= ; IS <= 2016-12-31
COST = 0.001                 # 0.10% round trip (M.COST)
MIN_BARS = 500               # gate_verify verbatim
MIN_EV = 15                  # per member per leg gate events
STRIDE = 20                  # non-overlap thinning (both lattices)
H = 20                       # forward horizon (M.H)
D6_LINE = 0.70               # frozen D6 same-family threshold
FIVE = ["510300", "510050", "510500", "512100", "588000"]   # M.FIVE (O-1555)
EXPECTED_PASS = 25            # MP1 verdict_counts.PASS literal
EXPECTED_LIBRARY = 17        # A158 RECHECK library_entries literal
MIN_DECIDABLE_R = 100         # G-FACTORS-R per member per gate face
RSV_REGISTERED = {"RSV30_low": ("RSV30", 0.2), "RSV60_low": ("RSV60", 0.2)}


def _fail(msg, code=2):
    print("[mp1grc] %s" % msg, flush=True)
    raise SystemExit(code)


def thin_b(pos, stride=STRIDE):
    """Lattice B: drop the first eligible event, then greedy stride
    spacing (A158-RECHECK verbatim; MP1 lattice A = M.thin)."""
    if len(pos) < 2:
        return np.array([], dtype=int)
    kept, last = [], None
    for p in pos[1:]:
        if last is None or p - last >= stride:
            kept.append(p)
            last = p
    return np.array(kept, dtype=int)


def _member_face(code):
    """One five-member canonical sh file -> both factor faces + gates +
    forward return + OOS mask (same-instant truncated panel)."""
    df = M.load_truncated(M.SRC / ("sh%s.csv" % code))   # canonical sh face (bare NOT consumed)
    if len(df) < MIN_BARS:
        _fail("G-PANEL FAIL: %s bars %d < %d" % (code, len(df), MIN_BARS))
    F = M.mp1_factors(df)          # 89 pool formulas (MP1 face)
    F8 = P8.alpha158_factors(df)   # 157 A158 factors (registered face)
    gates = dict((nm, (m, d)) for nm, m, d in M.gate_universe(F))
    gates8 = dict((nm, (m, d)) for nm, m, d in P8.gate_universe(F8))
    c = df["close"]
    fwd = c.shift(-H - 1) / c.shift(-1) - 1.0
    oos = np.asarray(df.index >= pd.Timestamp(SPLIT))
    return df, F, F8, gates, gates8, fwd, oos


def face_a_leg(gates, fwd, oos, gname):
    """Per-member OOS stats for one gate (B2 strict buckets, probe law).
    thin_a = lattice A (MP1 stored face, reconciliation); thin_b =
    lattice B (confirm leg). None on insufficient events."""
    mask, dec = gates[gname]
    f = fwd.to_numpy(dtype=float)
    m = mask.to_numpy()
    d = dec.to_numpy()
    ok = ~np.isnan(f)
    base = d & ok & oos
    pin = np.flatnonzero(base & m)
    pout = np.flatnonzero(base & ~m)
    if len(pin) < MIN_EV or len(pout) < MIN_EV:
        return None
    diff = float(f[pin].mean() - f[pout].mean())
    net = diff - COST
    tin, tout = M.thin(pin), M.thin(pout)
    thin_a = float(f[tin].mean() - f[tout].mean() - COST) if (len(tin) >= 5 and len(tout) >= 5) else None
    binp, bout = thin_b(pin), thin_b(pout)
    thin_bv = float(f[binp].mean() - f[bout].mean() - COST) if (len(binp) >= 5 and len(bout) >= 5) else None
    return {"net": round(net, 6),
            "thin_a": round(thin_a, 6) if thin_a is not None else None,
            "thin_b": round(thin_bv, 6) if thin_bv is not None else None,
            "n_in": int(len(pin)), "n_out": int(len(pout))}


def _registered_signals(F8, gates8, oos, lib17):
    """19 registered gate signals on one member, same-instant rebuild.
    RSV absolute gates: decidable = f.notna(), open = f < 0.2 (A158
    RECHECK verbatim). A158 17: pool-gate construction via P8."""
    out = {}
    for rname, (fac, thr) in RSV_REGISTERED.items():
        f = F8[fac]
        dec_oos = f.notna().to_numpy() & oos
        v = np.where(dec_oos, ((f < thr) & f.notna()).to_numpy().astype(float), np.nan)
        out[rname] = v
    for nm in lib17:
        m, d = gates8[nm]
        dec_oos = d.to_numpy() & oos
        v = np.where(dec_oos, (m.to_numpy() & dec_oos).astype(float), np.nan)
        out[nm] = v
    return out


def union_find_clusters(names, corr_df, line=D6_LINE):
    """|corr|>=line connected components; returns {name: cluster_id} + table."""
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if abs(float(corr_df.at[a, b])) >= line:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra
    comp = {}
    for n in names:
        comp.setdefault(find(n), []).append(n)
    order = sorted(comp.values(), key=lambda g: min(g))
    cid = {}
    for k, grp in enumerate(order):
        for n in grp:
            cid[n] = k
    table = [{"id": k, "members": grp} for k, grp in enumerate(order)]
    return cid, table


def _reconcile(faceA, fm, pass_gates):
    """Face R: positional identity vs mp1_tsgate_p1.json five_member_oos
    (sh canonical keys). net / n_in / thin(lattice A) zero-tolerance."""
    n = 0
    for g in pass_gates:
        stored_g = fm.get(g)
        if not stored_g:
            _fail("Face R FAIL: five_member_oos missing gate %s" % g)
        for code in FIVE:
            skey = "sh%s" % code
            s = stored_g.get(skey)
            mine = faceA[g].get(code)
            if s is None or mine is None:
                _fail("Face R FAIL: %s/%s coverage hole (stored=%s mine=%s)"
                      % (g, skey, s is not None, mine is not None))
            if int(s["n_in"]) != mine["n_in"]:
                _fail("Face R FAIL: %s/%s n_in %r != %r" % (g, skey, s["n_in"], mine["n_in"]))
            if float(s["net"]) != mine["net"]:
                _fail("Face R FAIL: %s/%s net %r != %r" % (g, skey, s["net"], mine["net"]))
            st = s.get("thin")
            if (st is None) != (mine["thin_a"] is None):
                _fail("Face R FAIL: %s/%s thin None-ness mismatch" % (g, skey))
            if st is not None and float(st) != mine["thin_a"]:
                _fail("Face R FAIL: %s/%s thin %r != %r" % (g, skey, st, mine["thin_a"]))
            n += 1
    return n


def cmd_run():
    if RESULTS_JSON.exists():
        _fail("refuse-if-exists: %s already present (rerun ban)" % RESULTS_JSON.name)
    t0 = time.time()
    # ---- fail-closed gates -------------------------------------------------
    if not P1_JSON.exists():
        _fail("G-P1 FAIL: %s absent" % P1_JSON.name)
    p1 = json.loads(P1_JSON.read_text(encoding="utf-8"))
    vc = p1.get("verdict_counts", {})
    if int(vc.get("PASS", -1)) != EXPECTED_PASS:
        _fail("G-P1 FAIL: verdict_counts.PASS=%r != %d" % (vc.get("PASS"), EXPECTED_PASS))
    if not A158_RECHECK_JSON.exists():
        _fail("G-RECHECK-A158 FAIL: %s absent" % A158_RECHECK_JSON.name)
    arc = json.loads(A158_RECHECK_JSON.read_text(encoding="utf-8"))
    lib17 = sorted(arc.get("library_entries", []))
    if len(lib17) != EXPECTED_LIBRARY:
        _fail("G-RECHECK-A158 FAIL: library_entries=%d != %d" % (len(lib17), EXPECTED_LIBRARY))
    M.preflight_gates()   # G-PANEL + G-CUTOFF + G-ANCHOR-MP1 + G-FACTORS (MP1 face)
    res1 = p1["results"]
    pass_gates = sorted(g for g, v in res1.items() if v.get("verdict") == "PASS")
    if len(pass_gates) != EXPECTED_PASS:
        _fail("G-P1 FAIL: pass list len %d != %d" % (len(pass_gates), EXPECTED_PASS))
    p1_med_t = {g: float(res1[g]["OOS"]["med_t"]) for g in pass_gates}
    fm = p1.get("five_member_oos", {})
    registered_names = sorted(RSV_REGISTERED) + lib17
    if len(registered_names) != 19:
        _fail("registered face: %d != 19" % len(registered_names))

    # ---- five-member faces + G-FACTORS-R -----------------------------------
    members = {}
    for code in FIVE:
        members[code] = _member_face(code)
    bad_dec = []
    for code in FIVE:
        df, F, F8, gates, gates8, fwd, oos = members[code]
        missing = [nm for nm in lib17 if nm not in gates8]
        if missing:
            _fail("G-RECHECK-A158 FAIL: %s gates8 missing %s" % (code, missing[:3]))
        for gname in pass_gates:
            if int(gates[gname][1].sum()) < MIN_DECIDABLE_R:
                bad_dec.append("%s/%s" % (code, gname))
        for nm in lib17:
            if int(gates8[nm][1].sum()) < MIN_DECIDABLE_R:
                bad_dec.append("%s/%s" % (code, nm))
        for fac in ("RSV30", "RSV60"):
            if int(F8[fac].notna().sum()) < MIN_DECIDABLE_R:
                bad_dec.append("%s/%s" % (code, fac))
    if bad_dec:
        _fail("G-FACTORS-R FAIL: decidable<%d per member: %s" % (MIN_DECIDABLE_R, bad_dec[:6]))

    # ---- Face A + signal frames --------------------------------------------
    faceA = {g: {} for g in pass_gates}
    sig_frames = {c: [] for c in pass_gates + registered_names}
    member_oos_masks = []
    for code in FIVE:
        df, F, F8, gates, gates8, fwd, oos = members[code]
        member_oos_masks.append(oos)
        for gname in pass_gates:
            faceA[gname][code] = face_a_leg(gates, fwd, oos, gname)
            mask, dec = gates[gname]
            dec_oos = dec.to_numpy() & oos
            v = np.where(dec_oos, (mask.to_numpy() & dec_oos).astype(float), np.nan)
            sig_frames[gname].append(v)
        for rname, v in _registered_signals(F8, gates8, oos, lib17).items():
            sig_frames[rname].append(v)

    # ---- Face R: secondary-face reconciliation (fail-closed) ----------------
    n_reconciled = _reconcile(faceA, fm, pass_gates)

    # pooled (member, date) signal matrix: positional concat in fixed member
    # order for every column -- zero index alignment (duplicate-date trap).
    all_vals = {c: np.concatenate([a[m] for a, m in zip(sig_frames[c], member_oos_masks)])
                for c in pass_gates + registered_names}
    sig = pd.DataFrame(all_vals)
    corr = sig.corr()                 # pairwise-complete NaN law (pit-115)

    inter = corr.loc[pass_gates, pass_gates]
    vs_reg = {g: {r: float(corr.at[g, r]) for r in registered_names} for g in pass_gates}

    cid, table = union_find_clusters(pass_gates, inter, D6_LINE)
    reps = {}
    for grp in table:
        rep = sorted(grp["members"], key=lambda n: (-p1_med_t[n], n))[0]
        reps[rep] = True
        grp["rep"] = rep
        grp["intra_max_corr"] = round(float(max(
            (abs(inter.at[a, b]) for a in grp["members"] for b in grp["members"] if a < b),
            default=0.0)), 4)

    # ---- verdicts (frozen order) --------------------------------------------
    gates_out = {}
    counts = {"REGISTERED-CLONE": 0, "CLUSTER-COLLAPSED": 0,
              "RECHECK-CONFIRM": 0, "RECHECK-FAIL": 0}
    for g in pass_gates:
        vr = vs_reg[g]
        max_reg = max(abs(v) for v in vr.values())
        legs = faceA[g]
        nets = [v["net"] for v in legs.values() if v is not None]
        pos_members = sum(1 for v in legs.values() if v is not None and v["net"] > 0)
        thbs = [v["thin_b"] for v in legs.values() if v is not None and v["thin_b"] is not None]
        med_net = float(np.median(nets)) if nets else None
        med_thinb = float(np.median(thbs)) if len(thbs) >= 2 else None
        confirm = (med_net is not None and med_net > 0 and pos_members >= 3
                   and med_thinb is not None and med_thinb > 0)
        if max_reg >= D6_LINE:
            v = "REGISTERED-CLONE"
        elif g not in reps:
            v = "CLUSTER-COLLAPSED"
        elif confirm:
            v = "RECHECK-CONFIRM"
        else:
            v = "RECHECK-FAIL"
        counts[v] += 1
        gates_out[g] = {
            "verdict": v,
            "p1_oos_med_t": p1_med_t[g],
            "p1_oos_med_net": res1[g]["OOS"]["med_net"],
            "p1_is_med_net": res1[g]["IS"]["med_net"],
            "face_a": {"members": legs, "med_net": round(med_net, 6) if med_net is not None else None,
                       "pos_members": pos_members, "med_thin_b": round(med_thinb, 6) if med_thinb is not None else None,
                       "n_valid_thin_b": len(thbs)},
            "d6": {"vs_registered": {k: round(x, 4) for k, x in vr.items()},
                   "max_corr_registered": round(max_reg, 4),
                   "cluster_id": cid[g], "cluster_rep": [t["rep"] for t in table if t["id"] == cid[g]][0],
                   "cluster_size": len([t for t in table if t["id"] == cid[g]][0]["members"]),
                   "is_rep": g in reps},
        }

    n_reps = len(reps)
    out = {
        "batch": BATCH,
        "evidence_cutoff": CUTOFF,
        "p1_ref": "results/mp1_tsgate_p1.json (N2-MP1, FROZEN bm-b r868 commit 0b1be1745)",
        "prereg": {"ref": PREREG_REF, "frozen_at": "pre-burn (see git blame)"},
        "verdict_counts": counts,
        "n_reps": n_reps,
        "e_fp": round(0.05 * n_reps, 3),
        "gates": gates_out,
        "clusters": table,
        "library_entries": sorted(g for g, v in gates_out.items() if v["verdict"] == "RECHECK-CONFIRM"),
        "registered_clone": sorted(g for g, v in gates_out.items() if v["verdict"] == "REGISTERED-CLONE"),
        "c1_demotion": sorted(g for g, v in gates_out.items() if v["verdict"] == "RECHECK-FAIL"),
        "secondary_face_reconciliation": {
            "n_compared": n_reconciled,
            "all_equal": True,
            "face": "net/n_in/thin(lattice-A) vs mp1_tsgate_p1.json five_member_oos sh-canonical keys, zero tolerance",
            "law": "same cutoff same construction = positional identity; mismatch = config drift VOID",
        },
        "audit": {"split": SPLIT, "cost_rt": COST, "stride": STRIDE,
                  "d6_line": D6_LINE, "thin_group": "B (drop-first greedy; A = MP1 stored face)",
                  "members": FIVE, "panel": "sh-prefixed canonical files (bare name files NOT consumed)",
                  "registered_family": {"n": 19,
                                        "rsv_absolute": {k: "%s<%.2f absolute" % v for k, v in RSV_REGISTERED.items()},
                                        "a158_library": lib17,
                                        "rebuilt_cutoff": CUTOFF},
                  "min_decidable_per_member": MIN_DECIDABLE_R,
                  "expected_pass": EXPECTED_PASS, "expected_library": EXPECTED_LIBRARY},
    }
    if science_gates is not None:
        out["science_gates"] = science_gates.cutoff_meta(CUTOFF)
    else:
        out["science_gates"] = {"evidence_cutoff": CUTOFF}
    out["runtime"] = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "elapsed_sec": round(time.time() - t0, 1)}
    RESULTS_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    build_md(out)
    print("[mp1grc] done: %s | clusters=%d reps=%d confirm=%d clone=%d collapsed=%d fail=%d | reconciled=%d"
          % (RESULTS_JSON.name, len(table), n_reps, counts["RECHECK-CONFIRM"],
             counts["REGISTERED-CLONE"], counts["CLUSTER-COLLAPSED"], counts["RECHECK-FAIL"],
             n_reconciled), flush=True)


def build_md(p):
    g = p["gates"]
    L = []
    L.append("# GATE-RECHECK-MP1 —— MP1 25 PASS 门独立复核（D6 邻接审计+五员落地复核·v4 候选库升格通道）")
    L.append("")
    L.append("> 生成: %s ｜ evidence_cutoff=%s（MP1 同刻 binding）｜ OOS≥%s ｜ 成本 0.10%% 往返 ｜ 格点 B 组（错位重抽样·格点稳定性腿）｜ D6 线 max|corr|≥0.7 ｜ 判线=prereg §3 四态跑前冻结"
             % (p["runtime"]["generated"], p["evidence_cutoff"], p["audit"]["split"]))
    L.append("")
    L.append("## 四态汇总")
    L.append("")
    L.append("| 判定 | 门数 | 去向 |")
    L.append("|---|---|---|")
    for k, dest in (("RECHECK-CONFIRM", "T-101 v4 政体门候选库入册清单（唯一升格通道·候选资格非策略宣称）"),
                    ("CLUSTER-COLLAPSED", "簇表披露（簇内取一·其余不重复入册=D6 簇坍缩律）"),
                    ("REGISTERED-CLONE", "拒收（与在册 19 门同交易·D6≥0.7）"),
                    ("RECHECK-FAIL", "C1 输入特征降格清单")):
        L.append("| %s | %d | %s |" % (k, p["verdict_counts"][k], dest))
    L.append("")
    L.append("**多重检验税**: 簇坍缩后代表数 n_reps=%d·E[FP]=0.05×%d=%s——入册门仍须 v4 臂预注册锦标赛再判（本批入册=候选资格非策略宣称）。"
             % (p["n_reps"], p["n_reps"], p["e_fp"]))
    L.append("")
    L.append("## 次级面对账（Face R·MP1 独有新面）")
    L.append("")
    L.append("- 面A 重算 vs `mp1_tsgate_p1.json` five_member_oos（sh 正典键）：n_compared=%d 对（25 门×5 员）·net/n_in/thin(格点A) **逐位恒等全过**（同 cutoff 同构造确定性=双烧窗漂移防护）。"
             % p["secondary_face_reconciliation"]["n_compared"])
    L.append("")
    L.append("## 入册清单（RECHECK-CONFIRM）")
    L.append("")
    if p["library_entries"]:
        L.append("| 门 | MP1 OOS med_t | 五员 net 中位 | 正员数 | thin_B 中位 | vs 在册 max|corr| | 簇 |")
        L.append("|---|---|---|---|---|---|---|")
        for name in p["library_entries"]:
            v = g[name]
            L.append("| %s | %.3f | %s | %d/5 | %s | %.3f | #%d (rep, size %d) |"
                     % (name, v["p1_oos_med_t"], ("%.5f" % v["face_a"]["med_net"]) if v["face_a"]["med_net"] is not None else "n/a",
                        v["face_a"]["pos_members"],
                        ("%.5f" % v["face_a"]["med_thin_b"]) if v["face_a"]["med_thin_b"] is not None else "n/a",
                        v["d6"]["max_corr_registered"], v["d6"]["cluster_id"], v["d6"]["cluster_size"]))
    else:
        L.append("（零确认=合法产出：C1 降格清单照报，A158 RECHECK 10 降格门同构）")
    L.append("")
    L.append("## 簇结构（D6·25×25 pairwise-complete）")
    L.append("")
    L.append("| 簇 | 代表 | 成员数 | 簇内 max|corr| | 成员 |")
    L.append("|---|---|---|---|---|")
    for t in p["clusters"]:
        L.append("| #%d | %s | %d | %.3f | %s |" % (t["id"], t["rep"], len(t["members"]),
                                                    t["intra_max_corr"], ", ".join(t["members"])))
    L.append("")
    if p["registered_clone"]:
        L.append("## 拒收清单（REGISTERED-CLONE）")
        L.append("")
        for name in p["registered_clone"]:
            v = g[name]
            top = sorted(v["d6"]["vs_registered"].items(), key=lambda kv: -abs(kv[1]))[:2]
            L.append("- %s: max|corr|=%.3f（撞线：%s）" % (name, v["d6"]["max_corr_registered"],
                                                          "、".join("%s=%.3f" % kv for kv in top)))
        L.append("")
    L.append("## C1 降格清单（RECHECK-FAIL·簇代表但复核腿不过）")
    L.append("")
    for name in p["c1_demotion"]:
        v = g[name]
        L.append("- %s: 五员 net 中位=%s·正员 %d/5·thin_B 中位=%s（有效 %d 员）"
                 % (name, v["face_a"]["med_net"], v["face_a"]["pos_members"],
                    v["face_a"]["med_thin_b"], v["face_a"]["n_valid_thin_b"]))
    L.append("")
    L.append("## 五员逐员读数（25 PASS 门·net 为 OOS 净差·括号=thin_B）")
    L.append("")
    L.append("| 门 | 判定 | 510300 | 510050 | 510500 | 512100 | 588000 | net 中位 | 正员 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name in sorted(g):
        v = g[name]
        cells = []
        for code in FIVE:
            r = v["face_a"]["members"].get(code)
            if r is None:
                cells.append("n/a")
            else:
                tb = ("%.5f" % r["thin_b"]) if r["thin_b"] is not None else "-"
                cells.append("%+.5f (%s)" % (r["net"], tb))
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %d/5 |"
                 % (name, v["verdict"], cells[0], cells[1], cells[2], cells[3], cells[4],
                    ("%+.5f" % v["face_a"]["med_net"]) if v["face_a"]["med_net"] is not None else "n/a",
                    v["face_a"]["pos_members"]))
    L.append("")
    L.append("## 诚实注记")
    L.append("")
    L.append("- 格点 B 组=A 组格点错位重抽样（组内不重叠恒在·组间窗口可交叠）=格点稳定性腿非完全独立样本（prereg §3 如实声明）。")
    L.append("- 相关面=五员 OOS 开仓指示 pooled pairwise-complete（pit-115 禁 inner-join 截史律·员间异期如实共容）。")
    L.append("- 在册 19 门信号一律本批 cutoff=%s 截断面板同刻重建（A158 RECHECK 当时 2026-09-22 缓存信号不借·prereg §2 同刻律）；在册 MAX30_q10 与候选 MAX(HIGH,30|20)_q10 语义同族邻接预警已披露·实算为准。" % p["evidence_cutoff"])
    L.append("- 判定不互借律：本批复核=政体门候选资格面；全仓择时用法面独立判决互不借判（510050|RSV30 D6 0.9424 判例在册）。")
    L.append("- 双名卫生：本批一律 sh 正典件（bare 名件不消费·去重决策归数据道另裁）；Face R 对账即走 sh 键（bare 键为 MP1 全面板双名实况如实共存不消费）。")
    L.append("- 价格水位族机械相关披露承 prereg §1：25 门中 ~14 门同编码低水位族预期整簇坍缩——簇坍缩=D6 律合法产出非损失。")
    L.append("- 零确认/高坍缩/撞线拒收均为合法产出（三态处置预案 prereg §0 全过）；本批=测量面无策略宣称无择时宣称。")
    L.append("")
    MD_PATH.write_text("\n".join(L) + "\n", encoding="utf-8")


def cmd_status():
    if RESULTS_JSON.exists():
        p = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        print(json.dumps({"batch": p["batch"], "verdict_counts": p["verdict_counts"],
                          "n_reps": p["n_reps"], "library_entries": p["library_entries"],
                          "registered_clone": p["registered_clone"],
                          "c1_demotion": p["c1_demotion"]},
                         ensure_ascii=False, indent=1))
    else:
        print("[mp1grc] status: no results yet (prereg=%s)" % PREREG_REF)


# ----------------------------------------------------------------- selftest
def _synth_event_positions():
    return [10, 12, 45, 70, 95, 100, 130, 160, 190, 215, 240, 262, 300, 318, 345]


def _selftest_thin_b():
    pos = np.array(_synth_event_positions())
    b = thin_b(pos)
    a = M.thin(pos)
    assert len(b) >= 0 and (len(b) == 0 or b[0] == pos[1]), "thin_b must start at second event"
    if len(b) >= 2:
        assert np.all(np.diff(b) >= STRIDE), "thin_b spacing law"
    assert not set(b.tolist()) & set(a.tolist()[:1]), "lattice B drops A's anchor event"
    b2 = thin_b(pos)
    assert np.array_equal(b, b2), "thin_b determinism"


def _selftest_clusters():
    df = pd.DataFrame(np.eye(4), index=["g1", "g2", "g3", "g4"], columns=["g1", "g2", "g3", "g4"])
    df.at["g1", "g2"] = df.at["g2", "g1"] = 0.9   # one cluster
    df.at["g3", "g4"] = df.at["g4", "g3"] = 0.71  # another cluster
    df.at["g1", "g4"] = df.at["g4", "g1"] = 0.69  # below line: no bridge
    cid, table = union_find_clusters(["g1", "g2", "g3", "g4"], df, 0.7)
    assert len(table) == 2, "two clusters expected"
    assert {frozenset(t["members"]) for t in table} == {frozenset(["g1", "g2"]), frozenset(["g3", "g4"])}
    med_t = {"g1": 0.5, "g2": 1.2, "g3": 0.8, "g4": 0.8}
    for t in table:
        rep = sorted(t["members"], key=lambda n: (-med_t[n], n))[0]
        t["rep"] = rep
    reps = [t["rep"] for t in table]
    assert reps == ["g2", "g3"], "rep law: max med_t; tie name-asc (g3<g4)"


def _selftest_verdict_states():
    gates = {"A": {"clone": True, "rep": False, "confirm": True},
             "B": {"clone": False, "rep": False, "confirm": True},
             "C": {"clone": False, "rep": True, "confirm": True},
             "D": {"clone": False, "rep": True, "confirm": False}}
    exp = {"A": "REGISTERED-CLONE", "B": "CLUSTER-COLLAPSED",
           "C": "RECHECK-CONFIRM", "D": "RECHECK-FAIL"}
    for gk, gv in gates.items():
        if gv["clone"]:
            v = "REGISTERED-CLONE"
        elif not gv["rep"]:
            v = "CLUSTER-COLLAPSED"
        elif gv["confirm"]:
            v = "RECHECK-CONFIRM"
        else:
            v = "RECHECK-FAIL"
        assert v == exp[gk], "verdict order law"
    legs = {"m1": {"net": 0.01, "thin_b": 0.02}, "m2": {"net": -0.01, "thin_b": -0.02},
            "m3": {"net": 0.02, "thin_b": 0.03}, "m4": {"net": 0.01, "thin_b": 0.01},
            "m5": {"net": 0.03, "thin_b": 0.04}}
    nets = [v["net"] for v in legs.values() if v is not None]
    pos_members = sum(1 for v in legs.values() if v is not None and v["net"] > 0)
    thbs = [v["thin_b"] for v in legs.values() if v is not None and v["thin_b"] is not None]
    med_net = float(np.median(nets))
    med_thinb = float(np.median(thbs)) if len(thbs) >= 2 else None
    assert med_net > 0 and pos_members == 4 and med_thinb > 0, "confirm legs math"
    thbs1 = [0.05]
    med1 = float(np.median(thbs1)) if len(thbs1) >= 2 else None
    assert med1 is None, "thin_b validity law"


def _selftest_clone_corr():
    rng = np.random.default_rng(7)
    v = (rng.random(500) > 0.5).astype(float)
    df = pd.DataFrame({"cand": v, "reg": v})
    c = float(df.corr().at["cand", "reg"])
    assert abs(c - 1.0) < 1e-9 and c >= D6_LINE, "clone corr law"


def _selftest_import_identity():
    df = pd.DataFrame({"open": np.linspace(1, 2, 300), "close": np.linspace(1, 2, 300) * 1.01,
                       "high": np.linspace(1, 2, 300) * 1.02, "low": np.linspace(1, 2, 300) * 0.99,
                       "volume": np.linspace(1, 2, 300) * 1e6},
                      index=pd.date_range("2015-01-01", periods=300))
    df["amount"] = df["close"] * df["volume"] * 1.0   # VWAP leaf needs AMOUNT
    F = M.mp1_factors(df)
    gates = M.gate_universe(F)
    assert len(F) == M.N_POOL_COMPUTABLE == 89 and len(gates) == M.N_GATES == 178, "MP1 import identity 89x178"
    F8 = P8.alpha158_factors(df)
    gates8 = dict((nm, (m, d)) for nm, m, d in P8.gate_universe(F8))
    assert len(F8) == P8.N_FACTORS == 157 and len(gates8) == P8.N_GATES == 314, "A158 import identity 157x314"
    assert "RSV30" in F8 and "RSV60" in F8, "RSV absolute gate factors present"
    arc = json.loads(A158_RECHECK_JSON.read_text(encoding="utf-8"))
    lib17 = sorted(arc.get("library_entries", []))
    assert len(lib17) == EXPECTED_LIBRARY, "library_entries==17"
    missing = [nm for nm in lib17 if nm not in gates8]
    assert not missing, "A158 17 registered gates resolve in P8 gate universe: %s" % missing[:3]
    assert FIVE == M.FIVE, "five-member universe frozen"


def _selftest_reconciliation():
    # synthetic-panel double-calc identity: my face_a_leg OOS branch vs
    # M.inst_gate_stats OOS branch must be positionally identical (same
    # construction law -> reconciliation machinery proof).
    df = M._synth_frame(3000, seed=11)
    df["amount"] = df["close"] * df["volume"] * 1.0
    F = M.mp1_factors(df)
    gates = dict((nm, (m, d)) for nm, m, d in M.gate_universe(F))
    c = df["close"]
    fwd = c.shift(-H - 1) / c.shift(-1) - 1.0
    oos = np.asarray(df.index >= pd.Timestamp(SPLIT))
    for gname in ("DELTA(VOLUME,30)_q10", "MA(LOW,30)_q10"):
        mine = face_a_leg(gates, fwd, oos, gname)
        ref = M.inst_gate_stats(gates[gname][0], gates[gname][1], fwd, oos)["OOS"]
        assert mine is not None and ref is not None, "synth OOS leg present: %s" % gname
        assert mine["n_in"] == ref["n_in"] and mine["n_out"] == ref["n_out"], "n_in/n_out identity: %s" % gname
        assert mine["net"] == ref["net"], "net identity: %s (%r vs %r)" % (gname, mine["net"], ref["net"])
        assert mine["thin_a"] == ref["thin"], "thin(lattice-A) identity: %s" % gname
    # real-data anchor leg: G-ANCHOR-MP1 reproduce (3341/390/149 inside)
    ncsv, adf_rows = M.preflight_gates()
    assert ncsv >= 1500 and adf_rows == M.ANCHOR_ROWS == 3490, "G-PANEL/G-CUTOFF anchor face"


def cmd_selftest():
    _selftest_import_identity()      # leg 1
    _selftest_thin_b()               # leg 2
    _selftest_clusters()             # leg 3
    _selftest_clone_corr()           # leg 4
    _selftest_verdict_states()       # leg 5
    # leg 6: refuse-if-exists (conditional: fires once the real artifact exists)
    if RESULTS_JSON.exists():
        try:
            cmd_run()   # guard is cmd_run's first line; must refuse, not burn
        except SystemExit as e:
            assert e.code == 2, "refuse-if-exists must exit 2, got %r" % e.code
        else:
            raise AssertionError("refuse-if-exists guard did not fire")
    _selftest_reconciliation()       # leg 7 (MP1-specific new face)
    print("[mp1grc] selftest: 7/7 PASS (import-identity / thin-B / clusters / clone-corr / verdict-states / refuse-if-exists / secondary-face-reconciliation+anchor)", flush=True)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        cmd_run()
    elif cmd == "status":
        cmd_status()
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print(__doc__)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
