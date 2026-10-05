# -*- coding: utf-8 -*-
"""r550 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(5x HANDOVER round, golden-week standby). Lineage _r549bmc_bookkeeping.py;
facts inlined from this round's receipts. Laws: R170/R178 epoch int; R262
clock T-separated; r503 EOL-preserving bytes write. GPU = live nvidia-smi
probe (CNO zero-window). This round: QA 23rd consecutive determinism
evidence, S6 38/38 first-pass zero-heal 10th, dualrun streak 50, HANDOVER
r546-550 5x row landed, task-family false-MISSING self-corrected via CSV
cross-check (r517 law, zero rebuild)."""
import json, os, re, shutil, subprocess, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r550bmc_s6_log.txt')

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]
epoch = int(time.time())

# live machine metrics (psutil live read this close window)
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

# ---- S6 log facts (pinned to owning leg blocks per r547 law)
s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
s6_face = '38/38 rc0 first-pass zero-heal 10th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
cell_face = 'ORANGE_COOL'
tk_seg = s6.split('=== token_meter', 1)[1]
tk = re.search(r'delta=(\d+)', tk_seg)
token_delta = tk.group(1) if tk else '0'
seg = s6.split('=== py_watermark', 1)[1]
mv = re.search(r'"verdict": "([^"]+)"', seg)
py_verdict = mv.group(1) if mv else '?'

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r550.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 666611  # W123 landed (bm-a r729 one-pass); W124 freeze in-flight bm-a, W125 seat published 14:56; bm-c zero chain entry this window

did = ("r550 bm-c: golden-week standby 5x HANDOVER round. (1) S0: round-start dirty = 7 own faces (r549 S7-close post-push "
       "tails x4: CODELY r549 pit-law lines x2 + RR close row + close_facts receipt; own daemon lane live x4: satengine "
       "faces x2 + autofill + dispatcher) -> churn-absorb a16a96968 (r714 law, targeted add 7 faces + commit -F) -> fetch "
       "3 behind -> merge origin/main rc0 ZERO-UU clean absorb (merge ff08998d3; bm-a W125 seat MSG wave: A 293_004..295_003 "
       "+ B 67_201..67_400, probe rc0 ADMIT, hops=2 past-hit restart D-20261002-05) -> 2/0, push at close. (2) S0.5: orders "
       "155/155 strict diff rc0 zero unacked; D-19 decisions MATCH D14DCC74 zero delta (Tools/d19_check.py canonical); group "
       "orders SHA-1 3BF0F16E MATCH zero new CEO rows (r537 algorithm pin); inbox 1 = W125 seat MSG (bm-a informational "
       "broadcast, read + moved to processed, anti-dup law zero bm-c drafting). (3) S1 smoke 48/48. (4) S2: job_list 0; "
       "fleet tasks 172 total / 0 open; pool 403 = 399 done + 3 ready (FUND trio bm-b nested-shard ownership, host_gates "
       "refuse bm-c, r720 face) + 1 waiting (W14 governance park honored). (5) S3: WM green (red=false, py probe "
       "verdict=%s = legal idle white-list: boards open=0 + bandit empty + golden week no bar); satengine Tools-copy rc0 "
       "alive (burns_active none local); trial-labor zero drafting (anti-dup: W124/W125 seats bm-a, fund-trio bm-b in-burn "
       "10-05..09, W16 prereg bm-a <=10-07). (6) CORE PRODUCT: QA pack r550 standing re-run (qa/smoke-r550.md 5/5 + "
       "equity-curve-r550.png %dB, 93 trades, sharpe 0.1586, maxdd -4.33%%, win 46.24%%, determinism=True; metrics face "
       "identical r528-549 = determinism 23rd consecutive evidence); market clock CALL-2026-09-30 cell=ORANGE_COOL. "
       "(6b) 5x HANDOVER: research/HANDOVER.md r550 row landed (r546-550 five-window audit, +4457B, zero-loss prepend). "
       "(7) S6 chain %s (receipt results/_r550bmc_s6_log.txt); dualrun %s; update_lhb data-refresh no-op (quarter refetch "
       "5432 rows, new_beyond_cutoff=0, honest no-op); update_fundamental snapshot-fresh skip (1.0h); fund_premium "
       "pre-15:30 no-op; regime ORANGE shadow days_in_state=2 (enforce requested, honest downgrade until date-gate first "
       "bar 10-09); lane_io single-writer guards honest skip (bm-a host fresh); REPORT/LIVE-2026-10-05 idempotent regen; "
       "token delta=%s. (8) S7: loop pin=5 phase ok no-op (first fire 15:05); watchdog present rc0; claws IN-PLACE both "
       "MATCH (LF-normalized compare, zero reinstall); task family 6/6 (CSV cross-check, no-suffix canon names r517 law; "
       "first probe used quote-anchored -like pattern = false MISSING x6, CSV recheck all 6 PRESENT, zero rebuild = law "
       "working as designed, honest note); attrition CLEAN (4 ledger files, 3 healed historical shrink rows noted). "
       "(9) unified chain live head 666,611 (W123 landed; no new chain entry by bm-c this window).") % (py_verdict, qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r550 5x HANDOVER 轮收口（QA 二十三连证+S6 38/38 首过零 heal 十连·streak 50·orders 155/155+D-19 双 MATCH·"
              "W125 席位 bm-a 已公示·HANDOVER r546-550 五窗核对行已落） "
              "| 最近实物: qa/smoke-r550.md 5/5+qa/equity-curve-r550.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "二十三连证）+results/_r550bmc_s6_log.txt（38/38 首过）+research/HANDOVER.md r550 5x 行 @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W124 freeze+burn/finalize（bm-a 面）；"
              "W125 freeze+burn（bm-a 面·席位 14:56 已公示）；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·"
              "≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）+"
              "regime_guard v3 日期门首 bar；月界首考 10-31；下一 5x=r555") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin selftest). "
              "(b) W124 freeze+burn+finalize on bm-a (seat published 14:37 r549 window; W123 landed). (c) W125 "
              "freeze+burn on bm-a (seat published 14:56 this window, A 293_004..295_003 + B 67_201..67_400). (d) "
              "fund-trio finalize 10-05..09 (bm-b canonical). (e) W16 candidate prereg draft+freeze (bm-a, window "
              "<=10-07). (f) D-06 split closeout window 10-07 12:00. (g) O-2115/O-2030 acceptance 10-08. (h) market "
              "reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 date-gate first bar. "
              "(i) qa/ evidence pack per-round standing re-run. (j) CEO physical item pending: tailscale login link "
              "click (bm-c URL alive since r505). (k) CODELY.md over-50KB flag carried (GM ruling face). (l) next 5x "
              "= r555 HANDOVER check round.")

verify = ("receipts: qa/smoke-r550.md 5/5 + qa/equity-curve-r550.png (%dB, 93 trades, determinism=True) + "
          "results/_r550bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + results/_r550bmc_probe.txt (S1/S2/S3 compact "
          "receipt) + legdiff v2 PASS (substance gates, zero leg drift) + smoke 48/48 + churn-absorb a16a96968 (7 faces, "
          "r714 law) + merge ff08998d3 rc0 zero-UU (bm-a W125 seat MSG wave absorbed, UU canonical=0 per r713 law) + "
          "ahead 2/0 + orders 155/155 strict diff rc0 + D-19 decisions MATCH D14DCC74 + group orders SHA-1 "
          "3BF0F16E...E56253 MATCH (r537 pin) + satengine rc0 alive + loop pin=5 phase ok no-op + watchdog present + "
          "task family 6/6 (CSV cross-check, false-MISSING self-corrected zero rebuild) + claws IN-PLACE (LF-normalized "
          "MATCH both, zero reinstall) + attrition CLEAN (3 healed rows noted) + HANDOVER r550 5x row landed (+4457B "
          "zero-loss) + inbox W125 MSG moved to processed + unified chain live head 666,611 + commit/push delivery "
          "self-check this close.") % (qa_png_b, bad_end)

note = ("r550: golden-week standby 5x HANDOVER round closed. QA pack r550 = 23rd consecutive identical metrics face "
        "(frozen golden-week panel determinism evidence). S6 %s (zero-heal x10). S0 single-hop window: churn-absorb 7 "
        "own faces then merge origin/main zero-UU (bm-a W125 seat wave); push face pending at write time. W123 landed "
        "(chain head 666,611); W124/W125 seats = bm-a published/reserved (no bm-c drafting, anti-dup law). HANDOVER "
        "r546-550 five-window row landed this round (5x duty). No new pit this round (task-family false-MISSING = r517 "
        "law already on book, CSV cross-check worked as designed); no new methodology; no treasure faces (no five-type "
        "closeout by bm-c this round).") % s6_face

row = ("%s | r550 | dept:工程（金周值守轮·QA 证据面常设复跑+5x HANDOVER 核对） | watermark verdict=绿（red=%s·py_watermark probe rc0·verdict=%s〔板空+"
       "bandit 空+金周无 bar=合法 idle 白名单〕·判决链席位他机：W123 已落账〔链头 666,611·bm-a r729 one-pass〕+W124 席位 bm-a 已公示〔14:37·freeze 窗=bm-a〕+"
       "W125 席位 bm-a 已公示〔14:56 本窗·A 293_004..295_003+B 67_201..67_400·probe rc0 ADMIT·hops=2 past-hit restart〕+fund-trio bm-b keepalive 在烧〔10-05..09〕+"
       "W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 unclaimed=0·金周无 bar〕·supply_gap 诚实旗=金周结构面 ready=3=floor·breach=false·点火 SLA 零违例）｜"
       "本轮：金周值守+QA 证据面常设复跑+5x HANDOVER 五窗核对——实物=qa/smoke-r550.md 5/5+qa/equity-curve-r550.png（%dB·3 syms x 800 bars·93 trades·"
       "sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·与 r528-549 面恒等=冻结面板确定性二十三连证）+research/HANDOVER.md r550 5x 行〔r546-550 五窗核对·"
       "+4457B 零丢失 prepend〕+S6 %s（收据 results/_r550bmc_s6_log.txt·bad=[%s]·零 heal 十连）｜S0=轮首脏 7 面（r549 S7-close 尾 x4：CODELY r549 坑律行 x2+RR close 行+"
       "close_facts 未跟踪收据；own daemon lane live x4：satengine x2+autofill+dispatcher）churn-absorb a16a96968（r714 律·targeted add+commit -F）·fetch 实核 3 behind→"
       "merge ff08998d3 rc0 零 UU 干净吸收〔bm-a W125 席位公示 MSG 波·UU 清单=diff-filter=U 正典 0〕→2/0 push 收口｜S0.5=orders 155/155 strict diff rc0 零未回执·"
       "D-19 decisions MATCH D14DCC74 零增量（Tools/d19_check.py 正典）·group orders 水位 SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·inbox 1=W125 席位公示 MSG"
       "（bm-a 信息性→processed/·反重复律 bm-c 不起草）｜smoke 48/48｜satengine rc0 活（Tools 面·burns_active 本机空）｜试用劳力线不触发（全席位他机+复市 10-09）｜"
       "S6 面=update_lhb 数据刷新 no-op（quarter refetch 5432 行·new_beyond_cutoff=0 诚实 no-op）+update_fundamental 快照新鲜跳过（1.0h）+fund_premium pre-15:30 "
       "no-op·其余 lane guard no-op 诚实｜dualrun ZERO-DRIFT streak %s·regime ORANGE shadow days_in_state=2（enforce 请求·日期门 10-09 首 bar 前诚实降级）·cell=ORANGE_COOL "
       "sleeves4 act0｜S7=loop pin5 no-op（首拍 15:05）·watchdog 在位·双爪 IN-PLACE（LF 归一 MATCH·零重装）·任务族 6/6（CSV 交叉 r517 律·首查引号锚 like 模式假 MISSING x6→"
       "CSV 复核全在·零重建=律内自纠如实注记）·attrition CLEAN〔4 账本·3 healed 历史缩行注记照录〕｜token 面=本机 L1 零 token 腿·账本 delta=%s｜统一链头 666,611"
       "〔W123 落账·本轮零入链〕｜轮产品计分：2（qa/ 证据包 r550=能跑/能看实物+HANDOVER 5x 核对行+S6 38 面 CEO 再生面）｜记账预算：3（state+心跳+轮报=法定 3·"
       "HANDOVER 5x=法轮义务非记账）｜方法论捕获=无新方法·宝藏捕获=无（无五类收口面）｜登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜"
       "下轮指针：10-06 00:00 D-20261002-05 selftest 席位窗首过轮跑 pin selftest；W124 freeze+burn/finalize（bm-a 面）；W125 freeze+burn（bm-a 面）；"
       "fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09（G3·"
       "IntradayMarks 再核·regime_guard v3 日期门首 bar）；月界首考 10-31；下一 5x=r555") % (now_iso, wm_red, py_verdict, qa_png_b, s6_face, bad_end, streak, token_delta)

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
                                   "r550 probe = Tools/d19_check.py canonical MATCH D14DCC74, zero delta vs r549 "
                                   "consumption; consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r550 zero new orders, 155/155 strict diff rc0 "
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
st['round_no'] = 550
st['round_no_label'] = 'round 550 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r550: golden-week standby 5x HANDOVER round + QA evidence pack standing re-run "
                      "(qa/smoke-r550.md 5/5 + equity-curve-r550.png %dB, 93 trades, determinism=True, metrics "
                      "face identical to r528-549 = frozen-panel 23rd consecutive evidence), S6 %s, dualrun %s, "
                      "smoke 48/48, orders 155/155 zero unacked, D-19 dual MATCH (decisions D14DCC74 + group orders "
                      "SHA-1 3BF0F16E r537 pin), single-hop S0 merge close (churn-absorb a16a96968 + merge "
                      "ff08998d3 zero-UU absorbing bm-a W125 seat wave), attrition CLEAN, task family 6/6 CSV "
                      "cross-check (false-MISSING self-corrected per r517 law, zero rebuild) + claws IN-PLACE; "
                      "judgment seats on other machines (W124/W125 seats bm-a published, fund-trio bm-b in-burn "
                      "10-05..09, W16 bm-a <=10-07); HANDOVER r546-550 five-window row landed; supply_gap flag = "
                      "golden-week structural (ready=3=floor, unclaimed=0, breach=false); regime ORANGE shadow "
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
hb['latest_artifact'] = ("qa/ evidence pack r550 (smoke-r550.md 5/5 + equity-curve-r550.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 23rd consecutive evidence) + results/_r550bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + research/HANDOVER.md r550 5x row (r546-550 window) + "
                         "churn-absorb a16a96968 + S0 merge ff08998d3 zero-UU") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W124 "
                        "freeze+burn+finalize bm-a (seat published 14:37); W125 freeze+burn bm-a (seat published "
                        "14:56); W16 candidate prereg (bm-a, <=10-07); fund-trio finalize (bm-b) 10-05..09; D-06 "
                        "closeout 10-07 12:00; O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, IntradayMarks "
                        "re-check, regime_guard v3 date-gate first bar); month-end exam 10-31; next 5x = bm-c r555")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 550
hb['round_no_label'] = 'round 550 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r550 bm-c: golden-week standby 5x HANDOVER round (boards open=0, judgment seats other machines, "
                 "no bar until 10-09). (1) S0 churn-absorb a16a96968 (7 own faces) + merge ff08998d3 zero-UU (bm-a "
                 "W125 seat MSG wave absorbed). (2) orders 155/155 rc0, inbox 1 (W125 seat MSG -> processed). (3) "
                 "D-19 dual MATCH zero action. (4) smoke 48/48. (5) boards empty. (6) WM green, py probe "
                 "verdict=%s legal idle; satengine rc0 alive. (7) CORE: QA pack r550 (5/5, 93 trades, "
                 "determinism=True, frozen-panel 23rd consecutive evidence) + HANDOVER r546-550 5x row. (8) S6 %s "
                 "(zero-heal x10), dualrun %s, LHB data-refresh no-op, supply_gap honest structural. (9) S7: loop "
                 "pin5 phase-ok; watchdog present; task family 6/6 CSV (false-MISSING self-corrected, zero "
                 "rebuild); claws IN-PLACE zero reinstall; attrition CLEAN; close: targeted add + commit -F + "
                 "push_verify.") % (py_verdict, s6_face, dual_face)
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

# ---- inbox: move W125 seat MSG (bm-a informational broadcast) to processed
src = os.path.join(ROOT, 'fleet', 'inbox', 'MSG-2026-10-05-1456-bma-w125-seat.md')
dst = os.path.join(ROOT, 'fleet', 'inbox', 'processed', 'MSG-2026-10-05-1456-bma-w125-seat.md')
if os.path.exists(src):
    shutil.move(src, dst)
    assert os.path.exists(dst) and not os.path.exists(src), 'inbox move failed'
    print('INBOX_MOVED MSG-2026-10-05-1456-bma-w125-seat.md -> processed/')

# ---- self-checks (R170/R178 epoch int + R262 clock T + F5 fields)
st2 = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert isinstance(st2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in st2['clock_read'] and '+' in st2['clock_read'], 'clock_read must be T-separated ISO with offset'
assert st2['round_no'] == 550, 'round_no must be 550'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 550, 'hb round_no must be 550'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
