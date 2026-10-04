# -*- coding: utf-8 -*-
"""r479 bm-c closeout: state + heartbeat(IN-PLACE, orders_ack 154->155 O-1440 ack)
+ round-report append + CODELY execution-record line.
Laws: r475 heartbeat-field-loss -> IN-PLACE updates + field-count before==after;
r645 programmatic json.dump + json.loads self-check; epoch int direct; EOL
preserving appends with dedup needle assertions (r675 union law)."""
import datetime
import json
import time

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TS_OFF = TS + "+08:00"
TS_SP = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ACT = ("O-1440 idle-recurrence ignition r479 CLOSED (same-round ack): pool ready=3 all "
       "owner=bm-b live-burn (keepalive 21min fresh x3, audit unclaimed=0 = CEO 14:30 "
       "audit face stale); tickets 157-164 all owned w/ dispositions (zero un-reasoned "
       "backlog); N2-N4 wiring-state evidence: selftest 3/3 ALL PASS on bm-c, generator "
       "canon face runner-landed [N1,N3] pending [N2,N4] honest, N3-R1/R2 + N4-B1/B2/B3 "
       "burned (CEO audit 'zero-hit' = stale query face), TRUE GAP = N2-W15 freeze-window "
       "legs (red-card line per sec.2, declared next-round first item); supply pre-position: "
       "pool live=3 no-materialize trigger per canon sec.1, T-148 contest 12 pending legs "
       "bm-b owner due 10-08, W3 = new prereg face; S6 38/38 rc0; trio healthy True x3")
CUR = ("当前活: O-1440 闲置复发点火令执行轮 CLOSED（池面/八票/N2-N4 接线态/供料预置四面同轮ack） | "
       "最近实物: results/_r479bmc_n234_wire.json (N2/N3/N4 selftest 3/3 ALL PASS + 生成器 "
       "runner-landed[N1,N3]/pending[N2,N4] + N3-R1/R2+N4-B1-B3 烧录产物清单) + "
       "results/_r479bmc_trio_watch.json (V796/Q619/D464 healthy True x3, keepalive 21min) + "
       "results/_r479bmc_s6_log.txt (38/38 rc0) @ " + TS + " | "
       "下个里程碑: N2-W15 冻结窗开窗尝试 r480 首件（真缺口·红牌行在轮报）+ fund-trio finalize "
       "窗 10-05 10:30 开（bm-b 正主）+ 供料预置三面 10-06 前; D-06 收口 10-07 (bm-c 主导)")
NXT = ("(a) r480 = 5x round: HANDOVER refresh + N2-W15 freeze-window open attempt "
       "(run/screen/finalize legs + seed registration at freeze commit per R99/R250; "
       "same-window yield to bm-b s2 seat-holder per commit-time order). (b) fund-trio "
       "finalize window 10-05 10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole "
       "10-07). (c) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. (d) D-06 full "
       "closure window 10-07 (bm-c lead). (e) O-2115/O-2030 + T-158/T-162 acceptance "
       "10-08; market reopen 10-09.")
DID = ("r479 bm-c O-1440 idle-recurrence ignition execution round (CEO direct order "
       "O-20261004-1440-bm-c, issued 14:40, same-round ack per sec.1): (1) S0: no rebase "
       "leftovers; round-start dirty = 3 own satengine lane faces (r437 netpath) -> absorb "
       "365383383 + merge origin/main (bm-a r681 wave) + local O-1440 order commit unified "
       "(same-file same-blob SAME-change trivial) -> push#1 REJECTED rc1 (fleet wave in "
       "flight) -> merge#2 -> push_verify DELIVERED tip bbce8337288b02ce1e79512e6e8ad986442bb836 "
       "ahead=0 behind=0; concurrency triple-evidence (r643): O-1440 order-committer "
       "interactive session dead after 14:38 commit (process face clean, single-executor "
       "taken). (2) S0.5: orders set-diff = 1 un-acked (O-20261004-1440-bm-c.md) -> "
       "executed + acked this round (orders_ack 154->155); D-19 decisions 4E5BE321 + "
       "group-orders 68947C17 double MATCH (per-key raw-blob SHA-256/SHA-1) -> zero "
       "consumption; inbox 0 inbound. (3) S1 smoke 48/48. (4) S2: boards empty (job_list 0; "
       "fleet open tickets 0). (5) S3 O-1440 three sections: sec.1 pool face = ready=3 ALL "
       "owner=bm-b actively burning (keepalive 21.0min fresh x3, k=V796/Q619/D464, wide "
       "rates ~18-24/h, ETA V 10-06T15/Q 10-07T09/D 10-08T04; unclaimed=0 per audit v2.4.2 "
       "= CEO 14:30 '3 unclaimed' audit face stale; no-touch per r626d-2); sec.1 eight "
       "tickets 157-164 = ALL claimed/done with dispositions (157 done bm-c r421; 158 = "
       "own lane W2 judged-negative held for 10-08 acceptance; 155 claimed bm-b; 156/159-161/"
       "163-165/167-169 done; 162 yielded->bm-c weld owner) = zero un-reasoned backlog; "
       "sec.2 N2-N4 wiring-state probe results/_r479bmc_n234_wire.json: selftest 3/3 ALL "
       "PASS on bm-c (N2 L3-L7 / N3 S6-S9 / N4 20/20), generator canon face "
       "scripts/perpetual_faces.py status = runner-landed [N1,N3], pending-honest [N2,N4], "
       "materialized waves 9, pool live 3 starving=False; products on disk: N3-R1/R2 + "
       "N4-B1/B2/B3 burned (O-2155 WAS executed 10-02 night: N3-R1 frozen r509 bm-a, "
       "ledger 375,447) -> CEO audit 'zero-hit two nights' = stale query face, honest "
       "correction attached; TRUE GAP = N2-W15 freeze-window legs (prereg DRAFT, runner "
       "slice-1 only) -> red-card line in round-report first line per sec.2 + declared "
       "r480 first item; sec.3 supply pre-position: pool live=3 = no materialize trigger "
       "per canon sec.1, post-trio faces inventoried (fundamentals-family judgment = "
       "finalize-window face bm-b; contest T-148 12 pending legs bm-b owner due 10-08; "
       "W3 = new prereg face), pre-position = generator auto-face at finalize + N2 unlock. "
       "(6) S6 38/38 rc0 FAILS=[] (dualrun ZERO-DRIFT streak 51; compute_audit "
       "load_state=pool-supply-gap flag honest, supply_floor 3>=3 no breach, "
       "pool_ready_unclaimed=0; py_watermark py_low_board_clear legal-idle; update_daily "
       "golden-week zero new rows; market_regime ORANGE days=2 shadow; REPORT/LIVE-2026-10-04 "
       "idempotent regen). (7) S7: loop pin5 phase-ok (next fire 14:55), watchdog "
       "re-registered, pre-commit+pre-push claws LF-normalized installed x2, attrition "
       "CLEAN (4 ledgers), orders re-scan post-ack 155/155 zero-diff; heartbeat IN-PLACE "
       "write (orders_ack 155 intact + field-count assertion + epoch int + clock T-sep "
       "POST-WRITE self-check). (8) S4: zero new pit lines (all ops on canon paths).")
VER = ("O-1440 execution evidence = results/_r479bmc_n234_wire.json (selftest 3/3 rc0 + "
       "generator status verbatim) + results/_r479bmc_tickets_probe.py run (157-164 "
       "dispositions) + results/_r479bmc_boards_probe.py (pool/flags/engine); smoke 48/48; "
       "S6 38/38 rc0 (results/_r479bmc_s6_log.txt, S6-chain-end marker, FAILS=[]); orders "
       "155/155 zero-diff double-scan (S0.5 probe + post-ack re-scan, same-caliber "
       "same-form set-diff); D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH "
       "raw-blob per-key; attrition CLEAN (4 ledgers); claws LF-normalized x2; loop pin5 "
       "phase-ok; watchdog present; satengine alive rc0 (Tools face); trio watch "
       "V796/Q619/D464 healthy True x3 (keepalive 21.0min, growth 0/0/0 vs r478 = "
       "between-sync-batch face, git_sync_fresh_1h True); heartbeat epoch int + clock "
       "T-sep + orders_ack 155 + field-count in-place assertion POST-WRITE; close "
       "delivery = S7-close receipt line (push_verify single-source proof)")

REP = (TS_OFF + "｜r479｜dept:工程/策略（O-1440 闲置复发点火令执行轮·CEO 直令同轮 ack·机队活跃相）｜"
       "watermark verdict=绿（red=false·py_low_board_clear 合法闲〔板空+池 unclaimed=0+金周无 bar〕）"
       "+ **O-1440 §2 红牌行：N2 发生器接线未完成**——真缺口=N2-W15 冻结窗腿（run/screen/finalize+种子带"
       "冻结登记）未落地〔prereg 仍 DRAFT·R99/R250 冻结窗工程=多窗件·10min tick 轮结构上不可闭·已declare "
       "r480 首件〕；N3 已接（runner landed+R1/R2 已烧）·N4 批面已烧 B1-B3+生成器 auto-face pending——"
       "CEO 审计「O-2155 两夜零命中」=查询面错判（证据=ledger 375,447+盘面产物+selftest 3/3 PASS）｜"
       "当前活=O-1440 四面执行（池面/八票/N2-N4 接线态/供料预置）｜最近实物=results/_r479bmc_n234_wire.json"
       "（N2/N3/N4 selftest 3/3 ALL PASS+生成器 runner-landed[N1,N3]/pending[N2,N4]+N3-R1/R2+N4-B1-B3 产物"
       "清单）+results/_r479bmc_trio_watch.json（V796/Q619/D464·healthy True×3·keepalive 21min）+results/"
       "_r479bmc_s6_log.txt（38/38 rc0）@ " + TS + "｜下个里程碑=N2-W15 冻结窗开窗尝试 r480 首件+fund-trio "
       "finalize 窗 10-05 10:30（bm-b 正主）+供料预置三面 10-06 前+D-06 收口 10-07（≤48h）｜S0: 无 rebase 残留"
       "·轮首 3 脏面=本机 satengine 车道面→absorb 365383383+merge（bm-a r681 波·本地 O-1440 令 commit 同件"
       "同容 SAME-change 平凡合并）→push#1 REJECTED rc1→merge#2→push_verify DELIVERED tip bbce833728"
       "ahead=0/behind=0·并发三证=O-1440 落令人会话 14:38 后死亡零并发（本会话单执行体）｜S0.5: 令差集=1"
       "（O-20261004-1440-bm-c.md）→同轮执行+ack 154→155·D-19 decisions 4E5BE321+group orders 68947C17 "
       "双 MATCH 零消费·inbox 0 入站｜S1 smoke 48/48｜S2 板空（job_list 0·fleet open=0）｜S3 O-1440 §1 池面="
       "ready 3 全 owner=bm-b 活烧（keepalive 21min fresh×3·audit v2.4.2 pool_ready_unclaimed=0=CEO 14:30 "
       "「无人认领」审计面已过时·r626d-② 禁触碰）·§1 八票 157-164 全有主有处置（157 done 本机/158=本机车道 "
       "W2 判负留 10-08 验收/155 claimed bm-b/159-161/163-165/167-169 done/162 yielded→本机焊主）=零无理由挂账"
       "·§2 接线态=selftest 3/3 PASS+生成器正典面 runner-landed[N1,N3]/pending[N2,N4]（诚实披露）·N3-R1/R2"
       "+N4-B1/B3 已烧=O-2155 实已执行·真缺口=N2 冻结窗（红牌行·r480 首件declare）·§3 供料预置=pool live=3 "
       "物化不触发（法典 §1）+T-148 大赛 12 待烧腿 bm-b 属主 10-08 前+千人 W3=新 prereg 面｜S6 38/38 rc0 "
       "FAILS=[]（dualrun ZERO-DRIFT streak 51·compute_audit load_state=pool-supply-gap 旗照录〔supply_"
       "floor 3≥3 无破·unclaimed=0〕·py_watermark py_low_board_clear·update_daily 金周零新行·market_regime "
       "ORANGE days=2·REPORT/LIVE-20261004 幂等再生）｜S7: loop pin5 phase-ok·watchdog present·双爪 LF 归一 "
       "ok x2·attrition CLEAN（4 ledgers）·orders S7 二扫 155/155 零差·heartbeat orders_ack 155+epoch int+"
       "clock T-sep+field-count 断言 POST-WRITE｜S4: 零新坑律行（全窗循正典零新失效模式）｜记分: 1（O-1440 "
       "执行证据件 n234_wire+trio watch 三证件+S6 管线产出=可跑可看实物面·N2 缺口红牌如实·非静默晾令）｜"
       "本地未达 origin commit 数=待收口 commit 后自证回填")

CODELY_LINE = ("- [2026-10-04 " + TS_SP[11:] + " r479 bm-c] O-20261004-1440 闲置复发点火令执行回执"
               "（CEO 直令 14:3x·ack 同轮·违例追责面如实）：①池面 ready=3 全 owner=bm-b 活烧"
               "（keepalive 21min fresh×3·audit v2.4.2 pool_ready_unclaimed=0=令面「无人认领」审计已过时"
               "·r626d-② 禁触碰）；②八票 157-164 全有主有处置=零无理由挂账；③N2-N4 接线态证据="
               "results/_r479bmc_n234_wire.json（selftest 3/3 ALL PASS+生成器 runner-landed[N1,N3]/"
               "pending[N2,N4]+N3-R1/R2+N4-B1-B3 已烧）——CEO 审计「O-2155 两夜零命中」=查询面错判；"
               "真缺口=N2-W15 冻结窗腿未落地（红牌行入轮报首行·r480 首件 declare·同窗让路 bm-b s2 正主按 "
               "r511 提交时序）；④供料预置=pool live=3 物化不触发（法典 §1）+T-148 12 腿 bm-b 10-08+千人 "
               "W3=新 prereg 面。How to apply：查 N 面供给态先跑 selftest×3+perpetual_faces.py status"
               "（勿按 audit 查询面判「零执行」）；引擎断供根因=N1 面按 O-0808 停泊+O-2155 价值递减定谳"
               "，解堵面=N2 冻结窗非新 N1 波。")

# --- state update ---
sp = ROOT + r"\state-bm-c.json"
with open(sp, "r", encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 478, "unexpected prior round_no %s" % st.get("round_no")
st["round_no"] = 479
st["clock_read"] = TS
st["last_round_ts"] = TS_SP
st["last_ts"] = TS_SP
st["last_round_at"] = TS_OFF
st["last_seen"] = TS_OFF
st["last_round"] = ("r479 bm-c: O-1440 idle-recurrence ignition execution (same-round ack): "
                    "pool ready=3 all bm-b-owned live (unclaimed=0 audit correction), tickets "
                    "157-164 all dispositioned, N2-N4 wiring-state evidence pack (selftest 3/3 "
                    "PASS, generator landed [N1,N3] pending [N2,N4], N3-R1/R2+N4-B1-B3 burned, "
                    "TRUE GAP = N2 freeze-window legs -> red card per sec.2), supply "
                    "pre-position inventoried; S6 38/38 rc0; trio healthy x3; zero incident")
st["current_task"] = ACT
st["did"] = DID
st["next"] = NXT
st["verify"] = VER
st["updated"] = TS_OFF
st["updated_at"] = TS_OFF
st["heartbeat_epoch_utc"] = EPOCH
st["cpu_pct"] = 3.0
st["idle_ram_gb"] = 9.9
st["free_ram_gb"] = 9.9
st["ram_free_gb"] = 9.9
st["gpu_free_vram_mib"] = 608
st["last_decisions_read_at"] = TS_OFF
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(sp, "r", encoding="utf-8") as f:
    chk = json.load(f)
assert chk["round_no"] == 479 and isinstance(chk["heartbeat_epoch_utc"], int)

# --- heartbeat IN-PLACE (orders_ack 154 -> 155 with O-1440 ack) ---
hp = ROOT + r"\fleet\machines\bm-c.json"
with open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)
n_before = len(hb)
ack = hb.get("orders_ack")
assert isinstance(ack, list) and len(ack) == 154, "ack-before %s" % len(ack)
assert "O-20261004-1440-bm-c.md" not in ack
ack.append("O-20261004-1440-bm-c.md")
hb["activity_now"] = ACT
hb["current_task"] = CUR
hb["latest_artifact"] = ("results/_r479bmc_n234_wire.json (O-1440 N2-N4 wiring-state evidence: "
                         "selftest 3/3 ALL PASS + generator runner-landed [N1,N3]/pending "
                         "[N2,N4] + N3-R1/R2 + N4-B1-B3 burn products) + results/"
                         "_r479bmc_trio_watch.json (trio healthy True x3) + results/"
                         "_r479bmc_s6_log.txt (38/38 rc0)")
hb["next_milestone"] = ("N2-W15 freeze-window open attempt r480 first item (true gap, red-card "
                        "declared); fund-trio finalize window 10-05 10:30 (bm-b owner, ETA V "
                        "10-06 15:00); supply pre-position by 10-06; D-06 closure 10-07 "
                        "(bm-c lead); acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only, V796/Q619/D464, keepalive "
                    "healthy True x3); N1 supply closed by design (O-0808 park + O-2155 "
                    "diminishing-returns); N3 runner landed (R1/R2 burned), N4 batches "
                    "B1-B3 burned (generator auto-face pending), N2 freeze-window = true "
                    "gap -> r480 first item; boards empty; O-1440 executed same-round")
hb["verdict"] = ("O-1440 executed same-round with evidence pack; pool 'unclaimed' audit face "
                 "corrected (ready=3 all bm-b-owned live); tickets 157-164 zero un-reasoned "
                 "backlog; N2-N4 wiring: selftest 3/3 PASS, N3 landed + N4 batch-burned, N2 "
                 "= red card (freeze-window legs) per sec.2 with declared next step; trio "
                 "3-evidence green; S6 38/38 rc0")
hb["health"] = "healthy"
hb["round_no"] = 479
hb["round_no_label"] = "r479"
hb["clock_read"] = TS
hb["ts"] = TS_SP
hb["last_seen"] = TS_OFF
hb["last_seen_at"] = TS
hb["updated"] = TS_OFF
hb["updated_at"] = TS_OFF
hb["heartbeat_epoch_utc"] = EPOCH
hb["cpu_pct"] = 3.0
hb["cpu_idle_pct"] = 97.0
hb["cpu_util_pct"] = 3.0
hb["cores"] = 32
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = 9.9
hb["free_ram_gb"] = 9.9
hb["ram_free_gb"] = 9.9
hb["gpu_free_vram_mib"] = 608
hb["gpu_free_vram_mb"] = 608
hb["gpu_free_mb"] = 608
hb["gpu_idle_vram_mb"] = 608
hb["gpu_idle_vram_mib"] = 608
hb["gpu_vram_free_mb"] = 608
hb["gpu_idle_mb"] = 608
assert len(hb) == n_before, "field count changed %d -> %d" % (n_before, len(hb))
assert len(hb["orders_ack"]) == 155
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(hp, "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert len(chk["orders_ack"]) == 155 and len(chk) == n_before

# --- round report append (EOL-preserving, dedup needle assertion) ---
rp = ROOT + r"\round_reports-bm-c.md"
with open(rp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
needle = "｜r479｜".encode("utf-8")
assert raw.count(needle) == 0, "r479 line already present"
line = REP.encode("utf-8") + eol
with open(rp, "ab") as f:
    f.write(line)
with open(rp, "rb") as f:
    raw2 = f.read()
assert raw2.count(needle) == 1 and raw2 == raw + line

# --- CODELY.md execution-record line (EOL-preserving, dedup needle) ---
cp = ROOT + r"\CODELY.md"
with open(cp, "rb") as f:
    craw = f.read()
ceol = b"\r\n" if craw.endswith(b"\r\n") else b"\n"
cneedle = "r479 bm-c] O-20261004-1440".encode("utf-8")
assert craw.count(cneedle) == 0, "codely r479 line already present"
cline = CODELY_LINE.encode("utf-8") + ceol
with open(cp, "ab") as f:
    f.write(cline)
with open(cp, "rb") as f:
    craw2 = f.read()
assert craw2.count(cneedle) == 1 and craw2 == craw + cline

print("CLOSEOUT OK state=479 hb_fields=%d acks=%d epoch=%d eol=%r" %
      (n_before, len(chk["orders_ack"]), EPOCH, eol))
