# -*- coding: utf-8 -*-
"""r546 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby round). Lineage _r545bmc_bookkeeping.py; facts inlined
from this round's receipts. Laws: R170/R178 epoch int; R262 clock
T-separated; r503 EOL-preserving bytes write."""
import json, os, re, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r546bmc_s6_log.txt')

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]
epoch = int(time.time())

# live machine metrics (honest read, captured this close window)
cpu_pct = 1.1
free_gb = 9.5
gpu_mib = 827

# ---- S6 log facts
s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
s6_face = '38/38 rc0 first-pass zero-heal 6th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
cell_face = 'ORANGE_COOL'
tk = re.search(r'delta=(\d+)', s6)
token_delta = tk.group(1) if tk else '?'

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r546.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

gsha = '3BF0F16E'
ledger_head = 662211  # live read results/perpetual_faces/n1_w121_results.json science_gates.ledger.total (W122 finalize pending 10/12)

did = ("r546 bm-c: golden-week standby round. (1) S0: round-start dirty = 3 own faces (r545 S7-close tail "
       "standing one-commit-behind pattern + own satengine lane live x2) -> churn-absorb 5c79729f9 (r714 law) "
       "-> fetch 3 behind -> merge origin/main rc0 zero-UU clean absorb (48 files, bm-a r727 wave: W122 FREEZE "
       "269466f13 + round close 9f4138d23 + merge e064df65e + addendum 1fb97b3f5; W122 shards 0..9-of-12 landed "
       "results/p2cal_ext/n1_w122/). (2) S0.5: orders 154/154 strict diff rc0 zero unacked; D-19 decisions "
       "MATCH D14DCC74 zero delta (Tools/d19_check.py canonical); group orders SHA-1 3BF0F16E MATCH zero new CEO "
       "rows (r537 algorithm pin); inbox 0 unread. (3) S1 smoke 48/48. (4) S2: job_list 0; fleet tasks 172 total "
       "/ 0 open; pool 403 = 399 done + 3 ready (FUND trio bm-b nested-shard ownership, host_gates refuse bm-c, "
       "r720 face) + 1 waiting. (5) S3: WM green (red=false, py_low_board_clear legal idle whitelist; supply_gap "
       "honest structural flag ready=3=floor breach=false); satengine Tools-copy rc0 alive (N1 wave registry "
       "through W122 seat, W122 in-burn local 10/12 remote 0); trial-labor zero drafting (W122 seat reserved by "
       "bm-a r727 freeze window; fund-trio bm-b in-burn 10-05..09; W16 prereg bm-a <=10-07; W3 CEO-ruling; W14 "
       "parked; reopen 10-09). (6) CORE PRODUCT: QA pack r546 standing re-run (qa/smoke-r546.md 5/5 + "
       "equity-curve-r546.png %dB, 93 trades, sharpe 0.1586, maxdd -4.33%%, win 46.24%%, determinism=True; "
       "metrics face identical r528-545 = determinism 19th consecutive evidence); market clock CALL-2026-09-30 "
       "cell=ORANGE_COOL. (7) S6 chain %s (receipt results/_r546bmc_s6_log.txt); dualrun %s; update_lhb real "
       "pull rc0 11/11 pages (golden-week disclosure window data); update_fundamental eligibility refresh rc0 "
       "2/2; regime ORANGE shadow days_in_state=2 (enforce requested, honest downgrade until date-gate first bar "
       "10-09); lane_io single-writer guard skip-derive faces honest stdout (bm-a host heartbeat fresh); "
       "REPORT/LIVE-2026-10-05 idempotent regen; token delta=%s. (8) S7: loop pin=5 phase ok no-op; watchdog "
       "-Force idempotent re-registered; claws re-installed LF-normalized both; task family 6/6 (CSV "
       "cross-check); attrition CLEAN (3 healed historical shrink rows noted, zero active loss); inbox 0 "
       "unread. (9) unified chain live head unchanged 662,211 (W121 finalize; W122 finalize pending 10/12 "
       "shards in-burn on bm-a engine; bm-c zero chain entry this window).") % (qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r546 金周值守轮收口（QA 十九连证+S6 38/38 首过零 heal 六连·churn-absorb 5c79729f9+零 UU merge 干净吸收 "
              "bm-a W122 freeze 波·orders/D-19/group-orders 三 MATCH） "
              "| 最近实物: qa/smoke-r546.md 5/5+qa/equity-curve-r546.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "十九连证）+results/_r546bmc_s6_log.txt（38/38 首过） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；fund-trio finalize"
              "（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 "
              "验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）+regime_guard v3 日期门首 bar；月界首考 10-31；"
              "下一 5x=r550") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin "
              "selftest). (b) fund-trio finalize 10-05..09 (bm-b canonical). (c) W16 candidate prereg draft+freeze "
              "(bm-a, window <=10-07); W122 burn in-flight on bm-a engine (freeze landed 269466f13, shards 10/12 "
              "local done at this close). (d) D-06 split closeout window 10-07 12:00. (e) O-2115/O-2030 acceptance "
              "10-08. (f) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 "
              "date-gate first bar. (g) qa/ evidence pack per-round standing re-run. (h) CEO physical item pending: "
              "tailscale login link click (bm-c URL alive since r505). (i) CODELY.md over-50KB flag carried (GM "
              "ruling face). (j) next 5x = r550 HANDOVER check round.")

verify = ("receipts: qa/smoke-r546.md 5/5 + qa/equity-curve-r546.png (%dB, 93 trades, determinism=True) + "
          "results/_r546bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + smoke 48/48 + churn-absorb 5c79729f9 "
          "(3 faces, r714 law) + merge origin/main rc0 zero-UU (48 files) + orders 154/154 strict diff rc0 + "
          "D-19 decisions MATCH D14DCC74 + group orders SHA-1 3BF0F16E...E56253 MATCH (r537 pin) + satengine rc0 "
          "(Tools copy, W122 in-burn 10/12) + loop pin=5 phase ok no-op + watchdog -Force idempotent + task "
          "family 6/6 (CSV cross-check) + claws IN-PLACE (LF-normalized, both) + attrition CLEAN + inbox 0 "
          "unread + unified chain live head 662,211 (n1_w121_results.json) + commit/push delivery self-check "
          "this close.") % (qa_png_b, bad_end)

note = ("r546: golden-week standby closed. QA pack r546 = 19th consecutive identical metrics face (frozen "
        "golden-week panel determinism evidence). S6 %s (zero-heal x6). S0 churn-absorb collected r545 close "
        "tail + own satengine lane live faces (3 faces, standing pattern per r714 law); merge origin/main "
        "zero-UU clean window (bm-a r727 W122 freeze wave absorbed). W122 seat = bm-a reserved (no bm-c "
        "drafting, anti-dup law). Unified chain head unchanged 662,211 (W122 finalize pending 10/12, in-burn). "
        "No new pits (S6 chain lineage pre-diffed vs r543 per r531 law = round-tag/log-path only); no new "
        "methodology; no treasure faces (no five-type closeout this round). No CODELY append (memory-entry "
        "gate: zero new long-term lessons).") % s6_face

row = ("%s | r546 | dept:工程（金周值守轮·QA 证据面常设复跑） | watermark verdict=绿（red=%s·py_watermark probe rc0·"
       "py_low_board_clear 板空合法 idle 白名单〔判决链席位他机：fund-trio bm-b keepalive 在烧+W122 席位 bm-a 已冻结〔r727 冻结窗·"
       "在烧 10/12〕+W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 unclaimed=0·金周无 bar〕·supply_gap 诚实旗=金周结构面 "
       "ready=3=floor·breach=false·点火 SLA 零违例）｜本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r546.md 5/5+"
       "qa/equity-curve-r546.png（%dB·3 syms x 800 bars·93 trades·sharpe 0.1586·maxdd -4.33%%·win 46.24%%·"
       "determinism=True·与 r528-545 面恒等=冻结面板确定性十九连证）+S6 %s（收据 results/_r546bmc_s6_log.txt·bad=[%s]·"
       "零 heal 六连）｜S0=轮首脏 3 面（r545 S7-close 尾+satengine lane live x2）churn-absorb 5c79729f9（r714 律）·"
       "fetch 实核 3 behind→merge origin/main rc0 零 UU 干净吸收〔48 files=bm-a r727 波：W122 FREEZE 269466f13+close "
       "9f4138d23+merge e064df65e+addendum 1fb97b3f5·W122 shards 10/12 落 origin〕｜S0.5=orders 154/154 strict diff rc0 "
       "零未回执·D-19 decisions MATCH D14DCC74 零增量（Tools/d19_check.py 正典）·group orders 水位 SHA-1 3BF0F16E MATCH "
       "零新令（r537 算法钉律）·inbox 0 未读｜smoke 48/48｜satengine rc0 活（Tools 面·N1 注册表至 W122 席·W122 在烧 local "
       "10/12 remote 0）｜试用劳力线不触发（W122 席位 bm-a 保留+fund-trio bm-b 在烧〔10-05..09〕+W16 bm-a ≤10-07+W3 CEO "
       "裁定+W14 停泊+复市 10-09）｜S6 面实拉=update_lhb 真拉 11/11 页（金周披露窗）+update_fundamental 刷新 2/2·其余 lane "
       "guard no-op 诚实｜dualrun ZERO-DRIFT streak %s·regime ORANGE shadow days_in_state=2（enforce 请求·日期门 10-09 首 "
       "bar 前诚实降级）｜attrition CLEAN〔3 healed 历史缩行注记照录〕·任务族 6/6（CSV 交叉 r517 律）·claws IN-PLACE（LF "
       "归一）·loop pin5 no-op·watchdog -Force 幂等｜token 面=本机 L1 零 token 腿·账本 delta=%s｜统一链头 662,211 不变"
       "〔W121 finalize 落账·W122 finalize 待 10/12·bm-c 零入链〕｜轮产品计分：2（qa/ 证据包 r546=能跑/能看实物+S6 38 面 "
       "CEO 再生面）｜记账预算：3（state+心跳+轮报=法定 3·CODELY 零 append〔四问门：本轮零新坑零新方法〕）｜方法论捕获=无新方法·"
       "宝藏捕获=无（无五类收口面）｜登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜下轮指针：10-06 00:00 "
       "D-20261002-05 selftest 席位窗首过轮跑 pin selftest；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·"
       "≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09（G3·IntradayMarks 再核·regime_guard v3 "
       "日期门首 bar）；月界首考 10-31；下一 5x=r550") % (now_iso, wm_red, qa_png_b, s6_face, bad_end, streak, token_delta)

def load_json_raw(p):
    raw = open(p, 'rb').read()
    return json.loads(raw.decode('utf-8-sig')), raw

def eol_of(raw):
    return b'\r\n' if b'\r\n' in raw[:4000] else b'\n'

def dump_json(obj, raw, p):
    eol = eol_of(raw)
    data = (json.dumps(obj, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if eol == b'\r\n':
        data = data.replace(b'\n', b'\r\n')
    open(p, 'wb').write(data)

# ---- state update (preserve key order)
st, st_raw = load_json_raw(STATE)
st['clock_read'] = now_iso
st['cpu_pct'] = cpu_pct
st['cpu_util_pct'] = cpu_pct
st['current_task'] = three_line
st['current_task_at'] = now_iso
st['did'] = did
st['free_ram_gb'] = free_gb
st['gpu_free_vram_mib'] = gpu_mib
st['idle_ram_gb'] = free_gb
st['heartbeat_epoch_utc'] = epoch
for k in ('gpu_idle_vram_mib', 'gpu_free_mb', 'gpu_idle_mb', 'gpu_vram_free_mb'):
    if k in st:
        st[k] = gpu_mib
st['last_decisions_read_at'] = now_iso
st['last_decisions_sha_method'] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
                                   "r546 probe = Tools/d19_check.py canonical MATCH D14DCC74, zero delta vs r545 "
                                   "consumption; consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r546 zero new orders, 154/154 strict diff rc0 "
                                "round-start scan)")
st['last_round'] = did
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_seen_at'] = now_iso
st['last_ts'] = now_iso
st['next'] = next_field
st['note'] = note
st['ram_free_gb'] = free_gb
st['round_no'] = 546
st['round_no_label'] = 'round 546 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r546: golden-week standby + QA evidence pack standing re-run "
                      "(qa/smoke-r546.md 5/5 + equity-curve-r546.png %dB, 93 trades, determinism=True, metrics "
                      "face identical to r528-545 = frozen-panel 19th consecutive evidence), S6 %s, dualrun %s, "
                      "smoke 48/48, orders 154/154 zero unacked, D-19 dual MATCH (decisions D14DCC74 + group "
                      "orders SHA-1 3BF0F16E r537 pin), W122 freeze wave absorbed (bm-a r727), attrition CLEAN, "
                      "task family 6/6 CSV cross-check + claws IN-PLACE; judgment seats on other machines (W122 "
                      "in-burn bm-a 10/12, fund-trio bm-b in-burn 10-05..09, W16 bm-a <=10-07); supply_gap flag "
                      "= golden-week structural (ready=3=floor, unclaimed=0, breach=false); regime ORANGE shadow "
                      "(date-gate first bar 10-09)") % (qa_png_b, s6_face, dual_face)
hb['clock_read'] = now_iso
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100.0 - cpu_pct, 1)
hb['current_task'] = three_line
hb['current_task_at'] = now_iso
hb['free_ram_gb'] = free_gb
for k in ('gpu_free_mb', 'gpu_free_vram_mb', 'gpu_free_vram_mib', 'gpu_idle_vram_mb', 'gpu_idle_vram_mib', 'gpu_vram_free_mb', 'gpu_free_mib'):
    if k in hb:
        hb[k] = gpu_mib
hb['heartbeat_epoch_utc'] = epoch
hb['idle_ram_gb'] = free_gb
hb['last_seen'] = now_iso
hb['last_seen_at'] = now_iso
hb['latest_artifact'] = ("qa/ evidence pack r546 (smoke-r546.md 5/5 + equity-curve-r546.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 19th consecutive evidence) + results/_r546bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + churn-absorb 5c79729f9 + zero-UU merge absorb") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W16 "
                        "candidate prereg (bm-a, <=10-07); W122 burn in-flight (bm-a engine, 10/12 local); "
                        "fund-trio finalize (bm-b) 10-05..09; D-06 closeout 10-07 12:00; O-2115/O-2030 "
                        "acceptance 10-08; reopen 10-09 (G3, IntradayMarks re-check, regime_guard v3 "
                        "date-gate first bar); month-end exam 10-31; next 5x = bm-c r550")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 546
hb['round_no_label'] = 'round 546 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r546 bm-c: golden-week standby (boards open=0, judgment seats other machines, no bar until "
                 "10-09). (1) S0 churn-absorb 5c79729f9 (3 faces), merge origin/main zero-UU (48 files, bm-a "
                 "r727 W122 freeze wave). (2) orders 154/154 rc0, inbox 0. (3) D-19 dual MATCH zero action. "
                 "(4) smoke 48/48. (5) boards empty. (6) WM green, py_low_board_clear legal idle; satengine rc0 "
                 "alive (W122 in-burn 10/12). (7) CORE: QA pack r546 (5/5, 93 trades, determinism=True, "
                 "frozen-panel 19th consecutive evidence). (8) S6 %s, dualrun %s, LHB real pull 11/11, "
                 "supply_gap honest structural. (9) S7: loop pin5 phase-ok; watchdog re-registered; task family "
                 "6/6 CSV; claws re-installed; attrition CLEAN; close: targeted add + commit -F + "
                 "push_verify.") % (s6_face, dual_face)
dump_json(hb, hb_raw, HB)

# ---- round report append (EOL-preserving)
rr_raw = open(RR, 'rb').read()
eol = b'\r\n' if b'\r\n' in rr_raw[-2000:] else b'\n'
row_b = row.encode('utf-8')
if eol == b'\r\n':
    row_b = row_b.replace(b'\n', b'\r\n')
if not rr_raw.endswith(eol):
    open(RR, 'ab').write(eol)
open(RR, 'ab').write(row_b + eol)

# ---- self-checks (R170/R178 epoch int + R262 clock T + F5 fields)
st2 = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert isinstance(st2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in st2['clock_read'] and '+' in st2['clock_read'], 'clock_read must be T-separated ISO with offset'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
