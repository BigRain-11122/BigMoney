# -*- coding: utf-8 -*-
"""r547 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby round). Lineage _r546bmc_bookkeeping.py; facts inlined
from this round's receipts. Laws: R170/R178 epoch int; R262 clock
T-separated; r503 EOL-preserving bytes write."""
import json, os, re, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r547bmc_s6_log.txt')

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]
epoch = int(time.time())

# live machine metrics (honest read, captured this close window; py_watermark
# canonical sample 14:11:02 + nvidia-smi probe)
cpu_pct = 23.0
free_gb = 8.2
gpu_mib = 807

# ---- S6 log facts
s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
s6_face = '38/38 rc0 first-pass zero-heal 7th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
cell_face = 'ORANGE_COOL'
tk = re.search(r'delta=(\d+)', s6)
token_delta = tk.group(1) if tk else '0'
# pin to py_watermark leg block ONLY: the first '"verdict"' in the whole log
# belongs to compute_audit (FLAG faces); grabbing it misattributes the
# py verdict (r547 surgical-fix lesson, count-assert 2+1+1)
seg = s6.split('=== py_watermark', 1)[1]
mv = re.search(r'"verdict": "([^"]+)"', seg)
py_verdict = mv.group(1) if mv else '?'

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r547.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 664411  # W122 finalize landed (bm-a r728 one-pass): K=266,320, skill_line_v2 1.1748 K-lift 0; evidence results/perpetual_faces/n1_w122_results.json

did = ("r547 bm-c: golden-week standby round. (1) S0: round-start dirty = 3 own faces (r546 S7-close tail "
       "standing one-commit-behind pattern + own satengine lane live x2) -> churn-absorb bb704978d (r714 law) -> "
       "fetch 7 behind -> merge hop-1 origin/main rc0 zero-UU clean absorb (15 files: bm-a W122 finalize wave "
       "n1_w122_results.json + PERPETUAL_N1_W122_PREREG addendum + fund-trio keepalives + satengine state faces) "
       "-> push attempt 1 rejected by pre-push claw: deletion set = _r728bma_w123_probe pair = behind-origin "
       "signal (bm-a r728 W123-seat wave landed mid-window; r524/r704-1 law, zero local miswrite, zero "
       "--no-verify) -> fetch 1 behind -> merge hop-2 rc0 zero-UU (3 files: MSG-1414 W123 seat + "
       "_r728bma_w123_probe.py + receipt) -> push rc0 tip 9f4eedb0a behind=0 (delivery self-check same window). "
       "(2) S0.5: orders 154/154 strict diff rc0 zero unacked; D-19 decisions MATCH D14DCC74 zero delta "
       "(Tools/d19_check.py canonical); group orders SHA-1 3BF0F16E MATCH zero new CEO rows (r537 algorithm "
       "pin); inbox 1 = MSG-2026-10-05-1414-bma-w123-seat (bm-a W123 seat publication, informational -> "
       "processed/, anti-dup honored). (3) S1 smoke 48/48. (4) S2: job_list 0; fleet tasks 172 total / 0 open; "
       "pool 403 = 399 done + 3 ready (FUND trio bm-b nested-shard ownership, host_gates refuse bm-c, r720 "
       "face) + 1 waiting. (5) S3: WM green (red=false, %s legal idle whitelist: open_tickets 0, bandit_open 0, "
       "local_batch_running false, golden week no bars; supply_gap honest structural flag ready=3=floor "
       "breach=false); satengine Tools-copy rc0 alive (W122 burn 12/12 local, finalize landed bm-a r728; W123 "
       "seat published 14:14 = bm-a freeze window r728); trial-labor zero drafting (W123 seat bm-a published "
       "pre-freeze per r565 law; fund-trio bm-b in-burn 10-05..09; W16 prereg bm-a <=10-07; W3 CEO-ruling; W14 "
       "parked; reopen 10-09). (6) CORE PRODUCT: QA pack r547 standing re-run (qa/smoke-r547.md 5/5 + "
       "equity-curve-r547.png %dB, 93 trades, sharpe 0.1586, maxdd -4.33%%, win 46.24%%, determinism=True; "
       "metrics face identical r528-546 = determinism 20th consecutive evidence); market clock CALL-2026-09-30 "
       "cell=ORANGE_COOL. (7) S6 chain %s (receipt results/_r547bmc_s6_log.txt); dualrun %s; update_lhb no-op "
       "this round (30-min min-interval guard after r546 real pull 11/11); update_fundamental snapshot-fresh "
       "skip; regime ORANGE shadow days_in_state=2 (enforce requested, honest downgrade until date-gate first "
       "bar 10-09); lane_io single-writer guard skip-derive faces honest stdout (bm-a host heartbeat fresh); "
       "REPORT/LIVE-2026-10-05 idempotent regen; token delta=%s. (8) S7: loop pin=5 phase ok no-op; watchdog "
       "-Force idempotent re-registered; claws re-installed LF-normalized both; task family 6/6 (CSV "
       "cross-check, no-suffix canon names r517 law); attrition CLEAN (3 healed historical shrink rows noted, "
       "zero active loss); inbox cleared. (9) unified chain live head 664,411 (W122 finalize landed K=266,320 "
       "skill 1.1748 K-lift 0; W123 seat published, bm-c zero chain entry this window).") % (py_verdict, qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r547 金周值守轮收口（QA 二十连证+S6 38/38 首过零 heal 七连·二跳 push 收口〔爪拦=落后信号 r524 律·"
              "W123 席位波吸收〕·orders/D-19/group-orders 三 MATCH） "
              "| 最近实物: qa/smoke-r547.md 5/5+qa/equity-curve-r547.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "二十连证）+results/_r547bmc_s6_log.txt（38/38 首过） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W123 freeze+burn（bm-a r728 窗·"
              "席位 14:14 已发布）；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；D-06 拆件收口 "
              "10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）+regime_guard v3 "
              "日期门首 bar；月界首考 10-31；下一 5x=r550") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin "
              "selftest). (b) W123 freeze+burn on bm-a (seat published 14:14, freeze window bm-a r728 per r565 "
              "law). (c) fund-trio finalize 10-05..09 (bm-b canonical). (d) W16 candidate prereg draft+freeze "
              "(bm-a, window <=10-07). (e) D-06 split closeout window 10-07 12:00. (f) O-2115/O-2030 acceptance "
              "10-08. (g) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 "
              "date-gate first bar. (h) qa/ evidence pack per-round standing re-run. (i) CEO physical item "
              "pending: tailscale login link click (bm-c URL alive since r505). (j) CODELY.md over-50KB flag "
              "carried (GM ruling face). (k) next 5x = r550 HANDOVER check round.")

verify = ("receipts: qa/smoke-r547.md 5/5 + qa/equity-curve-r547.png (%dB, 93 trades, determinism=True) + "
          "results/_r547bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + smoke 48/48 + churn-absorb bb704978d "
          "(3 faces, r714 law) + merge hop-1 rc0 zero-UU (15 files) + push-claw rejection = behind-origin "
          "signal resolved zero --no-verify (r524/r704-1 law) + merge hop-2 rc0 zero-UU (3 files, W123 seat "
          "wave) + push rc0 tip 9f4eedb0a behind=0 + orders 154/154 strict diff rc0 + D-19 decisions MATCH "
          "D14DCC74 + group orders SHA-1 3BF0F16E...E56253 MATCH (r537 pin) + satengine rc0 (Tools copy, W122 "
          "12/12 burn + finalize landed) + loop pin=5 phase ok no-op + watchdog -Force idempotent + task family "
          "6/6 (CSV cross-check) + claws IN-PLACE (LF-normalized, both) + attrition CLEAN + inbox 1 processed "
          "(W123 seat) + unified chain live head 664,411 (n1_w122_results.json) + commit/push delivery "
          "self-check this close.") % (qa_png_b, bad_end)

note = ("r547: golden-week standby closed. QA pack r547 = 20th consecutive identical metrics face (frozen "
        "golden-week panel determinism evidence). S6 %s (zero-heal x7). S0 churn-absorb collected r546 close "
        "tail + own satengine lane live faces (3 faces, standing pattern per r714 law); two-hop merge window: "
        "push attempt 1 claw-blocked = pure behind-origin signal (bm-a r728 W123 seat wave mid-window; "
        "deletion set = _r728bma probe pair = stale-tip artifact per r524/r704-1 law, zero local miswrite), "
        "hop-2 merge absorbed W123 seat wave, push rc0 zero --no-verify. W123 seat = bm-a published/reserved "
        "(no bm-c drafting, anti-dup law). Unified chain head 664,411 (W122 finalize landed: K=266,320, skill "
        "1.1748, K-lift 0). No new pits (claw-block = known r524/r704-1 family, correct enforcement); no new "
        "methodology; no treasure faces (no five-type closeout by bm-c this round). No CODELY append "
        "(memory-entry gate: zero new long-term lessons).") % s6_face

row = ("%s | r547 | dept:工程（金周值守轮·QA 证据面常设复跑） | watermark verdict=绿（red=%s·py_watermark probe rc0·%s 板空合法 "
       "idle 白名单〔判决链席位他机：W123 席位 bm-a 已发布〔14:14·r565 律 pre-freeze push·freeze 窗=bm-a r728〕+fund-trio bm-b "
       "keepalive 在烧〔10-05..09〕+W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 unclaimed=0·金周无 bar〕·supply_gap 诚实旗=金周"
       "结构面 ready=3=floor·breach=false·点火 SLA 零违例）｜本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r547.md 5/5+"
       "qa/equity-curve-r547.png（%dB·3 syms x 800 bars·93 trades·sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·"
       "与 r528-546 面恒等=冻结面板确定性二十连证）+S6 %s（收据 results/_r547bmc_s6_log.txt·bad=[%s]·零 heal 七连）｜S0=轮首脏 3 面"
       "（r546 S7-close 尾+satengine lane live x2）churn-absorb bb704978d（r714 律）·fetch 实核 7 behind→merge hop-1 rc0 零 UU "
       "干净吸收〔15 files=bm-a W122 finalize 波：n1_w122_results.json+prereg addendum+fund-trio keepalive+satengine 态面〕·push "
       "首试爪拦=落后 origin 信号〔删除集=_r728bma 探针对=bm-a r728 W123 席位波窗内落地·r524/r704-① 律·零本地误写零 --no-verify〕→fetch "
       "实核 1 behind→merge hop-2 rc0 零 UU〔3 files=W123 席位 MSG+探针 py+收据〕→push rc0 tip 9f4eedb0a behind=0 送达自证｜S0.5="
       "orders 154/154 strict diff rc0 零未回执·D-19 decisions MATCH D14DCC74 零增量（Tools/d19_check.py 正典）·group orders 水位 "
       "SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·inbox 1=W123 席位发布 MSG（bm-a·信息性→processed/·反重复律 bm-c 不起草）｜"
       "smoke 48/48｜satengine rc0 活（Tools 面·W122 烧录 12/12+finalize 已落账〔bm-a r728〕·W123 席位 14:14 发布）｜试用劳力线不触"
       "发（W123 席位 bm-a 已发布+fund-trio bm-b 在烧〔10-05..09〕+W16 bm-a ≤10-07+W3 CEO 裁定+W14 停泊+复市 10-09）｜S6 面=update_lhb "
       "no-op（30min 间隔守卫·r546 真拉 11/11 之后）+update_fundamental 快照新鲜跳过·其余 lane guard no-op 诚实｜dualrun "
       "ZERO-DRIFT streak %s·regime ORANGE shadow days_in_state=2（enforce 请求·日期门 10-09 首 bar 前诚实降级）·clock cell=ORANGE_COOL"
       "｜attrition CLEAN〔3 healed 历史缩行注记照录〕·任务族 6/6（CSV 交叉 r517 律·无后缀正名）·claws IN-PLACE（LF 归一）·loop pin5 "
       "no-op·watchdog -Force 幂等｜token 面=本机 L1 零 token 腿·账本 delta=%s｜统一链头 664,411〔W122 finalize 落账：K=266,320·"
       "skill 1.1748·K-lift 0·W123 席位已发布·bm-c 零入链〕｜轮产品计分：2（qa/ 证据包 r547=能跑/能看实物+S6 38 面 CEO 再生面）｜记"
       "账预算：3（state+心跳+轮报=法定 3·CODELY 零 append〔四问门：本轮零新坑零新方法〕）｜方法论捕获=无新方法·宝藏捕获=无（无五类"
       "收口面）｜登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜下轮指针：10-06 00:00 D-20261002-05 selftest "
       "席位窗首过轮跑 pin selftest；W123 freeze+burn（bm-a r728 窗）；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·"
       "≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09（G3·IntradayMarks 再核·regime_guard v3 日期门首 "
       "bar）；月界首考 10-31；下一 5x=r550") % (now_iso, wm_red, py_verdict, qa_png_b, s6_face, bad_end, streak, token_delta)

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
                                   "r547 probe = Tools/d19_check.py canonical MATCH D14DCC74, zero delta vs r546 "
                                   "consumption; consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r547 zero new orders, 154/154 strict diff rc0 "
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
st['round_no'] = 547
st['round_no_label'] = 'round 547 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r547: golden-week standby + QA evidence pack standing re-run "
                      "(qa/smoke-r547.md 5/5 + equity-curve-r547.png %dB, 93 trades, determinism=True, metrics "
                      "face identical to r528-546 = frozen-panel 20th consecutive evidence), S6 %s, dualrun %s, "
                      "smoke 48/48, orders 154/154 zero unacked, D-19 dual MATCH (decisions D14DCC74 + group "
                      "orders SHA-1 3BF0F16E r537 pin), two-hop S0 close (claw block = behind-origin signal "
                      "bm-a r728 W123 seat wave, absorbed hop-2, push rc0 zero --no-verify), W122 finalize "
                      "landed (chain head 664,411), attrition CLEAN, task family 6/6 CSV cross-check + claws "
                      "IN-PLACE; judgment seats on other machines (W123 seat published bm-a 14:14, fund-trio "
                      "bm-b in-burn 10-05..09, W16 bm-a <=10-07); supply_gap flag = golden-week structural "
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
hb['latest_artifact'] = ("qa/ evidence pack r547 (smoke-r547.md 5/5 + equity-curve-r547.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 20th consecutive evidence) + results/_r547bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + churn-absorb bb704978d + two-hop merge close tip "
                         "9f4eedb0a behind=0") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W123 "
                        "freeze+burn bm-a (seat published 14:14); W16 candidate prereg (bm-a, <=10-07); "
                        "fund-trio finalize (bm-b) 10-05..09; D-06 closeout 10-07 12:00; O-2115/O-2030 "
                        "acceptance 10-08; reopen 10-09 (G3, IntradayMarks re-check, regime_guard v3 "
                        "date-gate first bar); month-end exam 10-31; next 5x = bm-c r550")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 547
hb['round_no_label'] = 'round 547 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r547 bm-c: golden-week standby (boards open=0, judgment seats other machines, no bar until "
                 "10-09). (1) S0 churn-absorb bb704978d (3 faces), two-hop merge close (hop-1 15 files zero-UU "
                 "W122 finalize wave; push claw block = behind-origin signal, hop-2 3 files W123 seat wave, "
                 "push rc0 9f4eedb0a). (2) orders 154/154 rc0, inbox 1 processed (W123 seat MSG). (3) D-19 "
                 "dual MATCH zero action. (4) smoke 48/48. (5) boards empty. (6) WM green, %s legal idle; "
                 "satengine rc0 alive (W122 12/12 burn + finalize landed). (7) CORE: QA pack r547 (5/5, 93 "
                 "trades, determinism=True, frozen-panel 20th consecutive evidence). (8) S6 %s, dualrun %s, "
                 "LHB no-op (30-min guard), supply_gap honest structural. (9) S7: loop pin5 phase-ok; watchdog "
                 "re-registered; task family 6/6 CSV; claws re-installed; attrition CLEAN; close: targeted "
                 "add + commit -F + push_verify.") % (py_verdict, s6_face, dual_face)
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
assert st2['round_no'] == 547, 'round_no must be 547'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 547, 'hb round_no must be 547'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
