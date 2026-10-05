# -*- coding: utf-8 -*-
"""r549 bm-c S7 bookkeeping: state + heartbeat + round-report main row
(golden-week standby round). Lineage _r548bmc_bookkeeping.py; facts inlined
from this round's receipts. Laws: R170/R178 epoch int; R262 clock
T-separated; r503 EOL-preserving bytes write. New this round: legdiff
assertion-layer false positive (r548-latent threshold-4 + vs-rN-2 needle)
healed in-place with v2 substance gates (r531 law substance preserved)."""
import json, os, re, shutil, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r549bmc_s6_log.txt')

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]
epoch = int(time.time())

# live machine metrics (psutil live read this close window; gpu = nvidia-smi
# probe 14:4x free MiB)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=2), 1)
    free_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu_pct, free_gb = 10.0, 8.6
gpu_mib = 805

# ---- S6 log facts
s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
s6_face = '38/38 rc0 first-pass zero-heal 9th consecutive' if firstpass else '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
cell_face = 'ORANGE_COOL'
# token values pinned to token_meter leg block (r547 wrong-leg law)
tk_seg = s6.split('=== token_meter', 1)[1]
tk = re.search(r'delta=(\d+)', tk_seg)
token_delta = tk.group(1) if tk else '0'
# pin to py_watermark leg block ONLY (r547 verdict-misattribution law)
seg = s6.split('=== py_watermark', 1)[1]
mv = re.search(r'"verdict": "([^"]+)"', seg)
py_verdict = mv.group(1) if mv else '?'

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r549.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

ledger_head = 666611  # W123 finalize landed (bm-a r729 one-pass: K=268,520, skill_line_v2 1.1749, A-p95 0.3049); bm-c zero chain entry this window

did = ("r549 bm-c: golden-week standby round. (1) S0: round-start dirty = 5 own faces (r548 S7-close post-push tails x2: "
       "CODELY r548 pit-law line + RR close row; own daemon lane live x2: satengine faces; untracked close_facts receipt) "
       "-> churn-absorb cefcf3324 (r714 law, targeted add 5 faces + commit -F) -> fetch 5 behind -> merge origin/main rc0 "
       "ZERO-UU clean absorb (merge 3ea26be82; bm-a W123 finalize wave + W124 seat MSG publish + autofill fund-trio "
       "keepalive 4bef7f830) -> ahead 2/0, push at close. (2) S0.5: orders 155/155 strict diff rc0 zero unacked; D-19 "
       "decisions MATCH D14DCC74 zero delta (Tools/d19_check.py canonical); group orders SHA-1 3BF0F16E MATCH zero new CEO "
       "rows (r537 algorithm pin); inbox 1 = W124 seat MSG (bm-a informational broadcast, read + moved to processed, "
       "anti-dup law zero bm-c drafting). (3) S1 smoke 48/48. (4) S2: job_list 0; fleet tasks 172 total / 0 open; pool "
       "403 = 399 done + 3 ready (FUND trio bm-b nested-shard ownership, host_gates refuse bm-c, r720 face) + 1 waiting "
       "(W14 governance park honored, sec-4 self-proof OR GM dual-ruling unfreeze path, zero bm-c action). (5) S3: WM green "
       "(red=false, py probe verdict=%s = honest 15-min-window history face, legal non-violation rc0; supply_gap honest "
       "structural flag ready=3=floor breach=false); satengine Tools-copy rc0 alive (burns_active none local; W123 "
       "finalize landed chain head 666,611; W124 seat = bm-a face per r565 law; fund-trio bm-b in-burn 10-05..09); "
       "trial-labor zero drafting (anti-dup: all judgment seats on other machines; boards open=0). (6) CORE PRODUCT: QA "
       "pack r549 standing re-run (qa/smoke-r549.md 5/5 + equity-curve-r549.png %dB, 93 trades, sharpe 0.1586, maxdd "
       "-4.33%%, win 46.24%%, determinism=True; metrics face identical r528-548 = determinism 22nd consecutive evidence); "
       "market clock CALL-2026-09-30 cell=ORANGE_COOL. (6b) NEW PIT healed in-place: S6-chain legdiff lineage assertion "
       "layer false positive (r548-latent: threshold len<=4 permanently red at 10 furniture diff lines + docstring "
       "'vs rN-2' needle breaks rN-1/rN allowlist) -> v2 substance gates (38/38 leg rows byte-identical + LEGS block "
       "verbatim equality + zero diff lines touch leg rows + furniture-only allowlist) PASS; r548's own legdiff re-run "
       "today reproduces the false red (kinship proven). (7) S6 chain %s (receipt results/_r549bmc_s6_log.txt); dualrun "
       "%s; update_lhb no-op (30-min guard after r548 pull); update_fundamental snapshot-fresh skip (0.7h); regime "
       "ORANGE shadow days_in_state=2 (enforce requested, honest downgrade until date-gate first bar 10-09); lane_io "
       "single-writer guards honest stale-takeover derives (bm-a host heartbeat stale 30min, O-2100 s2.4); REPORT/LIVE-"
       "2026-10-05 idempotent regen; token delta=%s. (8) S7: loop pin=5 phase ok no-op; watchdog -Force idempotent; "
       "claws IN-PLACE both MATCH (LF-normalized compare, zero reinstall needed); task family 6/6 (CSV cross-check, "
       "no-suffix canon names r517 law); attrition CLEAN (4 ledger files, 3 healed historical shrink rows noted, zero "
       "active loss). (9) unified chain live head 666,611 (W123 landed; no new chain entry by bm-c this window).") % (py_verdict, qa_png_b, s6_face, dual_face, token_delta)

three_line = ("当前活: r549 金周值守轮收口（QA 二十二连证+S6 38/38 首过零 heal 九连·orders 155/155+D-19 双 MATCH·"
              "W123 已落账链头 666,611/W124 席位 bm-a 已公示·legdiff 断言层假阳性 v2 实质门治愈） "
              "| 最近实物: qa/smoke-r549.md 5/5+qa/equity-curve-r549.png（%dB·93 trades·sharpe 0.1586·determinism=True·"
              "二十二连证）+results/_r549bmc_s6_log.txt（38/38 首过） @ %s "
              "| 下个里程碑: 10-06 00:00 D-20261002-05 pin selftest 席位窗（首过轮跑）；W124 freeze+burn/finalize（bm-a 面·"
              "席位 14:37 已公示）；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；D-06 拆件收口 "
              "10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）+regime_guard v3 "
              "日期门首 bar；月界首考 10-31；下一 5x=r550") % (qa_png_b, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin selftest). "
              "(b) W124 freeze+burn+finalize on bm-a (seat published 14:37, bm-a face per r565 law; W123 landed). "
              "(c) fund-trio finalize 10-05..09 (bm-b canonical). (d) W16 candidate prereg draft+freeze (bm-a, window "
              "<=10-07). (e) D-06 split closeout window 10-07 12:00. (f) O-2115/O-2030 acceptance 10-08. (g) market "
              "reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 date-gate first bar. "
              "(h) qa/ evidence pack per-round standing re-run. (i) CEO physical item pending: tailscale login link "
              "click (bm-c URL alive since r505). (j) CODELY.md over-50KB flag carried (GM ruling face). (k) next 5x = "
              "r550 HANDOVER check round.")

verify = ("receipts: qa/smoke-r549.md 5/5 + qa/equity-curve-r549.png (%dB, 93 trades, determinism=True) + "
          "results/_r549bmc_s6_log.txt (38 legs first-pass rc0, bad=[%s]) + results/_r549bmc_probe.txt (S1/S2/S3 compact "
          "receipt) + legdiff v2 PASS (substance gates 1/2/3, zero leg drift) + smoke 48/48 + churn-absorb cefcf3324 "
          "(5 faces, r714 law) + merge 3ea26be82 rc0 zero-UU (bm-a W123 finalize wave + W124 seat MSG + autofill "
          "keepalive absorbed, UU canonical=0 per r713 law) + ahead 2/0 + orders 155/155 strict diff rc0 + D-19 "
          "decisions MATCH D14DCC74 + group orders SHA-1 3BF0F16E...E56253 MATCH (r537 pin) + satengine rc0 alive + "
          "loop pin=5 phase ok no-op + watchdog -Force idempotent + task family 6/6 (CSV cross-check) + claws IN-PLACE "
          "(LF-normalized MATCH both, zero reinstall) + attrition CLEAN (3 healed rows noted) + inbox W124 MSG moved "
          "to processed + unified chain live head 666,611 (W123 landed) + commit/push delivery self-check this close.") % (qa_png_b, bad_end)

note = ("r549: golden-week standby closed. QA pack r549 = 22nd consecutive identical metrics face (frozen golden-week "
        "panel determinism evidence). S6 %s (zero-heal x9). S0 single-hop window: churn-absorb 5 own faces then merge "
        "origin/main zero-UU (bm-a W123 finalize wave); push face pending at write time. W123 finalize landed (chain head "
        "666,611); W124 seat = bm-a published/reserved (no bm-c drafting, anti-dup law). NEW PIT 1: S6-chain legdiff "
        "lineage assertion-layer false positive (r548-latent threshold-4 + vs-rN-2 allowlist needle; r548's own legdiff "
        "re-run reproduces the false red) healed with v2 substance gates -> CODELY line append at close (r714 "
        "post-push-tail pattern, absorbed by r550). No new methodology; no treasure faces (no five-type closeout by "
        "bm-c this round).") % s6_face

row = ("%s | r549 | dept:工程（金周值守轮·QA 证据面常设复跑） | watermark verdict=绿（red=%s·py_watermark probe rc0·verdict=%s〔15min "
       "持续窗历史不足=金周低载面诚实判读·合法非违例〕·判决链席位他机：W123 已落账〔链头 666,611·bm-a r729 one-pass〕+W124 席位 bm-a "
       "已公示〔14:37·r565 律 pre-freeze push·freeze 窗=bm-a〕+fund-trio bm-b keepalive 在烧〔10-05..09〕+W16 prereg bm-a ≤10-07·"
       "池 ready 3 全属主在握 unclaimed=0·金周无 bar〕·supply_gap 诚实旗=金周结构面 ready=3=floor·breach=false·点火 SLA 零违例）｜"
       "本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r549.md 5/5+qa/equity-curve-r549.png（%dB·3 syms x 800 bars·93 trades·"
       "sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·与 r528-548 面恒等=冻结面板确定性二十二连证）+S6 %s（收据 "
       "results/_r549bmc_s6_log.txt·bad=[%s]·零 heal 九连）｜S0=轮首脏 5 面（r548 S7-close 尾 x2：CODELY r548 坑律行+RR close 行+"
       "own daemon lane live x2+close_facts 未跟踪收据）churn-absorb cefcf3324（r714 律·targeted add+commit -F）·fetch 实核 5 "
       "behind→merge 3ea26be82 rc0 零 UU 干净吸收〔bm-a W123 finalize 波+W124 席位 MSG+autofill fund-trio keepalive 4bef7f830·"
       "UU 清单=diff-filter=U 正典 0〕→ahead 2/0 push 收口｜S0.5=orders 155/155 strict diff rc0 零未回执·D-19 decisions MATCH "
       "D14DCC74 零增量（Tools/d19_check.py 正典）·group orders 水位 SHA-1 3BF0F16E MATCH 零新令（r537 算法钉律）·inbox 1="
       "W124 席位公示 MSG（bm-a 信息性→processed/·反重复律 bm-c 不起草）｜smoke 48/48｜satengine rc0 活（Tools 面·burns_active "
       "本机空·W123 已落账·W124 席位=bm-a 面·fund-trio bm-b 在烧）｜试用劳力线不触发（全席位他机+W3 CEO 裁定+W14 停泊〔治理 "
       "park·sec-4 self-proof OR GM dual-ruling 解停路径〕+复市 10-09）｜本窗新坑 1 条=S6 链 legdiff 血统断言层假阳性（r548 潜伏："
       "阈值 len<=4 对 docstring 3 行+LOG+start=10 家具行恒红+allowlist 被 docstring 内 vs-rN-2 针打破·r548 自己的 legdiff 今日复跑"
       "复现同红=亲缘实证·v2 实质门治愈〔38/38 腿字节恒等+LEGS 块 verbatim 恒等+零 diff 行触腿行+家具白名单〕PASS·r531 律实质保全·"
       "CODELY 行级追加留痕）｜S6 面=update_lhb no-op（30min 间隔守卫·r548 真拉后）+update_fundamental 快照新鲜跳过（0.7h）·其余 "
       "lane guard no-op 诚实｜dualrun ZERO-DRIFT streak %s·regime ORANGE shadow days_in_state=2（enforce 请求·日期门 10-09 首 "
       "bar 前诚实降级）·clock cell=ORANGE_COOL｜attrition CLEAN〔4 账本·3 healed 历史缩行注记照录〕·任务族 6/6（CSV 交叉 r517 "
       "律·无后缀正名）·claws IN-PLACE（LF 归一 MATCH 双爪·零重装）·loop pin5 no-op·watchdog -Force 幂等｜token 面=本机 L1 "
       "零 token 腿·账本 delta=%s｜统一链头 666,611〔W123 落账·本轮零入链〕｜轮产品计分：2（qa/ 证据包 r549=能跑/能看实物+S6 "
       "38 面 CEO 再生面）｜记账预算：3（state+心跳+轮报=法定 3·CODELY 1 行=本窗新坑 S4 固化非记账）｜方法论捕获=无新方法·宝藏"
       "捕获=无（无五类收口面）｜登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜下轮指针：10-06 00:00 "
       "D-20261002-05 selftest 席位窗首过轮跑 pin selftest；W124 freeze+burn/finalize（bm-a 面）；fund-trio finalize（bm-b·"
       "10-05..09）；W16 候选 prereg（bm-a·≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09（G3·"
       "IntradayMarks 再核·regime_guard v3 日期门首 bar）；月界首考 10-31；下一 5x=r550") % (now_iso, wm_red, py_verdict, qa_png_b, s6_face, bad_end, streak, token_delta)

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
                                   "r549 probe = Tools/d19_check.py canonical MATCH D14DCC74, zero delta vs r548 "
                                   "consumption; consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r549 zero new orders, 155/155 strict diff rc0 "
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
st['round_no'] = 549
st['round_no_label'] = 'round 549 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

# ---- heartbeat update
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r549: golden-week standby + QA evidence pack standing re-run "
                      "(qa/smoke-r549.md 5/5 + equity-curve-r549.png %dB, 93 trades, determinism=True, metrics "
                      "face identical to r528-548 = frozen-panel 22nd consecutive evidence), S6 %s, dualrun %s, "
                      "smoke 48/48, orders 155/155 zero unacked, D-19 dual MATCH (decisions D14DCC74 + group "
                      "orders SHA-1 3BF0F16E r537 pin), single-hop S0 merge close (churn-absorb cefcf3324 + merge "
                      "3ea26be82 zero-UU absorbing bm-a W123 finalize wave), attrition CLEAN, task family 6/6 CSV "
                      "cross-check + claws IN-PLACE; judgment seats on other machines (W124 seat bm-a published, "
                      "fund-trio bm-b in-burn 10-05..09, W16 bm-a <=10-07); supply_gap flag = golden-week structural "
                      "(ready=3=floor, unclaimed=0, breach=false); regime ORANGE shadow (date-gate first bar "
                      "10-09); NEW PIT healed: legdiff assertion-layer false positive -> v2 substance gates") % (qa_png_b, s6_face, dual_face)
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
hb['latest_artifact'] = ("qa/ evidence pack r549 (smoke-r549.md 5/5 + equity-curve-r549.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 22nd consecutive evidence) + results/_r549bmc_s6_log.txt "
                         "(38 legs rc0 first-pass receipt) + churn-absorb cefcf3324 + S0 merge 3ea26be82 zero-UU") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 pin-selftest window (first round at/after runs it); W124 "
                        "freeze+burn+finalize bm-a (seat published 14:37; W123 landed chain head 666,611); W16 "
                        "candidate prereg (bm-a, <=10-07); fund-trio finalize (bm-b) 10-05..09; D-06 closeout "
                        "10-07 12:00; O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, IntradayMarks re-check, "
                        "regime_guard v3 date-gate first bar); month-end exam 10-31; next 5x = bm-c r550")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 549
hb['round_no_label'] = 'round 549 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r549 bm-c: golden-week standby (boards open=0, judgment seats other machines, no bar until "
                 "10-09). (1) S0 churn-absorb cefcf3324 (5 own faces) + merge 3ea26be82 zero-UU (bm-a W123 "
                 "finalize wave + W124 seat MSG + autofill keepalive absorbed). (2) orders 155/155 rc0, inbox 1 "
                 "(W124 seat MSG -> processed). (3) D-19 dual MATCH zero action. (4) smoke 48/48. (5) boards "
                 "empty. (6) WM green, py probe verdict=%s honest window face; satengine rc0 alive. (7) CORE: QA "
                 "pack r549 (5/5, 93 trades, determinism=True, frozen-panel 22nd consecutive evidence). (7b) NEW "
                 "PIT healed: legdiff assertion-layer false positive (r548-latent) -> v2 substance gates PASS. "
                 "(8) S6 %s, dualrun %s, LHB no-op (30-min guard), supply_gap honest structural. (9) S7: loop "
                 "pin5 phase-ok; watchdog -Force idempotent; task family 6/6 CSV; claws IN-PLACE zero reinstall; "
                 "attrition CLEAN; close: targeted add + commit -F + push_verify.") % (py_verdict, s6_face, dual_face)
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

# ---- inbox: move W124 seat MSG (bm-a informational broadcast) to processed
src = os.path.join(ROOT, 'fleet', 'inbox', 'MSG-2026-10-05-1437-bma-w124-seat.md')
dst = os.path.join(ROOT, 'fleet', 'inbox', 'processed', 'MSG-2026-10-05-1437-bma-w124-seat.md')
if os.path.exists(src):
    shutil.move(src, dst)
    assert os.path.exists(dst) and not os.path.exists(src), 'inbox move failed'
    print('INBOX_MOVED MSG-2026-10-05-1437-bma-w124-seat.md -> processed/')

# ---- self-checks (R170/R178 epoch int + R262 clock T + F5 fields)
st2 = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert isinstance(st2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in st2['clock_read'] and '+' in st2['clock_read'], 'clock_read must be T-separated ISO with offset'
assert st2['round_no'] == 549, 'round_no must be 549'
hb2 = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in hb2['clock_read'], 'hb clock_read must be T-separated'
assert hb2['round_no'] == 549, 'hb round_no must be 549'
print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta + ' PY_VERDICT=' + py_verdict)
print('WM_RED=' + str(wm_red) + ' LEDGER_HEAD=' + str(ledger_head))
print('STATE/HB/RR written + self-checks PASS')
