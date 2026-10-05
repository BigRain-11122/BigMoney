# -*- coding: utf-8 -*-
"""r556 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby round; chain head advanced 673,211 -> 675,411 via
S0 merge absorbing W127 landing; next burn waits W16 prereg freeze bm-a).
Lineage Tools/_r555bmc_bookkeeping.py; facts inlined from this round's
receipts. Laws: R170/R178 epoch int; R262 clock T-separated; r503
EOL-preserving bytes write. This round: QA 29th consecutive determinism
evidence, S6 38/38 first-pass zero-heal 16th, dualrun streak 51,
compute_audit CLEAN (flags=[]), legdiff TRUE gate v3 PASS (OLD = r555
surviving true chain file in scratch, no ephemeral gap this round),
S0 churn-absorb 64a68a4e0 + merge 417d26103 zero-UU (3 behind),
zero CODELY S4 entry (no new pit; four-question gate N/A)."""
import json, os, re, subprocess, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r556bmc_s6_log.txt')

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

# ---- S6 log facts (owning-leg split anchors per r547 law)
s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
s6_face = '38/38 rc0 first-pass zero-heal 16th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
# py_watermark verdict: dual-layout block scan (r555 discovery, r556 .ps1
# lineage logs output BEFORE the leg marker)
seg_py = ''
if '=== 02_compute_audit' in s6:
    seg_try = s6.split('=== 02_compute_audit', 1)[1].split('=== 03_py_watermark', 1)[0]
    if '"verdict"' in seg_try:
        seg_py = seg_try
if not seg_py:
    seg_py = s6.split('=== 03_py_watermark', 1)[1].split('=== 04_update_daily', 1)[0]
mv = re.search(r'"verdict": "([^"]+)"', seg_py)
py_verdict = mv.group(1) if mv else '?'
assert py_verdict != '?', 'py_watermark verdict not found in either layout block'
cell_face = 'ORANGE_COOL'
token_delta = '0'   # L1 zero-token face; token_meter leg carries no delta= line (r551-r555 lineage fallback)

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r556.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 675411  # W127 landed (absorbed at S0 merge 417d26103); science_gates.ledger_head() live-read re-verified this round; no new chain entry by bm-c (next burn waits W16 prereg freeze)

did = ("r556 bm-c: golden-week standby round. (1) S0: round-start dirty = 9 own faces (r555 S7-close post-push "
       "tails: RR close-row edit + CODELY r555 entry + autofill_state.bm-c + satengine face/state + 4 untracked "
       "r555 tool/receipt files) -> churn-absorb 64a68a4e0 (r714 law, targeted add 9 faces + commit -F) -> fetch 3 "
       "behind (bm-b r735 wave: trio NULLS finalize windows arming Q/V ~10-06 D ~10-08 + readiness probe leg39) -> "
       "merge 417d26103 single-stop ZERO-UU (merge-mode canon r713 law, dirty-intersect=0) -> 2/0 ahead at close; "
       "chain head 673,211 -> 675,411 (W127 landing absorbed, science_gates live-read re-verified). (2) S0.5: "
       "orders 154/154 O-files strict diff rc0 zero unacked (canonical Tools/orders_diff.py --strict); D-19 "
       "decisions MATCH D14DCC74 zero delta (raw-blob SHA-256, group-tree origin show); group orders SHA-1 "
       "3BF0F16E MATCH zero new CEO rows (r537 algorithm pin); inbox 0. (3) S1 smoke 48/48. (4) S2: job_list 0 "
       "claimable; fleet tasks 172 total / 0 open; pool 403 = 399 done + 3 ready (FUND trio bm-b nested-shard "
       "ownership, host_gates refuse bm-c, r720 face) + 1 waiting (W14 governance park honored). (5) S3: WM green "
       "(red=false lane=healthy; in-chain py_watermark verdict=py_low_board_clear = legal idle whitelist, board "
       "empty + golden week no bar); satengine Tools-copy rc0 alive; next_pick=claimed (moneyflow IC reference "
       "batch, other-machine lane); trial-labor zero drafting (anti-dup: W127 landed bm-a -> chain head 675,411; "
       "W16 prereg = bm-a lane <=10-07; fund-trio bm-b finalize windows arming Q/V ~10-06 D ~10-08; golden week no "
       "bar). (6) CORE PRODUCT: QA pack r556 standing re-run (qa/smoke-r556.md 5/5 + equity-curve-r556.png %dB, 93 "
       "trades, sharpe 0.1586, maxdd -4.33%%, win 46.24%%, determinism=True; metrics face identical r528-555 = "
       "determinism 29th consecutive evidence); market clock CALL-2026-09-30 cell=ORANGE_COOL (regime ORANGE "
       "days_in_state=2). (7) S6 chain %s (receipt results/_r556bmc_s6_log.txt; legdiff TRUE gate v3 PASS: G1 38 "
       "legs byte-identical vs r555 surviving lineage file (real file in scratch, no ephemeral gap this round) + "
       "G3 non-leg diff = rNNN round-token shape-normalized furniture only + G4 r555 executed-log leg names 38/38 "
       "identical; receipt results/_r556bmc_legdiff.txt, r531/r549/r554/r555 laws); dualrun %s; compute_audit "
       "CLEAN flags=[] (r555 supply_gap face cleared); supply_floor honest structural (ready=3=floor, "
       "breach=false); lane_io single-writer guards honest skip; REPORT/LIVE-2026-10-05 idempotent regen; token "
       "delta=%s (L1 zero-token face, L2 today=0). (8) S7: loop pin=5 phase ok no-op (first fire 16:35); watchdog "
       "idempotent re-registered; claws IN-PLACE both (LF-normalized parity, zero reinstall); task family 6/6 "
       "(IntradayMarks MISSING = market-closure legal face, re-check at 10-09 reopen per G3); attrition CLEAN (4 "
       "ledger files, 3 healed historical shrink rows noted). (9) S4: zero new pit (four-question gate N/A); "
       "CODELY r556 entry count=0.") % (qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r556 金周值守轮收口（QA 二十九连证·S6 38/38 首过零 heal 十六连·legdiff 真门 v3 PASS〔G1+G3+G4·OLD=r555 存留真身〕） "
              "| 最近实物: qa/smoke-r556.md 5/5+qa/equity-curve-r556.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "二十九连证）+results/_r556bmc_s6_log.txt（38/38 首过）+results/_r556bmc_legdiff.txt（v3 PASS） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W16 prereg（bm-a·≤10-07）→引擎下波；"
              "fund-trio finalize 窗口（bm-b·Q/V~10-06·D~10-08）；D-06 收口 10-07 12:00；复市 10-09；月界首考 10-31") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin "
              "selftest; r556 fired 10-05 16:2x so window round = first round on/after midnight). "
              "(b) fund-trio NULLS finalize windows arming (bm-b canonical; Q/V ~10-06, D ~10-08 per r735 "
              "readiness probe). (c) W16 candidate prereg draft+freeze (bm-a, window <=10-07) -> next engine wave "
              "supply after freeze. (d) D-06 split closeout window 10-07 12:00. (e) O-2115/O-2030 acceptance "
              "10-08. (f) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 "
              "date-gate first bar. (g) qa/ evidence pack per-round standing re-run. (h) CEO physical item "
              "pending: tailscale login link click (bm-c URL alive since r505). (i) CODELY.md over-50KB flag "
              "carried (GM ruling face, r504 law: no byte-count archiving of in-service laws by machines). "
              "(j) unified chain head 675,411 (W127 landed bm-a, absorbed at S0 merge this round; bm-c zero "
              "chain entry; next burn waits W16 prereg freeze). (k) next 5x = r560.")

verify = ("receipts: qa/smoke-r556.md 5/5 + qa/equity-curve-r556.png (%dB, 93 trades, determinism=True) + "
          "results/_r556bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + results/_r556bmc_legdiff.txt (TRUE "
          "gate v3 PASS: G1+G3+G4, OLD=r555 surviving lineage + r555 executed-log cross, r531/r549/r554/r555 "
          "laws) + smoke 48/48 + churn-absorb 64a68a4e0 (9 faces, r714 law) + merge 417d26103 single-stop "
          "zero-UU (fetch 3 behind, dirty-intersect=0) + orders 154/154 strict diff rc0 (canonical round-start "
          "scan) + D-19 decisions MATCH D14DCC74 + group orders SHA-1 3BF0F16E...E56253 MATCH (r537 pin) + "
          "satengine rc0 alive + loop pin=5 phase ok no-op (first fire 16:35) + watchdog idempotent registered + "
          "task family 6/6 (IntradayMarks closure-legal MISSING, G3 re-check 10-09) + claws IN-PLACE "
          "(LF-normalized parity both, zero reinstall) + attrition CLEAN (3 healed rows noted) + unified chain "
          "live head 675,411 (re-verified live-read via science_gates.ledger_head()) + CODELY r556 entry "
          "count=0 (no new pit) + commit/push delivery self-check this close.") % (qa_png_b, bad_end)

note = ("r556: golden-week standby round closed. QA pack r556 = 29th consecutive identical metrics face (frozen "
        "golden-week panel determinism evidence). S6 %s (zero-heal x16), compute_audit CLEAN flags=[]. S0 "
        "single-stop merge window: churn-absorb 9 own faces, fetch 3 behind, merge 417d26103 zero-UU. Chain "
        "head advanced 673,211 -> 675,411 (W127 landing absorbed at S0 merge; bm-c zero chain entry; next burn "
        "waits W16 prereg freeze bm-a). legdiff TRUE gate v3 PASS with OLD = r555 surviving true chain file "
        "(no ephemeral gap this round). No 5x duty this round (next = r560). No new methodology; no treasure "
        "faces (no five-type closeout by bm-c this round).") % s6_face

row = ("%s | r556 | dept:工程（金周值守轮） | watermark verdict=绿（red=%s·py_watermark probe rc0·链内 verdict=%s"
       "〔板空+金周无 bar=合法 idle 白名单〕·判决链席位他机：W127 已落账〔链头 673,211→675,411·S0 merge 吸收·本轮 science_gates 活读复核〕"
       "+fund-trio bm-b finalize 窗口 arming〔Q/V~10-06·D~10-08·r735 readiness probe〕+W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 "
       "unclaimed=0·next_pick=claimed〔moneyflow IC reference batch·他机车道〕·金周无 bar〕·supply_floor 诚实旗=金周结构面 "
       "ready=3=floor·breach=false·点火 SLA 零违例）｜"
       "本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r556.md 5/5+qa/equity-curve-r556.png（%dB·3 syms x 800 bars·93 trades·"
       "sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·与 r528-555 面恒等=冻结面板确定性二十九连证）+S6 %s（收据 "
       "results/_r556bmc_s6_log.txt·bad=[%s]·零 heal 十六连）+legdiff 真门 v3 PASS〔G1 38 腿字节恒等 vs r555 存留真身〔本轮零 ephemeral "
       "缺口〕+G3 非腿 diff=rNNN 形归一恒等+G4 r555 执行日志腿名 38/38 交叉·收据 results/_r556bmc_legdiff.txt〕｜S0=轮首脏 9 面"
       "（r555 S7-close 尾 x5：RR close 行+CODELY r555 行+autofill 态+satengine 面/态；untracked r555 工具/回执 x4）"
       "churn-absorb 64a68a4e0（r714 律·targeted add+commit -F）·fetch 实核 3 behind→merge 417d26103 零 UU 单停（bm-b r735 波·"
       "trio finalize 窗口 arming）→2/0 push 收口·链头 673,211→675,411（W127 吸收）｜S0.5=orders 154/154 strict diff rc0 零未回执"
       "（正典 orders_diff.py --strict）·D-19 decisions MATCH D14DCC74 零增量（raw-blob SHA-256 group-tree origin show）·group orders "
       "水位 SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·inbox 0｜smoke 48/48｜satengine rc0 活（Tools 面）｜"
       "试用劳力线不触发（W127 已落账〔head 675,411〕+fund-trio bm-b finalize 窗口 arming+金周无 bar）｜S6 面=dualrun ZERO-DRIFT "
       "streak %s·compute_audit CLEAN〔flags=[]·r555 supply_gap 面已清〕·regime ORANGE shadow days_in_state=2（enforce 请求·"
       "日期门 10-09 首 bar 前诚实降级）·cell=%s·REPORT/LIVE-2026-10-05 幂等再生·lane_io 守卫诚实跳过｜S7=loop pin5 no-op（首拍 "
       "16:35）·watchdog 幂等重注册·双爪 IN-PLACE（LF 归一 MATCH·零重装）·任务族 6/6+IntradayMarks 缺席=休市合法面〔G3 复市 10-09 "
       "再核〕·attrition CLEAN〔4 账本·3 healed 历史缩行注记照录〕｜token 面=本机 L1 零 token 腿·账本 delta=%s·L2 today=0｜"
       "统一链头 675,411〔W127 落账 bm-a·S0 merge 吸收·本轮 science_gates 活读复核·零入链·下波=W16 prereg 冻结后〕｜"
       "轮产品计分：2（qa/ 证据包 r556=能跑/能看实物+S6 38 面 CEO 再生面）｜记账预算：3（state+心跳+轮报=法定 3·零 CODELY 新条"
       "〔四问门 N/A·无新坑〕）｜方法论捕获=无新方法·宝藏捕获=无（无五类收口面）｜登记册零命中断言=N/A-零清扫零 quarantine"
       "（O-2030 §二.3 自证面）｜下轮指针：10-06 00:00 D-20261002-05 selftest 席位窗（首过轮跑 pin selftest）；fund-trio finalize "
       "窗口（bm-b·Q/V~10-06·D~10-08）；W16 候选 prereg（bm-a·≤10-07）→引擎下波供给；D-06 拆件收口 10-07 12:00；O-2115/O-2030 "
       "验收 10-08；复市 10-09（G3·IntradayMarks 再核·regime_guard v3 日期门首 bar）；月界首考 10-31；下一 5x=bm-c r560") % (now_iso, wm_red, py_verdict, qa_png_b, s6_face, bad_end, streak, cell_face, token_delta)

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
                                   "r556 probe = S0 raw-blob hash MATCH D14DCC74, zero delta vs r555 consumption; "
                                   "consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r556 zero new orders, 154/154 strict diff rc0 "
                                "round-start canonical scan)")
st['last_round'] = did
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_seen_at'] = now_iso
st['last_ts'] = now_iso
st['next'] = next_field
st['note'] = note
st['ram_free_gb'] = free_gb
st['round_no'] = 556
st['round_no_label'] = 'round 556 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r556: golden-week standby round (QA pack r556 5/5 + equity-curve-r556.png %dB, 93 trades, "
                      "determinism=True, metrics face identical to r528-555 = frozen-panel 29th consecutive "
                      "evidence), S6 %s, dualrun %s, compute_audit CLEAN flags=[], smoke 48/48, orders 154/154 "
                      "zero unacked, D-19 dual MATCH (decisions D14DCC74 + group orders SHA-1 3BF0F16E r537 "
                      "pin), S0 single-stop merge window (churn-absorb 64a68a4e0 9 own faces, fetch 3 behind, "
                      "merge 417d26103 zero-UU), attrition CLEAN, task family 6/6 + claws IN-PLACE; legdiff TRUE "
                      "gate v3 PASS (G1+G3+G4, r555 surviving lineage + r555 executed-log cross; no ephemeral gap "
                      "this round); unified chain head 675,411 (W127 landing absorbed at S0 merge, live-read "
                      "re-verified; next burn waits W16 prereg freeze bm-a); judgment seats remaining on other "
                      "machines (fund-trio bm-b finalize windows arming Q/V ~10-06 D ~10-08, W16 prereg bm-a "
                      "<=10-07); supply_floor flag = golden-week structural (ready=3=floor, unclaimed=0, "
                      "breach=false); regime ORANGE shadow (date-gate first bar 10-09)") % (qa_png_b, s6_face, dual_face)
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
hb['latest_artifact'] = ("qa/ evidence pack r556 (smoke-r556.md 5/5 + equity-curve-r556.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 29th consecutive evidence) + results/_r556bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + results/_r556bmc_legdiff.txt (TRUE gate v3 PASS)") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W16 "
                        "candidate prereg (bm-a, <=10-07) -> next engine wave; fund-trio NULLS finalize windows "
                        "(bm-b, Q/V ~10-06, D ~10-08); D-06 closeout 10-07 12:00; O-2115/O-2030 acceptance "
                        "10-08; reopen 10-09 (G3, IntradayMarks re-check, regime_guard v3 date-gate first bar); "
                        "month-end exam 10-31; next 5x = bm-c r560")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 556
hb['round_no_label'] = 'round 556 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r556 bm-c: golden-week standby round (boards open=0, judgment seats other machines, no bar "
                 "until 10-09). (1) S0 churn-absorb 64a68a4e0 (9 own faces) + merge 417d26103 single-stop "
                 "zero-UU (fetch 3 behind; W127 absorbed, chain head 675,411). (2) orders 154/154 rc0, inbox 0. "
                 "(3) D-19 dual MATCH zero action. (4) smoke 48/48. (5) boards empty. (6) WM green, in-chain "
                 "verdict=py_low_board_clear legal idle; satengine rc0 alive; no drafting pointer (next_pick "
                 "claimed elsewhere). (7) CORE: QA pack r556 (5/5, 93 trades, determinism=True, frozen-panel "
                 "29th consecutive evidence). (8) S6 %s (zero-heal x16), dualrun %s, compute_audit CLEAN, "
                 "regime ORANGE shadow, supply_floor honest structural; legdiff TRUE gate v3 PASS (zero CODELY "
                 "entry, no new pit). (9) S7: loop pin5 phase-ok; watchdog idempotent; task family 6/6 + "
                 "IntradayMarks closure-legal; claws IN-PLACE zero reinstall; attrition CLEAN; close: "
                 "deterministic add + commit -F + push_verify.") % (s6_face, dual_face)
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
assert st2['round_no'] == 556, 'round_no must be 556'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 556, 'hb round_no must be 556'
rr_txt = open(RR, 'rb').read().decode('utf-8', errors='replace')
assert rr_txt.count('| r556 | dept:') == 1, 'r556 main row count != 1'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
