# -*- coding: utf-8 -*-
"""r285 bm-b: HANDOVER.md 5x check update (r285 multiple of 5) -- FIXED.

Fix vs first attempt (self-caught truncation near-miss): split-anchored
surgical edit MUST keep the split-tail BODY (parts[2] from its first
newline = the whole file body); only the leading bm-a-275 entry inside
parts[2] is dropped. Size-monotonicity gate asserted (rewrite face).

Two surgical edits, zero history-rewrite (r252 law):
1) header check-chain: prepend bm-b r285 entry, keep bm-a r280 + bm-b r280,
   drop oldest entry (bm-a r275) -- chain stays 3-deep.
2) append one dev-queue increment row (round 285 bm-b) at file end.
"""
import io

P = r"C:\Users\Administrator\Desktop\Bigmoney\research\HANDOVER.md"
raw = open(P, "rb").read()
N0 = len(raw)
bom = raw[:3] == b"\xef\xbb\xbf"
text = raw.decode("utf-8-sig" if bom else "utf-8")

SEP = "；上一次最近核对="
parts = text.split(SEP)
assert len(parts) == 3, f"unexpected chain shape: {len(parts)} parts"
# body of the file = parts[2] from its first newline (drop only the 275 entry)
assert parts[2].startswith("bm-a round 275"), parts[2][:40]
nl = parts[2].index("\n")
REST = parts[2][nl:]
assert REST.startswith("\n## "), REST[:20]
assert len(REST) > 150_000, f"body truncated face: {len(REST)}"
assert "R285" in REST[-300:], f"file-tail anchor missing: {REST[-120:]!r}"

new_entry = (
    "最近核对=bm-b round 285（2026-09-27 00:5x·对账增量=文末 round 285 bm-b 行"
    "〔bm-b r281-285 窗：**T-87 供给车道首拉健康监视窗**（冻结探针谱系 #2-#5 "
    "on_track 连续·r285 读数 828/5228=15.8%·rate 12.68/min·ETA Sun 06:39:35="
    "周一 09:15 死线前 26.6h·零形状缺陷）+S0 rebase 撞车解三连（r281 CODELY "
    "memory-union 结构坍塌根修〔merge-base 字节锚律〕/r283 16-UU skill 分类解"
    "/r284 平窗）**；统一链 187,845 实读平持=本窗零批 finalize（REV_OSC 判决格"
    "在档待 bm-a tick 重发·CN_TREND prereg 冻结未跑·MF_IC_P1 待源）〕）"
    + SEP + "bm-a round 280"
)
p0 = parts[0].replace("最近核对=bm-a round 280", new_entry, 1)
assert "bm-b round 285" in p0 and "bm-a round 280" in p0
text2 = p0 + SEP + parts[1] + REST
assert text2.count("最近核对=") >= 3

row = (
    "- 开发队列增量窗（接续版）**round 285 bm-b（5x 核对本轮），2026-09-27 00:5x "
    "补核；对账区间=增量 bm-b r281-285（基线=round 280 bm-a 行），统一链 187,845 "
    "实读平持（本窗零批 finalize：REV_OSC judged cells 在档未判=修后待 bm-a tick "
    "重发、CN_TREND_ETF_P1 prereg 冻结面未跑、MF_IC_P1 待 EM 源恢复 legal park）**："
    "①**r281-285=T-87 供给车道首拉健康监视窗+撞车解三连**——r281 探针#2 on_track"
    "（207/5228@00:03）+round_reports 尾换行拆行修复（R281 律）+CODELY.md rebase "
    "memory-union 结构坍塌根修（merge-base 字节锚=base+两侧 append 直拼律·r188/"
    "R208 族新参）；r283 探针#3（591/5228@00:34）+S7 push 撞 bm-a R280 同窗 S6 双产 "
    "16-UU skill 正典解（14 整字节 take-new+audit history union 202|201→203+"
    "autofill 同秒 tie→HEAD）；r284 探针#4（714/5228@00:43）+Optuna 计数面坑律（模板 "
    "id 误计=轮内自捕）；r285 探针#5 on_track（828/5228=15.8%·rate 12.68/min·ETA "
    "Sun 06:39:35·827/828@cutoff·零形状缺陷·速率面 3→5 稳定 12.61/12.65/12.68）"
    "——**冻结探针谱系 r281→r285 逐字复刻零重建（frozen-probe lineage face）**；"
    "②维护面：S6 22 腿 rc=0 逐轮（周末诚实 no-op 族·astock lock-alive no-op·WM "
    "probe=py_low_with_work_cands 合法闲面证明〔唯一 ready 分片 REV-OSC=bm-a lane "
    "本机依法跳过·bandit claimed/parked·板 0 open〕·compute_audit CLEAN）、smoke "
    "25/25 逐轮、orders 89/89 双扫零未回执、post_review 尾零 NO、板 0 open/33 "
    "claimed、迁移执行器 v2.2 armed precheck 等待面（Tuanjie 编辑器门·journal "
    "15min 心跳健康·窗口 09-29 12:00）；③观测（非本机车道）：bm-a R280 REV_OSC d6 "
    "崩根修（load_member_rets 元组未解包·工程修零判定窗）+CN_TREND_ETF_P1 prereg "
    "冻结（T-87 s2 #1·7 judged cells·seed 20270201）；bm-c r71 后结构性停摆维持；"
    "④指针：**09-28 周一开市窗=新 bar 全链接力**（update_daily→live.paper "
    "REGIME_GUARD v3 enforce 首跑→t35v→t24×2→aggr 20 账→grid 5 账首拍 marks→"
    "export→scorecard→daily_report）+T-87 pass 完成复探（ETA 06:40 后）+周一 "
    "09:15 首次日续拉实弹（stragglers gate 自愈）+10-01 月度三件套+REGIME_GUARD "
    "v3 日期门生效+T-70 中期判读 10-09+10-31 六员首检 all-HOLD+T-34 半档梯 11-01 "
    "不变。\n"
)
if not text2.endswith("\n"):
    text2 += "\n"
text2 += row
out = text2.encode("utf-8-sig" if bom else "utf-8")
# size-monotonicity gate: only the ~1KB 275-entry removed; net must grow
assert len(out) > N0, f"size gate FAIL: {len(out)} < {N0}"
assert len(out) - N0 < 8000, f"size gate FAIL: delta {len(out)-N0} too big"
with io.open(P, "wb") as f:
    f.write(out)
raw2 = open(P, "rb").read()
assert (raw2[:3] == b"\xef\xbb\xbf") == bom
assert len(raw2) == len(out)
t2 = raw2.decode("utf-8-sig" if bom else "utf-8")
assert "round 285 bm-b（5x 核对本轮）" in t2
assert "## 一、当前模式与怎么停/恢复" in t2          # body intact
assert t2.count("## ") >= 5                          # all sections alive
print(f"HANDOVER updated OK: {N0} -> {len(raw2)} bytes (+{len(raw2)-N0}), "
      f"chain 3-deep, body intact, {'BOM' if bom else 'no-BOM'}")
