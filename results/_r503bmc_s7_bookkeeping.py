# r503 bm-c S7 bookkeeping v2: eol-aware roundtrip gates (r485 host-eol law) + binary writes preserving CRLF face
# r678 diagnosis: state/heartbeat = standard dump modulo CRLF (raw == dumps.replace('\n','\r\n') exact) -> gate compares against host-eol form, write binary.
import json, time, os

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now = time.time()
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def load_with_eol(path):
    raw = open(path, 'rb').read().decode('utf-8')
    eol = '\r\n' if raw.count('\r\n') >= (raw.count('\n') - raw.count('\r\n')) else '\n'
    obj = json.loads(raw)
    redump = json.dumps(obj, ensure_ascii=False, indent=1)
    ok = (raw == redump) if eol == '\n' else (raw == redump.replace('\n', '\r\n'))
    return ok, obj, eol

def dump_binary(path, obj, eol):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    if eol == '\r\n':
        s = s.replace('\n', '\r\n')
    open(path, 'wb').write(s.encode('utf-8'))

# --- state-bm-c.json ---
sp = ROOT + r'\state-bm-c.json'
ok, st, eol = load_with_eol(sp)
print('state roundtrip(host-eol):', ok, 'eol=', repr(eol))
assert ok, 'state roundtrip gate FAIL even modulo EOL -> real non-standard face, line surgery required (r678)'
st['round_no'] = 503
st['did'] = ("r503 bm-c: custody/consumption round (back-to-back thin round after r502 full close 23:31). "
             "(1) S0: fetch origin zero-delta (behind=0/ahead=0 at 23:38), no merge needed; satengine 2 daemon faces absorbed at close (treadmill churn). "
             "(2) S0.5 dual-scan: orders 154/154, 0 unacked; D-19 dual flip consumed: group orders C6F5CC90->F06E044F (c1d1a4f two status flips "
             "O-20261004-2300 executed + O-1610 recon flip, BOTH Biggame-domain rows -> zero BigMoney action, watermark follows origin); "
             "decisions 937A373D->4E5BE321 (75c14df 23:39:25 accidental-deletion 5-face restore = HQ de-facto adjudication of MSG-2330 r639-family 2nd occurrence; "
             "delta = previously-consumed 10-03/10-04 batch sections + D-20261004-02 dispatch rows, receipts not re-litigated per r502). "
             "(3) S1 smoke 48/48. (4) S3: watermark green (red=false, next_pick claimed/parked self-heal); satengine Tools-face rc0 alive "
             "(wave116 6/12 burning, W118 queued, bm-a W119 seat adjacent-band no-collision); W3 judge custody tri-state IN_FLIGHT healthy; "
             "pool: N2-W15 11/12 with SHARD-2 LEGALLY TAKEN OVER by bm-c daemon (bm-b keepalive 23:20:14 -> 20.4min stall -> claim 23:40:38, health-machine takeover lane); "
             "fund trio NULLS x3 bm-b canonical; boards open=0 (claimed 45/done 119); judgment chains in flight -> standing-lane drafting NOT met, zero drafting. "
             "(5) S6 38/38 rc0 NON-ZERO=none; pool_dualrun ZERO-DRIFT streak 3 = flip-gate 3-consecutive-green evidence line REACHED (flip itself = separate round/session action per law). "
             "(6) S7: attrition CLEAN (4 ledgers, healed history rows recorded); quartet 4/4 (loop pin5 no-op, watchdog re-registered, both claws in-place).")
st['last_round'] = ("r503 bm-c: custody round -- S0 zero-delta fetch, S0.5 154/154 + D-19 dual flip consumed (orders=Biggame-domain status flips zero-action; "
                    "decisions=HQ restore adjudication), smoke 48/48, W3 IN_FLIGHT watch, N2-W15 SHARD-2 bm-c daemon takeover, S6 38/38 + dualrun streak 3, S7 quartet 4/4.")
st['verify'] = ("r503: receipts _r503bmc_s05.txt (154/154, 0 unacked; dual-key fresh hashes captured) + _r503bmc_ord_latest.txt (F06E044F full dump) + "
                "_r503bmc_dec_delta.py output (4E5BE321 + 32-line restore diff, previously-consumed faces) + _r503bmc_pool_watch.txt (N2-W15/fund-trio/boards face) + "
                "_r503bmc_s6_log.txt (38 legs rc0) + _r487bmc_w3_judge_verify.json (IN_FLIGHT) + smoke 48/48 + attrition CLEAN; "
                "delivery: round commit + push_verify this close.")
st['note'] = ("r503: back-to-back custody round. D-19 dual flip consumed (orders F06E044F = Biggame status flips zero-action; decisions 4E5BE321 = HQ 75c14df "
              "accidental-deletion restore, MSG-2330 adjudicated de-facto by HQ action). N2-W15 SHARD-2 taken over by bm-c daemon after bm-b 20.4min keepalive stall. "
              "S6 38/38, dualrun streak 3 = flip-gate evidence line reached. Zero drafting (judgment chains in flight). MSG-2330 left in inbox for other machines' "
              "consumption window (self-authored, content known).")
st['last_round_at'] = clock
st['last_round_ts'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
st['ts'] = clock
st['updated'] = clock
st['updated_at'] = clock
st['last_seen'] = clock
st['last_seen_at'] = clock
st['current_task_at'] = clock
st['round_no_label'] = 'round 503 (bm-c)'
st['clock_read'] = clock
st['last_decisions_read_at'] = clock
st['last_decisions_sha'] = '4E5BE321F9B7A15D7F58BAB3771ECF329534EED8D30B090CDAC4E9F151D911DC'
st['last_orders_sha'] = 'F06E044FD6DD854C7D1256EC63D7F0CBB4DE3A1C'
st['next'] = ("(a) W3 judge product first-check after landing ~10-05 02:00: python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure question + "
              "prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 evening). "
              "(b) N2-W15 SHARD-2 (bm-c daemon-owned since 23:40:38) -> 12/12 -> bm-a screen-finalize seat (r482 id-dup probe first). "
              "(c) D-20261004-05 acceptance window D-20261002-02/03 opens 10-05 00:00 (verification-hold face, keep-alive check); D-20261002-05 selftest seat 10-06 00:00; "
              "D-20261002-06 split closeout window 10-07. "
              "(d) fund-trio finalize 10-05..10-09 (bm-b canonical, watch only). "
              "(e) SOP gaps G1-G3 build per Oct windows (G3 with 10-09 market reopen data-chain re-arm). "
              "(f) O-2115/O-2030 acceptance 10-08. Pool dualrun flip-gate: streak 3 reached, flip plan decision = separate session (research/POOL_RETIREMENT_S3_WAVE1_ANALYSIS.md). Next 5x = bm-c r505.")
dump_binary(sp, st, eol)
chk = json.load(open(sp, encoding='utf-8'))
assert chk['round_no'] == 503, 'state round_no verify failed'
print('state OK round_no=503 dec_sha=', chk['last_decisions_sha'][:12], 'ord_sha=', chk['last_orders_sha'][:12])

# --- heartbeat ---
try:
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu, ram = None, None
hp = ROOT + r'\fleet\machines\bm-c.json'
ok2, hb, eol2 = load_with_eol(hp)
print('heartbeat roundtrip(host-eol):', ok2, 'eol=', repr(eol2))
assert ok2, 'heartbeat roundtrip gate FAIL even modulo EOL -> line surgery required (r678)'
hb['last_seen'] = clock
hb['heartbeat_epoch_utc'] = int(now)
hb['clock_read'] = clock
hb['round_no'] = 503
hb['round_no_label'] = 'round 503 (bm-c)'
hb['activity_now'] = ("r503: D-19 dual flip consumed (orders=Biggame status flips; decisions=HQ accidental-deletion restore adjudication of MSG-2330) + "
                      "N2-W15 SHARD-2 daemon takeover + S6 38/38 + dualrun streak 3 (flip-gate evidence line) + smoke 48/48")
hb['current_task'] = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 SHARD-2 本机 daemon 接管烧录（bm-b keepalive 停滞 20.4min→合法接管 23:40:38）+fund trio NULLS bm-b canonical | "
                      "最近实物: S6 38 腿 CEO 面再生+双跑对账 ZERO-DRIFT streak 3（flip 门证据线达成）+D-19 双键翻面消费（orders F06E044F/decisions 4E5BE321·restore=HQ 裁决落地） @ " + clock + " | "
                      "下个里程碑: w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；SHARD-2 烧完→12/12→bm-a screen-finalize；D-20261002-02/03 收口窗 10-05 00:00 开窗")
hb['health'] = 'healthy'
hb['verdict'] = ("r503 bm-c: custody/consumption round. (1) S0 zero-delta fetch (behind=0/ahead=0). (2) S0.5 dual-scan 154/154 zero unacked; D-19 dual flip consumed: "
                 "orders C6F5CC90->F06E044F = c1d1a4f two status flips both Biggame-domain (zero BigMoney action); decisions 937A373D->4E5BE321 = 75c14df 5-face "
                 "accidental-deletion restore = HQ de-facto adjudication of r502 MSG-2330 (delta = previously-consumed faces, receipts not re-litigated). "
                 "(3) S1 48/48. (4) S3: watermark green; satengine Tools-face rc0 alive (wave116 6/12); W3 IN_FLIGHT tri-state healthy; N2-W15 11/12 with SHARD-2 "
                 "legally taken over by bm-c daemon after bm-b 20.4min keepalive stall; fund trio bm-b canonical; boards open=0; standing-lane drafting NOT met (judgment chains in flight). "
                 "(5) S6 38/38 rc0 NON-ZERO=none; dualrun ZERO-DRIFT streak 3 = flip-gate evidence line reached. (6) S7 attrition CLEAN + quartet 4/4. "
                 "Product score: 1 (custody/consumption round: D-19 dual consumption + streak-3 evidence milestone + S6 CEO-face regen; no new runnable artifact this thin round)")
hb['prod_lanes'] = ("W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, ETA ~10-05 02:00, custody _r487bmc tri-state); "
                    "N2-W15 SCREEN fleet 11/12 (SHARD-2 bm-c daemon-owned since 23:40:38 takeover; bm-a screen-finalize seat next); "
                    "fund-trio NULLS x3 bm-b canonical keepalive (watch only); boards open=0; dualrun flip-gate streak 3 reached (flip decision = separate session); watermark green")
hb['latest_artifact'] = ("results/_r503bmc_s6_log.txt (38 legs rc0, CEO faces REPORT/LIVE-20261004 regen 23:4x) + dualrun streak 3 evidence row "
                         "(results/pool_dualrun.bm-c.jsonl) + D-19 dual consumption receipts (_r503bmc_s05.txt/_r503bmc_ord_latest.txt/_r503bmc_dec_delta.py)")
hb['next_milestone'] = ("w3_judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock (<=10-06 evening); N2-W15 12/12 -> bm-a screen-finalize; "
                        "D-20261002-02/03 window opens 10-05 00:00; fund-trio finalize 10-05..09; acceptance 10-08; market reopen 10-09")
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
dump_binary(hp, hb, eol2)
chk2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert chk2['round_no'] == 503
print('heartbeat OK epoch_int=', chk2['heartbeat_epoch_utc'], 'clock=', chk2['clock_read'])

# --- round report append (bytes mode per r641 mixed-encoding history law; r679 idempotence gate; host EOL preserved) ---
rp = ROOT + r'\round_reports-bm-c.md'
raw_rp = open(rp, 'rb').read()  # bytes, no strict decode (r641)
# FIX r503: gate marker MUST equal a byte sequence actually present in the appended line
# (first version used b'r503 bm-c' = close-line convention -> pre-gate always passed,
#  post-verify always failed -> triple append, healed by _r503bmc_report_heal.py)
marker = b' | r503 | dept:'
cnt = raw_rp.count(marker)
assert cnt == 0, 'r679 double-append guard: r503 round-line marker already present x%d' % cnt
rp_eol = b'\r\n' if raw_rp.count(b'\r\n') >= (raw_rp.count(b'\n') - raw_rp.count(b'\r\n')) else b'\n'
line = (clock + " | r503 | dept:研究（D-19 双键翻面消费·W3/N2 值守·舰队维护） | watermark verdict=绿（red=false·next_pick=moneyflow IC claimed/parked 自愈面·py_low=合法：W3 judge 在飞单核 finalize〔r487 标定〕+SHARD-2 daemon 烧录+池可领 0+金周无 bar） | "
        "当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 SHARD-2 本机 daemon 接管烧录（bm-b keepalive 23:20:14 停滞 20.4min→合法接管 23:40:38）+fund trio NULLS bm-b canonical | "
        "最近实物: S6 38 腿 CEO 面再生+双跑对账 ZERO-DRIFT streak 3（flip 门三连绿证据线达成·flip=另轮另会话动作）+D-19 双键消费（orders F06E044F=c1d1a4f 两翻牌行均 Biggame 域零动作·decisions 4E5BE321=75c14df 误删五面找回=HQ 对 MSG-2330 实质裁决·增量=r502 前已消费面零重复立案） @ " + clock + " | "
        "下个里程碑: w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；SHARD-2 烧完→12/12→bm-a screen-finalize（r482 id-dup 探针先行）；D-20261002-02/03 收口窗 10-05 00:00 开窗 | "
        "S0 fetch zero-delta（behind=0/ahead=0）；S1 smoke 48/48；S3 satengine rc0 活（wave116 6/12）+boards open=0（claimed 45/done 119）+判决链在飞→常设线零起草；S6 38/38 rc0 NON-ZERO=none；S7 attrition CLEAN+四件套 4/4（loop pin5 no-op·watchdog 重注册·双爪 in-place）；"
        "inbox: MSG-2330（self 发件）留他机消费窗；登记册零命中断言=不适用（零清扫零 quarantine 零归档动作） | ")
with open(rp, 'ab') as f:
    f.write(line.encode('utf-8') + rp_eol)
raw2 = open(rp, 'rb').read()
assert raw2.count(marker) == 1, 'r679 post-append verify failed (round-line marker)'
assert raw2.count(b'r503 bm-c') == 0, 'close-line marker must not exist before close append'
print('round report appended (bytes mode), round-line marker count=1, eol=', repr(rp_eol))
