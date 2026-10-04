# r502 bm-c S7 bookkeeping: state-bm-c.json + heartbeat + round report append (programmatic, r645/r678/r694 laws)
import json, time, io, os

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now = time.time()
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def roundtrip_gate(path):
    raw = open(path, 'rb').read().decode('utf-8')
    obj = json.loads(raw)
    redump = json.dumps(obj, ensure_ascii=False, indent=1)
    return raw == redump, obj

# --- state-bm-c.json ---
sp = ROOT + r'\state-bm-c.json'
ok, st = roundtrip_gate(sp)
print('state roundtrip:', ok)
assert ok, 'state roundtrip gate FAIL -> line surgery required (r678)'
st['round_no'] = 502
st['note'] = ("r502: D-19 dual-key flip consumed + O-20261004 SOP inventory delivered: S0 zero-intersect FF merge 4 commits (f1b041400); "
              "decisions 4E5BE321->937A373D (06e9a1a 23:08 removed 10-03/10-04 batch sections + 3 dispatch board rows = back to pre-10-03 bytes, "
              "r639-family second occurrence, MSG-2026-10-04-2330 filed for HQ adjudication, receipts not re-litigated, watermark follows origin); "
              "orders 68947C17->C6F5CC90 (38c4f2d backfill recovery O-2026-0930-027~030; O-027 SOP inventory delivered ahead of window "
              "research/SOP_INVENTORY_202610.md; O-028 P-32 fields already in heartbeat; O-029 night-watch aggregate face; O-030 executed); "
              "S1 smoke 48/48; S6 38/38 rc0 (dualrun ZERO-DRIFT streak 2, REPORT/LIVE regen); W3 judge IN_FLIGHT healthy (ETA ~10-05T02:00); "
              "N2-W15 11/12 (SHARD-2 bm-b keepalive 23:10:14); fund trio NULLS bm-b canonical; boards empty; zero drafting (judgment chains in flight)")
st['last_round_at'] = clock
st['ts'] = clock
st['updated'] = clock
st['last_seen'] = clock
st['round_no_label'] = 'round 502 (bm-c)'
st['clock_read'] = clock
st['last_decisions_sha'] = '937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1'
st['last_orders_sha'] = 'C6F5CC903AF37FA2B827B6694DDEA487A4241AD0'
st['next'] = ("(a) W3 judge product first-check after landing ~10-05 02:00: python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> "
              "treasure question + prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 evening). "
              "(b) N2-W15 SHARD-2 (bm-b) -> 12/12 -> bm-a screen-finalize seat (r482 id-dup probe first). "
              "(c) fund-trio finalize 10-05..10-09 (bm-b canonical, watch only). "
              "(d) SOP gaps G1-G3 build per Oct windows (G3 with 10-09 market reopen data-chain re-arm). "
              "(e) O-2115/O-2030 acceptance 10-08. Next 5x = bm-c r505.")
json.dump(st, io.open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(io.open(sp, encoding='utf-8'))
assert chk['round_no'] == 502, 'state round_no verify failed'
print('state OK round_no=502 dec_sha=', chk['last_decisions_sha'][:12], 'ord_sha=', chk['last_orders_sha'][:12])

# --- heartbeat ---
try:
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu, ram = None, None
hp = ROOT + r'\fleet\machines\bm-c.json'
ok2, hb = roundtrip_gate(hp)
print('heartbeat roundtrip:', ok2)
assert ok2, 'heartbeat roundtrip gate FAIL -> line surgery required (r678)'
hb['last_seen'] = clock
hb['heartbeat_epoch_utc'] = int(now)
hb['clock_read'] = clock
hb['round_no'] = 502
hb['round_no_label'] = 'round 502 (bm-c)'
hb['activity_now'] = ("r502: D-19 dual-key flip consumed (decisions batch-section removal = r639-family 2nd occurrence, MSG-2330 adjudication filed) + "
                      "O-2026-0930-027 SOP inventory delivered + S6 38/38 + smoke 48/48")
hb['current_task'] = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 SHARD-2 bm-b 在飞（fleet 面 11/12）+fund trio NULLS bm-b canonical | "
                      "最近实物: research/SOP_INVENTORY_202610.md（O-027 CEO SOP 建制令假期窗交付·23:3x）+S6 38 腿 CEO 面再生（REPORT/LIVE-20261004·23:2x）+MSG-2026-10-04-2330 D-19 二发定谳呈报 @ " + clock + " | "
                      "下个里程碑: w3_judge.json 落地（~10-05 02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；SHARD-2 烧完→12/12→bm-a screen-finalize；SOP 缺口 G1-G3 随 10 月窗")
hb['health'] = 'healthy'
hb['verdict'] = ("r502 bm-c: D-19 consumption + product round. (1) S0 zero-intersect FF merge 4 commits. (2) S0.5 dual-scan: orders 154/154 zero unacked; "
                 "decisions/orders both flipped -> consumed in-round: decisions batch-section removal (06e9a1a) = r639-family 2nd occurrence, "
                 "MSG-2330 filed for HQ adjudication (intentional cleanup vs accidental overwrite), receipts not re-litigated, watermark follows origin; "
                 "orders backfill O-2026-0930-027~030 -> O-027 SOP inventory delivered ahead of window (research/SOP_INVENTORY_202610.md, 57-line lightweight-gate compliant), "
                 "O-028 P-32 heartbeat fields verified in-place, O-029 night-watch aggregate face zero action, O-030 executed row consumed. (3) S1 48/48. "
                 "(4) S3: watermark green (py_low_with_work_cands = legal W3 judge local_batch_running single-core per r487 calibration); satengine Tools-face rc0 alive (wave116 6/12); "
                 "W3 verify IN_FLIGHT tri-state healthy; N2-W15 11/12; fund trio bm-b canonical; boards empty; standing-lane drafting conditions not met (judgment chains in flight). "
                 "(5) S6 38/38 rc0 NON-ZERO=none (dualrun ZERO-DRIFT streak 2; build_status stale-takeover derive legal per O-2100 s2.4). (6) S7 quartet 4/4 + attrition CLEAN. "
                 "Product score: 2 (CEO-order SOP inventory artifact + S6 38-face CEO regen + MSG adjudication filing)")
hb['prod_lanes'] = ("W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, spawn 21:25:28, ETA ~10-05 02:00, custody _r487bmc tri-state); "
                    "N2-W15 SCREEN fleet 11/12 done (SHARD-2 bm-b keepalive 23:10:14; bm-a screen-finalize seat); "
                    "fund-trio NULLS x3 bm-b canonical keepalive (watch only); O-027 SOP inventory delivered (bm-c r502); boards empty; watermark green")
hb['latest_artifact'] = "research/SOP_INVENTORY_202610.md (O-2026-0930-027 deliverable) + S6 38 legs rc0 CEO faces regen 23:2x (_r502bmc_s6_log.txt) + MSG-2026-10-04-2330-bmc-ALL"
hb['next_milestone'] = ("w3_judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock (<=10-06 evening); N2-W15 12/12 -> bm-a screen-finalize; "
                        "SOP G1-G3 Oct windows; fund-trio finalize 10-05..09; acceptance 10-08; market reopen 10-09")
if cpu is not None:
    hb['cpu_pct'] = cpu
    hb['cpu_util_pct'] = cpu
    hb['cpu_idle_pct'] = round(100 - cpu, 1)
if ram is not None:
    hb['free_ram_gb'] = ram
    hb['ram_free_gb'] = ram
    hb['idle_ram_gb'] = ram
for k in ('ts', 'updated', 'updated_at'):
    hb[k] = clock
json.dump(hb, io.open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk2 = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert chk2['round_no'] == 502
print('heartbeat OK epoch_int=', chk2['heartbeat_epoch_utc'], 'clock=', chk2['clock_read'])
