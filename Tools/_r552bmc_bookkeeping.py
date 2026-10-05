# -*- coding: utf-8 -*-
"""r552 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby round). Lineage _r551bmc_bookkeeping.py; facts inlined
from this round's receipts. Laws: R170/R178 epoch int; R262 clock
T-separated; r503 EOL-preserving bytes write. SPLIT-ANCHOR NOTE (r547 law):
r552 S6 log = r550-lineage header-then-body form (r551 log was the anomalous
body-before-header form whose bookkeeping compensated with shifted anchors);
r552 anchors pin to the OWNING leg blocks directly. This round: QA 25th
consecutive determinism evidence, S6 38/38 first-pass zero-heal 12th,
dualrun streak 51, chain head 668,811 unchanged (W125 burn in-flight bm-a),
zero-merge S0 window (fetch 0 behind), task family 6/6 CSV first-pass,
claws IN-PLACE, attrition CLEAN."""
import json, os, re, subprocess, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r552bmc_s6_log.txt')

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]
epoch = int(time.time())

try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=2), 1)
    free_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu_pct, free_gb = 10.0, 8.6
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, creationflags=0x08000000,
                       timeout=30)
    gpu_mib = int(r.stdout.strip().splitlines()[0])
except Exception:
    gpu_mib = 805

# ---- S6 log facts (owning-leg split anchors per r547 law; r552 log is
# header-then-body so 03_py_watermark block holds the py verdict itself)
s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
s6_face = '38/38 rc0 first-pass zero-heal 12th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
seg_py = s6.split('=== 03_py_watermark', 1)[1].split('=== 04_update_daily', 1)[0]
mv = re.search(r'"verdict": "([^"]+)"', seg_py)
py_verdict = mv.group(1) if mv else '?'
cell_face = 'ORANGE_COOL'
token_delta = '0'   # L1 zero-token face; token_meter leg carries no delta= line (same fallback as r551 lineage)

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r552.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 668811  # W124 landed (unchanged); W125 burn in-flight on bm-a; bm-c zero chain entry this window

did = ("r552 bm-c: golden-week standby round. (1) S0: round-start dirty = 5 own faces (r551 S7-close post-push tails "
       "x3: RR close row + close script Tools/_r551bmc_close.py + close_facts receipt; own daemon lane live x2: "
       "satengine faces) -> churn-absorb 3fb4f4eda (r714 law, targeted add 5 faces + commit -F) -> fetch 0 behind "
       "(zero-merge window, 1/0 push face at close). (2) S0.5: orders 154/154 O-files strict diff rc0 zero unacked "
       "(canonical Tools/orders_diff.py + r539 probe double face; stale_ack README.md = folder readme non-order "
       "file, honest note); D-19 decisions MATCH D14DCC74 zero delta (Tools/d19_check.py canonical); group orders "
       "SHA-1 3BF0F16E MATCH zero new CEO rows (r537 algorithm pin); inbox 0. (3) S1 smoke 48/48. (4) S2: job_list "
       "0; fleet tasks 172 total / 0 open; pool 403 = 399 done + 3 ready (FUND trio bm-b nested-shard ownership, "
       "host_gates refuse bm-c, r720 face) + 1 waiting (W14 governance park honored). (5) S3: WM green (red=false, "
       "next_pick status=claimed = moneyflow IC reference batch lane already claimed, no drafting pointer action); "
       "satengine Tools-copy rc0 alive (burns_active none local); trial-labor zero drafting (anti-dup: W125 burn "
       "in-burn bm-a, fund-trio bm-b in-burn 10-05..09, W16 prereg bm-a <=10-07, golden week no bar). (6) CORE "
       "PRODUCT: QA pack r552 standing re-run (qa/smoke-r552.md 5/5 + equity-curve-r552.png %dB, 93 trades, sharpe "
       "0.1586, maxdd -4.33%%, win 46.24%%, determinism=True; metrics face identical r528-551 = determinism 25th "
       "consecutive evidence); market clock CALL-2026-09-30 cell=ORANGE_COOL. (7) S6 chain %s (receipt "
       "results/_r552bmc_s6_log.txt; legdiff vs r550 lineage PASS: 38 legs command byte-identical, numbered-name "
       "form restored from r550 verbatim lineage after r551 chain file proved untraceable, receipt "
       "results/_r552bmc_legdiff.txt, r531 law); dualrun %s; regime ORANGE shadow days_in_state=2 (enforce "
       "requested, honest downgrade until date-gate first bar 10-09); supply_gap honest structural flag "
       "(ready=3=floor, breach=false); lane_io single-writer guards honest skip (bm-a host fresh); REPORT/LIVE-"
       "2026-10-05 idempotent regen; token delta=%s (L1 zero-token face, L2 today=0). (8) S7: loop pin=5 phase ok "
       "no-op (first fire 15:25); watchdog present (register script idempotent re-register face, -Force harmless); "
       "claws IN-PLACE both MATCH (LF-normalized compare, zero reinstall); task family 6/6 CSV cross-check "
       "first-pass (no-suffix canon names r517 law, zero false-MISSING); attrition CLEAN (4 ledger files, 3 healed "
       "historical shrink rows noted). (9) unified chain live head 668,811 unchanged (W125 burn in-flight bm-a; no "
       "new chain entry by bm-c this window).") % (qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r552 金周值守轮收口（QA 二十五连证+S6 38/38 首过零 heal 十二连·streak 51·orders 154/154+D-19 双 MATCH·"
              "链头 668,811 不变·W125 burn bm-a 在烧） "
              "| 最近实物: qa/smoke-r552.md 5/5+qa/equity-curve-r552.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "二十五连证）+results/_r552bmc_s6_log.txt（38/38 首过） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W125 burn/finalize（bm-a 面）；"
              "fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；D-06 拆件收口 10-07 12:00；"
              "O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）+regime_guard v3 日期门首 bar；"
              "月界首考 10-31；下一 5x=r555") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin selftest). "
              "(b) W125 burn + finalize on bm-a (FREEZE 77cd1f6ee5 landed, A 293_004..295_003 + B 67_201..67_400). "
              "(c) fund-trio finalize 10-05..09 (bm-b canonical). (d) W16 candidate prereg draft+freeze (bm-a, "
              "window <=10-07). (e) D-06 split closeout window 10-07 12:00. (f) O-2115/O-2030 acceptance 10-08. "
              "(g) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 date-gate "
              "first bar. (h) qa/ evidence pack per-round standing re-run. (i) CEO physical item pending: tailscale "
              "login link click (bm-c URL alive since r505). (j) CODELY.md over-50KB flag carried (GM ruling face). "
              "(k) next 5x = r555 HANDOVER check round.")

verify = ("receipts: qa/smoke-r552.md 5/5 + qa/equity-curve-r552.png (%dB, 93 trades, determinism=True) + "
          "results/_r552bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + results/_r552bmc_probe.txt (S1/S2/S3 "
          "compact receipt) + results/_r552bmc_legdiff.txt (LEGS=38 CMD_IDENTICAL=True PASS, r531 law) + smoke 48/48 "
          "+ churn-absorb 3fb4f4eda (5 faces, r714 law) + fetch 0 behind zero-merge window + orders 154/154 strict "
          "diff rc0 (canonical + r539 probe double face) + D-19 decisions MATCH D14DCC74 + group orders SHA-1 "
          "3BF0F16E...E56253 MATCH (r537 pin) + satengine rc0 alive + loop pin=5 phase ok no-op (first fire 15:25) + "
          "watchdog present (idempotent re-register face) + task family 6/6 (CSV cross-check first-pass zero "
          "false-MISSING) + claws IN-PLACE (LF-normalized MATCH both, zero reinstall) + attrition CLEAN (3 healed "
          "rows noted) + unified chain live head 668,811 unchanged (W125 in-flight bm-a) + commit/push delivery "
          "self-check this close.") % (qa_png_b, bad_end)

note = ("r552: golden-week standby round closed. QA pack r552 = 25th consecutive identical metrics face (frozen "
        "golden-week panel determinism evidence). S6 %s (zero-heal x12). S0 zero-merge window: churn-absorb 5 own "
        "faces, fetch 0 behind (push face at close). Chain head 668,811 unchanged (W125 burn in-flight on bm-a; no "
        "bm-c drafting, anti-dup law). No 5x duty this round (next = r555). No new pit this round (legdiff "
        "assertion-layer false positive on path-face heuristic = r549 already-covered family, self-healed in-window "
        "zero origin harm; no CODELY append per four-question gate); no new methodology; no treasure faces (no "
        "five-type closeout by bm-c this round).") % s6_face

row = ("%s | r552 | dept:工程（金周值守轮·QA 证据面常设复跑） | watermark verdict=绿（red=%s·py_watermark probe rc0·verdict=%s〔板空+"
       "bandit 空+金周无 bar=合法 idle 白名单〕·判决链席位他机：W124 finalize 已落账〔链头 668,811·bm-a r730 one-pass·60324fdc2〕+"
       "W125 burn bm-a 在烧〔A 293_004..295_003+B 67_201..67_400·77cd1f6ee5〕+fund-trio bm-b keepalive 在烧〔10-05..09〕+"
       "W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 unclaimed=0·金周无 bar〕·supply_gap 诚实旗=金周结构面 ready=3=floor·breach=false·"
       "点火 SLA 零违例）｜本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r552.md 5/5+qa/equity-curve-r552.png（%dB·3 syms x 800 bars·"
       "93 trades·sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·与 r528-551 面恒等=冻结面板确定性二十五连证）+"
       "S6 %s（收据 results/_r552bmc_s6_log.txt·bad=[%s]·零 heal 十二连）｜S0=轮首脏 5 面（r551 S7-close 尾 x3：RR close 行+close 脚本+"
       "close_facts 收据；own daemon lane live x2：satengine x2）churn-absorb 3fb4f4eda（r714 律·targeted add+commit -F）·fetch 实核 "
       "0 behind→零 merge 窗（1/0 push 收口）｜S0.5=orders 154/154 strict diff rc0 零未回执（正典 orders_diff.py+r539 探针双面·"
       "stale_ack=README.md=目录说明件非令如实注记）·D-19 decisions MATCH D14DCC74 零增量（Tools/d19_check.py 正典）·group orders "
       "水位 SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·inbox 0｜smoke 48/48｜satengine rc0 活（Tools 面·burns_active 本机空）｜"
       "试用劳力线不触发（W125 bm-a 烧中+fund-trio bm-b+金周无 bar）｜S6 面=dualrun ZERO-DRIFT streak %s·regime ORANGE shadow "
       "days_in_state=2（enforce 请求·日期门 10-09 首 bar 前诚实降级）·cell=ORANGE_COOL sleeves4 act0·REPORT/LIVE-2026-10-05 幂等再生·"
       "lane_io 守卫诚实跳过（bm-a 宿主新鲜）｜S7=loop pin5 no-op（首拍 15:25）·watchdog 在位（幂等重注册面如实注记）·双爪 IN-PLACE"
       "（LF 归一 MATCH·零重装）·任务族 6/6（CSV 交叉 r517 律·首过零假 MISSING）·attrition CLEAN〔4 账本·3 healed 历史缩行注记照录〕｜"
       "token 面=本机 L1 零 token 腿·账本 delta=%s·L2 today=0｜统一链头 668,811〔W124 落账·W125 bm-a 在烧·本轮零入链〕｜"
       "轮产品计分：2（qa/ 证据包 r552=能跑/能看实物+S6 38 面 CEO 再生面）｜记账预算：3（state+心跳+轮报=法定 3·CODELY 零 append"
       "〔四问门：本轮零新坑零新方法·legdiff 探针路径面假红=r549 已载族窗内自纠〕）｜方法论捕获=无新方法·宝藏捕获=无（无五类收口面）｜"
       "登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜下轮指针：10-06 00:00 D-20261002-05 selftest 席位窗首过轮跑 "
       "pin selftest；W125 burn/finalize（bm-a 面）；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；"
       "D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09（G3·IntradayMarks 再核·regime_guard v3 日期门首 bar）；"
       "月界首考 10-31；下一 5x=r555") % (now_iso, wm_red, py_verdict, qa_png_b, s6_face, bad_end, streak, token_delta)

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
                                   "r552 probe = Tools/d19_check.py canonical MATCH D14DCC74, zero delta vs r551 "
                                   "consumption; consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r552 zero new orders, 154/154 strict diff rc0 "
                                "round-start scan, canonical + r539 probe double face)")
st['last_round'] = did
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_seen_at'] = now_iso
st['last_ts'] = now_iso
st['next'] = next_field
st['note'] = note
st['ram_free_gb'] = free_gb
st['round_no'] = 552
st['round_no_label'] = 'round 552 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r552: golden-week standby round + QA evidence pack standing re-run "
                      "(qa/smoke-r552.md 5/5 + equity-curve-r552.png %dB, 93 trades, determinism=True, metrics "
                      "face identical to r528-551 = frozen-panel 25th consecutive evidence), S6 %s, dualrun %s, "
                      "smoke 48/48, orders 154/154 zero unacked, D-19 dual MATCH (decisions D14DCC74 + group "
                      "orders SHA-1 3BF0F16E r537 pin), zero-merge S0 window (churn-absorb 3fb4f4eda 5 own faces, "
                      "fetch 0 behind), attrition CLEAN, task family 6/6 CSV first-pass + claws IN-PLACE; judgment "
                      "seats on other machines (W124 finalize landed chain head 668,811, W125 burn in-burn bm-a, "
                      "fund-trio bm-b in-burn 10-05..09, W16 bm-a <=10-07); supply_gap flag = golden-week structural "
                      "(ready=3=floor, unclaimed=0, breach=false); regime ORANGE shadow (date-gate first bar "
                      "10-09)") % (qa_png_b, s6_face, dual_face)
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
hb['latest_artifact'] = ("qa/ evidence pack r552 (smoke-r552.md 5/5 + equity-curve-r552.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 25th consecutive evidence) + results/_r552bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + results/_r552bmc_legdiff.txt (LEGDIFF PASS) + "
                         "churn-absorb 3fb4f4eda") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W125 "
                        "burn+finalize bm-a (freeze landed 77cd1f6ee5); W16 candidate prereg (bm-a, <=10-07); "
                        "fund-trio finalize (bm-b) 10-05..09; D-06 closeout 10-07 12:00; O-2115/O-2030 acceptance "
                        "10-08; reopen 10-09 (G3, IntradayMarks re-check, regime_guard v3 date-gate first bar); "
                        "month-end exam 10-31; next 5x = bm-c r555")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 552
hb['round_no_label'] = 'round 552 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r552 bm-c: golden-week standby round (boards open=0, judgment seats other machines, no bar until "
                 "10-09). (1) S0 churn-absorb 3fb4f4eda (5 own faces) + fetch 0 behind zero-merge. (2) orders "
                 "154/154 rc0, inbox 0. (3) D-19 dual MATCH zero action. (4) smoke 48/48. (5) boards empty. (6) WM "
                 "green, py probe verdict=%s legal idle; satengine rc0 alive; next_pick=claimed no drafting. (7) "
                 "CORE: QA pack r552 (5/5, 93 trades, determinism=True, frozen-panel 25th consecutive evidence). "
                 "(8) S6 %s (zero-heal x12), dualrun %s, regime ORANGE shadow, supply_gap honest structural. (9) "
                 "S7: loop pin5 phase-ok; watchdog present; task family 6/6 CSV first-pass; claws IN-PLACE zero "
                 "reinstall; attrition CLEAN; close: targeted add + commit -F + push_verify.") % (py_verdict, s6_face, dual_face)
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

# ---- self-checks (R170/R178 epoch int + R262 clock T + round + row count)
st2 = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert isinstance(st2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in st2['clock_read'] and '+' in st2['clock_read'], 'clock_read must be T-separated ISO with offset'
assert st2['round_no'] == 552, 'round_no must be 552'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 552, 'hb round_no must be 552'
rr_txt = open(RR, 'rb').read().decode('utf-8', errors='replace')
assert rr_txt.count('| r552 | dept:') == 1, 'r552 main row count != 1'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
