# r781 bm-b closeout: CODELY pit line + inbox move + round report + state.json + heartbeat
# (python driver, file-based, avoids PS inline-quoting pits)
import json, os, shutil, time, datetime

NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
R = "r781"

# 1) CODELY.md pit line append
pit = ("- [2026-10-06 20:4x r781 bm-b] **PS 管道缓冲吞增量输出坑（Select-Object -Last 包装=活进度 runner 假死 5 分钟斩首·r778-cont 驱动模式的包装面失效实弹）**："
 "S6 全链 python 驱动器自带 per-leg stdout 进度（r778-cont 模式本为避开 5-min cancel 而设计），但外层 PS 命令以 `| Select-Object -Last N` 包装时全量缓冲到进程结束才放行——"
 "shell 工具 5 分钟零输出判死自动斩首，链在 LEG 36 后被腰斩（01-36 已落 log 零伤，37-39 秒级腿补跑即愈）。"
 "正法=①长活 runner（>3min）shell 驱动禁用 Select-Object/Out-String 等缓冲管道包装，裸流输出；②更正=分离 spawn+文件重定向+轮询 log（pit-spawn 长活分离律的 PS 包装新子面——runner 有活进度≠工具看得到）；"
 "③被斩后先查 log 尾定已跑腿集，幂等面直接补跑余腿勿全量重放。"
 "How to apply：一切 >3 分钟长活的 shell 驱动禁缓冲管道包装；S6 链被斩照本轮补腿范式（log 尾定位+补跑 37-39）。| dept:工程 | r781 收口窗\n")
with open("CODELY.md", "a", encoding="utf-8") as f:
    f.write(pit)

# 2) inbox MSG -> processed
src = "fleet/inbox/MSG-2026-10-06-194x-bma-w164-seat.md"
dst = "fleet/inbox/processed/MSG-2026-10-06-194x-bma-w164-seat.md"
if os.path.exists(src):
    os.makedirs("fleet/inbox/processed", exist_ok=True)
    shutil.move(src, dst)
    inbox_moved = True
else:
    inbox_moved = "already-moved"

# 3) round report line
rr = (f"{TS} | round 781 (bm-b, dept:工程 -- dead-r781-session absorb close-out + S6 full-chain regen + O-1845 令2 LLM-via-C adoption landed) | "
 "watermark verdict: GREEN (decisions A44C39E0 MATCH unchanged; orders 631E5DF2 MATCH unchanged = zero delta zero consumption, dual read via r631 sparse-clone recipe _r781bmb_d19_read.py runtime-anchored) | "
 "S0: identity=bm-b anchored (machine.json first-read); fetch behind-7 with dirty-overlap-16: treasure_guard restore gate = 15 reproducible rc0 + token_usage.json class=append-only-ledger rc3 HARD REJECT -> per-key union comparison origin-wins-all-differing-keys (local=bm-b stale-behind view, origin 19:35 fresher; aside extract preserved) -> stash-push-16 -> ff-only 968082cdf -> stash-drop; process-tree probe = single executor (codely 14140=self, fund_quality+fund_divlowvol burn runners alive, zero concurrent session) | "
 "S0.5: orders 159/159 zero unacked; S3: board empty (all claimed), watermark red=false lane=healthy, saturation engine alive exit0 idle queue=0, moneyflow IC candidate parked source-blocked (panel complete=false conn_stopped; one-line waiting-state declaration, no re-scan) | "
 "S6: dead-session chain (19:53 legs 01-39 rc0 minus golden-week 25-28) absorbed + FULL REGEN re-run -- beheaded post-LEG36 by 5-min no-output cancel via Select-Object buffering wrapper (pit recorded CODELY.md; legs 37-39 completed inline) = 39/39 rc0 final | "
 "dead-session deliverable VERIFIED+ABSORBED: scripts/llm_assist.py O-1845 令2 LLM-via-C routing (bm-b primary = C qwen3.6-coder:35b @ 100.123.74.104:11434, local qwen3.8:4b demoted fallback, BIGMONEY_LLM_ROUTE yield valve, keep_alive=-1 repin) -- py_compile rc0 + selftest rc0 (gen=自检通过, active route=c) + C /api/tags 3-model live + research/auto/review-llm_assist-20261006.md (LLM self-review 5 findings advisory, next-round triage candidates) | "
 "trio: V 2000/2000 done; Q 1748/2000 D 1453/2000 alive burning dup_k=0 (Q eta ~10-06 23:3x, D ~10-08); finalize_trio_readiness mechanical_ready=False (G1=False G2/G3=True) G4=PENDING, window 10-05..10-09 | "
 "QA pack r781 5/5 (93 trades determinism=True, dead-session product standing) | W164 seat MSG processed (bm-a 80th owned wave, E36 staircase 23rd instance, bm-a freeze ADMIT chain -- zero bm-b action, moved processed) | "
 "smoke 48/48 PASS | S7: attrition guard 4 ledgers CLEAN (healed rows historical), dashboard_status ts-bump = legal stale-takeover derive (host face 50min stale at leg time, O-2100 s2.4, bm-c r632 precedent, disclosed) | "
 "verification: S6 39/39 rc0 + selftest route=c live + /api/tags 3 models + QA 5/5 + attrition CLEAN + D-19 dual MATCH | local undelivered-to-origin commit count: 0 | "
 "next pointer: D-06 closeout 10-07 12:00 (CODELY.md ~59KB hot-cold re-org first item) + Q completes ~23:3x + review-doc 5 findings triage | "
 "product score 2 (llm_assist C-routing = usable channel product + S6 39-leg regen + QA pack)\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(rr)

# 4) state.json
with open("state.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 781
st["note"] = ("r781: dead-r781-session absorb close-out (its 19:53 S6 chain legs 01-39 rc0 + QA pack r781 5/5 + llm_assist.py O-1845-令2 LLM-via-C routing "
 "all absorbed; full chain re-regen 20:15-20:2x after 5-min-cancel behead, legs 37-39 completed; C-route selftest live route=c) + "
 "S0 dirty-overlap-16 resolution (treasure_guard gate: 15 reproducible rc0, token_usage ledger-class rc3 -> per-key union origin-wins, aside extract; stash->ff 968082cdf->drop) + "
 "D-19 dual MATCH zero delta (dec A44C39E0 / ord 631E5DF2) + orders 159/159 zero unacked + W164 seat MSG processed (bm-a-owned) + "
 "trio: V done, Q 1748/D 1453 alive dup_k=0 (Q eta ~23:3x, D ~10-08), readiness G1=False G2/G3=True G4=PENDING window 10-05..10-09; "
 "NEW PIT: PS pipeline buffering (Select-Object wrapper) swallows live per-leg stdout -> 5-min no-output cancel beheads long runners (CODELY line landed)")
st["ts"] = st["updated"] = st["last_seen"] = st["last_round_at"] = st["last_round_ts"] = st["clock_read"] = TS
st["round_no_label"] = "r781"
st["last_decisions_sha"] = "A44C39E01F9781BE981E208A48D852F6BCEF44709D004128591A88DF13C62EFB"
st["last_orders_sha"] = "631E5DF26951337D4B8E10A72D7292126D8FA2727089119BE1F2792AA53C0497"
st["last_decisions_read_at"] = TS
st["last_orders_read_at"] = TS
st["last_orders_sha_note"] = "r781: dual read via _r781bmb_d19_read.py (r631 sparse-clone recipe, runtime state-anchored); zero delta both faces (dec A44C39E0 MATCH since 12:31, ord 631E5DF2 MATCH since r780)"
st["next"] = ("(1) D-06 group closeout 10-07 12:00: CODELY.md hot-cold re-org (~59KB>50KB, receipts/flow lines to memory-archive/202610.md per r444 pattern) + domain-file residual items; "
 "(2) trio watch: Q completes ~10-06 23:3x, D eta ~10-08 -> when both 2000: G1 green + G3 rehearsal re-verify + G4 (governance ruling or r638 fallback) -> fund trio finalize within window 10-05..10-09; "
 "(3) market reopen 10-08: S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce; "
 "(4) review-llm_assist 5 findings triage (405 misreport / usage-log compaction / os.replace race / num_predict hardcode / path traversal) as next-round small-fix candidates; "
 "(5) moneyflow IC reference batch stays parked until panel unblocks (source-blocked, 30-min self-heal)")
st["did"] = ("r781: dead-session absorb (S6 chain + QA pack + llm_assist.py C-routing verified live: selftest route=c, py_compile rc0, /api/tags 3-model) + "
 "S0 overlap-16 stash/ff/drop with treasure_guard gate + token_usage per-key union + full S6 re-regen 39/39 rc0 (behead-recover: legs 37-39 inline) + "
 "D-19 dual MATCH + W164 MSG processed + smoke 48/48 + S7 self-heal all green")
st["verdict"] = "green: dead-session absorbed clean (llm_assist C-routing live); Q 1748/D 1453 burns alive dup_k=0; integration behind-0; zero unacked orders"
st["current_task"] = "r781 closed; next = D-06 closeout window prep + trio Q/D burn watch + review findings triage"
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# 5) heartbeat
hb_path = "fleet/machines/bm-b.json"
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = TS
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 6.8
hb["gpu_free_vram_gb"] = 3.65
hb["gpu_free_vram_mb"] = 3656
hb["round_no"] = 781
hb["round"] = 781
hb["last_round_at"] = TS
hb["ts"] = TS
hb["updated"] = TS
hb["verdict"] = ("green: r781 closed (dead-session absorb + S6 39/39 rc0 regen + llm_assist LLM-via-C routing LIVE route=c); "
 "Q 1748/D 1453 burns alive; integration behind-0; local undelivered 0")
hb["current_task"] = "trio Q/D burn watch (V done 2000/2000) + D-06 closeout window 10-07 12:00 (CODELY hot-cold re-org first item) + review findings triage"
hb["now_active"] = ("FUND trio NULLS judgment batch: V COMPLETE 2000/2000; Q 1748/2000 D 1453/2000 alive burning dup_k=0 "
 "(Q eta ~10-06 23:3x, D eta ~10-08); trio finalize window 10-05..10-09, mechanical_ready=False G1 pending Q+D, G4 governance pending")
hb["latest_artifact"] = ("scripts/llm_assist.py LLM-via-C routing live (selftest active route=c @20:3x, qwen3.6-coder:35b via C tailnet) + "
 "qa/smoke-r781.md QA pack 5/5 @19:55 + results/_r781bmb_s6_chain.log 39/39 rc0 @20:15-20:2x")
hb["next_milestone"] = ("D-06 group closeout 10-07 12:00 (CODELY.md ~59KB hot-cold re-org); Q completes ~10-06 23:3x, D ~10-08; "
 "market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first new bar)")
hb["task"] = "FUND trio NULLS judgment batch lane (V done; Q/D burn watch) + D-06 closeout prep"
hb["last_action"] = ("r781 closed+delivered: dead-session absorb (S6 chain + QA 5/5 + llm_assist.py O-1845-令2 C-routing verified live) + "
 "S0 overlap-16 treasure_guard-gated stash/ff/drop (token_usage ledger-class union origin-wins + aside) + "
 "D-19 dual MATCH + orders 159/159 + W164 MSG processed + S6 full re-regen 39/39 rc0 (5-min-cancel behead recovered legs 37-39) + smoke 48/48")
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verification
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"], "clock_read must be T-separated ISO8601"
print("closeout OK; epoch=", chk["heartbeat_epoch_utc"], "type=", type(chk["heartbeat_epoch_utc"]).__name__)
print("inbox_moved:", inbox_moved)
print("state round_no:", json.load(open("state.json", encoding="utf-8"))["round_no"])
print("CODELY.md size:", os.path.getsize("CODELY.md"))
