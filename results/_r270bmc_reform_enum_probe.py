"""_r270bmc_reform_enum_probe.py — O-20260930-1058/O-1101 重估面步①：档存枚举。

机械档存重读（零重烧·禁翻案律兼容）：
  - W1-W12 w{N}_judge.json + w{N}_screen_cells.csv 档存读取；
  - 技能线过线者（g1_pass=true）全枚举 + 各波最佳（passers 内 max dsr；无 passer 波=全 cells max dsr 诚实标注非过线）；
  - 每员四维原始材料抽取（收益面/稳健面/防过拟合面/防运气面——重估评分面的输入面）。

诚实标注（MSG-20260930-1330 §1/§4）：
  - 本枚举全部读数=RW-1 修复前引擎产出（pre-RW-1 archive epoch）——重估烧批在 RW-1~4 全绿解冻后
    以新引擎重跑产生新读数；本件读数仅作档存盘点与四维材料索引，不作重估评分值。
  - dsr/n_trials=全局试验账本时代读数（改革废除面·O-1058 §一定谳）——重估时由批内 FDR q≤10% 替代。

产出：
  - results/registration_reform/REEVAL_ROSTER_W1_W12.json（重估面持久名册·烧批消费面）
  - results/_r270bmc_reform_enum_facts.json（探针证据件）

用法：python results/_r270bmc_reform_enum_probe.py [--selftest]
"""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVES = list(range(1, 13))  # W1-W12（W13 在飞按其冻结预注册跑完不污染·O-1058 §三2）
ROSTER_OUT = os.path.join(ROOT, "results", "registration_reform", "REEVAL_ROSTER_W1_W12.json")
FACTS_OUT = os.path.join(ROOT, "results", "_r270bmc_reform_enum_facts.json")
ENGINE_EPOCH = "pre-RW-1-archive"  # MSG-1330 §1：旧引擎读数一律作废=本件仅档存盘点不作评分值


def load_wave(wave: int):
    judge_path = os.path.join(ROOT, "results", f"trial_labor_w{wave}", f"w{wave}_judge.json")
    screen_path = os.path.join(ROOT, "results", f"trial_labor_w{wave}", f"w{wave}_screen_cells.csv")
    with open(judge_path, encoding="utf-8") as f:
        judge = json.load(f)
    screen = {}
    with open(screen_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            screen[row["candidate_id"]] = row
    return judge, screen


def four_dim_materials(cell: dict, screen_row) -> dict:
    """四维原始材料（档存面·pre-RW-1 epoch）。"""
    legs = cell.get("legs", {}) or {}
    legL = legs.get("L", {}) or {}
    dual = cell.get("dual_nulls", {}) or {}
    dsr_obj = cell.get("dsr", {}) or {}
    g1 = cell.get("g1_prime_v2", {}) or {}
    beat = legL.get("beat", {}) or {}
    return {
        "ret": {  # ①收益面（O-1058 §二2：Sharpe/年化/收益天花板 O-1126——天花板面=冻结窗步②接线）
            "sharpe_full_L": legL.get("sharpe_full"),
            "beat6m_rate_L": (beat.get("6m") or {}).get("rate"),
            "beat12m_rate_L": (beat.get("12m") or {}).get("rate"),
            "beat24m_rate_L": (beat.get("24m") or {}).get("rate"),
            "n_trades_L": legL.get("n_trades"),
            "n_entries_L": legL.get("n_entries"),
        },
        "robust": {  # ②稳健面：bootstrap 下界/政体分段/成本×2（成本面=烧批重跑时新引擎产出·档存面无）
            "dual_bootstrap_ci": dual.get("bootstrap_ci"),
            "dual_ci_lower_positive": dual.get("ci_lower_positive"),
            "dual_signflip_p": dual.get("signflip_p"),
            "g1_ci95_low": ((g1.get("bootstrap_ci") or {}).get("ci95_low")),
            "regime_start_windows_L": legL.get("regime_start_windows"),
            "dd_full": (float(screen_row["dd_full"]) if screen_row and screen_row.get("dd_full") not in (None, "") else None),
        },
        "anti_overfit": {  # ③防过拟合面：族内 PBO（D6 跨族相关=冻结窗步⑤补全面）
            "family_pbo": cell.get("family_pbo"),
        },
        "anti_luck": {  # ④防运气面：全局账本时代 DSR（改革后=批内折减 DSR 四维之一·非唯一处刑门）
            "dsr_global_era": dsr_obj.get("dsr"),
            "n_trials_global_era": dsr_obj.get("n_trials"),
        },
        "meta": {
            "family": (screen_row.get("family") if screen_row else None),
            "module": (screen_row.get("module") if screen_row else None),
            "fn": (screen_row.get("fn") if screen_row else None),
            "verdict_archived": cell.get("verdict"),
        },
    }


def build_roster():
    per_wave = {}
    passers = []
    wave_bests = []
    for wave in WAVES:
        judge, screen = load_wave(wave)
        cells = judge.get("cells", [])
        wave_passers = [c for c in cells if c.get("g1_pass")]
        for c in wave_passers:
            passers.append((wave, c, screen.get(c.get("candidate_id"))))
        if wave_passers:
            best = max(wave_passers, key=lambda c: (c.get("dsr") or {}).get("dsr", 0.0))
            best_note = "best-of-wave (skill-line passer)"
        else:
            best = max(cells, key=lambda c: ((c.get("dsr") or {}).get("dsr", 0.0), (c.get("g1_prime_v2") or {}).get("sharpe_full", 0.0)))
            best_note = "best-of-wave HONEST-NON-PASSER (zero skill-line passer in wave)"
        wave_bests.append((wave, best, screen.get(best.get("candidate_id")), best_note))
        per_wave[f"W{wave}"] = {
            "n_cells": len(cells),
            "n_skill_passers": len(wave_passers),
            "n_eligible_g2_archived": judge.get("n_eligible_g2"),
            "evidence_cutoff": judge.get("evidence_cutoff"),
            "wave_best": {
                "candidate_id": best.get("candidate_id"),
                "note": best_note,
                "g1_pass": bool(best.get("g1_pass")),
                "dsr_global_era": (best.get("dsr") or {}).get("dsr"),
            },
        }
    roster = {}
    for wave, cell, srow in passers:
        cid = cell["candidate_id"]
        entry = roster.setdefault(cid, {
            "candidate_id": cid,
            "waves": [],
            "roles": [],
            "g1_pass": True,
        })
        entry["waves"].append(f"W{wave}")
        if "skill-line-passer" not in entry["roles"]:
            entry["roles"].append("skill-line-passer")
        entry["four_dim_materials"] = four_dim_materials(cell, srow)
    for wave, cell, srow, note in wave_bests:
        cid = cell["candidate_id"]
        entry = roster.setdefault(cid, {
            "candidate_id": cid,
            "waves": [],
            "roles": [],
            "g1_pass": bool(cell.get("g1_pass")),
        })
        if f"W{wave}" not in entry["waves"]:
            entry["waves"].append(f"W{wave}")
        entry["roles"].append(note)
        if not entry.get("four_dim_materials"):
            entry["four_dim_materials"] = four_dim_materials(cell, srow)
    return roster, per_wave, len(passers)


def main() -> int:
    roster, per_wave, n_passers = build_roster()
    o1058_claim = 18
    out = {
        "probe": "_r270bmc_reform_enum_probe",
        "round": 270,
        "machine": "bm-c",
        "orders": ["O-20260930-1058", "O-20260930-1101"],
        "freeze_checklist_step": "REGISTRATION_REFORM_FDR4D §9-① 档存枚举",
        "engine_epoch": ENGINE_EPOCH,
        "engine_epoch_note": (
            "all readings archived pre-RW-1; per MSG-20260930-1330 old-engine readings are void as "
            "decision values -- this roster is an inventory + four-dim material index ONLY; re-eval "
            "burn (after RW-1~4 all green unfreeze) regenerates all readings under new engine"
        ),
        "n_passers_total": n_passers,
        "o1058_claimed_18_check": {
            "claimed": o1058_claim,
            "actual": n_passers,
            "match": n_passers == o1058_claim,
            "honest_note": ("与 O-1058 §一宣称一致" if n_passers == o1058_claim else
                            "与 O-1058 §一宣称 18 有出入——如实记录以档存实数为准（禁翻案律：不改动任何历史判定）"),
        },
        "per_wave": per_wave,
        "roster": sorted(roster.values(), key=lambda e: e["candidate_id"]),
        "n_roster_members": len(roster),
        "w13_note": "W13 在飞按其已冻结预注册跑完不污染（O-1058 §三2）——不入重估名册",
    }
    os.makedirs(os.path.dirname(ROSTER_OUT), exist_ok=True)
    with open(ROSTER_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    facts = {
        "probe": "_r270bmc_reform_enum_probe",
        "roster_out": os.path.relpath(ROSTER_OUT, ROOT),
        "n_passers_total": n_passers,
        "n_roster_members": len(roster),
        "o1058_claimed_18_match": n_passers == o1058_claim,
        "per_wave_counts": {w: v["n_skill_passers"] for w, v in per_wave.items()},
        "waves_with_zero_passers": [w for w, v in per_wave.items() if v["n_skill_passers"] == 0],
        "wave_best_ids": {w: v["wave_best"]["candidate_id"] for w, v in per_wave.items()},
    }
    with open(FACTS_OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(f"[enum] passers={n_passers} (O-1058 claim 18 match={n_passers == o1058_claim}) roster={len(roster)}")
    for w in sorted(per_wave):
        v = per_wave[w]
        print(f"  {w}: cells={v['n_cells']} passers={v['n_skill_passers']} best={v['wave_best']['candidate_id']} ({v['wave_best']['note']})")
    print(f"[enum] roster -> {os.path.relpath(ROSTER_OUT, ROOT)}")
    return 0


def selftest() -> int:
    roster, per_wave, n_passers = build_roster()
    assert len(WAVES) == 12 and set(per_wave) == {f"W{i}" for i in WAVES}, "wave coverage"
    assert n_passers > 0, "passers must be non-empty (O-1058: 18 claimed)"
    ids = [e["candidate_id"] for e in roster.values()]
    assert len(ids) == len(set(ids)), "roster id uniqueness"
    for e in roster.values():
        assert e["candidate_id"] and e["waves"] and e["roles"], f"entry completeness {e['candidate_id']}"
        mat = e["four_dim_materials"]
        assert set(mat) >= {"ret", "robust", "anti_overfit", "anti_luck", "meta"}, "four-dim faces present"
        d = mat["anti_luck"]["dsr_global_era"]
        assert d is None or (0.0 <= d <= 1.0), f"dsr range {e['candidate_id']}"
    for w, v in per_wave.items():
        assert v["n_cells"] >= v["n_skill_passers"] >= 0, f"counts {w}"
        assert v["wave_best"]["candidate_id"], f"wave best present {w}"
        if v["n_skill_passers"] == 0:
            assert "NON-PASSER" in v["wave_best"]["note"], f"non-passer honesty tag {w}"
    print("selftest: all enum invariants PASS")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
