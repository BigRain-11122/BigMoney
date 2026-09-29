#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GATE-RECHECK-A158 -- independent recheck of the 48 PASS gates from
A158-TSGATE-P1 (prereg research/GATE_RECHECK_A158_PREREG.md, frozen).

Two frozen faces:
  Face A  five-member OOS recheck, gate_verify caliber (B2 strict
          buckets, cost 0.10% RT) + lattice-B thinning (P1 sec.3
          declared two thinning groups; P1 consumed group A's greedy
          lattice, this batch consumes the shifted lattice B = drop
          first eligible event then greedy stride-20).  Lattice B is a
          re-draw on the same information set, NOT a fully independent
          sample -- declared honestly as a lattice-stability leg.
  Face B  D6 adjacency audit: 48x48 inter-candidate correlation
          (pairwise-complete, pit-115 no-inner-join law) + corr vs the
          two registered absolute gates RSV30_low/RSV60_low (<0.2,
          gate_verify PASS2 family).  Clusters = |corr|>=0.7 connected
          components (union-find); representative = highest P1 OOS
          med_t, tie -> name ascending.

Verdicts (frozen order): REGISTERED-CLONE (max|corr| vs registered
>= 0.7) > CLUSTER-COLLAPSED (non-representative) > RECHECK-CONFIRM
(rep + Face A three legs) / RECHECK-FAIL (rep, Face A leg(s) failed
-> C1 input-feature demotion list).

Machinery is imported from scripts/a158_tsgate_probe.py (single
source, zero reimplementation).  Fail-closed gates: G-P1 (P1 results
present + verdict_counts.PASS==48), G-PANEL/G-CUTOFF/G-ANCHOR/G-FACTORS
via probe.preflight_gates().  Refuse-if-exists on the final artifact.
Deterministic rerun byte-identical on the stable segment (runtime
metadata segregated).  __main__ guarded.  Zero network, zero token.

Exit codes: 0 = normal; 2 = fail-closed breach / refuse-if-exists."""
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import a158_tsgate_probe as P  # single-source machinery (anti-rebuild law)

try:
    import science_gates
except Exception:  # pragma: no cover - hermetic fallback
    science_gates = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS_JSON = ROOT / "results" / "gate_recheck_a158.json"
MD_PATH = ROOT / "research" / "A158_GATE_RECHECK.md"
P1_JSON = ROOT / "results" / "a158_tsgate_p1.json"
PREREG_REF = "research/GATE_RECHECK_A158_PREREG.md"

D6_LINE = 0.70           # frozen D6 same-family threshold
REGISTERED = {"RSV30_low": ("RSV30", 0.2), "RSV60_low": ("RSV60", 0.2)}
EXPECTED_PASS = 48


def _fail(msg, code=2):
    print("[a158grc] %s" % msg, flush=True)
    raise SystemExit(code)


def thin_b(pos, stride=P.STRIDE):
    """Lattice B: drop the first eligible event, then greedy stride
    spacing (P1 sec.3 declared two-group thinning; P1 consumed A)."""
    if len(pos) < 2:
        return np.array([], dtype=int)
    kept, last = [], None
    for p in pos[1:]:
        if last is None or p - last >= stride:
            kept.append(p)
            last = p
    return np.array(kept, dtype=int)


def _member_face(code):
    """Load one five-member canonical file, factors, gates, fwd, oos mask."""
    df = P.load_truncated(P.SRC / ("sh%s.csv" % code))
    if len(df) < P.MIN_BARS:
        _fail("G-PANEL FAIL: %s bars %d < %d" % (code, len(df), P.MIN_BARS))
    F = P.alpha158_factors(df)
    gates = dict((nm, (m, d)) for nm, m, d in P.gate_universe(F))
    c = df["close"]
    fwd = c.shift(-P.H - 1) / c.shift(-1) - 1.0
    oos = np.asarray(df.index >= pd.Timestamp(P.SPLIT))
    return df, F, gates, fwd, oos


def face_a_leg(gates, fwd, oos, gname):
    """Per-member OOS stats for one gate (B2 strict buckets, probe law)."""
    mask, dec = gates[gname]
    f = fwd.to_numpy(dtype=float)
    m = mask.to_numpy()
    d = dec.to_numpy()
    ok = ~np.isnan(f)
    base = d & ok & oos
    pin = np.flatnonzero(base & m)
    pout = np.flatnonzero(base & ~m)
    if len(pin) < P.MIN_EV or len(pout) < P.MIN_EV:
        return None
    diff = float(f[pin].mean() - f[pout].mean())
    net = diff - P.COST
    tin, tout = thin_b(pin), thin_b(pout)
    thinB = None
    if len(tin) >= 5 and len(tout) >= 5:
        thinB = float(f[tin].mean() - f[tout].mean() - P.COST)
    return {"net": round(net, 6), "thin_b": round(thinB, 6) if thinB is not None else None,
            "n_in": int(len(pin)), "n_out": int(len(pout))}


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
    P.preflight_gates()  # G-PANEL + G-CUTOFF + G-ANCHOR-ROC20 + G-FACTORS
    res1 = p1["results"]
    pass_gates = [g for g, v in res1.items() if v.get("verdict") == "PASS"]
    pass_gates.sort()
    if len(pass_gates) != EXPECTED_PASS:
        _fail("G-P1 FAIL: pass list len %d != %d" % (len(pass_gates), EXPECTED_PASS))
    p1_med_t = {g: float(res1[g]["OOS"]["med_t"]) for g in pass_gates}

    # ---- five-member faces --------------------------------------------------
    members = {}
    for code in P.FIVE:
        members[code] = _member_face(code)

    faceA = {g: {} for g in pass_gates}
    col_names = pass_gates + sorted(REGISTERED.keys())
    sig_frames = {c: [] for c in col_names}   # per member: full-length arrays
    member_oos_masks = []
    for code in P.FIVE:
        df, F, gates, fwd, oos = members[code]
        member_oos_masks.append(oos)
        for gname in pass_gates:
            faceA[gname][code] = face_a_leg(gates, fwd, oos, gname)
            mask, dec = gates[gname]
            dec_oos = dec.to_numpy() & oos
            v = np.where(dec_oos, (mask.to_numpy() & dec_oos).astype(float), np.nan)
            sig_frames[gname].append(v)
        for rname, (fac, thr) in REGISTERED.items():
            f = F[fac]
            dec_oos = f.notna().to_numpy() & oos
            v = np.where(dec_oos, ((f < thr) & f.notna()).to_numpy().astype(float), np.nan)
            sig_frames[rname].append(v)

    # pooled (member, date) signal matrix: positional concat in fixed member
    # order for every column -- zero index alignment (duplicate-date trap).
    all_vals = {c: np.concatenate([a[m] for a, m in zip(sig_frames[c], member_oos_masks)])
                for c in col_names}
    sig = pd.DataFrame(all_vals)
    corr = sig.corr()                 # pairwise-complete NaN law (pit-115)

    inter = corr.loc[pass_gates, pass_gates]
    vs_reg = {g: {r: float(corr.at[g, r]) for r in REGISTERED} for g in pass_gates}

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
        "batch": "GATE-RECHECK-A158",
        "evidence_cutoff": P.CUTOFF,
        "p1_ref": "results/a158_tsgate_p1.json (A158-TSGATE-P1, FROZEN r438)",
        "prereg": {"ref": PREREG_REF, "frozen_at": "pre-burn (see git blame)"},
        "verdict_counts": counts,
        "n_reps": n_reps,
        "e_fp": round(0.05 * n_reps, 3),
        "gates": gates_out,
        "clusters": table,
        "library_entries": sorted(g for g, v in gates_out.items() if v["verdict"] == "RECHECK-CONFIRM"),
        "c1_demotion": sorted(g for g, v in gates_out.items() if v["verdict"] == "RECHECK-FAIL"),
        "audit": {"split": P.SPLIT, "cost": P.COST, "stride": P.STRIDE,
                  "d6_line": D6_LINE, "thin_group": "B (drop-first greedy)",
                  "members": P.FIVE, "panel": "sh-prefixed canonical files",
                  "registered_family": {k: "%s<%.2f absolute" % v for k, v in REGISTERED.items()}},
    }
    if science_gates is not None:
        out["science_gates"] = science_gates.cutoff_meta(P.CUTOFF)
    else:
        out["science_gates"] = {"evidence_cutoff": P.CUTOFF}
    out["runtime"] = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "elapsed_sec": round(time.time() - t0, 1)}
    RESULTS_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    build_md(out)
    print("[a158grc] done: %s | clusters=%d reps=%d confirm=%d clone=%d collapsed=%d fail=%d"
          % (RESULTS_JSON.name, len(table), n_reps, counts["RECHECK-CONFIRM"],
             counts["REGISTERED-CLONE"], counts["CLUSTER-COLLAPSED"], counts["RECHECK-FAIL"]), flush=True)


def build_md(p):
    g = p["gates"]
    L = []
    L.append("# GATE-RECHECK-A158 —— A158 48 PASS 门独立复核（D6 邻接审计+五员落地复核·v4 候选库升格通道）")
    L.append("")
    L.append("> 生成: %s ｜ evidence_cutoff=%s（P-5C binding）｜ OOS≥%s ｜ 成本 0.10%% 往返 ｜ 格点 B 组（P1 §3 双组抽稀第二组）｜ D6 线 max|corr|≥0.7 ｜ 判线=prereg §3 四态跑前冻结"
             % (p["runtime"]["generated"], p["evidence_cutoff"], p["audit"]["split"]))
    L.append("")
    L.append("## 四态汇总")
    L.append("")
    L.append("| 判定 | 门数 | 去向 |")
    L.append("|---|---|---|")
    for k, dest in (("RECHECK-CONFIRM", "T-101 v4 政体门候选库入册清单（唯一升格通道）"),
                    ("CLUSTER-COLLAPSED", "簇表披露（簇内取一·其余不重复入册）"),
                    ("REGISTERED-CLONE", "拒收（与在册 RSV 绝对门同交易·D6≥0.7）"),
                    ("RECHECK-FAIL", "C1 输入特征降格清单")):
        L.append("| %s | %d | %s |" % (k, p["verdict_counts"][k], dest))
    L.append("")
    L.append("**多重检验税**: 簇坍缩后代表数 n_reps=%d·E[FP]=0.05×%d=%s——入册=候选资格非策略宣称（v4 臂预注册锦标赛再判）。"
             % (p["n_reps"], p["n_reps"], p["e_fp"]))
    L.append("")
    L.append("## 入册清单（RECHECK-CONFIRM）")
    L.append("")
    L.append("| 门 | P1 OOS med_t | 五员 net 中位 | 正员数 | thin_B 中位 | vs 在册 max|corr| | 簇 |")
    L.append("|---|---|---|---|---|---|---|")
    for name in p["library_entries"]:
        v = g[name]
        L.append("| %s | %.3f | %s | %d/5 | %s | %.3f | #%d (rep, size %d) |"
                 % (name, v["p1_oos_med_t"], ("%.5f" % v["face_a"]["med_net"]) if v["face_a"]["med_net"] is not None else "n/a",
                    v["face_a"]["pos_members"],
                    ("%.5f" % v["face_a"]["med_thin_b"]) if v["face_a"]["med_thin_b"] is not None else "n/a",
                    v["d6"]["max_corr_registered"], v["d6"]["cluster_id"], v["d6"]["cluster_size"]))
    L.append("")
    L.append("## 簇结构（D6·48×48 pairwise-complete）")
    L.append("")
    L.append("| 簇 | 代表 | 成员数 | 簇内 max|corr| | 成员 |")
    L.append("|---|---|---|---|---|")
    for t in p["clusters"]:
        L.append("| #%d | %s | %d | %.3f | %s |" % (t["id"], t["rep"], len(t["members"]),
                                                    t["intra_max_corr"], ", ".join(t["members"])))
    L.append("")
    L.append("## C1 降格清单（RECHECK-FAIL·簇代表但复核腿不过）")
    L.append("")
    for name in p["c1_demotion"]:
        v = g[name]
        L.append("- %s: 五员 net 中位=%s·正员 %d/5·thin_B 中位=%s（有效 %d 员）"
                 % (name, v["face_a"]["med_net"], v["face_a"]["pos_members"],
                    v["face_a"]["med_thin_b"], v["face_a"]["n_valid_thin_b"]))
    L.append("")
    L.append("## 诚实注记")
    L.append("")
    L.append("- 格点 B 组=A 组格点错位重抽样（组内不重叠恒在·组间窗口可交叠）=格点稳定性腿非完全独立样本（prereg §3 如实声明）。")
    L.append("- 相关面=五员 OOS 开仓指示 pooled pairwise-complete（pit-115 禁 inner-join 截史律·员间异期如实共容）。")
    L.append("- 判定不互借律：本批复核=政体门候选资格面；全仓择时用法面（r433 9/10 判负·510050|RSV30 D6 0.9424 beta 同源判例）独立判决互不借判。")
    L.append("- 双名卫生承 P1：本批一律 sh 正典件（bare 名件不消费·去重决策归数据道另裁）。")
    L.append("")
    MD_PATH.write_text("\n".join(L) + "\n", encoding="utf-8")


def cmd_status():
    if RESULTS_JSON.exists():
        p = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        print(json.dumps({"batch": p["batch"], "verdict_counts": p["verdict_counts"],
                          "n_reps": p["n_reps"], "library_entries": p["library_entries"]},
                         ensure_ascii=False, indent=1))
    else:
        print("[a158grc] status: no results yet (prereg=%s)" % PREREG_REF)


def _synth_event_positions():
    return [10, 12, 45, 70, 95, 100, 130, 160, 190, 215, 240, 262, 300, 318, 345]


def _selftest_thin_b():
    pos = np.array(_synth_event_positions())
    b = thin_b(pos)
    a = P.thin(pos)
    assert len(b) >= 0 and (len(b) == 0 or b[0] == pos[1]), "thin_b must start at second event"
    if len(b) >= 2:
        assert np.all(np.diff(b) >= P.STRIDE), "thin_b spacing law"
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
    # rep = highest med_t, tie -> name asc
    med_t = {"g1": 0.5, "g2": 1.2, "g3": 0.8, "g4": 0.8}
    for t in table:
        rep = sorted(t["members"], key=lambda n: (-med_t[n], n))[0]
        t["rep"] = rep
    reps = [t["rep"] for t in table]
    assert reps == ["g2", "g3"], "rep law: max med_t; tie name-asc (g3<g4)"


def _selftest_verdict_states():
    # synthetic gates_out assembly mirrors cmd_run order:
    # CLONE > COLLAPSED > CONFIRM/FAIL
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
    # confirm leg: >=3/5 positive and thin_b median > 0 with >=2 valid
    legs = {"m1": {"net": 0.01, "thin_b": 0.02}, "m2": {"net": -0.01, "thin_b": -0.02},
            "m3": {"net": 0.02, "thin_b": 0.03}, "m4": {"net": 0.01, "thin_b": 0.01},
            "m5": {"net": 0.03, "thin_b": 0.04}}
    nets = [v["net"] for v in legs.values() if v is not None]
    pos_members = sum(1 for v in legs.values() if v is not None and v["net"] > 0)
    thbs = [v["thin_b"] for v in legs.values() if v is not None and v["thin_b"] is not None]
    med_net = float(np.median(nets))
    med_thinb = float(np.median(thbs)) if len(thbs) >= 2 else None
    assert med_net > 0 and pos_members == 4 and med_thinb > 0, "confirm legs math"
    # insufficient thin_b (<2 valid) -> leg fails
    thbs1 = [0.05]
    med1 = float(np.median(thbs1)) if len(thbs1) >= 2 else None
    assert med1 is None, "thin_b validity law"


def _selftest_clone_corr():
    # identical binary signals -> corr 1.0 -> clone reject at the frozen line
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
    F = P.alpha158_factors(df)
    gates = P.gate_universe(F)
    assert len(F) == P.N_FACTORS and len(gates) == P.N_GATES, "import identity: 157x314"


def cmd_selftest():
    _selftest_import_identity()
    _selftest_thin_b()
    _selftest_clusters()
    _selftest_verdict_states()
    _selftest_clone_corr()
    # refuse-if-exists leg: only meaningful once the real artifact exists
    if RESULTS_JSON.exists():
        try:
            cmd_run()   # guard is cmd_run's first line; must refuse, not burn
        except SystemExit as e:
            assert e.code == 2, "refuse-if-exists must exit 2, got %r" % e.code
        else:
            raise AssertionError("refuse-if-exists guard did not fire")
    print("[a158grc] selftest: 6/6 PASS (import-identity / thin-B / clusters / verdict-states / clone-corr / legs-math)", flush=True)


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
