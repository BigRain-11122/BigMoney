# -*- coding: utf-8 -*-
"""r851 bm-a closeout writer: S5 ledger append (ROOT canonical GBK) + state + heartbeat.
Multi-writer law 2026-10-06: python fresh read-modify-write, no replace-tool."""
import io, json, time, datetime
sys_stamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- S5 ledger append (ROOT round_reports-bm-a.md; append-only, tail-anchored) ----
# r844-queued fork/encoding pit: file body is mixed-encoding archive (GBK head,
# UTF-8 tail since r850). Append BYTES matching the tail convention; never
# decode the full body.
line = (
 "2026-10-08T00:3x+08:00 | r851 bm-a (dept:research) | watermark verdict: green (red=false lane=healthy; next_pick=claimed moneyflow IC batch parked source-blocked; compute_audit FLAG pool_starvation+supply_floor breach=true -> canonical response = W180 seat chain in-flight 本轮) | 当前活: W180 seat chain half-window closed（probe ADMIT + seat push + band gate 四腿 ADMIT） | 最近实物: results/_r851bma_w180_probe_receipt.json + fleet/inbox/processed/MSG-2026-10-08-0030-bma-w180-seat.md + results/_r851bma_w180_bandgate.json @2026-10-08T00:2x（origin d3b0737fe seat / e069782f7 self-ack） | 下个里程碑: r852 W180 prereg+freeze 五面 gated push（S80 grounding 已备 _r851bma_w180_seat_chain_continuation.md·引擎随后自烧 12 分片）+ 今日 15:30 复市首 bar 数据链全门 re-arm+REGIME_GUARD v3 enforce 激活（窗≤今日收盘） | did: S0 锚定 bm-a+孤儿面 1 只读探针+pull behind-0+S0.5 orders 51/51 零未回执+DEC/ORD 水位 ee659451/2bb2ee75 python 正典恒等零动作（PS 伪哈希当场让位=r828/r832 家族坑避开）+S1 smoke 48/48+S3 主产出=W180 pre-seat probe（r848 血统适配·leg0 177 行 tail=W179 head 799,505 机读·leg1 A 410_804..412_803 阶梯 FORTIETH hops=1+B 412_804..413_003 W141 leg2 hops=1 与 r848 leg4 预告逐字兑现·leg2 冲突 0·leg3 origin 空档·leg4 W181+ 投影 A 412_804..414_803/B 413_004..413_203 B-in-A）→ seat MSG 直推 d3b0737fe（r565 早公示律）→ self-ack inbox→processed e069782f7（r848 先例）→ band gate 四腿 ADMIT（leg0b own-seat-on-origin+leg1 parity+leg2 zero-conflicts+leg3 W181 projection·receipt _r851bma_w180_bandgate.json）+ S80 grounding 落 continuation file（W179 results JSON 键名机读核验+S80 pair 骨架+quirk 保留清单·r852 buildgen 免重推）+S6 38/38 rc0（dualrun ZERO-DRIFT streak 51@406·复市前全门诚实 no-op cutoff 09-30·REPORT/LIVE-20261008 双面幂等再产·moneyflow rank pass+ah refresh 分离 spawn 披露）+S7 quartet 绿（pin=8 no-op·watchdog 幂等重注册·双爪 parity True/True·attrition CLEAN 4 件）+idle_trigger --worked idle_rounds=0 | scoring: 2（席位链半窗实物=probe+seat+bandgate 三件上 origin+带法阶梯第 40 例推进）| 记账预算: 4/5（state+轮账行+心跳+closeout commit）| 宝藏捕获问: 本批零新方法零新宝藏（r848 血统 verbatim 复用·S80 grounding=下轮备料非新方法·TREASURE/METHODOLOGY 零 append）| 本地未达 origin commit 数=0（push 后 fetch+rev-list 自证）| 孤儿面=1（round-zero 探针只读·ComfyUI idle server CEO 属主免杀档）| next-round pointer: r852=W180 prereg buildgen（S80 map=continuation file·AST 抽取 r849 BACK179/EXPECT）+freeze 五面（PF N1_BANDS[180]/n1 WAVE_CONFIGS[180]+materializer+PASS-claim）+banned gate+pf 9/9+n1 selftest 双绿+冻结 commit（surgical 若竞态）→ 引擎自烧；+10-08 15:30 复市数据链 re-arm+OSS ledger S3/S4/S5 扫描窗 10-09+O-1850 VL 共居 3 读数+CEO 令执行件推进（P-audit 10-12/R-research+REGIME-5 10-14）| [r851 bm-a]"
)
p = "round_reports-bm-a.md"
old = open(p, "rb").read()
last_line = old[old.rstrip(b"\r\n").rfind(b"\n") + 1:] if b"\n" in old.rstrip(b"\r\n") else old
last_txt = None
for enc in ("utf-8", "gbk"):
    try:
        last_txt = last_line.decode(enc)
        tail_enc = enc
        break
    except UnicodeDecodeError:
        continue
assert last_txt is not None, "last line not decodable in either convention"
assert "r850 bm-a" in last_txt, "tail anchor: last line is not r850"
payload = (line + "\n").encode(tail_enc)
if not old.endswith(b"\n"):
    payload = b"\n" + payload
open(p, "ab").write(payload)
chk_tail = open(p, "rb").read()[-len(payload):]
assert chk_tail == payload, "ledger append roundtrip drift"
print("ledger appended:", len(payload), "bytes, tail_enc =", tail_enc)

# ---- state-bm-a.json ----
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round"] = 851; st["round_no"] = 851; st["loop_round"] = "r851"; st["last_round"] = "r851"
st["current_task"] = ("W180 seat chain landed (probe+seat+bandgate ADMIT); r852: prereg+freeze five-face "
                      "gated push (S80 grounding ready); 10-08 market-reopen data chain re-arm after 15:30")
st["did"] = ("r851: W180 seat chain half-window one-pass (probe r848-bloodline rc0 ADMIT A 410_804..412_803 "
             "staircase FORTIETH hops=1 / B 412_804..413_003 W141 leg2 hops=1, naive 410_604..412_603 refused "
             "by W179 B exactly as r848 leg4 mandated -> seat MSG push d3b0737fe -> self-ack e069782f7 -> band "
             "gate four legs ADMIT) + S80 grounding continuation file + S0.5 orders 51/51 + DEC/ORD watermark "
             "identical python-canonical zero-action + S1 smoke 48/48 + S6 38 legs rc0 (dualrun ZERO-DRIFT "
             "streak 51; pre-market honest no-op family cutoff 09-30; REPORT/LIVE-20261008 twins idempotent) + "
             "S7 quartet green + attrition CLEAN + idle_trigger --worked")
st["heartbeat_epoch_utc"] = epoch
st["last_action"] = ("W180 seat chain half-window closed on origin (d3b0737fe seat + e069782f7 self-ack; band "
                     "gate ADMIT; r852 = prereg+freeze gated push)")
st["last_round_at"] = sys_stamp; st["last_round_ts"] = sys_stamp; st["last_run"] = sys_stamp
st["last_seen"] = sys_stamp; st["ts"] = sys_stamp; st["clock_read"] = sys_stamp
st["updated"] = sys_stamp
st["last_decisions_at"] = sys_stamp
st["last_decisions_seen"] = ("hash ee659451 identical at r851 python-canonical re-read (K: tree absent -> local "
                             "FluxGroup fallback D-20261004-02(3)); PS-pipeline artifact 1a7facb3 rejected per r828/r832; "
                             "orders.md 2bb2ee75 identical zero-action")
st["next"] = ("r852: W180 prereg+freeze gated push (S80 continuation file ready: AST-extract r849 BACK179/EXPECT, "
              "S80 pair skeleton, W179 results keys verified) -> engine self-burn 12 shards -> finalize r853; "
              "+ 10-08 15:30 market-reopen first-bar data chain re-arm (all gates fire + REGIME_GUARD v3 enforce "
              "activation) + OSS ledger S3/S4/S5 pending-scan by 10-09 + O-1850 VL pull+co-residence test 3 "
              "readings + CEO order execution files advance")
st["latest_artifact"] = "results/_r851bma_w180_bandgate.json (W180 seat chain half-window ADMIT; origin d3b0737fe/e069782f7)"
st["verify"] = ("seat chain: probe rc0 ADMIT legs 0-4 + band gate 4/4 ADMIT + seat on origin verified; smoke 48/48; "
                "S6 38/38 rc0; attrition CLEAN; orders 51/51; quartet 4/4; dualrun streak 51; local "
                "not-at-origin=0 post-push fetch self-check")
st["now_active"] = ("W180 seat chain landed (r852 prereg+freeze next); 10-08 reopen-day data chain re-arm after "
                   "15:30 + CEO order files advance (P-audit 10-12 / R-research+REGIME-5 10-14)")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written round 851")

# ---- heartbeat fleet/machines/bm-a.json ----
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
it = json.load(open("results/idle_trigger_state.bm-a.json", encoding="utf-8"))
hb["last_seen"] = sys_stamp
hb["current_task"] = st["current_task"]
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = sys_stamp
hb["ts"] = sys_stamp
for k in ("idle_rounds", "agenda_starved", "ram_free_pct", "vram_free_gb", "two_read_red"):
    if k in it:
        hb[k] = it[k]
hb["verdict"] = "green"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
print("heartbeat written epoch-int verified:", chk["heartbeat_epoch_utc"])
