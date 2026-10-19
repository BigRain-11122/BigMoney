# -*- coding: utf-8 -*-
"""r1133 bm-c: W281 PREREG substitutions as exact old->new pairs (cascade-free, count-asserted).

Every OLD side is MEASURED verbatim on the frozen W280 face
(results/_w281bmc_w280_frozen_face.txt = git show 5f279e44fc:research/PERPETUAL_N1_W280_PREREG.md,
pre-run face with §7/§8 placeholders -- the HEAD twin is post-backfill and is NOT used, r1049/r1052 law).
Every NEW side is authored from the W281 seat receipt (results/_w281bmc_20261020_probe_receipt.json)
plus the W280 fivekeys (results/_r1132bmc_w280_fivekeys.json).

Pair discipline: single left-to-right scan; each pair declares its expected occurrence count in the
current face; fail-closed before any write (r587 no-transcription law).
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w281bmc_w280_frozen_face.txt")
F = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")

PAIRS = []


def add(old, new, expect=1):
    PAIRS.append((old, new, expect))


# ---------------- line 1: header / chain ledger ----------------
add(
    u"# PERPETUAL-N1-W280 预注册 · N1 nulls-deepening 池第 278 枚",
    u"# PERPETUAL-N1-W281 预注册 · N1 nulls-deepening 池第 279 枚",
)
add(u"engine_owner 行 269 注册在册（表尾 W281 行【bm-c r1123 五面冻结 splice 3810f4a7ac 落地 19:3x",
    u"engine_owner 行 270 注册在册（表尾 W282 行【bm-c r1131 五面冻结 splice 7a5b47ff94 落地 01:5x")
add(
    u"【results/p2cal_ext/n1_w279/ 12/12·ledger append 498d178d0b+332e8e8656】·**W279 finalize 已落地**"
    u"【n1_w279_results.json 机读·净账本锚头 1,038,135·K=611,720 合并池·W279 finalize one-pass bm-c r1124 窗 20:0x"
    u"·estate chain r1122/r1123/r1124 W279 全周期 ba5c725b42+3810f4a7ac+6bdbdb9a07】",
    u"【results/p2cal_ext/n1_w280/ 12/12·ledger append a4cf451113+982058016c】·**W280 finalize 已落地**"
    u"【n1_w280_results.json 机读·净账本锚头 1,040,335·K=613,920 合并池·W280 finalize one-pass bm-c r1131 窗 02:0x"
    u"·estate chain r1129/r1130/r1131 W280 全周期 5f279e44fc+7a5b47ff94+341a90637a】",
)
add(
    u"bm-c r1130 席位 MSG-20261020-@@SEAT_HHMM@@-bmc-w281-seat 已推 origin @@SEAT_SHA@@·probe receipt _w280bmc_20261019 机证",
    u"bm-c r1133 席位 MSG-20261020-@@SEAT_HHMM@@-bmc-w282-seat 已推 origin @@SEAT_SHA@@·probe receipt _w281bmc_20261020 机证",
)
add(
    u"→freeze 时 live derive bmc rows 98+候选=第 99 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】",
    u"→freeze 时 live derive bmc rows 99+候选=第 100 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】",
)
add(u"【bm-c 循环班 r1130 席位窗 2026-10-20 01:0x",
    u"【bm-c 循环班 r1133 席位窗 2026-10-20 02:3x")
add(
    u"**W280=bm-c own-wave window per chain-order law（W277 bm-c→W278 bm-c→W279 bm-c→W280 bm-c own-turn rotation"
    u"·seat owner per chain-order law）**",
    u"**W281=bm-c own-wave window per chain-order law（W278 bm-c→W279 bm-c→W280 bm-c→W281 bm-c own-turn rotation"
    u"·seat owner per chain-order law）**",
)
# ---------------- line 2: order sources ----------------
add(u"saturation_engine.py status live-read r1130：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    u"saturation_engine.py status live-read r1133：burns_active=[] queue_next=[] 实读·heartbeat 新鲜")
add(
    u"**波号 280=注册表 W279 席后首个自由号**【probe leg3 vacancy 机证（r1130 席位窗实跑：origin inbox 零 W280 席位外机命中"
    u"+origin perpetual_faces.py 零 280 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W280 WAVE_CONFIGS"
    u"+origin 零 PERPETUAL_N1_W280_PREREG.md 四查+零 skip-ahead W281/W282 席位声明）】",
    u"**波号 281=注册表 W280 席后首个自由号**【probe leg3 vacancy 机证（r1133 席位窗实跑：origin inbox 零 W281 席位外机命中"
    u"+origin perpetual_faces.py 零 281 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W281 WAVE_CONFIGS"
    u"+origin 零 PERPETUAL_N1_W281_PREREG.md 四查+零 skip-ahead W282/W283 席位声明）】",
)
# ---------------- line 3: bands ----------------
add(u"ADMIT 回执=results/_w279bmc_20261019_probe_receipt.json",
    u"ADMIT 回执=results/_w281bmc_20261020_probe_receipt.json")
add(u"**A-ext seed=631_301..633_300**", u"**A-ext seed=633_501..635_500**")
add(
    u"（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十九次连续 A-hop）**："
    u"A 面算术续带 631_101..633_100（自注册 W279 A 尾 631_100 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）"
    u"起点即 REFUSED（注册 W279 B 带 631_101..631_300 落 naive A 窗内=staircase re-emergence affects A 承袭"
    u"·W279 prereg §5 item5 post-W279-REGISTERED pre-disclosure 兑现 r587 如实披露）→walk 越注册 W279 B 尾 631_300"
    u"→A first-clean **631_301..633_300**·**hops=1**·**A 落位 base==注册前波 B 尾+1（631_300+1）机检关系**"
    u"（A_hop_chain 1 跳 verbatim leg1 机证〔window 631_101..633_100→jump 631_301·refuser band 631_101..631_300〕"
    u"·A_clean_at_naive_start=false·A_staircase_hop_past_W279_B=true"
    u"·A base>=registered prior-wave B tail+1 floor relation）",
    u"（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第三十一次连续 A-hop）**："
    u"A 面算术续带 633_301..635_300（自注册 W280 A 尾 633_300 续）在席位窗宇宙（post-W280-REGISTERED 终态注册）"
    u"起点即 REFUSED（注册 W280 B 带 633_301..633_500 落 naive A 窗内=staircase re-emergence affects A 承袭"
    u"·W280 prereg §5 item5 post-W280-REGISTERED pre-disclosure 兑现 r587 如实披露）→walk 越注册 W280 B 尾 633_500"
    u"→A first-clean **633_501..635_500**·**hops=1**·**A 落位 base==注册前波 B 尾+1（633_500+1）机检关系**"
    u"（A_hop_chain 1 跳 verbatim leg1 机证〔window 633_301..635_300→jump 633_501·refuser band 633_301..633_500〕"
    u"·A_clean_at_naive_start=false·A_staircase_hop_past_W280_B=true"
    u"·A base>=registered prior-wave B tail+1 floor relation）",
)
add(u"**B-ext exit seed=633_301..633_500**", u"**B-ext exit seed=635_501..635_700**")
add(
    u"（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第三十次连续 above-own-A 落位）**："
    u"B naive 续带 631_301..631_500（自注册 W279 B 尾 631_300+1 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）"
    u"起点即 REFUSED（naive B 窗 631_301..631_500 落本波 A first-clean 窗 631_301..633_300 内"
    u"=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    u"——**own-A reservation standard leg 越本波 A 窗 631_301..633_300**（1 hop）→**1 hop** 落位 **633_301..633_500**"
    u"·**B 落位 base==本波 A 窗尾+1（633_300+1）EXACT 机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true"
    u"·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证·非转录 r587·AB 同窗互斥面 leg2 律在场）",
    u"（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第三十二次连续 above-own-A 落位）**："
    u"B naive 续带 633_501..633_700（自注册 W280 B 尾 633_500+1 续）在席位窗宇宙（post-W280-REGISTERED 终态注册）"
    u"起点即 CLEAN 于注册宇宙（probe leg1 relation_asserts B_naive_clean_vs_registered=true）但落本波 A first-clean 窗"
    u" 633_501..635_500 内=own-A reservation cascade standard leg 强制（probe leg1 B_semantics 机证·B_hop_lands_inside_A=true）"
    u"——**own-A reservation standard leg 越本波 A 窗 633_501..635_500**（1 hop）→**1 hop** 落位 **635_501..635_700**"
    u"·**B 落位 base==本波 A 窗尾+1（635_500+1）EXACT 机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true"
    u"·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证·非转录 r587·AB 同窗互斥面 leg2 律在场）",
)
add(
    u"**W279 prereg §5 item5 投影承接面注记兑现+落位一致如面**：投影预言 W280 A naive 631_101..633_100 "
    u"将被注册 W279 B 带拒（staircase affects A 承袭·第二十九次连续 A-hop）与 B own-A reservation cascade 上移"
    u"——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    u"R281：W280 带（A 631_301..633_300/B 633_301..633_500）注册后对 W281+ 的拒面影响=W280 冻结方 leg4 前瞻已机证（见 §5 item5）。",
    u"**W280 prereg §5 item5 投影承接面注记兑现+落位一致如面**：投影预言 W281 A naive 633_301..635_300 "
    u"将被注册 W280 B 带拒（staircase affects A 承袭·第三十一次连续 A-hop）与 B own-A reservation cascade 上移"
    u"——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    u"R282：W281 带（A 633_501..635_500/B 635_501..635_700）注册后对 W282+ 的拒面影响=W281 冻结方 leg4 前瞻已机证（见 §5 item5）。",
)
# ---------------- reuse domain / splice window ----------------
add(u"（W2..W279 落地 runner 的 wave 参数化复用", u"（W2..W280 落地 runner 的 wave 参数化复用")
add(u"【本机 bm-c 实例·heartbeat 新鲜实读 r1130 窗·队列空转 idle】",
    u"【本机 bm-c 实例·heartbeat 新鲜实读 r1133 窗·队列空转 idle】")
add(
    u"selftest W279 face 将随五面冻结落地验证）。本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w280bmc_freeze_edits.py"
    u"（按 _w279bmc_freeze_edits.py 模板派生·gate0.5 自查 W279 行+W279 finalize 件在场=已绿·未落即 loud abort 兜底）"
    u"=**splice 执行窗派生落地（r1122/r1123 W279 全周期先例实时间线：prereg ba5c725b42 落于 r1122 窗·"
    u"splice 3810f4a7ac 落于 r1123 执行窗 19:3x——**W280 freeze 面：W279 own-wave finalize 已落地=席位时即解锁"
    u"——席位 r1124 窗+prereg r1130 窗落地 per seat-first law O-20261010-2350 §2·splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。",
    u"selftest W280 face 将随五面冻结落地验证）。本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w281bmc_freeze_edits.py"
    u"（按 _w280bmc_freeze_edits.py 模板派生·gate0.5 自查 W280 行+W280 finalize 件在场=已绿·未落即 loud abort 兜底）"
    u"=**splice 执行窗派生落地（r1129/r1130/r1131 W280 全周期先例实时间线：prereg 5f279e44fc 落于 r1130 窗·"
    u"splice 7a5b47ff94 落于 r1131 执行窗 01:5x——**W281 freeze 面：W280 own-wave finalize 已落地=席位时即解锁"
    u"——席位 r1132 窗+prereg r1133 窗落地 per seat-first law O-20261010-2350 §2·splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。",
)
# ---------------- §0 batch identity ----------------
add(
    u"- 批名=**PERPETUAL-N1-W280**。N=**2,200**（A 档 2,000；B 档 200）；账本 **+2,200**（null trials 计数自 K2200 先例）；"
    u"prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）：**W1..W279 N1 注册全部落地**"
    u"【W279=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W279**【净账本锚头 **1,038,135**·K=611,720 合并池"
    u"·n1_w279_results.json 机读·W279 finalize one-pass bm-c r1124 窗 20:0x】】；**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**"
    u"（上游 W279 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    u"- 批名=**PERPETUAL-N1-W281**。N=**2,200**（A 档 2,000；B 档 200）；账本 **+2,200**（null trials 计数自 K2200 先例）；"
    u"prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）：**W1..W280 N1 注册全部落地**"
    u"【W280=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W280**【净账本锚头 **1,040,335**·K=613,920 合并池"
    u"·n1_w280_results.json 机读·W280 finalize one-pass bm-c r1131 窗 02:0x】】；**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**"
    u"（上游 W280 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
)
add(u"累计 null 池=611,720+2,200（本波）=**613,920 投影**",
    u"累计 null 池=613,920+2,200（本波）=**616,120 投影**")
# ---------------- §0 claim line ----------------
add(u"MSG-20261020-@@SEAT_HHMM@@-bmc-w281-seat 已推 origin @@SEAT_SHA@@ r565 律（bm-c r1130 席·queue-head seat-first lane）",
    u"MSG-20261020-@@SEAT_HHMM@@-bmc-w282-seat 已推 origin @@SEAT_SHA@@ r565 律（bm-c r1133 席·queue-head seat-first lane）")
add(
    u"·probe W281+ 投影 A naive 633_301..635_300 **CLEAN**（hops=0·pre-W280 宇宙零 live refusers）"
    u"/ B naive 631_301..631_500 CLEAN hops=0 **但落 naive W280 A 窗内**→own-A reservation cascade 下 staircase 级联上移 "
    u"**staircase face 延续 live re-derive governs 预披露**（投影 A naive 633_301..635_300 CLEAN·hops=0"
    u"——**post-W280-REGISTERED 预披露：naive W280 A 起点将被注册 W280 B 带 633_301..633_500 拒=staircase affects A 第三十次连续 A-hop 预期**；"
    u"投影 B naive 633_501..633_700 clean 但落 naive W280 A 窗 633_301..635_300 内——**above-own-A 承袭面："
    u"W280 B 633_301..633_500 落本波 A 窗之上〔第三十次连续〕·W280 A 面 1-hop=staircase affects A〔第二十九次连续〕"
    u"·W281 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace"
    u"·注册 W280 B 带将拒 naive W280 A 窗仅当重叠——**W281 freezer 承接面强制注记：须在 post-W280 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））",
    u"·probe W282+ 投影 A naive 635_501..637_500 **CLEAN**（hops=0·pre-W281 宇宙零 live refusers）"
    u"/ B naive 635_701..635_900 CLEAN hops=0 **但落投影 A 窗内**→own-A reservation cascade 下 staircase 级联上移 "
    u"**staircase face 延续 live re-derive governs 预披露**（投影 A naive 635_501..637_500 CLEAN·hops=0"
    u"——**post-W281-REGISTERED 预披露：naive W282 A 起点将被注册 W281 B 带 635_501..635_700 拒=staircase affects A 第三十二次连续 A-hop 预期**；"
    u"投影 B naive 635_701..635_900 clean 但落投影 A 窗 635_501..637_500 内——**above-own-A 承袭面："
    u"W281 B 635_501..635_700 落本波 A 窗之上〔第三十二次连续〕·W281 A 面 1-hop=staircase affects A〔第三十一次连续〕"
    u"·W282 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace"
    u"·注册 W281 B 带将拒 naive W282 A 窗仅当重叠——**W282 freezer 承接面强制注记：须在 post-W281 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））",
)
add(
    u"T-2026-10-01 s1 引擎线第 270 波【bm-c 第九十九枚自有波【机面 derive：probe leg0 bmc_rows=98 attempt-continuity face"
    u"（r1124 窗算法·bm-c own seat+bmc live rows 98 实读）——freeze 时 live derive bmc rows 98+候选=第 99 枚 EXACT"
    u"（以 freeze 时 live derive 为准 r587/r359）】】",
    u"T-2026-10-01 s1 引擎线第 271 波【bm-c 第一百枚自有波【机面 derive：probe leg0 bmc_rows=99 attempt-continuity face"
    u"（r1132 窗算法·bm-c own seat+bmc live rows 99 实读）——freeze 时 live derive bmc rows 99+候选=第 100 枚 EXACT"
    u"（以 freeze 时 live derive 为准 r587/r359）】】",
)
add(u"（波号=注册表 W279 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261020-@@SEAT_HHMM@@-bmc-w281-seat",
    u"（波号=注册表 W280 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261020-@@SEAT_HHMM@@-bmc-w281-seat")
# ---------------- §0 RAM face (live placeholder) ----------------
add(u"**RAM face 如实注记：本窗 free RAM ~2.2GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测"
    u"·GPU=gen-only 车道 idle（nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释）",
    u"**RAM face 如实注记：本窗 free RAM @@RAM_FACE@@GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测"
    u"·GPU=gen-only 车道 idle（nvidia-smi 实读 @@VRAM_G@@ VRAM 占用·MV 车道已收官 GPU idle 回释）")
add(u"·W279 冻结窗 ~2.2G bm-c 实锚）", u"·W279 冻结窗 ~2.2G bm-c 实锚·W280 冻结窗 ~2.2G bm-c 实锚）")
# ---------------- §0 materialization / engine note ----------------
add(u"**引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1130 窗实读·队列空转 idle——五面冻结编辑落工作栈后引擎下一 cycle "
    u"n1_bands() mtime 复读复烧自见 W280 行并点火自烧",
    u"**引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1133 窗实读·队列空转 idle——五面冻结编辑落工作栈后引擎下一 cycle "
    u"n1_bands() mtime 复读复烧自见 W281 行并点火自烧")
# ---------------- engine instance path (bm-c instance = Tools/, verified live r1133) ----------------
add(u"引擎侧 `scripts/saturation_engine.py`【本机 bm-c 实例",
    u"引擎侧 `Tools/saturation_engine.py`【本机 bm-c 实例")
add(u"点火面 `scripts/saturation_engine.py`（本机 bm-c 实例",
    u"点火面 `Tools/saturation_engine.py`（本机 bm-c 实例")
# ---------------- §0.5 banned gate ----------------
add(u"python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W280_PREREG.md",
    u"python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W281_PREREG.md")
add(u"（p2_calibration v1/v2 canon；v1 ext；v2..W279 落地）", u"（p2_calibration v1/v2 canon；v1 ext；v2..W280 落地）")
# ---------------- §3 A rung ----------------
add(
    u"- **A 档**（j=0..1,999）：entry rng seed=**631_301+j**（法典 §4 W280 行 A=631_301..633_300"
    u"·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十九次连续 A-hop）**："
    u"A 算术续带 631_101..633_100（自注册 W279 A 尾 631_100 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）起点即 REFUSED"
    u"（注册 W279 B 带 631_101..631_300 落 naive A 窗内=W279 prereg §5 item5 post-W279-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    u"→walk 越注册 W279 B 尾 631_300→A first-clean 631_301..633_300·**hops=1**·**A 落位 base==注册前波 B 尾+1（631_300+1）机检关系**"
    u"（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W279_B=true）"
    u"·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`",
    u"- **A 档**（j=0..1,999）：entry rng seed=**633_501+j**（法典 §4 W281 行 A=633_501..635_500"
    u"·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第三十一次连续 A-hop）**："
    u"A 算术续带 633_301..635_300（自注册 W280 A 尾 633_300 续）在席位窗宇宙（post-W280-REGISTERED 终态注册）起点即 REFUSED"
    u"（注册 W280 B 带 633_301..633_500 落 naive A 窗内=W280 prereg §5 item5 post-W280-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    u"→walk 越注册 W280 B 尾 633_500→A first-clean 633_501..635_500·**hops=1**·**A 落位 base==注册前波 B 尾+1（633_500+1）机检关系**"
    u"（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W280_B=true）"
    u"·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`",
)
# ---------------- §3 B rung ----------------
add(
    u"- **B 档**（j=0..199）：entry rng=**631_301+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
    u"exit rng=**633_301+j**（法典 §4 W280 行 B=633_301..633_500·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    u"B naive 续带 631_301..631_500（自注册 W279 B 尾 631_300+1 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）起点即 REFUSED"
    u"（naive B 窗落本波 A first-clean 窗 631_301..633_300 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    u"→own-A reservation 越本波 A 窗 631_301..633_300→1 hop 落位 633_301..633_500·**B 落位 base==本波 A 窗尾+1（633_300+1）机检关系**"
    u"（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执·第三十次连续 above-own-A 落位如实注记）"
    u"·非转录 r587·与 W279 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
    u"- **B 档**（j=0..199）：entry rng=**633_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
    u"exit rng=**635_501+j**（法典 §4 W281 行 B=635_501..635_700·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    u"B naive 续带 633_501..633_700（自注册 W280 B 尾 633_500+1 续）在席位窗宇宙（post-W280-REGISTERED 终态注册）起点即 CLEAN 于注册宇宙"
    u"（probe leg1 relation_asserts B_naive_clean_vs_registered=true）但落本波 A first-clean 窗 633_501..635_500 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证"
    u"→own-A reservation 越本波 A 窗 633_501..635_500→1 hop 落位 635_501..635_700·**B 落位 base==本波 A 窗尾+1（635_500+1）机检关系**"
    u"（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执·第三十二次连续 above-own-A 落位如实注记）"
    u"·非转录 r587·与 W280 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
)
# ---------------- §3 determinism / disjointness ----------------
add(u"本波设计=W2..W279 逐字复用", u"本波设计=W2..W280 逐字复用")
add(u"W280 带与 v1 在用带", u"W281 带与 v1 在用带")
add(u"W2..W279 带（冻结时点全注册单态）", u"W2..W280 带（冻结时点全注册单态）")
add(u"本波机验 ADMIT 回执在场=_w280bmc_20261019 探针窗", u"本波机验 ADMIT 回执在场=_w281bmc_20261020 探针窗")
# ---------------- §4 readout ----------------
add(u"canon 120 + 已落账净值（起草窗实流 W1..W279 已落账 611,720 实测〔n1_w279_results.json 机读·W279 finalize 已落〕）+本波 2,200",
    u"canon 120 + 已落账净值（起草窗实流 W1..W280 已落账 613,920 实测〔n1_w280_results.json 机读·W280 finalize 已落〕）+本波 2,200")
add(u"batch_name=\"PERPETUAL-N1-W280\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w280_results.json\"",
    u"batch_name=\"PERPETUAL-N1-W281\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w281_results.json\"")
# ---------------- §5 predictions ----------------
add(u"（起草窗实况注记：**W1..W279 N1 注册全部落地**（W279 finalize 已落地 20:0x）——**本波 §5 预测键=**W279 实测值"
    u"**【results/perpetual_faces/n1_w279_results.json·N1 面最新已 finalize 键·20:0x finalize one-pass】",
    u"（起草窗实况注记：**W1..W280 N1 注册全部落地**（W280 finalize 已落地 02:0x）——**本波 §5 预测键=**W280 实测值"
    u"**【results/perpetual_faces/n1_w280_results.json·N1 面最新已 finalize 键·02:0x finalize one-pass】")
add(u"1. W280-only mu 与累计池 merged mu（W279 实测键 **−0.09282363**·K=611,720 合并池·W279-only 实测 **−0.10331555**）"
    u"差异 **|Δ|<0.02**（W2..W279 共二百七十八面实测 mu 稳定先例·单波跨键微；W279-only vs merged 实差 0.0105 在带内）。",
    u"1. W281-only mu 与累计池 merged mu（W280 实测键 **−0.09284669**·K=613,920 合并池·W280-only 实测 **−0.09925886**）"
    u"差异 **|Δ|<0.02**（W2..W280 共二百七十九面实测 mu 稳定先例·单波跨键微；W280-only vs merged 实差 0.0064 在带内）。")
add(u"2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24506025**=W279 合并池实测）。",
    u"2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24507971**=W280 合并池实测）。")
add(u"3. A 档 full_sharpe_p95 与 W279 A 档 p95（**0.3104** 实测锚）差 **<0.05**（门标注法 W5..W279 先例",
    u"3. A 档 full_sharpe_p95 与 W280 A 档 p95（**0.3294** 实测锚）差 **<0.05**（门标注法 W5..W280 先例")
add(
    u"4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W279 先例链披露"
    u"【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W279 实测 K-lift **+0.0000**·line_merged@K611,720 **1.197**"
    u"·line_pre_w279 1.197·n_eff_held_equal 1,035,935；se_mu 收窄链 …→W273 **0.000319**→W274 **0.000318**"
    u"→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 投影 0.000313】）。",
    u"4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W280 先例链披露"
    u"【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W280 实测 K-lift **+0.0001**·line_merged@K613,920 **1.1972**"
    u"·line_pre_w280 1.1971·n_eff_held_equal 1,038,135；se_mu 收窄链 …→W274 **0.000318**"
    u"→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 **0.000313**→W281 投影 0.000313】）。",
)
add(
    u"5. **W281+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 633_301..635_300 **CLEAN**"
    u"（hops=0·pre-W280 宇宙零 live refusers）——**post-W280-REGISTERED 预披露：naive W280 A 起点将被注册 W280 B 带 633_301..633_500 拒"
    u"（staircase-affects-A 第三十次连续 A-hop 预期）**；B naive **633_501..633_700 CLEAN（hops=0）但落投影 A 窗 633_301..635_300 内**"
    u"（W281p_B_lands_inside_W281p_A_naive=true——**staircase face 延续**：W280 A 631_301..633_300+B 633_301..633_500 注册后 "
    u"naive W280 A 窗起点即被注册 W280 B 带拒（staircase affects A 承袭·第三十次连续 A-hop 预期）→A first-clean 将上移"
    u"·B own-A reservation cascade 落位相应上移——post-W280 宇宙 live re-derive 必变·禁转录投影）；"
    u"**W280 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    u"（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268"
    u"/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279/W280=A/B 双 1-hop 形态连续二十九波如实注记"
    u"·seed-gap face 已于 W252 终结=A 首跳如实注记）——W280 冻结方必须在 post-W280 注册宇宙重 derive 且 derive B 时预留本波 A 窗 "
    u"631_301..633_300+本波 B 带 633_301..633_500——leg2 律/E36 卡·W141 先例；verify at W281 prereg，hop 链逐跳在 probe 回执。",
    u"5. **W282+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 635_501..637_500 **CLEAN**"
    u"（hops=0·pre-W281 宇宙零 live refusers）——**post-W281-REGISTERED 预披露：naive W282 A 起点将被注册 W281 B 带 635_501..635_700 拒"
    u"（staircase-affects-A 第三十二次连续 A-hop 预期）**；B naive **635_701..635_900 CLEAN（hops=0）但落投影 A 窗 635_501..637_500 内**"
    u"（W282p_B_lands_inside_W282p_A_naive=true——**staircase face 延续**：W281 A 633_501..635_500+B 635_501..635_700 注册后 "
    u"naive W282 A 窗起点即被注册 W281 B 带拒（staircase affects A 承袭·第三十二次连续 A-hop 预期）→A first-clean 将上移"
    u"·B own-A reservation cascade 落位相应上移——post-W281 宇宙 live re-derive 必变·禁转录投影）；"
    u"**W282 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    u"（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268"
    u"/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279/W280/W281=A/B 双 1-hop 形态连续三十波如实注记"
    u"·seed-gap face 已于 W252 终结=A 首跳如实注记）——W282 冻结方必须在 post-W281 注册宇宙重 derive 且 derive B 时预留本波 A 窗 "
    u"633_501..635_500+本波 B 带 635_501..635_700——leg2 律/E36 卡·W141 先例；verify at W282 prereg，hop 链逐跳在 probe 回执。",
)
# ---------------- §6 artifacts ----------------
add(u"run --shard k --of 12 --wave 280/finalize --wave 280", u"run --shard k --of 12 --wave 281/finalize --wave 281")
add(u"（n1_w280/ 分片计数增长·唯一点火证据·r325 律）", u"（n1_w281/ 分片计数增长·唯一点火证据·r325 律）")
add(u"`results/p2cal_ext/n1_w280/shard-<k>-of-12.json`", u"`results/p2cal_ext/n1_w281/shard-<k>-of-12.json`")
add(u"`results/perpetual_faces/n1_w280_results.json`", u"`results/perpetual_faces/n1_w281_results.json`")
add(u"engine_owner==bm-c 98 行注册〔冻结时点〕+ 本候选", u"engine_owner==bm-c 99 行注册〔冻结时点〕+ 本候选")
# ---------------- §7/§8 backfill algorithm names ----------------
add(u"bm-c r1130 W280 §7 范式", u"bm-c r1133 W281 §7 范式")
add(u"bm-c r1130 W280 §8 范式", u"bm-c r1133 W281 §8 范式")
# ---------------- footer ----------------
add(u"**W280 五面 splice（法典 §4 注册行+WAVE_CONFIGS）——W279 own-wave finalize 已落地=席位时即解锁（n1_w279_results.json 机读在场·gate0.5 绿）",
    u"**W281 五面 splice（法典 §4 注册行+WAVE_CONFIGS）——W280 own-wave finalize 已落地=席位时即解锁（n1_w280_results.json 机读在场·gate0.5 绿）")