import json, time, datetime, platform, subprocess, os

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S') + ('+' if now.utcoffset() >= datetime.timedelta(0) else '-') + f"{abs(int(now.utcoffset().total_seconds()//3600)):02d}:00"
epoch = int(time.time())
ROUND = 558

# --- state.json (bm-b uses state.json per fleet README sec.6) ---
st = json.load(open('state.json', encoding='utf-8'))
old_round = st.get('round_no', 0)
st['round_no'] = ROUND
st['note'] = ("r558: W49 FULL DELIVERY surgical e488e8008 (12/12 products + finalize K=103,520 ledger 470,148 chain seat, prereg s7/s8) "
              "+ W51 same-window same-band DOUBLE-FREEZE with bm-c r350 f640e8848 (bands bit-identical A 145_004..147_003 / B 46_001..46_200, "
              "r530 cross-validation) -> commit-order YIELD five steps (in-flight shard-1 burn killed, reset origin, local re-burns untracked-discarded, "
              "gate tool yield-archived, MSG-0610); engine owner-gate verified (W51 foreign, queue 0); "
              "LOWAMP-P3-NULLS burn complete 2000/2000; S6 chain 36/36 rc0; WM py_low_board_clear (holiday legal idle); "
              "round label note: r558 number collides with bm-a r558 same-window (independent series, honest note)")
st['last_round_at'] = iso
st['last_round_ts'] = epoch
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert json.load(open('state.json', encoding='utf-8'))['round_no'] == ROUND
print(f'state.json: round {old_round} -> {ROUND}')

# --- heartbeat fleet/machines/bm-b.json ---
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
try:
    cpu = float(subprocess.check_output(
        ['powershell', '-NoProfile', '-Command',
         '(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average'],
        text=True).strip() or 0)
except Exception:
    cpu = hb.get('cpu_util_pct', 0)
try:
    ram_out = subprocess.check_output(
        ['powershell', '-NoProfile', '-Command',
         '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)'],
        text=True)
    free_ram = float(ram_out.strip())
except Exception:
    free_ram = hb.get('free_ram_gb', 0)
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['round_no'] = ROUND
hb['current_task'] = ("r558 W49 surgical delivery e488e8008 (chain head 470,148) + W51 double-freeze YIELD to bm-c (five steps done, "
                      "engine owner-gate verified) + S6 chain 36/36 rc0")
hb['cpu_util_pct'] = cpu
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['ram_free_gb'] = free_ram
hb['verdict'] = ("GREEN W49 delivered+finalized (K=103,520 ledger 470,148, chain seat ahead of in-flight W48/W50 per r518 origin-timing) "
                 "+ W51 same-band yield to bm-c r350 (bit-identical derive cross-validation, zero ledger pollution, finalize never ran) "
                 "+ LOWAMP-P3-NULLS 2000/2000 complete + S6 full rc0 + WM py_low_board_clear holiday-legal-idle")
hb['round_no_label'] = 'r558'
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
hb2 = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in hb2['clock_read'], 'clock_read must be T-separated (R262 law)'
print('heartbeat: epoch int OK, clock T OK, round', hb2['round_no'])

# --- round report append (bm-b file per fleet README sec.6) ---
rr_path = 'logs/iteration-loop/round_reports.md'
line = (
    f"{iso} | r558 | W49 SURGICAL DELIVERY + W51 DOUBLE-FREEZE YIELD | "
    f"S0 surgical e488e8008: W49 12/12 products + n1_w49_results.json FINALIZE (ledger 467,948+2,200=470,148 CHAIN HEAD, prev=W47 head origin-timing derive, "
    f"K=103,520==sec0 projection, S5 4/4 PASS prereg-backfilled) + prereg s7/s8 + engine lane faces + append unions (pool_core_samples +10, ledger_bm-b +9) -- "
    f"payload 31 files, deletion-set empty, push OK, W48/W50 in-flight seat race won (r518 origin-timing law) | "
    f"S0.5 orders diff 0 unacked; D-19 dec_sha MATCH-unchanged (r481 temp-partial-clone recipe) | S1 smoke 47/47 PASS | "
    f"S3: engine alive rc0 (W49 12/12 burned, queue 0); board T-141 mine=standing (s1+s3 done r508, acceptance face in-flight fleet-wide) | "
    f"NEVER-DRY standing step: W51 FREEZE three-gate ADMIT (band gate _r558bmb_w51_band_gate.py: A 145_004..147_003 arithmetic CLEAN + B 46_001..46_200 forced skip "
    f"past SEED_REGISTRY xlib_synth_null_a=46_000 per W50-row W51+ WARNING published refusal face, 49-row table + N3-R1 + probe cluster + origin slot vacancy; "
    f"banned_direction_gate ADMIT rc0; selftest PASS incl. W51 materializer refusal-face-avoidance leg) -> local commit 384996181 -> "
    f"PUSH REJECTED = bm-c r350 f640e8848 same-window W51 FREEZE already on origin, bands BIT-IDENTICAL (r530 deterministic same-band cross-validation, "
    f"independent derives agree on both sides + same refusal facts + same W52+ projection) -> COMMIT-ORDER YIELD r511 five steps: "
    f"(1) in-flight shard-1 burn killed pid47820 + tick owner-gate auto-skip verified (active_burns 0, queue 0, W51=foreign bm-c row) "
    f"(2) main reset to origin 7657895b0, canon four-files origin-side verbatim (W51 row owner=bm-c verified by import) "
    f"(3) local re-burn products (n1_w51/shard-0 complete + shard-1 partial) UNTRACKED-DISCARDED zero-committed (r525 law: never touch origin true-owner products) "
    f"(4) gate tool + S0 tools yield-archived via cherry-pick checkout from 384996181 "
    f"(5) MSG-20261002-0610-bm-b yield receipt sent | science: W51 finalize NEVER ran on bm-b = zero ledger double-count; "
    f"LOWAMP-P3-NULLS burn COMPLETE 2000/2000 (daemon harvest flip face) | "
    f"S6 chain 36/36 rc0: dualrun ZERO-DRIFT streak 4/3, compute_audit clean (holiday idle), WM py_low_board_clear (=legal idle whitelist: board clear + bandit "
    f"parked + no runnable batch, holiday window + post-yield state), update_daily/lhb/futures/astock/etf/rev_osc/minute no-op fresh-or-guard honest, "
    f"t24 promotion 0/22 eligible honest, aggr/alloc/grid paper marks no-op idempotent, system_v1 stdout-only lane-guard, t35 export 2026-09-30, "
    f"daily_scorecard + REPORT-2026-10-02 (5 faces) + LIVE-2026-10-02 (ORANGE) + build_status regenerated (bm-a host fresh, no takeover needed), "
    f"token L2 0 today, attrition CLEAN | "
    f"S7: loop pin=2 no-op, watchdog re-registered S4U, pre-commit claw installed, inbox MSG-0530 (r533 legacy disclosure) processed->archive, "
    f"state 532->558 (r529 skip law: git self-labels through r556 + this window r558; round-number collision with bm-a r558 same-window honest note -- "
    f"independent per-machine series, zero account pollution) | "
    f"CEO view: current=W51 yield closeout + S6/S7 full-chain loop (engine idle, board clear, holiday legal-idle); "
    f"latest artifact=results/perpetual_faces/n1_w49_results.json (05:06, chain head 470,148) + e488e8008 12/12 delivery + docs/live_usage/LIVE-2026-10-02.md (ORANGE); "
    f"next milestone=W52 freeze (next round, fetch-verified table tail after bm-c W51 closeout -- same-band collision window dissolves once W51 seat closes) "
    f"+ W48/W50 finalize chain-seat watch (bm-a r558 already re-deriving W48 finalize prev=470,148 per r518 seat-loss law, window <=48h) | "
    f"NEXT r559: W52 freeze (fetch+tail-row lock, first-free-number); watch W48/W50/W51 finalize landings (chain head rolls 470,148->472,348->...); "
    f"LOWAMP-P3 harvest-flip verify; local-unsynced-commits check after final push"
)
with open(rr_path, 'a', encoding='utf-8') as f:
    f.write('\n' + line + '\n')
print('round report appended, chars:', len(line))

# --- memory append (S4, one entry, four-question gate passed) ---
mem_path = 'CODELY.md'
entry = (
    f"\n- [2026-10-02 05:3x r558 bm-b] never-dry 表尾锁撞面第三例（W12 三冻/W39 双冻/W51 双冻）+单点拒绝唯一解根因定谳：W51 双机同窗独立机闸 derive "
    f"带位逐位同（A 145_004..147_003 算术 CLEAN/B 46_001..46_200 跳位·refusal facts 同=[SEED_REGISTRY xlib_synth_null_a=46_000]）——**B 侧拒绝面=单点 "
    f"SEED_REGISTRY 拒绝时跳位解唯一（vs 带级公示投影拒绝亦唯一）=确定性设计下同带撞面不可靠错峰避免**（可靠错峰=号位声明〔bm-a W48 先例〕或表尾原子锁——均未建）。"
    f"让路五步实弹新序=杀在飞分片烧录（pid 级·tick 引擎下一 tick owner gate 自动跳 foreign 行=自然截断续燃面）→reset origin（canon 全取）→本机重烧件 "
    f"untracked 弃置零入册→工具件 cherry-pick 自弃置 commit 入档（yield receipt）→MSG 回执。How to apply：撞面已烧时 finalize 绝跑（账本零双计为底线）；"
    f"复位后引擎验证唯一证据=active_burns/queue 面（产物增长律的反面=零点火证明）。\n"
)
with open(mem_path, 'a', encoding='utf-8') as f:
    f.write(entry)
print('CODELY.md memory entry appended, bytes:', len(entry.encode('utf-8')))
