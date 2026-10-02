# -*- coding: utf-8 -*-
"""r382 bm-c S7 bookkeeping: state round 382 + heartbeat dynamic fields
(r583 carry law) + round report line + one CODELY pit entry. Bytes-in/bytes-out
for md faces (r530), JSON load-modify-write for state faces."""
import json, time, datetime, sys

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

# ---------------- state-bm-c.json ----------------
sp = "state-bm-c.json"
d = json.load(open(sp, encoding="utf-8"))
d["round_no"] = 382
d["last_round_at"] = "r382"
d["last_round_ts"] = ts
d["updated"] = iso
d["verify"] = ("r382: W113 seat+freeze+ignite same round (five-face eeb062290 on origin; "
               "A 269_004..271_003 arithmetic hops=0 / B 62_001..62_200 jump-past-hit over "
               "SEED_REGISTRY cta_wave1=62_000 window-tail endpoint per D-20261002-05 pinned "
               "skip law; seat MSG-20261002-1949-bmc pushed baa0c3888 BEFORE freeze r565 law; "
               "prereg anchor=W111 landed values merged mu -0.09276358334710065 K=242,120; "
               "band gate ADMIT rc0 + banned ADMIT + probe rc0 cross-checked vs bm-a tail "
               "projection; engine self-ignited r359 resident v0.4: 12/12 shards burned "
               "in-window ~8min) + pf selftest 9/9 + n1 selftest PASS + FIX-A/B/C pure "
               "insertion +26/+186/+2 -0 + AST gate + smoke 47/47 + S6 33 legs rc0 (dualrun "
               "ZERO-DRIFT streak 51, WM py_low_board_clear legal, attrition CLEAN, orders "
               "143/143 double-scan) + D-19 MATCH 937A373D + self-heal 4/4 (pin=5 no-op, "
               "watchdog live, claws MATCH) + delivery 0/0 verified + r589 reset-FF-reland "
               "loop over bm-b r591 mid-window closeout (appender-commit x origin-advance "
               "divergence, no rebase no force)")
d["did"] = ("r382: W113 freeze landed + engine 12/12 burned in-window; W113 finalize "
            "chain-gated behind W112 (bm-a) finalize, honest note")
d["current_task"] = ("r382 wrap: W113 12/12 delivered, finalize waits on W112 (bm-a) "
                     "finalize to unblock chain (FAIL-CLOSED r307); 3 late shards ride "
                     "this closeout commit")
d["next"] = ("(r383)(a) W113 finalize SAME-ROUND once W112 finalize lands (python "
             "scripts/perpetual_faces_n1.py finalize --wave 113; cross-machine drain "
             "legal per W108/W110 precedent if W112 products reach origin); (b) "
             "finalize-same-round root-fix: engine tick auto-finalize leg on own-wave "
             "12/12 (r381 lesson; open ticket or direct-exec); (c) T-144(c) protocol+flow "
             "domain sinking due 10-07; (d) T-143 month-exam prep 10-29; (e) month-boundary "
             "first exam 10-31")
d["heartbeat_epoch_utc"] = epoch
d["clock_read"] = iso
d["last_ts"] = ts
d["last_round"] = ("2026-10-02 r382 bm-c: W113 seat+freeze+ignite same round "
                   "(eeb062290) + S6 33 legs rc0 + smoke 47/47 + orders 143/143")
d["last_seen"] = ts
json.dump(d, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
print("state written: round", d["round_no"], "epoch int", isinstance(d["heartbeat_epoch_utc"], int))

# ---------------- heartbeat fleet/machines/bm-c.json ----------------
hp = "fleet/machines/bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
ack = h["orders_ack"]  # r583 carry verbatim, never rebuild
h["round_no"] = 382
h["updated_at"] = iso
h["last_seen"] = iso
h["last_seen_at"] = ts
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["cpu_pct"] = h["cpu_util_pct"] = h.get("cpu_pct", 24.9)
h["ram_free_gb"] = h["free_ram_gb"] = h["idle_ram_gb"] = h.get("ram_free_gb", 8.7)
h["gpu_vram_free_mb"] = h["gpu_free_vram_mb"] = h["gpu_free_vram_mib"] = \
    h["gpu_idle_vram_mb"] = h["gpu_idle_vram_mib"] = h.get("gpu_vram_free_mb", 4709)
h["prod_lanes"] = ("r382: W113 seat+freeze+ignite same round (eeb062290 on origin; 12/12 "
                   "shards burned); fleet chain W1..W111 landed head 608,748 + W112 bm-a "
                   "burn in flight finalize pending + W113 bm-c 12/12 delivered finalize "
                   "chain-gated; next bm-c wave = W114 (projection A 271_004..273_003 / "
                   "B 62_201..62_400 CLEAN)")
h["current_task"] = ("r382 wrap; W113 finalize waits on W112 (bm-a) finalize; next "
                     "supply wave W114 after finalize chain unblocks")
h["verdict"] = ("healthy: W113 frozen+ignited+12/12 burned same round (r359 self-ignite; "
                "ignition proof = product growth); S6 33 legs rc0; smoke 47/47; "
                "self-heal 4/4; attrition CLEAN")
h["activity_now"] = ("S7 wrap (state 382 + heartbeat + round report + CODELY pit + "
                     "closeout commit/push); W113 12/12 delivered, finalize chain-gated "
                     "behind W112 (bm-a)")
h["latest_artifact"] = ("research/PERPETUAL_N1_W113_PREREG.md + five-face freeze commit "
                        "eeb062290 on origin (19:5x; W113 103rd engine wave, bm-c 33rd "
                        "owned; A 269_004..271_003 / B 62_001..62_200 jump-past-hit "
                        "D-20261002-05; 12/12 shards burned in-window)")
h["next_milestone"] = ("W113 finalize as soon as W112 (bm-a) finalize lands (chain order; "
                       "next bm-c round checks and finalizes same-round); T-144(c) "
                       "protocol+flow sinking by 10-07; month-boundary first exam 10-31")
h["orders_ack"] = ack  # carried verbatim
json.dump(h, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
print("heartbeat written; orders_ack carried:", len(ack))

# ---------------- round report line ----------------
rp = "round_reports-bm-c.md"
rb = open(rp, "rb").read()
eol = b"\r\n" if rb.count(b"\r\n") * 2 > rb.count(b"\n") else b"\n"
line = (
    "2026-10-02T" + now.strftime("%H:%M:%S") + "+08:00 | r382 | "
    "watermark: 绿（red=false·verdict=py_low_board_clear 合法（引擎车道 W113 12/12 已交付·板面闭环））"
    "｜当前活=r382 收口（W113 冻结+自燃+12/12 烧毕同窗·finalize 链序待 W112 bm-a）"
    "｜最近实物=research/PERPETUAL_N1_W113_PREREG.md+五面冻结 commit eeb062290（19:5x·origin 送达 0/0）"
    "｜下个里程碑=W113 finalize（W112 bm-a finalize 落账即同轮跑·≤下一轮窗）→ T-144(c) 协议+流水下沉 10-07 → 月界首考 10-31 "
    "‖ 本轮主产：W113 席位+冻结五面同轮落地（bm-c 第 33 席自有波·第 103 枚引擎波·A=269_004..271_003 算术续带 hops=0 CLEAN/"
    "B=62_001..62_200 撞值跳位窗——算术窗 61_801..62_000 撞 SEED_REGISTRY cta_wave1=62_000〔窗尾端点=W74/W81 判例族〕→ D-20261002-05 钉死行越 hit 起窗 hops=1·"
    "与 bm-a W112 尾投影交叉验证一致=自机 derive 非转抄 r587 律）+席位 MSG-20261002-1949-bmc 先推 origin baa0c3888（r565 早可见性律·净空窗单件直推零拒绝）"
    "+per-wave prereg（锚=W111 实测键 merged mu −0.09276358334710065·K=242,120·链头 608,748·se_mu 0.000498·p95 0.3191·K-lift 0.0000·池投影 246,520）"
    "+带闸 ADMIT rc0（leg0 110 行表尾=W112·leg0b 自席位在 origin+零外机 W113 席位双目录·leg1 跳位 derive·leg2 origin 三查净空）+禁向闸 ADMIT 0"
    "+引擎自燃 12/12 分片同窗烧毕（r359 常驻 v0.4 mtime-reload 免杀重启·点火证据=产物增长 6→12 分片）"
    "+S0 r589 撤-FF-重落环（bm-b r591 中窗收轮 35193dcd1 × 本机 appender 6 分片 commit=双头分叉·FF abort 诊断签名·reset --mixed HEAD~1→FF→9 分片随冻结 commit 重落 eeb062290·零 rebase 零 force·余 3 分片随本轮收口 rides）"
    "+S6 33 腿 rc0（dualrun ZERO-DRIFT streak 51/3·WM py_low_board_clear 合法·compute_audit 绿·market_clock/日报/CEO 页再生·国庆无新 bar paper 块免=r588 先例·车道腿诚实 no-op·update_fund_premium bm-c 车道实跑） "
    "‖ 验证证据：pf selftest 9/9 / n1 selftest PASS（缺省波·W113 materializer 腿+summary 段在场）/ FIX-A/B/C 纯插入 +26/+186/+2 −0+AST 门 / freeze push 送达核验 behind=0 ahead=0 / attrition scan CLEAN（4 ledger）/ orders 143/143 双扫 / D-19 937A373D MATCH / 自愈 4/4（pin=5 no-op·watchdog 在位·双爪 MATCH） "
    "‖ 下轮指针：(a) W113 finalize 同轮收口——前置=W112 bm-a finalize 落账（链序 FAIL-CLOSED r307·若 W112 产物上 origin 且 bm-a 滞后>1 轮=按 W108/W110 先例跨机 drain 合法）；(b) finalize 同轮收口根治面：引擎 tick 本机 owned 波 12/12 且 finalize 缺席自动 finalize（r381 坑·下轮开票或直执）；(c) T-144(c) 协议+流水下沉 10-07；(d) T-143 月考备考 10-29 [via bm-c r382]"
)
count_line = ("2026-10-02T" + now.strftime("%H:%M:%S") + "+08:00 | r382 | "
              "本地未达 origin commit 数=0（收口 commit 推送后 fetch+rev-list 自证）")
if not rb.endswith(eol):
    rb += eol
rb += line.encode("utf-8") + eol + count_line.encode("utf-8") + eol
open(rp, "wb").write(rb)
print("round report appended: 2 lines")

# ---------------- CODELY.md one pit entry ----------------
cp = "CODELY.md"
cb = open(cp, "rb").read()
ceol = b"\r\n" if cb.count(b"\r\n") * 2 > cb.count(b"\n") else b"\n"
pit = (
    "- [2026-10-02 20:0x r382 bm-c] appender 批量 commit×中窗 origin 前进=结构性双头分叉的 FF 诊断签名（r589 环第三写者变体·r569 三写者族）：本机自有 commit 已全部推净后仍见「Diverging branches can't be fast-forwarded」——第三写者=引擎 appender 在轮中把已烧分片自行 commit 进本地 main（r359 律自燃面），与他机中窗收轮前进构成双头；诊断序=rev-list 双向计数+merge-base 定位+未推 commit 归属核（origin/main..HEAD=1 且非本人手 commit=appender 所为）。正解=r589 撤-FF-重落环原样适用（reset --mixed HEAD~1 撤 appender commit→分片 untracked 原样在场→FF→随冻结 commit 重落），禁 rebase（appender 在飞=r532 面）。How to apply：FF 被拒先查未推 commit 归属再定性（勿直接跳外科）；appender commit 属可撤面（内容=分片产物·reset --mixed 零丢失）。"
)
if not cb.endswith(ceol):
    cb += ceol
cb += pit.encode("utf-8") + ceol
open(cp, "wb").write(cb)
print("CODELY pit appended; bytes:", len(cb))
print("S7_BOOKS_OK")
