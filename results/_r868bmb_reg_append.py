# -*- coding: utf-8 -*-
"""r868 post-finalize closeout appends: pit-ps direct-write entry (r666
exception: CODELY.md main at 108B cap headroom), TREASURE_REGISTRY row,
METHODOLOGY_ASSETS E54 card. All append-only, LF, md5 accounting on the
pit entry per r825 convention."""
import hashlib

PIT = "research/pit-ps.md"
TRE = "knowledge/TREASURE_REGISTRY.md"
MET = "knowledge/METHODOLOGY_ASSETS.md"

pit_line = (
    "- [2026-10-11 07:5x r868 bm-b] **Python 逐判据计数字典推导吞噬共享 generator"
    "（MP1 finalize verdict_counts_by-wave 清零实弹）**：`_verdict_counts(agg, pred)` pred 分支返"
    " generator，`{v: sum(1 for a in sel if a[\"verdict\"]==v) for v in (...)}` 首键 PASS 消费整条"
    " generator 后续键全零（穷尽）——实弹=波次分组表只显 PASS 计数（W19 8/W20 17）PARTIAL/FAIL/N/A "
    "全零；总计数走 `agg.values()`（dict 视图可重迭代）恒正确=误差只藏派生面，主计数对账不报警。"
    "How to apply：凡 per-key 共享可迭代体的计数/聚合=先物化 `[...]` 再多趟；逐判据/分桶统计脚本必配"
    "「分组和==总数」对账腿（本窗 8+32+56+17+11+54==178 当场逮住）；总数与分组用不同迭代对象时双疑。"
    "治愈=results/_r868bmb_wave_heal.py（逐门真值重算+双面 raw-text 治愈+对账 assert）。"
)

before = open(PIT, "rb").read()
assert before.endswith(b"\n")
new_blob = before + pit_line.encode("utf-8") + b"\n"
md5 = hashlib.md5(new_blob).hexdigest()
acct = ("> Direct-write line (r868 bm-b, post-split convention direct-write, r666 exception: "
        "CODELY.md main at 108B cap headroom -> new pit enters domain file directly): "
        "+1 new pit (Python per-verdict dict-comprehension swallows shared generator, "
        "wave-table zeroing face) - appended %d B - LF blob net - md5=%s - file-tail append "
        "- the in-file accounting line is authoritative.\n" % (len(pit_line.encode("utf-8")) + 1, md5))
new_blob += acct.encode("utf-8")
with open(PIT, "wb") as fh:
    fh.write(new_blob)
import json
assert hashlib.md5(open(PIT, "rb").read()).hexdigest() == hashlib.md5(new_blob).hexdigest()

tre_line = (
    "- 2026-10-11 07:5x bm-b r868 研究判决批收口捕获（N2-MP1 素材池消费批 wave-1 finalize 类·"
    "TREASURE_PROTECTION_LAW §1）：results/mp1_tsgate_p1.json + research/MP1_TSGATE.md 入册——素材池"
    "首次消费可判读数（96 员→89 可算→178 门→1,013 工具：PASS=25·PARTIAL=43·FAIL=110·N/A=0；价格水位类 "
    "q10 低分位门族主发现 OOS 净差中位 +1.1%~+1.3%/20d·正份额 0.74-0.77；锚 G-ANCHOR-MP1 in-run 双复现 "
    "3341/390/149；E[FP]=8.9 披露在案，PASS 仅获独立复核资格）；方法论 E54 卡随批（runner 克隆+池公式面"
    "换装+t23 单源 import+池身份漂移护栏=wave-2+ 复用范式）；同窗 pit-ps 新坑一行（generator 单次消费坑）。"
)
with open(TRE, "a", encoding="utf-8", newline="") as fh:
    fh.write(tre_line + "\n")

met_line = (
    "- **E54 素材池消费普查法（A158 runner 克隆+池公式面换装+t23 单源评估）**：proven·研究面。以 "
    "A158-TSGATE-P1 runner 为基座，把因子面换装成「素材池员公式」评估面——四件套：①parse_formula 逆解"
    "析器（formula_str 渲染文法镜像·round-trip 全验）+t23.evaluate import 单源零重写（[n,1] 单标的面；"
    "CSRANK 截面算子构造性排除如实披露）；②池装载器冻结身份漂移护栏（员数/跨波 overlap/排除类数/锚员 pin，"
    "一面不符=拒烧）；③锚从起草探针读数选立并 fail-closed（probe-facts 三元组 in-run 复现）；④selftest "
    "hermetic 多腿（解析器/评估器手值腿+实数据锚腿+refuse-if-exists 腿）。附 §5 预测带校准律：预测带必须锚定"
    "同机械先例实绩率（本窗 PASS∈[0,12] MISS vs A158 实绩 15.3%——MP1 实测 14.0% 与先例恒等=纯先验设定方法"
    "论错误）。证据=scripts/mp1_tsgate_probe.py（selftest 30/30×2）+results/mp1_tsgate_p1.json+research/"
    "N2_MP1_PREREG.md §7/§8。\n- 2026-10-11 07:5x·bm-b r868（N2-MP1 finalize 收口步·O-20261002-2100 "
    "捕获律 live 实证：素材池首消费普查全链落地）。"
)
with open(MET, "a", encoding="utf-8", newline="") as fh:
    fh.write(met_line + "\n")

for p in (PIT, TRE, MET):
    b = open(p, "rb").read()
    print(p, len(b), "B", "crlf:", b.count(b"\r\n"), "lf:", b.count(b"\n"))
print("pit md5:", md5)
