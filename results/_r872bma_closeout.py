# -*- coding: utf-8 -*-
"""r872 bm-a S7 closeout: report row (ROOT canonical) + state + heartbeat.
Machine-fresh values; heartbeat epoch as JSON int (R170/R178 law)."""
import json, time, io, subprocess, sys, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec='seconds')

# --- resource probe (heartbeat fields) ---
ram = None
try:
    ram_out = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
        capture_output=True, text=True, timeout=30)
    ram = int(ram_out.stdout.strip()) // 1024  # MB
except Exception:
    ram = None
vram_free = None
try:
    v = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=20)
    vram_free = round(int(v.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    vram_free = None
cpu_pct = 0.0
try:
    c = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         '(Get-CimInstance Win32_Processor).LoadPercentage'],
        capture_output=True, text=True, timeout=30)
    cpu_pct = int(c.stdout.strip())
except Exception:
    pass

# --- 1. report row (ROOT canonical, r844 law; UTF-8 + CRLF tail per r843) ---
ROW = (
    "2026-10-08T09:16:30+08:00 | r872 | bm-a | dept:research/engine | "
    "WM-VERDICT: green (red=false lane healthy; engine ALIVE idle queue-0 "
    "post-W183 burn 12/12; W184 prereg frozen this window = next supply link landed; "
    "trial-labor supply standing) | "
    "当前活: W184 prereg buildgen+build+banned ADMIT 全链本窗落地 (r869 bloodline AST "
    "50/50 DRY green + vestigial @N171 stray-check extension; bands A 419_604..421_603 "
    "staircase FORTY-FOURTH E36 / B 421_604..421_803 own-A reserved W141 leg2; anchors "
    "W183 finalize actuals K 400,520 / head 808,918 / mu -0.0928 no-roll / sigma 0.245099 / "
    "p95 0.3018 / line 1.1855 K-lift +0.0000; prereg 21,446B; freeze-time blob 7be9ca473b) + "
    "ledger heal (r870/r871 rows verbatim re-land ROOT canonical, sha16 463c8a5c/ad9700ca, "
    "closeout-script legacy-path pit 3rd instance CODELY 30,683B) | "
    "最近实物: research/PERPETUAL_N1_W184_PREREG.md (21,446B banned-ADMIT) + "
    "results/_r872bma_w184_buildgen.py (r869 bloodline, DRY 50+3 all-green first run) + "
    "FREEZE-candidate prereg commit f908433c4 pushed @2026-10-08T09:1x | "
    "下个里程碑: W184 registry FREEZE chain (freeze buildgen -> N1_BANDS[184]+WAVE_CONFIGS[184]"
    "+materializer+PASS-claim insertions -> pf 9/9 + n1 selftest W184 mat leg -> FREEZE push -> "
    "tick 自烧点火 12 shards, ETA r873 本窗) + 15:30 收盘 re-arm (zt_pool 首个真实 accrual=10-08 bar"
    "+REGIME_GUARD v3 enforce+bar-conditioned legs) + W183 ledger row 175th-wave carry | "
    "did: S0-1 孤儿面=0 + S0 churn-absorb+rebase E42 writer-pause 窗 (behind-6 bm-c r747 吸收 "
    "干净零 UU, push f4071a955) + S0.5 双扫未回执=0 + D-19 DEC/ORD 双 hash UNCHANGED (python "
    "raw-bytes canonical 路径 r870 律) + S1 smoke 49/49 + S3 ledger heal P0 (r870/r871 轮报行落 "
    "legacy 路径=r864 坑第3例, r865 verbatim 复迁法本窗治愈+CODELY 坑律 432B 30,683B 线内) + "
    "W184 prereg 全链 (probe 回执 r870 ADMIT 机读 -> buildgen AST 血统 50/50 -> DRY 50 live+3 "
    "vestigial stray-checks 全绿首跑 -> build 脚本 25,691B -> prereg 21,446B -> banned gate "
    "ADMIT rc0 -> 13-face 字节 spot-verify -> freeze push f908433c4 not-at-origin=0) + "
    "S6 41/41 rc0 (dualrun streak 51 ZERO-DRIFT / collectors pre-15:30 合法 no-op / "
    "scorecard 6+28+7 cards / paper legs idempotent / REPORT+LIVE-2026-10-08 再生 / "
    "token 0 today / attrition CLEAN 4 files) + S7 quartet green (loop pin8 no-op / watchdog "
    "Ready / 双爪 CR-normalized MATCH) + orders 双扫 0 + inbox 0 + idle --worked | "
    "验证: smoke 49/49 + W184 buildgen DRY 50+3 全绿 + prereg post-transform asserts PASS + "
    "banned ADMIT rc0 + 13-face spot-verify OK (6 期望误报逐一核销=U+2212 显示形/链内计数) + "
    "S6 41/41 rc0 + attrition CLEAN + not-at-origin=0 + orphan face=0"
)

p = r'round_reports-bm-a.md'
b = open(p, 'rb').read()
addition = ROW.encode('utf-8') + b'\r\n'
if not b.endswith(b'\n'):
    addition = b'\r\n' + addition
assert b'| r872 |' not in b, 'row already present'
with open(p, 'ab') as f:
    f.write(addition)
b2 = open(p, 'rb').read()
assert ROW.encode('utf-8') in b2
print('report row landed, root file now', len(b2), 'bytes')

# --- 2. state file update (round_no 872 -> 873) ---
sp = r'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 873
st['round'] = 872
st['last_round'] = 'r872'
st['last_round_at'] = TS
st['last_round_ts'] = TS
st['last_round_closed'] = TS
st['last_run'] = TS
st['last_seen'] = TS
st['loop_round'] = 'r872'
st['updated'] = TS
st['ts'] = TS
st['clock_read'] = TS
st['current_task'] = ("W184 registry FREEZE chain (freeze buildgen -> N1_BANDS[184]+WAVE_CONFIGS[184]"
                      "+materializer+PASS-claim -> pf/n1 selftests -> FREEZE push -> tick ignition "
                      "12 shards) + 15:30 re-arm (zt_pool first real accrual + REGIME_GUARD v3 "
                      "enforce + bar-conditioned legs)")
st['did'] = ("r872: ledger heal r870/r871 verbatim re-land ROOT (legacy-path pit 3rd instance, "
             "CODELY entry) + W184 prereg buildgen/build/banned ADMIT frozen+pushed f908433c4 "
             "(bands A 419_604..421_603 44th staircase / B 421_604..421_803; anchors W183 "
             "finalize K 400,520 head 808,918 mu -0.0928 sigma 0.245099 p95 0.3018 line 1.1855) + "
             "S6 41/41 rc0 + quartet green")
st['last_action'] = ("r872 close: W184 prereg freeze candidate pushed; r873 next: W184 registry "
                     "FREEZE + engine self-ignition (r869 freeze-buildgen bloodline), then W184 "
                     "burn 12 shards + finalize one-pass same-window (r381 lesson)")
st['next'] = ("r873: W184 FREEZE chain + tick ignition (engine self-burn 12 shards ~11min) + "
              "15:30 re-arm (zt_pool FIRST REAL accrual = 10-08 bar, REGIME_GUARD v3 enforce, "
              "bar-conditioned legs live.paper/t35_open_fill_verify/prospect)")
st['last_artifact'] = ("research/PERPETUAL_N1_W184_PREREG.md (21,446B banned-ADMIT, freeze "
                       "commit f908433c4) + results/_r872bma_w184_buildgen.py @2026-10-08T09:1x")
st['latest_artifact'] = st['last_artifact']
st['now_active'] = "r872 closed: W184 prereg frozen; freeze+ignition carried to r873"
st['verify'] = ("smoke 49/49 + W184 buildgen DRY 50+3 first-run green + prereg post-transform "
                "PASS + banned ADMIT rc0 + 13-face spot-verify + S6 41/41 rc0 (attrition CLEAN) "
                "+ orders 双扫 0 + DEC/ORD UNCHANGED + orphan face=0 + not-at-origin=0 + "
                "quartet green + idle --worked")
st['notes'] = st.get('notes', '') + (
    " r872: ledger heal third instance (r870/r871 closeout scripts wrote report rows to "
    "logs/iteration-loop legacy face; verbatim re-land per r865 precedent, sha16 "
    "463c8a5c8eba13e6/ad9700ca57ef1bcb; pit CODELY 30,683B under 30,720 cap). W184 buildgen "
    "structural notes vs r869 bloodline: @S55@/@SEATPUB@ s82-rolled (all constituents "
    "map-covered); @N171@/@N170@/@N169@ vestigial EXPECT=0 stray-check skip (legal bare-183 "
    "strays = fixed MSG-183x refs); cascade W180->W181 fixes composite window-list placeholder.")
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state updated: round_no=873')

# --- 3. heartbeat ---
epoch = int(time.time())
hb = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
hb['last_seen'] = TS
hb['ts'] = TS
hb['clock_read'] = TS
hb['heartbeat_epoch_utc'] = epoch
hb['cpu_cores'] = 32
hb['ram_free_mb'] = ram
hb['vram_free_gb'] = vram_free
hb['cpu_pct'] = cpu_pct
hb['current_task'] = st['current_task']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
json.dump(hb, open(r'fleet\machines\bm-a.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
# verify epoch int (R170/R178 law)
chk = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated ISO8601'
print('heartbeat written: epoch', chk['heartbeat_epoch_utc'], 'ram_free_mb', ram,
      'vram_free_gb', vram_free, 'cpu_pct', cpu_pct)
