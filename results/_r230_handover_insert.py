# -*- coding: utf-8 -*-
"""r230 bm-b 5x HANDOVER incremental-window insert (r210 anchor-insert
law: insert own increment BEFORE the previous-reconciliation anchor, no
whole-line overwrite, no number stealing). Window = r226-230."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PATH = "research/HANDOVER.md"
raw = open(PATH, encoding="utf-8").read()

ANCHOR = "；上一次核对=bm-a round 205（2026-09-26 02:2x"
assert raw.count(ANCHOR) == 1, f"anchor not unique: {raw.count(ANCHOR)}"

INC = ("；bm-b round 230（2026-09-26 07:1x·单机核 r226-230 增量窗）R230 增量="
       "①**P-1e 收割批一次定稿+幸存者登记（r226·dept:研究）**："
       "P1E 4/4 分片收割+finalize fail-closed（幸存 2/7=zoo85_stv+zoo92_coin_team·"
       "IS IC −0.0467/−0.0750·IR −0.440/−0.492·OOS 留存 120%/109%·负号 7/7·"
       "V2 铁线 0.026 h20 crosser·§5 四方预测全中·账本 +157=183,292·"
       "等效门 2.22e-16·引擎账本零动）+STRATEGY_LIBRARY §四 Zoo 行幸存者登记"
       "（合成批另开预注册认领制注记）；"
       "②**邻检前置机件全弧（r227/r228·dept:研究+工程）**："
       "P1E_NEIGHBOR_CORR_CHECK spec+runner 池化（selftest 19/19·探针锚 6F1+2F2 "
       "fail-closed）→收割 verdict=pass max|corr|=0.4829<0.7 硬线"
       "（stv↔terrified .3365/.4384·coin↔GTJA070/081 .2584/.2028·coin↔lhb20 "
       ".2302/.4829=判定面 max·advisory stv↔lhb20 F2 0.519 仅披露）→"
       "双员取得联合合成批独立列资格+SATISFIED booking 同 commit；"
       "r228 claim_lost_yield=committed-but-unlaunched limbo 坑律首捕"
       "（正解=同轮即发 autofill tick·禁手跑 runner 绕池）；"
       "③**P1E_SYNTH 预注册冻结（r229）**：zoo_pair_2 联合合成批"
       "（K=2 定向 z 等权 min_valid=2·nullA=C(7,2) 21 对全枚举同偏同秤·"
       "nullB=50 组 K=2 白噪 M_close_tr seed 带 67200 自身 IS IC 符号定向·"
       "N_eff=72+2 条件报告列·V1/V2/V3/A3 h10 唯一门控·evidence_cutoff 09-22·"
       "零授权条款+PASS/FAIL 双分支判前写死+SEED_REGISTRY p1e_synth_null_b）；"
       "④**P1E_SYNTH runner 交付+池化+发射（r230·dept:研究+工程）**："
       "scripts/p1e_synth.py 复用-only 交付（p1e_ic_batch loaders/build_masks/"
       "equivalence_gate+p1e_factors 冻结构造器+composite_ic.xs_zscore+"
       "_ic_series_fast+gates_v123+append_ledger r217 嵌入律）·"
       "selftest 19 检全 PASS（配方单调锚 |IC|=1.0·毒记录 VOID 腿·J7 z 轴第 4 例·"
       "21 对枚举·种子带 67200..67299·夹具日历跨 IS_END 新律）·"
       "VOID 级确定性锚=7 员对母批记录 5e-5·RAM 守卫 <6GB exit 3·"
       "finalize fail-closed+gate_attrition 行+§7/§8 回填=收割轮指针；"
       "07:04:04 autofill 发射 pid17616 target_met=true fill_latency 8.8min"
       "（claim_lost_yield ×2 同轮 tick 正典解实弹二连）+"
       "双回合 S6 镜像撞车 12-UU+11-UU skill dogfood#6 两连解"
       "（_r230_resolve.py 通用两遍·compute_audit 202/204 union 零丢失·"
       "autofill launches union cap50·js 孪生 .json meta.generated_at 选侧·"
       "快照 take-new 双向自动选侧=第二回合正确取 bm-a 07:00 新面）；"
       "⑤维护横贯（r226-230）：S6 17 腿全绿×5（周末 no-op 族·regime ORANGE d2 "
       "shadow 五连·cutoff 09-24·09-28 下 bar·月度三件套非月首轮跳过）+"
       "smoke 25/25×5+orders 74/74 双扫零差×5+板 0 open/22 claimed 全有主")

out = raw.replace(ANCHOR, INC + ANCHOR, 1)
assert out != raw and out.count("bm-b round 230（") == 1
open(PATH, "w", encoding="utf-8", newline="").write(out)
chk = open(PATH, encoding="utf-8").read()
assert INC[:40] in chk and chk.count(ANCHOR) == 1
n = len(chk.encode("utf-8"))
print(f"HANDOVER r230 incremental window inserted before anchor; "
      f"size={n} bytes, round-230 mention count=1")
