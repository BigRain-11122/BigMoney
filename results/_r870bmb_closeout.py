# -*- coding: utf-8 -*-
"""r870 bm-b closeout appends: tech.md T25 done-flip + METHODOLOGY E55 card
+ TREASURE r870 line. UTF-8 explicit (PS 5.1 ANSI trap law). Idempotent-guarded
(each append refuses if its marker already present)."""
import io
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

TECH = ROOT + r"\state\queue\tech.md"
METH = ROOT + r"\knowledge\METHODOLOGY_ASSETS.md"
TREA = ROOT + r"\knowledge\TREASURE_REGISTRY.md"


def append_line(path, marker, line):
    txt = io.open(path, encoding="utf-8").read()
    if marker in txt:
        print("[closeout] skip (marker present): %s" % marker[:40])
        return
    if not txt.endswith("\n"):
        txt += "\n"
    io.open(path, "w", encoding="utf-8", newline="").write(txt + line)
    print("[closeout] appended: %s" % marker[:40])


# 1) tech.md T25 row: open -> done (slice-2+3 full-chain closed)
txt = io.open(TECH, encoding="utf-8").read()
OLD = "open（r869 bm-b 认领·slice-1 起草窗）"
NEW = "done（r870 bm-b 判决·slice-2+3 同轮全链闭环：runner+FROZEN v1.0 五条件+烧录判决 CONFIRM=5/CLONE=0/COLLAPSED=16/FAIL=4）"
if OLD in txt:
    assert txt.count(OLD) == 1, "T25 open marker not unique"
    txt = txt.replace(OLD, NEW)
    io.open(TECH, "w", encoding="utf-8", newline="").write(txt)
    print("[closeout] tech.md T25 -> done")
elif NEW in txt:
    print("[closeout] tech.md T25 already done")
else:
    print("[closeout] ERROR: T25 marker not found")
    sys.exit(2)

# 2) METHODOLOGY_ASSETS.md E55 card (secondary-face reconciliation law)
E55 = ("- **E55 冻结批存档次级面逐位对账腿（recompute-vs-frozen-secondary-face positional identity）**"
       "：proven，研究面对。复核/续费批的漂移防护新面——runner 在烧录时对冻结批已存档的次级面"
       "（如 mp1_tsgate_p1.json five_member_oos）逐位重算对账：net/n_in/thin(格点A) 三字段"
       "rounded-6 零容差恒等断言，任一失配=fail-closed VOID（配置错配/双烧窗漂移防护），"
       "全过=同 cutoff 同构造确定性实证。双名面板必须先钉键面（sh 正典键 vs bare 名键=不同文件"
       "不同数据——对账与先验实读一律同键面，否则键面错配假漂移/假先验）。"
       "selftest 腿=合成面板双算恒等（本 runner face_a_leg OOS 分支 vs 冻结批 inst_gate_stats OOS 分支）"
       "+真数据锚腿。证据：scripts/mp1_gate_recheck.py（selftest 7/7）+"
       "results/gate_recheck_mp1.json secondary_face_reconciliation 125/125 all_equal。\n"
       "- 2026-10-11 08:3x：bm-b r870（GATE-RECHECK-MP1 finalize 收口步·O-202602-2100 捕获律 live 实证："
       "MP1 独有新面首次实弹 125/125 全过）。\n")
append_line(METH, "E55 冻结批存档次级面逐位对账腿", E55)

# 3) TREASURE_REGISTRY.md r870 line (verdict finalize + roster move)
TR = ("- 2026-10-11 08:3x bm-b r870 研究判决收口步（GATE-RECHECK-MP1 finalize 类·TREASURE_PROTECTION_LAW §1）："
      "results/gate_recheck_mp1.json + research/MP1_GATE_RECHECK.md 入册——MP1 25 PASS 门独立复核判决面"
      "（CONFIRM=5→T-101 v4 政体门候选库入册清单·与 A158 RECHECK 17 门同库并列：MA(LOW,30)_q10 水位巨簇代表"
      "+CORR(OPEN,VWAP,10)_q90+CORR(MA(CLOSE,10),VWAP,10)_q90+CORR(HIGH,MUL(CLOSE,HIGH),20)_q90"
      "+DELTA(MAX(RET,30),5)_q90；CLONE=0（MAX30_q10 邻接预警实算 0.252<0.7 收口）；COLLAPSED=16"
      "（价格水位巨簇 size17 intra=1.000 整簇坍缩合法产出）；FAIL=4→C1 降格清单）；"
      "E[FP]=0.05×9=0.45；Face R 次级面对账 125/125 逐位恒等（新面首次实弹）；"
      "方法论 E55 卡随批（冻结批存档次级面逐位对账腿·sh 正典键面律）；"
      "证据链=prereg FROZEN v1.0（commit c01757733）+判决面 JSON/MD+§7/§8 回填。\n")
append_line(TREA, "r870 研究判决收口步（GATE-RECHECK-MP1", TR)

print("[closeout] all done rc0")
