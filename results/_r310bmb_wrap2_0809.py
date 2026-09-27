# -*- coding: utf-8 -*-
"""r310 bm-b wrap pass-2: mid-round CEO order O-20260927-0809 catch-and-dispose
(S7 double-scan law -- order landed 08:09, pulled into tree 08:14 via push-retry
rebase, AFTER the 08:12 orders scan; this pass acks + wires the T-90 spec upgrade)."""
import json, datetime, io, glob, os

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
assert "+" in NOW_ISO and "T" in NOW_ISO
HB = "fleet/machines/bm-b.json"
RR = "logs/iteration-loop/round_reports.md"
STATE = "logs/iteration-loop/state.json"
T90 = "fleet/tasks/T-2026-09-27-90-P1.json"
EV = "results/_r310bmb_wrap2_0809.json"

# ---- 1. T-90 ticket: progress note for the amendment (spec text = GM's, untouched)
t = json.load(io.open(T90, encoding="utf-8"))
assert "AMENDMENT per CEO order O-20260927-0809" in t["spec"], "GM amendment not present in spec"
assert "bm-b" in t["claimed_by"], t["claimed_by"]
t["progress_r310bmb_amendment"] = (
    "r310 pass-2 @ " + NOW_ISO + " (O-20260927-0809 mid-round catch): prereg "
    "research/DECISION_CHAIN_E2E_P1.md + §9 ZERO-RUN AMENDMENT frozen (scale upgrade: faces {base,x2} "
    "full grid x windows {6m,12m,24m} x both axes 2,761 starts; N_eff re-derived = 16,566 new envelope "
    "cells (A1-x2+A2-x2+B-{base,x2}+D-{base,x2} x 2,761; A1/A2 base = T-34-counted re-derivation not "
    "recounted, G-REPRO base-face gate kept, x2 face G-REPRO-exempt disclosed); J-TARGET added verbatim "
    "per O-0809 sec.2 (A1 pooled beat > B AND worst-start dd >= -0.10, reported alongside J-C lines, "
    "no merging); version ledger research/DECISION_CHAIN_LEDGER.md created with v1 baseline row "
    "(change=none baseline, mechanism hypothesis=prereg s1 alpha, verdict=PENDING); anti-dredging 3 "
    "gates wired (iteration count into N_eff series-corrected DSR/PBO, mechanism hypothesis per "
    "version, no same-version result-driven edits); runner next round = full-grid scope per R99")
json.dump(t, io.open(T90, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("T-90 ticket: amendment progress noted")

# ---- 2. heartbeat: orders regen with O-0809 + faces update
order_files = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
assert "O-20260927-0809-bm-a.md" in order_files, order_files[-3:]
hb = json.load(io.open(HB, encoding="utf-8"))
prev = set(hb.get("orders_ack", "").split())
missing = [o for o in order_files if o not in prev]
assert missing == ["O-20260927-0809-bm-a.md"], "unexpected orders delta: %r" % missing
epoch = int(datetime.datetime.now().astimezone().timestamp())
hb["last_seen"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = ("r310 wrap pass-2: O-20260927-0809 acked + wired (prereg s9 zero-run amendment "
                      "scale-up + DECISION_CHAIN_LEDGER v1 + J-TARGET CEO line); next round = T-90 full-grid "
                      "runner + T-89 slice-1b runner -> pool")
hb["verdict"] = ("green; CEO orders O-0752/O-0758/O-0809 all acked (O-0809 mid-round catch per S7 "
                 "double-scan law); T-90 bm-b-owned: prereg FROZEN + s9 zero-run amendment per O-0809 "
                 "scale mandate (full grid base+x2, N_eff 16,566 new cells) + version ledger v1; T-89 "
                 "bm-b-owned: slice-1b runner next; S6 30/30 rc=0; smoke 25/25; migration armed editor-"
                 "gated normal (window to 09-29 12:00)")
hb["orders_ack"] = " ".join(order_files)
hb["n_orders_ack"] = len(order_files)
json.dump(hb, io.open(HB, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# ---- 3. round report addendum line
ADD = (NOW_ISO + " | r310 bm-b ADDENDUM (S7 double-scan catch): 轮中 CEO 令 O-20260927-0809（链条大幅回测+迭代机制令·"
 "bm-a GM 08:09 签发 6679bb17 08:10:12 落·本机 08:14 push-retry rebase 拉入=晚于 08:12 orders 扫描）→ 本窗处置："
 "①预注册 research/DECISION_CHAIN_E2E_P1.md §9 零跑修正案冻结（冻结 a9ed12ff 08:08:09 先于令约 1 分钟·零格已烧=合法修正窗 r251/r280 先例）："
 "规模律升格 faces {base,x2} 全网格×窗 {6m,12m,24m}×双轴 2,761 起点（原 x2 不入批条款作废）+N_eff 重定 16,566 新包络格"
 "（A1-x2/A2-x2/B-{base,x2}/D-{base,x2}×2,761·A1/A2 base=T-34 已计重派生不重计·G-REPRO base 面门维持·x2 面免 G-REPRO 如实注记）"
 "+J-TARGET 新增（CEO §二冻结口径逐字：A1 pooled beat > B 且最差起点 dd ≥ −0.10·与 J-C 系并列禁合并·预测 v1 PASS 15-35%=断环定位驱动 v2 迭代=令内建机制非批失败）"
 "+迭代系列/反 dredging 三闸接线（v1 基线版·迭代数入 N_eff 系列校正·每版必带机制假设·禁看当版改当版）；"
 "②版本台账 research/DECISION_CHAIN_LEDGER.md 建立（v1 基线行落册·append-only）；③T-90 票面 progress_r310bmb_amendment 注记"
 "（GM spec 升格 6679bb17 零触碰）；④orders_ack 93→" + str(len(order_files)) + " 全枚举再生回执 | evidence: "
 "research/DECISION_CHAIN_E2E_P1.md §9+research/DECISION_CHAIN_LEDGER.md+results/_r310bmb_wrap2_0809.json+commit 待推")
with io.open(RR, "a", encoding="utf-8", newline="\n") as f:
    f.write(ADD + "\n")

# ---- 4. state: next pointer refreshed to amended scope
st = json.load(io.open(STATE, encoding="utf-8"))
assert st["round_no"] == 310
st["next"] = ("T-90 runner=decision_chain_e2e.py 全量网格版（Stage A 成员曲线 base+x2 双面复用/重派生 2x16,566 格→"
              "Stage B 四臂×双面包络 16,566 新格→hermetic selftest+B7b 契约腿→runnable_pool·J-TARGET CEO 线入判）+"
              "T-89 slice-1b runner=prospect_regime_segments.py→池；09-28 周一首新 bar 全链+T-87 首续拉；"
              "10-01 月度三件套+REGIME_GUARD v3 日期门；迁移窗至 09-29 12:00")
st["updated_at"] = NOW_ISO
json.dump(st, io.open(STATE, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# ---- 5. gates
hb2 = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int) and "T" in hb2["clock_read"] and "+" in hb2["clock_read"]
assert set(hb2["orders_ack"].split()) == set(order_files) and hb2["n_orders_ack"] == len(order_files)
rr_tail = io.open(RR, encoding="utf-8").read().rstrip("\n").splitlines()[-1]
assert "O-20260927-0809" in rr_tail and rr_tail.startswith(NOW_ISO[:16]), "addendum tail gate"
ev = {"ts": NOW_ISO, "heartbeat_epoch_utc": epoch, "n_orders_ack": len(order_files),
      "newly_acked": missing, "gates": "epoch int PASS + clock PASS + orders regen PASS + "
      "T-90 spec-amendment assert PASS + report addendum tail PASS"}
json.dump(ev, io.open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False))
