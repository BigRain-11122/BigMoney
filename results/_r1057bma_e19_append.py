# -*- coding: utf-8 -*-
"""r1057 bm-a: append E19 row + consumption record to state/queue/explore.md (fresh read-modify-write)."""
import io

PATH = "state/queue/explore.md"

ROW = ("| E19 | 双温度计对照描述探针（E18 digest 指针消费面：P6 情绪温度计 regime_thermo 日面 × E18 基本面温度计 fund_thermo 年频面"
       "——同域年对照表 2005-2025 全年 21 行+2026H1 半窗旗标行；关键面相关水平+YoY 差分双面（趋势稳健执法）25 对零缺值；"
       "零判据零网络零 marks·judged face 须另开票走 PREREG_TEMPLATE 正门）"
       "——r1057 bm-a 队列登记认领同轮完成出列（T-18 CLEAR+T19 seed gate hits=[] 双闸前置·E18 先例）；"
       "探针 scripts/dual_thermo_probe.py〔selftest 19/19 hermetic·run rc0·幂等重跑 sha16 5c3f86e56a83f595 字节恒等〕；"
       "证据 results/dual_thermo/{dual_thermo.csv,dual_thermo.json}〔情绪 cutoff 2026-09-22×基本面 cutoff 2026-06-30·n_full_years=21〕；"
       "digest research/digests/DIGEST-20261018-e19-dual-thermo.md；"
       "核心读数：①roe_med×seal_rate_mean 水平 +0.434/差分 +0.425（差分面成立=非纯共趋势·盈利改善年封板韧性同步改善）"
       "②ni_pos_share×seal_rate_mean +0.516 最强读数（差分 0.328）"
       "③情绪极端≠基本面极端：2015 情绪峰（日均涨停 145/恐慌 11 日/高度 11.2）roE 12.05 中位年 vs 2007 基本面峰（roe 15.45/覆盖 93.8%）"
       "情绪面温和（68/日零恐慌）=两族极端年零重合"
       "④2024-2026 分离面：日均涨停 96/94.5 史高二三位而 roe 4.89→2.08 史低+封住率 0.16 史低=「摸板多封死少」与 2017「少而封死」镜像"
       "⑤Sloan 楔子×情绪≈零相关（-0.08/+0.05）+恐慌面与基本面全正交（+0.076/+0.103）=情绪只看赚不赚不看是不是现金；"
       "诚实面：n=21 小样本零显著性/2026 半窗旗标排除/同域共位非先行滞后/as-collected+thermo 近似双承接；"
       "E18 digest 头条勘注一行（楔子全史最低=2011 -0.296/61.7%·2007 为第四位·数据面零翻案）"
       " | scripts/dual_thermo_probe.py | done |\n")

RECORD = ("> r1057 消耗记录（bm-a）：E19 本轮登记认领同轮完成出列——双温度计对照描述探针全链交付"
          "（T-18 CLEAR+T-19 hits=[] 双闸→探针 19/19 selftest+run rc0+幂等 sha16 恒等→22 行证据+digest 落盘）；"
          "judged 判据面升级走 PREREG_TEMPLATE 正门另开票·三轴合壁（情绪×指数×基本面）归委员会/GM 署名票。探索队列 E19 出列。\n")

with io.open(PATH, "r", encoding="utf-8") as f:
    text = f.read()
if "E19" in text and "双温度计对照描述探针" in text:
    print("SKIP: E19 row already present (idempotent append)")
else:
    if not text.endswith("\n"):
        text += "\n"
    text += ROW + RECORD
    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("APPENDED: E19 row + consumption record")
