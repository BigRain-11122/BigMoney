# -*- coding: utf-8 -*-
"""r478 bm-c closeout: state + heartbeat(IN-PLACE) + round-report append.
Laws: r475 heartbeat-field-loss lesson -> IN-PLACE field updates only, field-count
before==after assertion, orders_ack count==154 intact; r645 programmatic json.dump
+ json.loads self-check; heartbeat epoch int(time.time()) direct; EOL-preserving
report append with dedup needle assertion."""
import datetime
import json
import time

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TS_OFF = TS + "+08:00"
TS_SP = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ACT = ("golden-week watch r478 CLOSED: trio 3-evidence healthy (V796/Q619/D464, "
       "+3/+3/+2 vs r675, keepalive 9.7min, ETA V 10-06T15/Q 10-07T09/D 10-08T04); "
       "engine supply-exhaustion characterized (N1 waves all consumed, awaiting "
       "wave-3/T-86 legs); S6 38/38 rc0")
CUR = ("当前活: golden-week watch r478 CLOSED (trio 3-evidence healthy V796/Q619/D464, engine supply exhausted by design) | "
       "最近实物: results/_r478bmc_trio_watch.json (3-evidence probe, baseline r675) + results/_r478bmc_s6_log.txt (38/38 rc0) @ " + TS + " | "
       "下个里程碑: fund-trio finalize window 10-05 10:30 opens (bm-b owner, ETA V 10-06 15:00); D-06 closure 10-07 (bm-c lead); market reopen 10-09")
NXT = ("(a) r479 watch round: trio probe baseline V796/Q619/D464; escalate only on NEW "
       "keepalive-unhealthy or heartbeat >20min + origin silence past watchdog window. "
       "(b) fund-trio finalize window 10-05 10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole 10-07). "
       "(c) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. (d) D-06 full closure window "
       "10-07 (bm-c lead). (e) O-2115/O-2030 acceptance 10-08; T-158 W2 acceptance pack 10-08; "
       "market reopen 10-09; next 5x = bm-c r480.")
DID = ("r478 bm-c golden-week watch round (zero incident): (1) S0: no rebase leftovers; "
       "round-start dirty = 3 own satengine/autofill lane faces; origin behind=3 (r477 "
       "post-receipt merge pair + bm-a r680 LHB closure) zero-intersection -> absorb "
       "c0eb1ebc2 + merge zero-UU -> push REJECTED rc1 (bm-b r675 wave in flight) -> "
       "merge#2 zero-UU -> push_verify DELIVERED tip 79e7e9c89 ahead=0 behind=0; "
       "concurrency triple-evidence probe (r643): 05:05 pair = resident satengine daemon "
       "(legal long-lived), 14:2x = own tick chain + shell hosts, r477 session dead after "
       "14:22:05 last push. (2) S0.5: orders 153/153 zero un-acked (same-caliber same-form "
       "set-diff, S0.5 + S7 double-scan, probe _r478bmc_orders_d19_probe.py); inbox 0 "
       "inbound (MSG-1332 closed by bm-b receipt = next-pointer(b) discharged); D-19 "
       "decisions 4E5BE321 + group-orders 68947C17 double MATCH (per-key raw-blob SHA-256/"
       "SHA-1 caliber) -> zero consumption. (3) S1 smoke 48/48. (4) S2: boards empty "
       "(job_list 0; fleet tickets open=0, 45 claimed = lanes; T-158 = W2 judged-negative "
       "closed, held for 10-08 acceptance). (5) S3: satengine rc0 alive (Tools face, cycle "
       "2084 @14:29:07); WM red=false healthy; py_low_board_clear legal idle; engine state "
       "characterized: burns_active=[], done_count 1356, N1 registered waves all consumed "
       "(quarantine [12,11] old-case only) = supply exhausted by design, next face = "
       "wave-3 grammar (blocked on T-86 census legs, bm-a lane); fund-trio watch: "
       "V796/Q619/D464 of 2000, delta +3/+3/+2 vs r675 baseline, keepalive 9.7min healthy "
       "True x3 (owners=bm-b, claim intact no-touch per r626d-2), wide-window rates "
       "24.4/20.5/17.9 per h, ETA V 10-06T15/Q 10-07T09/D 10-08T04 -> zero escalation per "
       "r477-补 re-based criteria; W14 parked per O-0808. (6) S6 38/38 rc0 FAILS=[] "
       "(dualrun ZERO-DRIFT streak 51, 368 entries; update_daily golden-week cutoff "
       "2026-09-30 zero new rows; market_regime ORANGE shadow days=2; lhb 11-page "
       "incremental refresh; REPORT/LIVE-2026-10-04 idempotent regen state=ORANGE). "
       "(7) S7: loop pin5 phase-ok (next fire 14:35), watchdog present, claws x2 ok, "
       "attrition CLEAN (4 ledgers), orders re-scan 153/153 zero-diff; heartbeat "
       "IN-PLACE write (orders_ack 154 intact + field-count assertion + epoch int + "
       "clock T-sep self-checked). (8) S4: zero new pit lines (all operations on canon "
       "paths, no new failure modes -> zero CODELY append).")

VER = ("S6 38/38 rc0 FAILS=[] (results/_r478bmc_s6_log.txt, S6-chain-end marker); smoke "
       "48/48; orders 153/153 zero-diff double-scan (same-caliber same-form set-diff, "
       "_r478bmc_orders_d19_probe.py); D-19 decisions 4E5BE321 + group-orders 68947C17 "
       "double MATCH raw-blob per-key caliber; attrition CLEAN (4 ledgers); claws "
       "LF-normalized ok x2; loop pin5 phase-ok; watchdog present; satengine alive rc0 "
       "(Tools face, cycle 2084); trio watch V796/Q619/D464 healthy True x3 (owners=bm-b, "
       "keepalive 9.7min, growth +3/+3/+2 vs r675); heartbeat epoch int + clock T-sep + "
       "orders_ack 154 intact + field-count in-place assertion POST-WRITE; close delivery "
       "= S7-close report line (push_verify single-source proof)")

REP = (TS_OFF + "｜r478｜dept:工程（golden-week 值守轮·零事故·机队活跃相）｜watermark verdict=绿"
       "（red=false healthy·satengine rc0 活〔Tools 注册面·cycle 2084@14:29:07·burns_active=[]·"
       "N1 注册波全 12/12 耗尽=供给面按设计关闸·quarantine 仅 [12,11] 老例留痕·下个面孔=wave-3 "
       "grammar 需 T-86 census legs（bm-a 车道）〕）｜当前活=金周值守+fund-trio NULLS 三证进度读数+"
       "引擎供给耗尽定性｜最近实物=results/_r478bmc_trio_watch.json（V796/Q619/D464·delta +3/+3/+2 "
       "vs r675 基线·keepalive 9.7min healthy True×3·wide-rate 24.4/20.5/17.9/h·ETA V 10-06T15/"
       "Q 10-07T09/D 10-08T04）+results/_r478bmc_s6_log.txt（S6 38/38 rc0·chain-end+FAILS=[]）｜"
       "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主）+D-06 收口 10-07（bm-c 主导）+"
       "O-2115/O-2030 acceptance 10-08+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 3 脏面=本机 "
       "satengine/autofill 车道面·origin behind=3（r477 post-receipt 双 merge+bm-a r680）零交集"
       "（r437 预对齐）→并发三证探活（r643 律：05:05 对=常驻 satengine daemon 合法长活·14:2x=本 "
       "tick 链+壳宿主·r477 会话 14:22:05 最后 push 后死亡零并发）→absorb c0eb1ebc2+merge 零 UU→"
       "push REJECTED rc1（bm-b r675 wave 在途）→merge#2 零 UU→push_verify DELIVERED tip "
       "79e7e9c89·ahead=0/behind=0｜S0.5: 令差集=0（153/153 同口径同形态集合比对零差·S0.5+S7 双扫）"
       "·inbox 0 入站（MSG-1332 已由 bm-b 闭环回执消费=r477 next 指针(b) 收口）·D-19 decisions "
       "4E5BE321 MATCH+group orders 68947C17 MATCH（per-key raw-blob SHA-256/SHA-1 双口径）→零消费｜"
       "S1 smoke 48/48｜S2 板空（job_list 0·fleet 票 open=0·45 claimed=各机车道·T-158=W2 判负收口"
       "留值守至 10-08 acceptance·T-143 accounts face 10-29 交付线维持）｜S3: satengine rc0 活"
       "（Tools 注册面）·WM red=false healthy·py_low_board_clear 合法 idle（板空+金周无 bar）·"
       "FUND trio 全 bm-b 属主 healthy（watch-only·claim 完好零触碰·r626d-②）·W14 停泊维持 per "
       "O-0808｜S6 38/38 rc0 FAILS=[]（dualrun ZERO-DRIFT streak 51〔368 entries〕·compute_audit "
       "pool-supply-gap standing 态照录〔r474 定谳〕·update_daily 金周 cutoff 2026-09-30 零新行·"
       "market_regime ORANGE shadow days=2·lhb 11 页增量刷新+fundamental 快照新鲜跳过+b_layer mask "
       "幂等再生·REPORT/LIVE-2026-10-04 幂等再生 state=ORANGE·金周无新 bar 腿诚实 no-op 族全过）｜"
       "S7: loop pin5 phase-ok（next fire 14:35）·watchdog present·双爪 LF 归一 ok x2·attrition "
       "CLEAN（4 ledgers）·orders S7 二扫 153/153 零差｜S4: 零新坑律行（四问门：全窗循正典零新失效"
       "模式→零 CODELY append）｜记分: 1（S6 管线产出+trio watch 三证证据件+双探针件=可跑实物面·"
       "等待态声明：finalize 窗 10-05 开·N1 供给耗尽按设计关闸待 wave-3/T-86 腿+trio bm-b 属主+板空="
       "零新面孔可烧·非空转）｜本地未达 origin commit 数=待收口 commit 后自证回填")

# --- state update ---
sp = ROOT + r"\state-bm-c.json"
with open(sp, "r", encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 477, "unexpected prior round_no %s" % st.get("round_no")
st["round_no"] = 478
st["clock_read"] = TS
st["last_round_ts"] = TS_SP
st["last_ts"] = TS_SP
st["last_round_at"] = TS_OFF
st["last_seen"] = TS_OFF
st["last_round"] = ("r478 bm-c: golden-week watch + trio 3-evidence healthy (V796/Q619/D464, "
                    "+3/+3/+2 vs r675, keepalive 9.7min) + engine supply-exhaustion by-design "
                    "characterization + S6 38/38 rc0 + push-race cycle (bm-b r675 wave) resolved "
                    "canon-netpath -> DELIVERED; zero incident")
st["current_task"] = ACT
st["did"] = DID
st["next"] = NXT
st["verify"] = VER
st["updated"] = TS_OFF
st["updated_at"] = TS_OFF
st["heartbeat_epoch_utc"] = EPOCH
st["cpu_pct"] = 2.0
st["idle_ram_gb"] = 9.7
st["free_ram_gb"] = 9.7
st["ram_free_gb"] = 9.7
st["gpu_free_vram_mib"] = 608
st["last_decisions_read_at"] = TS_OFF
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(sp, "r", encoding="utf-8") as f:
    chk = json.load(f)
assert chk["round_no"] == 478 and isinstance(chk["heartbeat_epoch_utc"], int)

# --- heartbeat IN-PLACE ---
hp = ROOT + r"\fleet\machines\bm-c.json"
with open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)
n_before = len(hb)
ack_before = hb.get("orders_ack")
assert isinstance(ack_before, list) and len(ack_before) == 154
hb["activity_now"] = ACT
hb["current_task"] = CUR
hb["latest_artifact"] = ("results/_r478bmc_trio_watch.json (3-evidence trio probe, r675 baseline) "
                         "+ results/_r478bmc_s6_log.txt (38/38 rc0)")
hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 opens (bm-b owner, ETA V 10-06 "
                        "15:00 / Q 10-07); D-06 closure 10-07 (bm-c lead); O-2115/O-2030 "
                        "acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only, V796/Q619/D464, keepalive "
                    "healthy True x3, claim intact); N1 supply exhausted by design (waves all "
                    "consumed, next face wave-3 needs T-86 legs); boards empty; zero-incident "
                    "watch round, fleet active (bm-a r680 / bm-b r675 waves landed in-window)")
hb["verdict"] = ("healthy watch round by-threshold; trio 3-evidence green (growth +3/+3/+2 vs "
                 "r675, keepalive 9.7min); engine alive idle (supply exhausted by design); "
                 "boards empty; W14 parked per O-0808; zero escalation per re-based criteria")
hb["health"] = "healthy"
hb["round_no"] = 478
hb["round_no_label"] = "r478"
hb["clock_read"] = TS
hb["ts"] = TS_SP
hb["last_seen"] = TS_OFF
hb["last_seen_at"] = TS
hb["updated"] = TS_OFF
hb["updated_at"] = TS_OFF
hb["heartbeat_epoch_utc"] = EPOCH
hb["cpu_pct"] = 2.0
hb["cpu_idle_pct"] = 98.0
hb["cpu_util_pct"] = 2.0
hb["cores"] = 32
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = 9.7
hb["free_ram_gb"] = 9.7
hb["ram_free_gb"] = 9.7
hb["gpu_free_vram_mib"] = 608
hb["gpu_free_vram_mb"] = 608
hb["gpu_free_mb"] = 608
hb["gpu_idle_vram_mb"] = 608
hb["gpu_idle_vram_mib"] = 608
hb["gpu_vram_free_mb"] = 608
hb["gpu_idle_mb"] = 608
assert len(hb) == n_before, "field count changed %d -> %d" % (n_before, len(hb))
assert hb["orders_ack"] is ack_before or hb["orders_ack"] == ack_before
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(hp, "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert len(chk["orders_ack"]) == 154 and len(chk) == n_before

# --- round report append (EOL-preserving, dedup needle assertion) ---
rp = ROOT + r"\round_reports-bm-c.md"
with open(rp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
needle = "｜r478｜".encode("utf-8")
assert raw.count(needle) == 0, "r478 line already present"
line = REP.encode("utf-8") + eol
with open(rp, "ab") as f:
    f.write(line)
with open(rp, "rb") as f:
    raw2 = f.read()
assert raw2.count(needle) == 1 and raw2 == raw + line
print("CLOSEOUT OK state=478 hb_fields=%d acks=%d epoch=%d eol=%r" %
      (n_before, len(chk["orders_ack"]), EPOCH, eol))
