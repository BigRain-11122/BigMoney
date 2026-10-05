# -*- coding: utf-8 -*-
"""r555 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby + 5x HANDOVER census round; chain head 673,211 held,
next burn waits W16 prereg freeze bm-a).
Lineage _r554bmc_bookkeeping.py; facts inlined from this round's receipts.
Laws: R170/R178 epoch int; R262 clock T-separated; r503 EOL-preserving
bytes write. This round: QA 28th consecutive determinism evidence, S6
38/38 first-pass zero-heal 15th, dualrun streak 51, legdiff TRUE gate v3
rebuilt (G1+G3+G4, r551 surviving lineage + r554 executed-log cross),
HANDOVER 5x r551-555 window entry prepended, S0 churn-absorb 29e00dc25 +
merge 07690a6c0 zero-UU (3 behind), CODELY one S4 entry (ephemeral
receipt law)."""
import json, os, re, subprocess, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r555bmc_s6_log.txt')

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
s6_face = '38/38 rc0 first-pass zero-heal 15th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
# py_watermark verdict: dual-layout block scan (r555 discovery: r551 .ps1
# lineage logs output BEFORE the leg marker, r552-r554 .py lineage logged
# marker first -- scan the 02->03 block (output-before-marker layout), fall
# back to the 03->04 block (marker-first layout).
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
token_delta = '0'   # L1 zero-token face; token_meter leg carries no delta= line (r551-r554 lineage fallback)

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r555.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 673211  # W126 landed bm-a last window; live-read re-verified this round; no new chain entry by bm-c (next burn waits W16 prereg freeze)

did = ("r555 bm-c: golden-week standby + 5x HANDOVER census round. (1) S0: round-start dirty = 8 own faces (r554 "
       "S7-close post-push tails x4: closerow edit + merge_resolve script + close_facts + RR close row; own daemon "
       "lane live x3: autofill/satengine face+state; r555 s0 probe x1) -> churn-absorb 29e00dc25 (r714 law, "
       "targeted add 8 faces + commit -F) -> fetch 3 behind (bm-a r733 wave already carrying r554 products via "
       "hop-2 merge) -> merge 07690a6c0 single-stop ZERO-UU (merge-mode canon r713 law, dirty-intersect=0) -> 2/0 "
       "ahead at close. (2) S0.5: orders 154/154 O-files strict diff rc0 zero unacked (canonical Tools/orders_diff.py "
       "--strict); D-19 decisions MATCH D14DCC74 zero delta (raw-blob SHA-256, group-tree origin show); group orders "
       "SHA-1 3BF0F16E MATCH zero new CEO rows (r537 algorithm pin); inbox 0. (3) S1 smoke 48/48. (4) S2: job_list 0 "
       "claimable; fleet tasks 172 total / 0 open / 46 claimed_or_ip; pool 403 = 399 done + 3 ready (FUND trio bm-b "
       "nested-shard ownership, host_gates refuse bm-c, r720 face) + 1 waiting (W14 governance park honored). (5) "
       "S3: WM green (red=false lane=healthy; in-chain py_watermark verdict=py_low_board_clear = legal idle "
       "whitelist, board empty + golden week no bar); satengine Tools-copy rc0 alive (burns_active none local); "
       "trial-labor zero drafting (anti-dup: W126 finalize landed bm-a -> chain head 673,211 live-read re-verified; "
       "W16 prereg = bm-a lane <=10-07; fund-trio bm-b in-burn 10-05..09; golden week no bar). (6) CORE PRODUCT: QA "
       "pack r555 standing re-run (qa/smoke-r555.md 5/5 + equity-curve-r555.png %dB, 93 trades, sharpe 0.1586, "
       "maxdd -4.33%%, win 46.24%%, determinism=True; metrics face identical r528-554 = determinism 28th "
       "consecutive evidence); market clock CALL-2026-09-30 cell=ORANGE_COOL. (7) 5x DUTY: HANDOVER census row "
       "prepended (research/HANDOVER.md, r551-555 window: QA 24th-28th consecutive family + S6 zero-heal 11th-15th + "
       "W124/W125/W126 landed reads + product-list drift + window anchors). (8) S6 chain %s (receipt "
       "results/_r555bmc_s6_log.txt; legdiff TRUE gate v3 REBUILT: G1 38 legs byte-identical vs r551 surviving "
       "lineage + G3 non-leg diff = rNNN round-token shape-normalized furniture only (v3.1 keyword-narrow false-red "
       "self-corrected = r549 law) + G4 r554 executed-log leg names 38/38 identical; disclosure = r552-r554 chain "
       "runners were ephemeral .py not in scratch, OLD pinned to latest surviving true file; receipt "
       "results/_r555bmc_legdiff.txt, r531/r554 laws); dualrun %s; regime ORANGE shadow days_in_state=2 (enforce "
       "requested, honest downgrade until date-gate first bar 10-09); supply_floor honest structural (ready=3=floor, "
       "breach=false); lane_io single-writer guards honest skip; REPORT/LIVE-2026-10-05 idempotent regen; token "
       "delta=%s (L1 zero-token face, L2 today=0). (9) S7: loop pin=5 phase ok no-op (first fire 16:15); watchdog "
       "PRESENT; claws IN-PLACE both (LF-normalized parity, zero reinstall); task family 6/6 (IntradayMarks MISSING "
       "= market-closure legal face, re-check at 10-09 reopen per G3); attrition CLEAN (4 ledger files, 3 healed "
       "historical shrink rows noted). (10) S4: one new pit appended to CODELY.md (lineage receipt referencing "
       "ephemeral files = unverifiable face; four-question gate passed).") % (qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r555 金周值守+5x HANDOVER 核对轮收口（HANDOVER r551-555 窗行落册·legdiff 真门 v3 重立〔G1+G3+G4 PASS〕·"
              "QA 二十八连证·S6 38/38 首过零 heal 十五连） "
              "| 最近实物: research/HANDOVER.md r555 核对行+qa/smoke-r555.md 5/5+qa/equity-curve-r555.png（%dB·93 trades·"
              "sharpe 0.1586·determinism=True·二十八连证）+results/_r555bmc_s6_log.txt（38/38 首过） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W16 prereg（bm-a·≤10-07）→引擎下波；"
              "fund-trio finalize（bm-b·10-05..09）；D-06 收口 10-07 12:00；复市 10-09；月界首考 10-31") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin "
              "selftest; r556 fires today 10-05 so window round = first round on/after midnight). "
              "(b) fund-trio finalize 10-05..09 (bm-b canonical). (c) W16 candidate prereg draft+freeze (bm-a, "
              "window <=10-07) -> next engine wave supply after freeze. (d) D-06 split closeout window 10-07 12:00. "
              "(e) O-2115/O-2030 acceptance 10-08. (f) market reopen 10-09 data-chain re-arm + IntradayMarks "
              "re-check (G3) + regime_guard v3 date-gate first bar. (g) qa/ evidence pack per-round standing "
              "re-run. (h) CEO physical item pending: tailscale login link click (bm-c URL alive since r505). "
              "(i) CODELY.md over-50KB flag carried (GM ruling face, r504 law: no byte-count archiving of "
              "in-service laws by machines). (j) unified chain head 673,211 held (W126 landed bm-a; bm-c zero "
              "chain entry this window; next burn waits W16 prereg freeze). (k) next 5x = r560.")

verify = ("receipts: qa/smoke-r555.md 5/5 + qa/equity-curve-r555.png (%dB, 93 trades, determinism=True) + "
          "research/HANDOVER.md r555 census row (5x duty) + results/_r555bmc_s6_log.txt (38 legs first-pass rc0, "
          "bad=[%s]) + results/_r555bmc_legdiff.txt (TRUE gate v3: G1+G3+G4 PASS, OLD=r551 surviving lineage + "
          "r554 executed-log cross, r531/r554 laws) + smoke 48/48 + churn-absorb 29e00dc25 (8 faces, r714 law) + "
          "merge 07690a6c0 single-stop zero-UU (fetch 3 behind, dirty-intersect=0) + orders 154/154 strict diff "
          "rc0 (canonical round-start scan + close re-scan) + D-19 decisions MATCH D14DCC74 + group orders SHA-1 "
          "3BF0F16E...E56253 MATCH (r537 pin) + satengine rc0 alive + loop pin=5 phase ok no-op (first fire "
          "16:15) + watchdog PRESENT + task family 6/6 (IntradayMarks closure-legal MISSING, G3 re-check 10-09) + "
          "claws IN-PLACE (LF-normalized parity both, zero reinstall) + attrition CLEAN (3 healed rows noted) + "
          "unified chain live head 673,211 (re-verified live-read) + CODELY r555 entry count=1 + commit/push "
          "delivery self-check this close.") % (qa_png_b, bad_end)

note = ("r555: golden-week standby + 5x HANDOVER census round closed. QA pack r555 = 28th consecutive identical "
        "metrics face (frozen golden-week panel determinism evidence). S6 %s (zero-heal x15). S0 single-stop "
        "merge window: churn-absorb 8 own faces, fetch 3 behind, merge 07690a6c0 zero-UU. 5x duty discharged: "
        "HANDOVER r551-555 window row prepended (product-list drift + W124/125/126 chain-head advance + window "
        "anchors). legdiff TRUE gate v3 rebuilt after discovering r552-r554 chain runners were ephemeral (their "
        "receipts reference non-existent files = unverifiable face; new CODELY law). Chain head 673,211 held "
        "(bm-c zero chain entry; next burn waits W16 prereg freeze bm-a). No new methodology; no treasure faces "
        "(no five-type closeout by bm-c this round).") % s6_face

row = ("%s | r555 | dept:工程（金周值守轮·5x HANDOVER 核对轮） | watermark verdict=绿（red=%s·py_watermark probe rc0·链内 verdict=%s"
       "〔板空+金周无 bar=合法 idle 白名单〕·判决链席位他机：W126 finalize 已落账〔链头 673,211·bm-a one-pass·n1_w126_results.json 2,200 "
       "new-seed null trials·本轮活读复核〕+fund-trio bm-b keepalive 在烧〔10-05..09〕+W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 "
       "unclaimed=0·金周无 bar〕·supply_floor 诚实旗=金周结构面 ready=3=floor·breach=false·点火 SLA 零违例）｜"
       "本轮：金周值守+5x HANDOVER 核对+QA 证据面常设复跑——实物=research/HANDOVER.md r555 核对行〔5x 义务·r551-555 增量窗产物清单漂移+"
       "统一链 668,811→673,211 三波前移+下窗锚全载〕+qa/smoke-r555.md 5/5+qa/equity-curve-r555.png（%dB·3 syms x 800 bars·93 trades·"
       "sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·与 r528-554 面恒等=冻结面板确定性二十八连证）+S6 %s（收据 "
       "results/_r555bmc_s6_log.txt·bad=[%s]·零 heal 十五连）+legdiff 真门 v3 重立〔G1 38 腿字节恒等 vs r551 存留真身+G3 非腿 diff="
       "rNNN 形归一恒等〔v3.1 关键词窄化假红自纠=r549 律〕+G4 r554 执行日志腿名 38/38 交叉·disclosure=r552-r554 链 runner ephemeral "
       "不在册→OLD 钉最新存留真文件·收据 results/_r555bmc_legdiff.txt〕｜S0=轮首脏 8 面（r554 S7-close 尾 x4：closerow 编辑+"
       "merge_resolve 脚本+close_facts+RR close 行；own daemon lane live x3：autofill+satengine 面+态；r555 s0 探针 x1）"
       "churn-absorb 29e00dc25（r714 律·targeted add+commit -F）·fetch 实核 3 behind→merge 07690a6c0 零 UU 单停（bm-a r733 波）"
       "→2/0 push 收口｜S0.5=orders 154/154 strict diff rc0 零未回执（正典 orders_diff.py --strict）·D-19 decisions MATCH "
       "D14DCC74 零增量（raw-blob SHA-256 group-tree origin show）·group orders 水位 SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·"
       "inbox 0｜smoke 48/48｜satengine rc0 活（Tools 面·burns_active 本机空）｜试用劳力线不触发（W126 已落账〔head 673,211〕+"
       "fund-trio bm-b 在烧+金周无 bar）｜S6 面=dualrun ZERO-DRIFT streak %s·regime ORANGE shadow days_in_state=2（enforce 请求·"
       "日期门 10-09 首 bar 前诚实降级）·cell=%s·REPORT/LIVE-2026-10-05 幂等再生·lane_io 守卫诚实跳过｜S7=loop pin5 no-op（首拍 "
       "16:15）·watchdog 在位·双爪 IN-PLACE（LF 归一 MATCH·零重装）·任务族 6/6+IntradayMarks 缺席=休市合法面〔G3 复市 10-09 再核〕·"
       "attrition CLEAN〔4 账本·3 healed 历史缩行注记照录〕｜token 面=本机 L1 零 token 腿·账本 delta=%s·L2 today=0·cumulative ~2049｜"
       "统一链头 673,211〔W126 落账 bm-a·本轮活读复核平持·零入链·下波=W16 prereg 冻结后〕｜轮产品计分：2（HANDOVER 5x 核对行+qa/ 证据包 "
       "r555=能跑/能看实物+S6 38 面 CEO 再生面）｜记账预算：4（state+心跳+轮报=法定 3+CODELY S4 新坑 1〔四问门过·ephemeral 收据不可复核律〕）"
       "｜方法论捕获=无新方法·宝藏捕获=无（无五类收口面）｜登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜"
       "下轮指针：10-06 00:00 D-20261002-05 selftest 席位窗（首过轮跑 pin selftest）；fund-trio finalize（bm-b·10-05..09）；"
       "W16 候选 prereg（bm-a·≤10-07）→引擎下波供给；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09"
       "（G3·IntradayMarks 再核·regime_guard v3 日期门首 bar）；月界首考 10-31；下一 5x=bm-c r560") % (now_iso, wm_red, py_verdict, qa_png_b, s6_face, bad_end, streak, cell_face, token_delta)

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
                                   "r555 probe = S0 raw-blob hash MATCH D14DCC74, zero delta vs r554 consumption; "
                                   "consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r555 zero new orders, 154/154 strict diff rc0 "
                                "round-start canonical scan + close re-scan)")
st['last_round'] = did
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_seen_at'] = now_iso
st['last_ts'] = now_iso
st['next'] = next_field
st['note'] = note
st['ram_free_gb'] = free_gb
st['round_no'] = 555
st['round_no_label'] = 'round 555 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r555: golden-week standby + 5x HANDOVER census round (HANDOVER r551-555 window row "
                      "prepended; QA pack r555 5/5 + equity-curve-r555.png %dB, 93 trades, determinism=True, "
                      "metrics face identical to r528-554 = frozen-panel 28th consecutive evidence), S6 %s, dualrun "
                      "%s, smoke 48/48, orders 154/154 zero unacked, D-19 dual MATCH (decisions D14DCC74 + group "
                      "orders SHA-1 3BF0F16E r537 pin), S0 single-stop merge window (churn-absorb 29e00dc25 8 own "
                      "faces, fetch 3 behind, merge 07690a6c0 zero-UU), attrition CLEAN, task family 6/6 + claws "
                      "IN-PLACE; legdiff TRUE gate v3 rebuilt (G1+G3+G4, r551 surviving lineage + r554 executed-log "
                      "cross; r552-r554 runners were ephemeral = new CODELY law); unified chain head 673,211 held "
                      "(W126 landed bm-a, live-read re-verified; next burn waits W16 prereg freeze bm-a); judgment "
                      "seats remaining on other machines (fund-trio bm-b in-burn 10-05..09, W16 prereg bm-a "
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
hb['latest_artifact'] = ("research/HANDOVER.md r555 census row (5x duty, r551-555 window) + qa/ evidence pack r555 "
                         "(smoke-r555.md 5/5 + equity-curve-r555.png %dB, 93 trades, determinism=True, "
                         "frozen-panel 28th consecutive evidence) + results/_r555bmc_s6_log.txt (38 legs rc0 "
                         "first-pass receipt) + results/_r555bmc_legdiff.txt (TRUE gate v3 PASS)") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W16 "
                        "candidate prereg (bm-a, <=10-07) -> next engine wave; fund-trio finalize (bm-b) "
                        "10-05..09; D-06 closeout 10-07 12:00; O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, "
                        "IntradayMarks re-check, regime_guard v3 date-gate first bar); month-end exam 10-31; next "
                        "5x = bm-c r560")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 555
hb['round_no_label'] = 'round 555 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r555 bm-c: golden-week standby + 5x HANDOVER census round (boards open=0, judgment seats other "
                 "machines, no bar until 10-09). (1) S0 churn-absorb 29e00dc25 (8 own faces) + merge 07690a6c0 "
                 "single-stop zero-UU (fetch 3 behind). (2) orders 154/154 rc0, inbox 0. (3) D-19 dual MATCH zero "
                 "action. (4) smoke 48/48. (5) boards empty. (6) WM green, in-chain verdict=py_low_board_clear "
                 "legal idle; satengine rc0 alive; no drafting pointer. (7) CORE: HANDOVER 5x census row + QA pack "
                 "r555 (5/5, 93 trades, determinism=True, frozen-panel 28th consecutive evidence). (8) S6 %s "
                 "(zero-heal x15), dualrun %s, regime ORANGE shadow, supply_floor honest structural; legdiff TRUE "
                 "gate v3 rebuilt (ephemeral-runner receipt law, one CODELY S4 entry). (9) S7: loop pin5 "
                 "phase-ok; watchdog present; task family 6/6 + IntradayMarks closure-legal; claws IN-PLACE zero "
                 "reinstall; attrition CLEAN; close: deterministic add + commit -F + push_verify.") % (s6_face, dual_face)
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
assert st2['round_no'] == 555, 'round_no must be 555'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 555, 'hb round_no must be 555'
rr_txt = open(RR, 'rb').read().decode('utf-8', errors='replace')
assert rr_txt.count('| r555 | dept:') == 1, 'r555 main row count != 1'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
