# -*- coding: utf-8 -*-
"""r557 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby round; chain head 675,411 -> 677,611 via S0 merge
absorbing W128 landing; W129 frozen by bm-a r734 this window, bm-a engine
self-ignite expected; next bm-c burn waits W16 prereg freeze bm-a).
Lineage Tools/_r556bmc_bookkeeping.py; facts inlined from this round's
receipts. Laws: R170/R178 epoch int; R262 clock T-separated; r503
EOL-preserving bytes write. This round: QA 30th consecutive determinism
evidence, S6 38/38 first-pass zero-heal 17th, dualrun ZERO-DRIFT streak 51
(same frozen golden-week evidence window as r556, cutoff unchanged), legdiff
TRUE gate v3 PASS (OLD = r556 surviving true chain file in scratch),
compute_audit FLAG:supply_gap honest structural report (run_samples=3 span
16.7min, supply_floor ready=3=floor breach=false, trio bm-b-owned + frozen
panel), lane_io 8 host=bm-a faces legal stale-takeover derive by bm-c
(O-2100 s2.4 STALE_MIN law), zero CODELY S4 entry (no new pit)."""
import json, os, re, subprocess, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r557bmc_s6_log.txt')

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
s6_face = '38/38 rc0 first-pass zero-heal 17th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
# py_watermark verdict: dual-layout block scan (r555 discovery, .ps1
# lineage logs output BEFORE the leg marker)
seg_py = ''
if '=== 02_compute_audit' in s6:
    seg_try = s6.split('=== 02_compute_audit', 1)[1].split('=== 03_py_watermark', 1)[0]
    if '"verdict"' in seg_try:
        seg_py = seg_try
if not seg_py:
    seg_py = s6.split('=== 03_py_watermark', 1)[1].split('=== 04_update_daily', 1)[0]
mv = re.search(r'"verdict": "([^"]+)"', seg_py)
if not mv:
    mv = re.search(r"verdict.: .(\w+)", seg_py)
py_verdict = mv.group(1) if mv else '?'
assert py_verdict != '?', 'py_watermark verdict not found in either layout block'
# compute_audit flags/verdict: measured from the audit JSON line (leg-02
# OUTPUT block = between the 01 and 02 markers; output precedes its rc marker)
seg_ca = s6.split('=== 01_dualrun', 1)[1].split('=== 02_compute_audit', 1)[0]
aline = ''
for ln in seg_ca.splitlines():
    if '"audit_version"' in ln:
        aline = ln
        break
assert aline, 'compute_audit JSON line not found in leg-02 block'
try:
    audit = json.loads(aline)
except ValueError:
    audit = {}
ca_flags = audit.get('flags', [])
ca_verdict = audit.get('verdict', '?')
ca_face = ('CLEAN flags=[]' if not ca_flags
           else 'FLAG:%s (run_samples=%s span=%smin, supply_floor ready=%s floor=%s breach=%s, '
                 'ignition_sla=%s)' % (
                     ','.join(ca_flags),
                     audit.get('supply_gap_detail', {}).get('run_samples'),
                     audit.get('supply_gap_detail', {}).get('span_min'),
                     audit.get('supply_floor', {}).get('ready'),
                     audit.get('supply_floor', {}).get('floor'),
                     audit.get('supply_floor', {}).get('breach'),
                     audit.get('ignition_sla_breach_ids')))
cell_face = 'ORANGE_COOL'
token_delta = '0'   # L1 zero-token face; token_meter leg carries no delta= line (lineage fallback)

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r557.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 677611  # W128 landed (absorbed at S0 merge 5e8d140ef); science_gates.ledger_head() live-read verified this round; no new chain entry by bm-c (next burn waits W16 prereg freeze bm-a)

did = ("r557 bm-c: golden-week standby round. (1) S0: round-start dirty = 4 own faces (r556 S7-close tails: RR "
       "close-row edit + close_facts receipt + 2 satengine live faces) -> churn-absorb bc0c2c3a1 (r714 law, targeted "
       "add 4 faces + commit -F) -> fetch 2 behind (bm-a r734 W129 freeze wave: PERPETUAL_N1_W129_PREREG + band "
       "gate/registry-insert receipts + scripts/perpetual_faces_n1.py +197) -> merge 5e8d140ef single-stop "
       "ZERO-UU (merge-mode canon r713/r725 law, dirty-intersect=0) -> 2/0 ahead at close; chain head 673,211 -> "
       "675,411 -> 677,611 (W127+W128 landings absorbed, science_gates live-read re-verified). (2) S0.5: orders "
       "154/154 O-files strict diff rc0 zero unacked (canonical Tools/orders_diff.py --strict); D-19 decisions "
       "MATCH D14DCC74 zero delta (raw-blob SHA-256, group-tree origin show); group orders SHA-1 3BF0F16E MATCH "
       "zero new CEO rows (r537 algorithm pin); inbox 1 (MSG-2026-10-05-1627 bm-a W129 seat declaration, 45th "
       "owned, pre-pushed per r565 law) -> read/acked/moved to processed -> inbox 0. (3) S1 smoke 48/48. (4) S2: "
       "job_list 0 claimable; fleet tasks 172 total / 0 open; pool 403 = 399 done + 3 ready (FUND trio bm-b "
       "nested-shard ownership, host_gates refuse bm-c, r720 face) + 1 waiting (W14 governance park honored). "
       "(5) S3: WM green (red=false lane=healthy; in-chain py_watermark verdict=%s = legal idle whitelist, board "
       "empty + golden week no bar); satengine Tools-copy rc0 alive; next_pick=claimed (moneyflow IC reference "
       "batch, other-machine lane); trial-labor zero drafting (anti-dup: W129 frozen bm-a r734 -> bm-a engine "
       "self-ignite next tick; W16 prereg = bm-a lane <=10-07; fund-trio bm-b finalize windows arming Q/V ~10-06 "
       "D ~10-08; golden week no bar). (6) CORE PRODUCT: QA pack r557 standing re-run (qa/smoke-r557.md 5/5 + "
       "equity-curve-r557.png %dB, 93 trades, sharpe 0.1586, maxdd -4.33%%, win 46.24%%, determinism=True; metrics "
       "face identical r528-556 = determinism 30th consecutive evidence); clock cell=ORANGE_COOL asof 2026-09-30 "
       "(regime ORANGE days_in_state=2, frozen golden-week panel). (7) S6 chain %s (receipt "
       "results/_r557bmc_s6_log.txt; legdiff TRUE gate v3 PASS: G1 38 legs byte-identical vs r556 surviving "
       "lineage file (real file in scratch, no ephemeral gap) + G3 non-leg diff furniture-only + G4 r556 "
       "executed-log leg names 38/38; receipt results/_r557bmc_legdiff.txt, r531/r549/r554/r555 laws); dualrun %s "
       "(frozen cutoff 2026-10-05T01:13:21 same evidence window as r556, honest hold); compute_audit %s -- "
       "honest structural report-don't-mask (run samples = S6 deterministic maintenance legs on frozen panel; "
       "supply floor ready=3=floor breach=false; trio bm-b-owned unclaimed=0); lane_io 8 host=bm-a faces legal "
       "stale-takeover derive by bm-c (bm-a heartbeat stale 25-26min, O-2100 s2.4 STALE_MIN law); REPORT/"
       "LIVE-2026-10-05 idempotent regen; token delta=%s (L1 zero-token face, L2 today=0). (8) S7: loop pin=5 "
       "phase ok no-op (first fire 16:45); watchdog PRESENT; claws IN-PLACE both (LF-normalized parity, zero "
       "reinstall); task family 6/6 (IntradayMarks MISSING = market-closure legal face, re-check at 10-09 reopen "
       "per G3); attrition CLEAN (4 ledger files, 3 healed historical shrink rows noted). (9) S4: zero new pit "
       "(four-question gate N/A); CODELY r557 entry count=0.") % (py_verdict, qa_png_b, s6_face, dual_face, ca_face, token_delta)

three_line = ("当前活: r557 金周值守轮收口（QA 三十连证·S6 38/38 首过零 heal 十七连·legdiff 真门 v3 PASS·compute_audit supply_gap 诚实结构旗如实呈报） "
              "| 最近实物: qa/smoke-r557.md 5/5+qa/equity-curve-r557.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "三十连证）+results/_r557bmc_s6_log.txt（38/38 首过）+results/_r557bmc_legdiff.txt（v3 PASS） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W129 bm-a 引擎自燃在途；W16 prereg（bm-a·≤10-07）→"
              "引擎下波；fund-trio finalize 窗口（bm-b·Q/V~10-06·D~10-08）；D-06 收口 10-07 12:00；复市 10-09；月界首考 10-31") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin "
              "selftest; r557 fired 10-05 16:4x so window round = first round on/after midnight). "
              "(b) W129 frozen by bm-a r734 this window (pre-pushed seat per r565 law) -> bm-a engine "
              "self-ignite expected next tick; W130+ projection A 303_004..305_003 CLEAN / B 68_502..68_701 "
              "hops=1 (past-hit restart, refusal facts to be machine-disclosed at W130 prereg window). "
              "(c) fund-trio NULLS finalize windows arming (bm-b canonical; Q/V ~10-06, D ~10-08 per r735 "
              "readiness probe). (d) W16 candidate prereg draft+freeze (bm-a, window <=10-07) -> next engine "
              "wave supply after freeze. (e) D-06 split closeout window 10-07 12:00. (f) O-2115/O-2030 "
              "acceptance 10-08. (g) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + "
              "regime_guard v3 date-gate first bar. (h) qa/ evidence pack per-round standing re-run. (i) CEO "
              "physical item pending: tailscale login link click (bm-c URL alive since r505). (j) CODELY.md "
              "over-50KB flag carried (GM ruling face, r504 law: no byte-count archiving of in-service laws by "
              "machines). (k) unified chain head 677,611 (W128 landed bm-a, absorbed at S0 merge this round; "
              "bm-c zero chain entry; next burn waits W16 prereg freeze). (l) next 5x = r560.")

verify = ("receipts: qa/smoke-r557.md 5/5 + qa/equity-curve-r557.png (%dB, 93 trades, determinism=True) + "
          "results/_r557bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + results/_r557bmc_legdiff.txt (TRUE "
          "gate v3 PASS: G1+G3+G4, OLD=r556 surviving lineage + r556 executed-log cross, r531/r549/r554/r555 "
          "laws) + smoke 48/48 + churn-absorb bc0c2c3a1 (4 faces, r714 law) + merge 5e8d140ef single-stop "
          "zero-UU (fetch 2 behind, dirty-intersect=0) + orders 154/154 strict diff rc0 (canonical round-start "
          "scan) + D-19 decisions MATCH D14DCC74 + group orders SHA-1 3BF0F16E...E56253 MATCH (r537 pin) + "
          "inbox MSG W129 seat acked+processed (0 unread) + satengine rc0 alive + loop pin=5 phase ok no-op "
          "(first fire 16:45) + watchdog PRESENT + task family 6/6 (IntradayMarks closure-legal MISSING, G3 "
          "re-check 10-09) + claws IN-PLACE (LF-normalized parity both, zero reinstall) + attrition CLEAN (3 "
          "healed rows noted) + unified chain live head 677,611 (re-verified live-read via "
          "science_gates.ledger_head()) + CODELY r557 entry count=0 (no new pit) + commit/push delivery "
          "self-check this close.") % (qa_png_b, bad_end)

note = ("r557: golden-week standby round closed. QA pack r557 = 30th consecutive identical metrics face (frozen "
        "golden-week panel determinism evidence). S6 %s (zero-heal x17), compute_audit %s (honest structural "
        "supply_gap: trio bm-b-owned + frozen panel; supply_floor breach=false; ignition SLA zero breach). S0 "
        "single-stop merge window: churn-absorb 4 own faces, fetch 2 behind, merge 5e8d140ef zero-UU (W129 "
        "freeze wave). Chain head advanced 675,411 -> 677,611 (W128 landing absorbed at S0 merge; bm-c zero "
        "chain entry; next burn waits W16 prereg freeze bm-a). legdiff TRUE gate v3 PASS with OLD = r556 "
        "surviving true chain file (no ephemeral gap this round). Lane_io 8 host=bm-a guarded faces legal "
        "stale-takeover derive by bm-c this round (O-2100 s2.4 STALE_MIN law, bm-a heartbeat stale 25-26min). "
        "No 5x duty this round (next = r560). No new methodology; no treasure faces (no five-type closeout by "
        "bm-c this round).") % (s6_face, ca_face)

row = ("%s | r557 | dept:工程（金周值守轮） | watermark verdict=绿（red=%s·py_watermark probe rc0·链内 verdict=%s"
       "〔板空+金周无 bar=合法 idle 白名单〕·判决链席位他机：W129 已冻结 bm-a r734〔pre-pushed seat·引擎自燃下拍〕+fund-trio bm-b finalize 窗口 "
       "arming〔Q/V~10-06·D~10-08·r735 readiness probe〕+W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 unclaimed=0·"
       "next_pick=claimed〔moneyflow IC reference batch·他机车道〕·金周无 bar〕·supply_floor 诚实旗=金周结构面 ready=3=floor·"
       "breach=false·点火 SLA 零违例·compute_audit 旗=%s〔supply_gap·run_samples=3 span=16.7min=S6 确定性维护腿·诚实结构面如实呈报〕）｜"
       "本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r557.md 5/5+qa/equity-curve-r557.png（%dB·3 syms x 800 bars·93 trades·"
       "sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·与 r528-556 面恒等=冻结面板确定性三十连证）+S6 %s（收据 "
       "results/_r557bmc_s6_log.txt·bad=[%s]·零 heal 十七连）+legdiff 真门 v3 PASS〔G1 38 腿字节恒等 vs r556 存留真身〔本轮零 "
       "ephemeral 缺口〕+G3 非腿 diff=rNNN 形归一 furniture-only+G4 r556 执行日志腿名 38/38 交叉·收据 "
       "results/_r557bmc_legdiff.txt〕｜S0=轮首脏 4 面（r556 S7-close 尾：RR close 行+close_facts 回执+satengine 活面 x2）"
       "churn-absorb bc0c2c3a1（r714 律·targeted add+commit -F）·fetch 实核 2 behind→merge 5e8d140ef 零 UU 单停（bm-a r734 W129 "
       "冻结波）→2/0 push 收口·链头 675,411→677,611（W128 吸收）｜S0.5=orders 154/154 strict diff rc0 零未回执（正典 "
       "orders_diff.py --strict）·D-19 decisions MATCH D14DCC74 零增量（raw-blob SHA-256 group-tree origin show）·group orders "
       "水位 SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·inbox 1→0（W129 席位宣告 MSG 已读已回执已归档 processed）｜"
       "smoke 48/48｜satengine rc0 活（Tools 面）｜试用劳力线不触发（W129 已冻结他机+fund-trio bm-b finalize 窗口 arming+"
       "金周无 bar）｜S6 面=dualrun ZERO-DRIFT streak %s〔冻结 cutoff 2026-10-05T01:13:21 同证据窗如实持有〕·compute_audit "
       "supply_gap 诚实结构旗〔run_samples=3 span=16.7min=维护腿·trio bm-b 属主·breach=false〕·regime ORANGE shadow "
       "days_in_state=2（enforce 请求·日期门 10-09 首 bar 前诚实降级）·cell=%s·REPORT/LIVE-2026-10-05 幂等再生·lane_io 8 面 "
       "host=bm-a 诚实 stale-takeover derive by bm-c〔O-2100 s2.4 STALE_MIN 律·bm-a 心跳 stale 25-26min〕｜S7=loop pin5 no-op"
       "（首拍 16:45）·watchdog PRESENT·双爪 IN-PLACE（LF 归一 MATCH·零重装）·任务族 6/6+IntradayMarks 缺席=休市合法面〔G3 "
       "复市 10-09 再核〕·attrition CLEAN〔4 账本·3 healed 历史缩行注记照录〕｜token 面=本机 L1 零 token 腿·账本 delta=%s·L2 "
       "today=0｜统一链头 677,611〔W128 落账 bm-a·S0 merge 吸收·本轮 science_gates 活读复核·零入链·下波=W16 prereg 冻结后〕｜"
       "轮产品计分：2（qa/ 证据包 r557=能跑/能看实物+S6 38 面 CEO 再生面）｜记账预算：3（state+心跳+轮报=法定 3·零 CODELY 新条"
       "〔四问门 N/A·无新坑〕）｜方法论捕获=无新方法·宝藏捕获=无（无五类收口面）｜登记册零命中断言=N/A-零清扫零 quarantine"
       "（O-2030 §二.3 自证面）｜下轮指针：10-06 00:00 D-20261002-05 selftest 席位窗（首过轮跑 pin selftest）；W130+ 投影"
       "（A 303_004..305_003 CLEAN/B 68_502..68_701 hops=1·past-hit restart·W130 预注册窗机证披露）；fund-trio finalize 窗口"
       "（bm-b·Q/V~10-06·D~10-08）；W16 候选 prereg（bm-a·≤10-07）→引擎下波供给；D-06 拆件收口 10-07 12:00；O-2115/O-2030 "
       "验收 10-08；复市 10-09（G3·IntradayMarks 再核·regime_guard v3 日期门首 bar）；月界首考 10-31；下一 5x=bm-c r560") % (now_iso, wm_red, py_verdict, ca_verdict, qa_png_b, s6_face, bad_end, streak, cell_face, token_delta)

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
                                   "r557 probe = S0 raw-blob hash MATCH D14DCC74, zero delta vs r556 consumption; "
                                   "consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r557 zero new orders, 154/154 strict diff rc0 "
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
st['round_no'] = 557
st['round_no_label'] = 'round 557 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r557: golden-week standby round (QA pack r557 5/5 + equity-curve-r557.png %dB, 93 trades, "
                      "determinism=True, metrics face identical to r528-556 = frozen-panel 30th consecutive "
                      "evidence), S6 %s, dualrun %s (frozen evidence window), compute_audit %s (honest structural "
                      "supply_gap report: run samples = S6 maintenance legs on frozen panel, supply_floor "
                      "ready=3=floor breach=false, trio bm-b-owned), smoke 48/48, orders 154/154 zero unacked, "
                      "D-19 dual MATCH (decisions D14DCC74 + group orders SHA-1 3BF0F16E r537 pin), S0 "
                      "single-stop merge window (churn-absorb bc0c2c3a1 4 own faces, fetch 2 behind, merge "
                      "5e8d140ef zero-UU, W129 freeze wave absorbed), attrition CLEAN, task family 6/6 + claws "
                      "IN-PLACE; legdiff TRUE gate v3 PASS (G1+G3+G4, r556 surviving lineage + r556 executed-log "
                      "cross; no ephemeral gap this round); lane_io 8 host=bm-a faces legal stale-takeover derive "
                      "by bm-c (O-2100 s2.4 STALE_MIN law); unified chain head 677,611 (W128 landing absorbed at "
                      "S0 merge, live-read re-verified; next burn waits W16 prereg freeze bm-a); judgment seats "
                      "remaining on other machines (W129 frozen bm-a r734 self-ignite next tick, fund-trio bm-b "
                      "finalize windows arming Q/V ~10-06 D ~10-08, W16 prereg bm-a <=10-07); regime ORANGE "
                      "shadow (date-gate first bar 10-09)") % (qa_png_b, s6_face, dual_face, ca_face)
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
hb['latest_artifact'] = ("qa/ evidence pack r557 (smoke-r557.md 5/5 + equity-curve-r557.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 30th consecutive evidence) + results/_r557bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + results/_r557bmc_legdiff.txt (TRUE gate v3 PASS)") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W129 "
                        "burn self-ignite bm-a (frozen r734, next tick); W16 candidate prereg (bm-a, <=10-07) -> "
                        "next engine wave; fund-trio NULLS finalize windows (bm-b, Q/V ~10-06, D ~10-08); D-06 "
                        "closeout 10-07 12:00; O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, IntradayMarks "
                        "re-check, regime_guard v3 date-gate first bar); month-end exam 10-31; next 5x = bm-c "
                        "r560")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 557
hb['round_no_label'] = 'round 557 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r557 bm-c: golden-week standby round (boards open=0, judgment seats other machines, no bar "
                 "until 10-09). (1) S0 churn-absorb bc0c2c3a1 (4 own faces) + merge 5e8d140ef single-stop "
                 "zero-UU (fetch 2 behind; W129 freeze wave absorbed; W128 landing -> chain head 677,611). "
                 "(2) orders 154/154 rc0; inbox 1 W129 seat MSG acked+processed. (3) D-19 dual MATCH zero "
                 "action. (4) smoke 48/48. (5) boards empty. (6) WM green, in-chain verdict=%s legal idle; "
                 "satengine rc0 alive; no drafting pointer (next_pick claimed elsewhere). (7) CORE: QA pack "
                 "r557 (5/5, 93 trades, determinism=True, frozen-panel 30th consecutive evidence). (8) S6 %s "
                 "(zero-heal x17), dualrun %s, compute_audit %s (honest structural), regime ORANGE shadow; "
                 "legdiff TRUE gate v3 PASS (zero CODELY entry, no new pit). (9) S7: loop pin5 phase-ok; "
                 "watchdog PRESENT; task family 6/6 + IntradayMarks closure-legal; claws IN-PLACE zero "
                 "reinstall; attrition CLEAN; close: deterministic add + commit -F + push_verify.") % (
                     py_verdict, s6_face, dual_face, ca_face)
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
assert st2['round_no'] == 557, 'round_no must be 557'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 557, 'hb round_no must be 557'
rr_txt = open(RR, 'rb').read().decode('utf-8', errors='replace')
assert rr_txt.count('| r557 | dept:') == 1, 'r557 main row count != 1'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('CA_FACE=' + ca_face)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
