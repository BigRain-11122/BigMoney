from pathlib import Path

# r307/r412 mechanical backfill: prereg s7/s8 after finalize (two-state
# guard: the anchors were placeholder-only at freeze, backfill is the
# legitimate post-burn state). Byte-level LF edit per r500 lesson.

p = Path(r"research/PERPETUAL_N1_W38_PREREG.md")
data = p.read_bytes().decode("utf-8")

old7 = "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n（占位·finalize 窗机械回填。）"
new7 = (
    "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n"
    "- finalize one-pass 2026-10-02 01:30（bm-b r530·链序解锁窗：W37 finalize 已由 bm-c 落账"
    "〔r342 同窗·n1_w37_results.json 在 origin〕→本波 FAIL-CLOSED 等待解除·12/12 分片完备性门过"
    "〔r310 律·ls-tree 12/12〕）。\n"
    "- S5 判据 4/4 PASS（锚=W36 实测〔冻结窗锚〕；锚滚动律披露：W37 finalize 落账先于本波 "
    "finalize 窗→按滚动条款以 W37 实测复核亦全过〔双锚面披露〕）：\n"
    "  1. mu 漂移：W38-only **−0.098857** vs W36 锚 −0.091452〔|Δ|=0.0074<0.02 PASS〕"
    "/vs W37-only 滚动锚 −0.090349〔|Δ|=0.0085<0.02 PASS〕；merged（K=81,520）**−0.091622**。\n"
    "  2. sigma 相对变化：W38-only **0.245276** vs W36 锚 0.244847〔+0.17%<±10% PASS〕"
    "/vs W37-only 0.246920〔−0.66%<±10% PASS〕；merged **0.244915**。\n"
    "  3. A 族 full_sharpe_p95：**0.3119** vs W36 锚 0.3205〔Δ=0.0086<0.05 PASS〕"
    "/vs W37 滚动锚 0.3204〔Δ=0.0085<0.05 PASS〕（门校准注记：结果知情校准面·测量面零注册利害）。\n"
    "  4. K-lift 线移动：**−0.0001**〔1.1575→1.1574 @n_eff_held 443,940〕≤0.02 PASS"
    "（W3..W38 先例族内〔含 W36 +0.0011/W37 +0.0003/W38 −0.0001〕如实报负）。\n"
    "- 账本：prev **443,940**〔==W37 finalize 落账头 441,740+2,200·derive 禁手抄自证〕"
    "＋本波 2,200＝total **446,140**·voids_applied LOWAMP-P1/P2 继承面 ✓；"
    "skill_line_v2 消费 n_eff=443,940（W37+W38 合并池 K=81,520 同步加深）。\n"
    "- 链序注记：W38 finalize 依 r543 链序在 W37 finalize 之后落账；W39（bm-c r342 冻结）"
    "烧录在飞——其 finalize 链序排本波之后。"
)

old8 = "## §8 批后复盘【必填·s7-T】\n\n（占位·finalize 窗机械回填。）"
new8 = (
    "## §8 批后复盘【必填·s7-T】\n\n"
    "- 设计零偏差：frozen v1 设计逐字复用（run_one 引擎同源），W38-only mu/sigma 与先例族"
    "〔W2..W37〕逐面同域，零断裂信号；B 族 p_exit=0.05 配对律齐备（n=200）。\n"
    "- 波节奏面：W38=烧录〔r529 冻结→r530 12/12 烧毕+产品外科交付〕→finalize〔r530 同窗〕"
    "全生命周期跨一轮完成；r529 冻结窗标注的「W37 finalize 先行」链序如实执行"
    "（bm-c r342 落 W37 finalize→本波解锁→一过定稿·r538 禁盲重跑律执行）。\n"
    "- 测量面结论：累计 null 池 K=81,520〔+W37 2,200 合并〕，mu −0.0916 / sigma 0.2449 稳定，"
    "se_mu 随累计加深收窄——null 基线置信面继续加深，无质变；canon flip 不在本波"
    "（治理提案面素材累计·K2200 同律）。\n"
    "- 下游接线：skill_line_v2 @n_eff 443,940 线 1.1574（−0.0001）——判线共享库消费面自动。"
)

for tag, old, new in ((7, old7, new7), (8, old8, new8)):
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    assert data.count(old) == 1, f"anchor s{tag} not unique"
    data = data.replace(old, new)

p.write_bytes(data.encode("utf-8"))
print("W38 prereg s7/s8 mechanical backfill landed (byte-level LF)")
