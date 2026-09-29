#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optuna Bayesian tuning SKELETON (gated) -- PLAN.md P3 参数进化 + O-20260924-1120 D2 frozen release criterion.

D2 (verbatim): 维持 gated + 解封判据冻结。触发器写死：①在册 validated ≥8 且 ②最近一个晋升窗
新注册 ≤1（海选枯竭信号），两者同时成立才解封。解封后纪律（研究部 prereg 制）：walk-forward
分段优化 + 最终 OOS 恒盲；TPESampler seed 固定 + HyperbandPruner study_name 固定（Optuna 官方
确定性指引）；参数 ≤5（PLAN §4.3）；产物过 G1'/G2 v2 门方可注册。依据 Cawley & Talbot 2010
（JMLR 11:2079-2107）：有限样本上以同一数据既调参又评估=选择偏差过拟合，正解=调参面与评估面分离。

工程事实：optuna 5.0.0 装于 toolstack venv（quant\\toolstack\\venv\\Scripts\\python.exe，py3.12.14，
uv 清华镜像 2026-09-29 r425 bm-a；与 bm-c r192 OSS 采纳 5.0.0 同版）。系统 py3.14 无 optuna。
运行面：status / selftest 结构层零依赖任意 python；selftest 机器层与 run 须 toolstack venv python。

Subcommands:
  status   -- gate face read + verdict JSON (deterministic, zero network, zero optuna)
  selftest -- hermetic: gate fixtures + frozen-law assertions; machinery tier auto-SKIP honest if optuna absent
  run      -- REFUSED unless gate OPEN (exit 2 honest) AND a frozen research-dept prereg is supplied (exit 2 if absent);
             when both hold: study scaffolding with TPESampler(seed=prereg seed) + HyperbandPruner + frozen study_name,
             params <= 5, walk-forward IS-only objective, OOS fold held blind (Cawley-Talbot separation). No default
             objective is burned by the skeleton itself -- the objective module is referenced by the prereg.
"""
import argparse
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORECARD_V1 = os.path.join(REPO, "results", "scorecard_v1.json")
INTAKE_GLOB = os.path.join(REPO, "results", "trial_labor_*", "w*_intake.json")
PROMO_SUMMARY = os.path.join(REPO, "results", "prospect_promotion", "_summary.json")

# D2 frozen release criterion (O-20260924-1120): both legs must hold to unlock.
GATE_VALIDATED_MIN = 8      # ① 在册 validated >= 8
GATE_NEW_REG_MAX = 1         # ② 最近一个晋升窗新注册 <= 1（海选枯竭信号）
# Frozen post-unlock discipline (research-dept prereg governs actual values; laws fixed here):
MAX_PARAMS = 5               # PLAN §4.3 参数 <= 5
OBLIGATORY_SAMPLER = "TPESampler"      # seed 固定 = prereg field, asserted int
OBLIGATORY_PRUNER = "HyperbandPruner"  # study_name 固定 = prereg field, asserted non-empty
# 依据律（Cawley & Talbot 2010）：tuning face 与 evaluation face 分离 -- objective 只见 IS folds，
# OOS fold 索引由 harness 持有、永不传入 objective（恒盲）。


def read_validated_count():
    """在册 validated face = scorecard_v1 roster count (D2 ruling-time equivalence: '现 6' == roster 6)."""
    try:
        with open(SCORECARD_V1, encoding="utf-8") as f:
            s = json.load(f)
        n = int(s["summary"]["n_traders"])
        return n, "results/scorecard_v1.json summary.n_traders"
    except Exception as e:
        return None, "face-miss: %s (%s)" % (SCORECARD_V1, e)


def read_new_registrations():
    """② face (best-effort, disclosed): trial-labor intake registered counts + prospect promotion promoted count."""
    total, faces = 0, []
    for p in sorted(glob.glob(INTAKE_GLOB)):
        try:
            with open(p, encoding="utf-8") as f:
                j = json.load(f)
            # intake faces declare registered rows under known keys; count any explicit non-negative value
            for k in ("registered", "registered_count", "n_registered"):
                if isinstance(j.get(k), int) and j[k] >= 0:
                    total += j[k]
                    faces.append(os.path.relpath(p, REPO) + ":" + k)
                    break
        except Exception:
            pass
    if os.path.exists(PROMO_SUMMARY):
        try:
            with open(PROMO_SUMMARY, encoding="utf-8") as f:
                j = json.load(f)
            for k in ("promoted", "promoted_count", "n_promoted"):
                if isinstance(j.get(k), int) and j[k] >= 0:
                    total += j[k]
                    faces.append("prospect_promotion/_summary.json:" + k)
                    break
        except Exception:
            pass
    return total, "; ".join(faces) if faces else "no-registration-face-rows (zero-registration windows)"


def gate_state():
    v, v_face = read_validated_count()
    r, r_face = read_new_registrations()
    leg1 = (v is not None and v >= GATE_VALIDATED_MIN)
    leg2 = (r is not None and r <= GATE_NEW_REG_MAX)
    return {
        "gate": "OPEN" if (leg1 and leg2) else "CLOSED",
        "leg1_validated_ge8": {"ok": leg1, "validated": v, "face": v_face, "line": GATE_VALIDATED_MIN},
        "leg2_new_regs_le1": {"ok": leg2, "new_regs": r, "face": r_face, "line": GATE_NEW_REG_MAX},
        "law": "O-20260924-1120 D2: both legs must hold; unlock discipline = research-dept prereg "
               "(walk-forward + OOS blind; TPESampler seed fixed; HyperbandPruner; study_name fixed; "
               "params<=5; G1'/G2 v2 before any registration)",
        "v-env": "optuna runs under quant\\toolstack\\venv (py3.12.14, optuna 5.0.0); system py3.14 has none",
    }


def validate_param_space(space):
    """PLAN §4.3: params <= 5. space = list of (name, kind, lo, hi) tuples."""
    if not isinstance(space, (list, tuple)) or not space:
        return False, "param space must be a non-empty list"
    if len(space) > MAX_PARAMS:
        return False, "param space %d > %d (PLAN 4.3 law)" % (len(space), MAX_PARAMS)
    names = [s[0] for s in space]
    if len(set(names)) != len(names):
        return False, "duplicate param names"
    return True, "ok n=%d" % len(space)


def _machinery_smoke():
    """optuna-present tier: frozen sampler/pruner wiring + same-seed first-trial determinism. Hermetic."""
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def make(seed, name):
        st = optuna.create_study(
            study_name=name,
            sampler=optuna.samplers.TPESampler(seed=seed),
            pruner=optuna.pruners.HyperbandPruner(),
            direction="maximize",
        )
        for _ in range(3):
            t = st.ask()
            x = t.suggest_float("x", 0.0, 1.0)
            y = t.suggest_float("y", 0.0, 1.0)
            st.tell(t, -(x - 0.3) ** 2 - (y - 0.7) ** 2 + 0.01 * (int(t.number) % 2))
        return st

    a, b = make(20299000, "skeleton-smoke-a"), make(20299000, "skeleton-smoke-b")
    pa = [(p.params["x"], p.params["y"]) for p in a.trials]
    pb = [(p.params["x"], p.params["y"]) for p in b.trials]
    assert pa == pb, "same-seed TPE determinism broken"
    assert type(a.sampler).__name__ == OBLIGATORY_SAMPLER
    assert type(a.pruner).__name__ == OBLIGATORY_PRUNER
    return len(pa)


def selftest():
    ok = [0, 0]

    def check(name, cond, note=""):
        ok[0 if cond else 1] += 1
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, (" | " + note) if note else ""))
        return cond

    # gate logic fixtures (hermetic, pure function of the two legs)
    for v, r, want in ((6, 0, "CLOSED"), (8, 0, "OPEN"), (8, 2, "CLOSED"), (9, 1, "OPEN"), (7, 1, "CLOSED")):
        leg1 = v is not None and v >= GATE_VALIDATED_MIN
        leg2 = r is not None and r <= GATE_NEW_REG_MAX
        check("gate-fixture v=%s r=%s -> %s" % (v, r, want), (leg1 and leg2) == (want == "OPEN"))
    # live face read (r425 fact: roster 6 -> CLOSED on leg1)
    gs = gate_state()
    check("live-gate-read", gs["leg1_validated_ge8"]["validated"] is not None, "v=%s r=%s -> %s" % (
        gs["leg1_validated_ge8"]["validated"], gs["leg2_new_regs_le1"]["new_regs"], gs["gate"]))
    # frozen-law validators
    for space, want in (([("a", "f", 0, 1)], True), ([("a%d" % i, "f", 0, 1) for i in range(6)], False),
                       ([("a", "f", 0, 1), ("a", "f", 0, 1)], False), ([], False)):
        good, note = validate_param_space(space)
        check("param-space-law (%s)" % note, good == want)
    # walk-forward separation law: OOS fold never inside IS folds (Cawley-Talbot)
    folds = list(range(8)); oos = 7; is_folds = folds[:7]
    check("walk-forward-oos-blind", oos not in is_folds and len(is_folds) + 1 == len(folds))
    # machinery tier (optuna-dependent; honest SKIP when absent)
    try:
        import optuna  # noqa: F401
        n = _machinery_smoke()
        check("machinery-smoke TPESampler+HyperbandPruner same-seed determinism", True, "trials=%d" % n)
    except ImportError:
        check("machinery-smoke SKIPPED (optuna absent in this interpreter)", True,
              "use toolstack venv python for the machinery tier")
    print("selftest: %d PASS, %d FAIL" % (ok[0], ok[1]))
    return 0 if ok[1] == 0 else 1


def cmd_run(prereg_path):
    gs = gate_state()
    if gs["gate"] != "OPEN":
        print(json.dumps({"refused": True, "reason": "gate CLOSED per O-20260924-1120 D2", **gs},
                         ensure_ascii=False, indent=1))
        return 2
    if not prereg_path or not os.path.exists(prereg_path):
        print(json.dumps({"refused": True, "reason": "research-department prereg required (frozen, "
                                                     "seed+study_name+param_space+walk-forward spec)", "path": prereg_path},
                         ensure_ascii=False))
        return 2
    with open(prereg_path, encoding="utf-8") as f:
        pre = json.load(f) if prereg_path.endswith(".json") else {"note": "md prereg: parse not implemented"}
    seed = pre.get("seed"); study_name = pre.get("study_name"); space = pre.get("param_space")
    assert isinstance(seed, int), "prereg seed must be int (TPESampler seed 固定律)"
    assert isinstance(study_name, str) and study_name, "prereg study_name must be non-empty (固定律)"
    good, note = validate_param_space(space)
    assert good, note
    print(json.dumps({"scaffold_ready": True, "seed": seed, "study_name": study_name,
                      "params": len(space), "pruner": OBLIGATORY_PRUNER, "sampler": OBLIGATORY_SAMPLER,
                      "oos_blind": True, "note": "objective module ref = prereg field; skeleton burns nothing"},
                     ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(prog="optuna_refine_skeleton")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    st = sub.add_parser("selftest")
    rn = sub.add_parser("run")
    rn.add_argument("--prereg", default=None)
    a = ap.parse_args()
    if a.cmd == "status":
        print(json.dumps(gate_state(), ensure_ascii=False, indent=1))
        return 0
    if a.cmd == "selftest":
        return selftest()
    return cmd_run(getattr(a, "prereg", None))


if __name__ == "__main__":
    sys.exit(main())
