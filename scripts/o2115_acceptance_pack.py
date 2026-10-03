# -*- coding: utf-8 -*-
"""O-2115 acceptance evidence pack (T-158 consumption face / O-20261002-2115 sec.3).

Deterministic L1 aggregation over in-repo artifacts: zero network, zero engine,
zero new science. Re-run any time; regenerates results/o2115_acceptance/pack_latest.json
+ docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md in place (content deterministic
except the generated/asof envelope).

Four statutory items (O-20261002-2115-bm-c.md sec.3, 10-08 governance day):
  (1) T-145 PIT audit + census H unlock evaluation + first fundamental-family prereg FROZEN
  (2) deep-axis low-amplitude new-family prereg in pool
  (3) thousand-trial wave-2 judgment face
  (4) engine fire distribution -- new-face share visible

Subcommands: run (default) | selftest
Exit codes: 0 = ok, 2 = mechanism failure (missing artifact face -> honest MISSING marker,
           never fabricated).
"""
import io
import json
import os
import sys

RB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(RB, "results")
DOCS_O2115 = os.path.join(RB, "docs", "o2115_acceptance")
OUT_DIR = os.path.join(RESULTS, "o2115_acceptance")

O2115_ISSUED = "2026-10-02 21:15"  # O-20261002-2115 issuance (order file header)

# O-2115 sec.1 named new lines -> entry-id prefixes
NEW_LINE_PREFIXES = ("FUND-", "LOWAMP-DEEP-", "MASS-TRIAL-W2-")
PERPETUAL_PREFIXES = ("PERPETUAL-N1-", "PERPETUAL-N3-", "PERPETUAL-N4-")


def classify_entry(entry_id):
    if not isinstance(entry_id, str) or not entry_id:
        return "unknown"
    if entry_id.startswith(NEW_LINE_PREFIXES):
        return "o2115_new"
    if entry_id.startswith(PERPETUAL_PREFIXES):
        return "perpetual_continuation"
    return "other_lines"


def in_window(ts, start=O2115_ISSUED):
    return isinstance(ts, str) and ts >= start


def _read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def _exists(rel):
    return os.path.exists(os.path.join(RB, rel))


def _grep_marker(path, marker):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            return marker in f.read()
    except OSError:
        return False


def pool_entries():
    p = os.path.join(RESULTS, "runnable_pool.json")
    d = _read_json(p)
    items = d if isinstance(d, list) else d.get("entries", d.get("items", []))
    return {e.get("id"): e for e in items if isinstance(e, dict) and e.get("id")}


def pool_family_state(prefix):
    """Aggregate status of pool entries whose id starts with prefix."""
    ent = pool_entries()
    fam = {k: v for k, v in ent.items() if k.startswith(prefix)}
    per_status = {}
    for k, v in fam.items():
        per_status.setdefault(v.get("status", "?"), []).append(k)
    return {
        "n_entries": len(fam),
        "by_status": {s: len(v) for s, v in sorted(per_status.items())},
        "done_share": (len(per_status.get("done", [])) / len(fam)) if fam else 0.0,
        "ids": sorted(fam.keys()),
    }


def fire_distribution():
    """Count autofill launches per machine since O-2115 issuance; classify faces."""
    per_machine = {}
    for mid in ("bm-a", "bm-b", "bm-c"):
        p = os.path.join(RESULTS, "autofill_state.%s.json" % mid)
        if not os.path.exists(p):
            per_machine[mid] = {"missing": True, "launches": 0, "classes": {}}
            continue
        d = _read_json(p)
        classes = {}
        n = 0
        for l in d.get("launches", []):
            if not in_window(l.get("ts")):
                continue
            n += 1
            c = classify_entry(l.get("entry"))
            classes[c] = classes.get(c, 0) + 1
        per_machine[mid] = {"missing": False, "launches": n, "classes": classes}
    total = sum(m["launches"] for m in per_machine.values())
    agg = {}
    for m in per_machine.values():
        for c, k in m["classes"].items():
            agg[c] = agg.get(c, 0) + k
    new = agg.get("o2115_new", 0)
    return {
        "window_start": O2115_ISSUED,
        "per_machine": per_machine,
        "total_launches": total,
        "class_totals": agg,
        "o2115_new_share": (new / total) if total else 0.0,
    }


def prereg_frozen(fam):
    """Mechanical freeze evidence: pool registration face (prereg_ref carries FROZEN,
    pool admission = the operative freeze record) + prereg template freeze clause
    (跑前 commit 冻结) present in the file itself."""
    path = os.path.join(RB, "research", "%s.md" % fam)
    if not os.path.exists(path):
        return False, "prereg_file_missing"
    tmpl = _grep_marker(path, "跑前 commit 冻结")
    pool_frozen = False
    for k, v in pool_entries().items():
        if k.startswith(fam) and "FROZEN" in (v.get("prereg_ref") or ""):
            pool_frozen = True
            break
    return (tmpl and pool_frozen), "pool prereg_ref FROZEN + template freeze clause"


def item1_fundamentals():
    ev = []
    pit_ok = _exists(r"results\fund_pit_audit\audit_results.json")
    ev.append({"face": "pit_audit", "present": pit_ok,
               "ref": "results/fund_pit_audit/audit_results.json (bm-c 2026-10-02 21:21, structure PASS)"})
    unlock = None
    if _exists(r"results\fund_h_unlock_eval.json"):
        unlock = _read_json(r"results\fund_h_unlock_eval.json")
        ev.append({"face": "unlock_eval", "present": True,
                   "n_unlock": unlock.get("n_unlock"), "n_stay_locked": unlock.get("n_stay_locked"),
                   "ref": "results/fund_h_unlock_eval.json (T-145 leg b)"})
    else:
        ev.append({"face": "unlock_eval", "present": False})
    ds = None
    if _exists(r"results\fund_history_status.json"):
        ds = _read_json(r"results\fund_history_status.json")
        ev.append({"face": "dataset_complete", "present": bool(ds.get("complete")),
                   "done_symbols": ds.get("done_symbols"), "ref": "results/fund_history_status.json (T-131)"})
    else:
        ev.append({"face": "dataset_complete", "present": False})
    frozen = []
    for fam in ("FUND-VALUE-P1", "FUND-QUALITY-P1", "FUND-DIVLOWVOL-P1"):
        is_frozen, how = prereg_frozen(fam)
        frozen.append({"family": fam, "prereg_frozen": is_frozen,
                       "freeze_evidence": how, "pool": pool_family_state(fam)})
    met = (pit_ok and unlock is not None and ds is not None
           and all(f["prereg_frozen"] for f in frozen))
    return {"item": 1, "title": "T-145 PIT审计+解锁评估+首批基本面族prereg冻结",
            "status": "met" if met else "partial", "evidence": ev, "frozen_families": frozen}


def item2_deep_axis():
    is_frozen, how = prereg_frozen("LOWAMP-DEEP-P1")
    pool = pool_family_state("LOWAMP-DEEP-P1")
    in_pool = is_frozen and pool["n_entries"] > 0
    return {"item": 2, "title": "深轴低振幅新家族prereg在池",
            "status": "met" if in_pool else "partial",
            "evidence": [{"face": "prereg_frozen", "present": is_frozen,
                          "freeze_evidence": how, "ref": "research/LOWAMP-DEEP-P1.md"},
                         {"face": "pool_state", "present": True, **pool}]}


def item3_w2_judgment():
    p = os.path.join(RESULTS, "mass_trial", "w2_judge.json")
    if not os.path.exists(p):
        return {"item": 3, "title": "千人wave-2判决面", "status": "pending",
                "evidence": [{"face": "w2_judge", "present": False}]}
    d = _read_json(p)
    complete = bool(d.get("complete"))
    neg = {"n_judge_cells": d.get("n_judge_cells"), "n_eligible_g2": d.get("n_eligible_g2"),
           "n_stage1_survivors": d.get("n_stage1_survivors"), "evidence_cutoff": d.get("evidence_cutoff")}
    return {"item": 3, "title": "千人wave-2判决面",
            "status": "met" if complete else "in_flight",
            "verdict_note": ("judged LANDED r444 -- honest NEGATIVE: eligible_g2=0 "
                             "(E[FP]=40.25 @ nominal 5%), funnel does not survive G2 at thousand-scale"
                             if complete and d.get("n_eligible_g2") == 0 else None),
            "evidence": [{"face": "w2_judge", "present": True, **neg,
                          "ref": "results/mass_trial/w2_judge.json + T-158 r444"}]}


def item4_fire():
    fd = fire_distribution()
    fd["title"] = "引擎火力分布新面孔占比"
    fd["item"] = 4
    fd["status"] = "met" if fd["total_launches"] > 0 else "pending"
    return fd


def risk_flags():
    ent = pool_entries()
    nulls = {k: ent.get(k, {}).get("status", "MISSING")
             for k in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS")}
    return [
        {"flag": "fund_trio_nulls_pool_state", "state": nulls,
         "note": "rightful burner = bm-b per MSG-1132/MSG-1155 division (r617-r620); "
                 "off-caliber-era burns killed+discarded (r622/r629); finalize window 10-05..10-09"},
        {"flag": "pre_ruling_G_SEG", "note": "G-SEG structural: monthly-freq chop=14<50 -> "
                 "verdict=insufficient-sample before all gates; GM ruling pending (bm-a zero unilateral action, r633 MSG-2026-10-03-1720)"},
        {"flag": "pre_ruling_VALUE_passive", "note": "FUND-VALUE cmd_finalize passive-window crash "
                 "(t0=1994-05-03 -> base_j=0); owner-fix = bm-b (r633 MSG-2026-10-03-1720)"},
        {"flag": "n1_supply", "note": "W116+ N1 supply assessment: O-2115 sec-2 supply priority = "
                 "new-direction furnaces > perpetual N1 deep-dig (113 waves diminishing); "
                 "fund-trio in flight -> N1 stays closed this window"},
    ]


def build_pack():
    import datetime
    now = datetime.datetime.now()
    pack = {
        "generated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "asof_date": now.strftime("%Y-%m-%d"),
        "order_ref": "O-20261002-2115-bm-c sec.3 (10-08 governance-day acceptance)",
        "acceptance_date": "2026-10-08",
        "machine_view": "bm-c (shared-artifact aggregation, machine-agnostic rerun)",
        "items": [item1_fundamentals(), item2_deep_axis(), item3_w2_judgment(), item4_fire()],
        "risk_flags": risk_flags(),
    }
    statuses = [i["status"] for i in pack["items"]]
    pack["summary"] = {
        "n_met": statuses.count("met"),
        "statuses": statuses,
        "pack_verdict": ("ALL_MET" if all(s == "met" for s in statuses)
                         else "PARTIAL (%d/4 met)" % statuses.count("met")),
    }
    return pack


def render_md(pack):
    L = []
    L.append("# O-2115 验收实况页（10-08 治理日证据包 · 可复跑自动再生）")
    L.append("")
    L.append("- 生成：%s · 视角：%s · 验收日：%s" % (pack["generated"], pack["machine_view"], pack["acceptance_date"]))
    L.append("- 总判：**%s**（逐件见下；负结果如实照报）" % pack["summary"]["pack_verdict"])
    L.append("")
    for it in pack["items"]:
        L.append("## 件%d · %s — %s" % (it["item"], it["title"], it["status"].upper()))
        if it["item"] == 4:
            fd = it
            L.append("")
            L.append("窗口（%s 起）三机 autofill 点火计数：**总 %d 次**" % (fd["window_start"], fd["total_launches"]))
            L.append("")
            L.append("| 类别 | 次数 |")
            L.append("|---|---|")
            for c, k in sorted(fd["class_totals"].items()):
                L.append("| %s | %d |" % (c, k))
            L.append("")
            L.append("**O-2115 新面孔占比 = %.1f%%**（分母=窗口内全部点火）" % (100.0 * fd["o2115_new_share"]))
            L.append("")
            L.append("| 机器 | 窗口内点火 | 分类 |")
            L.append("|---|---|---|")
            for mid, m in sorted(fd["per_machine"].items()):
                L.append("| %s | %d | %s |" % (mid, m["launches"], json.dumps(m["classes"], ensure_ascii=False)))
            L.append("")
            continue
        if it.get("verdict_note"):
            L.append("")
            L.append("> %s" % it["verdict_note"])
        L.append("")
        for e in it.get("evidence", []):
            bits = []
            for kk in ("face", "present", "n_unlock", "n_stay_locked", "done_symbols",
                       "n_entries", "done_share", "by_status", "n_judge_cells",
                       "n_eligible_g2", "n_stage1_survivors", "evidence_cutoff"):
                if kk in e:
                    bits.append("%s=%s" % (kk, json.dumps(e[kk], ensure_ascii=False) if not isinstance(e[kk], (int, float, bool)) else e[kk]))
            if "ref" in e:
                bits.append("ref=%s" % e["ref"])
            L.append("- " + " · ".join(bits))
        for f in it.get("frozen_families", []):
            L.append("- 族 %s：prereg FROZEN=%s · 池 %d 面 done占比 %.0f%%" %
                     (f["family"], f["prereg_frozen"], f["pool"]["n_entries"], 100.0 * f["pool"]["done_share"]))
        L.append("")
    L.append("## 风险与待决旗")
    L.append("")
    for r in pack["risk_flags"]:
        st = r.get("state")
        L.append("- **%s**：%s%s" % (r["flag"], r["note"], (" 状态=%s" % json.dumps(st, ensure_ascii=False)) if st else ""))
    L.append("")
    L.append("---")
    L.append("再跑：`python scripts/o2115_acceptance_pack.py run` · 自检：`selftest` · 证据零网络零新判据，纯聚合面。")
    return "\n".join(L) + "\n"


def cmd_run():
    pack = build_pack()
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    with io.open(os.path.join(OUT_DIR, "pack_latest.json"), "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=1)
    if not os.path.isdir(DOCS_O2115):
        os.makedirs(DOCS_O2115)
    with io.open(os.path.join(DOCS_O2115, "O2115-ACCEPTANCE-LIVE.md"), "w", encoding="utf-8") as f:
        f.write(render_md(pack))
    print("PACK_OK verdict=%s items=%s new_share=%.3f out=%s" %
          (pack["summary"]["pack_verdict"], pack["summary"]["statuses"],
           pack["items"][3]["o2115_new_share"], os.path.join(OUT_DIR, "pack_latest.json")))
    return 0


def cmd_selftest():
    fails = []
    # classification
    cases = [("FUND-VALUE-P1-NULLS", "o2115_new"), ("LOWAMP-DEEP-P1-NULLS", "o2115_new"),
             ("MASS-TRIAL-W2-JUDGE-SHARD-0", "o2115_new"), ("PERPETUAL-N1-W5-SHARD-2", "perpetual_continuation"),
             ("PERPETUAL-N3-R2-COMPOSITE-CE-01", "perpetual_continuation"),
             ("CONTEST-YTD-P1-SHARD-0OF8", "other_lines"), ("", "unknown"), (None, "unknown")]
    for cid, want in cases:
        got = classify_entry(cid)
        if got != want:
            fails.append("classify %r -> %s want %s" % (cid, got, want))
    # window
    if not in_window("2026-10-03 02:09:09"):
        fails.append("in_window true-case failed")
    if in_window("2026-10-01 09:26:02"):
        fails.append("in_window false-case failed")
    if in_window(None):
        fails.append("in_window None-case failed")
    # md render hermetic
    pack = {"generated": "T", "machine_view": "bm-c", "acceptance_date": "2026-10-08",
            "summary": {"pack_verdict": "X"},
            "items": [{"item": 3, "title": "t", "status": "met", "verdict_note": "n",
                       "evidence": [{"face": "w2_judge", "present": True, "n_judge_cells": 805}]}],
            "risk_flags": [{"flag": "f", "note": "n"}]}
    md = render_md(pack)
    if "件3" not in md or "风险与待决旗" not in md or "f" not in md:
        fails.append("render_md content missing")
    print("SELFTEST %s (%d fails)" % ("PASS" if not fails else "FAIL", len(fails)))
    for x in fails:
        print("  FAIL:", x)
    return 0 if not fails else 2


def main(argv):
    sub = argv[1] if len(argv) > 1 else "run"
    if sub == "run":
        return cmd_run()
    if sub == "selftest":
        return cmd_selftest()
    print("usage: o2115_acceptance_pack.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
