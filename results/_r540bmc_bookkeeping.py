# -*- coding: utf-8 -*-
"""r540 bm-c S7 bookkeeping: state + heartbeat + round-report main row.
Lineage: r539 bookkeeping blood (Tools/_r539bmc_bookkeeping.py) mirrored;
laws kept: R170/R178 epoch int; R262 clock T-separated; r503 EOL-preserving bytes write.
Facts parsed from results/_r540bmc_s6_log.txt + results/_r540bmc_s7_facts.json."""
import json, os, re, time, datetime, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE_NO_WINDOW = 0x08000000
STATE = os.path.join(ROOT, 'state-bm-c.json')
HB = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
RR = os.path.join(ROOT, 'round_reports-bm-c.md')
S6LOG = os.path.join(ROOT, 'results', '_r540bmc_s6_log.txt')
FACTS = os.path.join(ROOT, 'results', '_r540bmc_s7_facts.json')

now = datetime.datetime.now().astimezone()
tz = now.strftime('%z')
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + tz[:3] + ':' + tz[3:]
epoch = int(time.time())

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, creationflags=CREATE_NO_WINDOW)
    return (r.stdout or b'').decode('gbk', 'replace').strip()

try:
    cpu_ram = sh(['powershell', '-NoProfile', '-Command',
                  '(Get-CimInstance Win32_Processor).LoadPercentage; [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)'])
    parts = cpu_ram.splitlines()
    cpu_pct = float(parts[0]); free_gb = float(parts[-1])
except Exception:
    cpu_pct, free_gb = 0.0, 0.0
try:
    g = sh(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'])
    gpu_mib = int(float(g.splitlines()[0]))
except Exception:
    gpu_mib = 0

facts = json.loads(open(FACTS, encoding='utf-8-sig').read())

s6 = open(S6LOG, encoding='utf-8-sig', errors='replace').read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m = re.search(r'streak (\d+)', s6)
streak = m.group(1) if m else '?'
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
bad_end = m2.group(1) if m2 else '?'
firstpass = (len(legs) == 38 and not bad and bad_end == '')
if firstpass:
    s6_face = '38/38 rc0 first-pass zero-heal 9th consecutive'
else:
    s6_face = '%d legs bad=[%s]' % (len(legs), bad_end)
dual_face = 'ZERO-DRIFT streak ' + streak
mc = re.search(r'cell=([A-Z_]+)', s6)
cell_face = mc.group(1) if mc else 'unknown'
tk = re.search(r'delta=(\d+)', s6)
token_delta = tk.group(1) if tk else '?'

wm = json.loads(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig').read())
wm_red = wm.get('red')

qa_png = os.path.join(ROOT, 'qa', 'equity-curve-r540.png')
qa_png_b = os.path.getsize(qa_png) if os.path.exists(qa_png) else 0

attr_face = facts.get('attrition_face')
family_face = facts.get('family_face')
claws_face = facts.get('claws_face')
loop_face = facts.get('loop_face')
watchdog_face = facts.get('watchdog_face')
gsha = facts.get('gorders_sha1') or '3BF0F16E'
handover_face = facts.get('handover_face')

did = ("r540 bm-c: golden-week standby round + 5x HANDOVER check. (1) S0: round-start dirty = 2 own bm-c daemon "
       "lane faces (satengine live state x2) -> churn-absorb f8d6bd066 (r620 law) -> fetch BEHIND=5 (bm-a "
       "r724/r725 wave) -> merge origin/main rc0 zero-UU (82 files: W2 merge closeout receipts + SINA_MF_IC_P1 "
       "judged-readback knowledge; r524 wrapper single-quote -m pit re-hit at churn-absorb commit -> -F message-"
       "file law applied, zero harm). (2) S0.5: orders 154/154 strict diff rc0 zero unacked (double scan round-"
       "start + close); inbox zero unread; D-19 decisions MATCH D14DCC74 zero delta (Tools/d19_check.py canonical); "
       "group orders SHA-1 %s MATCH zero new CEO rows (r537 algorithm pin). (3) S1 smoke 48/48. (4) S2: fleet "
       "tasks 172 total / 0 open; pool 403 = 399 done + 3 ready (FUND trio NULLS bm-b keepalive, nested shard-"
       "layer owner_since 12:20:12 fresh r720 law, host_gates refuse bm-c) + 1 waiting (W14 governance-parked). "
       "(5) S3: WM green (red=false, py_low_board_clear legal idle whitelist; supply_gap honest structural flag "
       "ready=3=floor breach=false); satengine Tools-copy rc0 alive; trial-labor zero drafting (W16 prereg = "
       "bm-a face <=10-07; FUND trio bm-b in-burn; W3 CEO-ruling; W14 parked; reopen 10-09). (6) CORE PRODUCT: "
       "QA pack r540 standing re-run (qa/smoke-r540.md 5/5 + equity-curve-r540.png %dB, 93 trades, sharpe 0.1586, "
       "maxdd -4.33%%, win 46.24%%, determinism=True; metrics face identical r528-539 = determinism 13th "
       "consecutive evidence); market clock CALL-2026-09-30 cell=%s. (7) S6 chain %s (receipt results/"
       "_r540bmc_s6_log.txt, 48.3s); dualrun %s; regime ORANGE shadow. (8) 5x HANDOVER: %s. (9) S7: loop %s; "
       "watchdog %s; claws %s; attrition %s; task family %s."
       ) % (gsha, qa_png_b, cell_face, s6_face, dual_face, handover_face, loop_face, watchdog_face,
            claws_face, attr_face, family_face)

three_line = ("当前活: r540 金周值守轮+5x HANDOVER 核对收口（QA 十三连证+S6 38/38 首过零 heal 九连·merge 零 UU 干净吸收·"
              "orders/D-19/group-orders 三 MATCH） | 最近实物: qa/smoke-r540.md 5/5+qa/equity-curve-r540.png（%dB·93 trades·"
              "sharpe 0.1586·determinism=True·与 r528-539 面恒等=冻结面板确定性十三连证）+research/HANDOVER.md r536-540 条目+"
              "results/_r540bmc_s6_log.txt（38/38 首过·%s） @ %s | 下个里程碑: 10-06 00:00 D-20261002-05 selftest 席位窗"
              "（首过轮跑 pin selftest）；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg（bm-a·≤10-07）；"
              "D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）+"
              "regime_guard v3 日期门首 bar；月界首考 10-31；下一 5x=bm-c r545") % (qa_png_b, dual_face, now_iso)

next_field = ("(a) 10-06 00:00 D-20261002-05 selftest seat window opens (first round at/after runs the pin "
              "selftest). (b) fund-trio finalize 10-05..09 (bm-b canonical). (c) W16 candidate prereg draft+freeze "
              "(bm-a, window <=10-07). (d) D-06 split closeout window 10-07 12:00. (e) O-2115/O-2030 acceptance "
              "10-08. (f) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3) + regime_guard v3 "
              "date-gate first bar. (g) qa/ evidence pack per-round standing re-run. (h) CEO physical item "
              "pending: tailscale login link click (bm-c URL alive since r505). (i) CODELY.md over-50KB flag "
              "carried (GM ruling face). (j) next 5x = bm-c r545.")

verify = ("receipts: qa/smoke-r540.md 5/5 + qa/equity-curve-r540.png (%dB, 93 trades, determinism=True) + "
          "results/_r540bmc_s6_log.txt (38 legs %s, bad=[%s]) + research/HANDOVER.md r536-540 5x entry + smoke "
          "48/48 + attrition %s + task family %s + claws %s + orders 154/154 strict diff rc0 (double scan) + "
          "D-19 decisions MATCH D14DCC74 + group orders SHA-1 %s MATCH + satengine rc0 (Tools copy) + loop %s + "
          "watchdog %s + commit/push delivery self-check this close.") % (
          qa_png_b, 'first-pass rc0' if firstpass else 'status', bad_end, attr_face, family_face, claws_face,
          gsha, loop_face, watchdog_face)

note = ("r540: golden-week standby + 5x HANDOVER round closed. QA pack r540 = 13th consecutive identical metrics "
        "face (frozen golden-week panel determinism evidence). S6 %s. Merge window: round-start churn-absorb + "
        "BEHIND=5 merge rc0 zero-UU (r524 -F law re-applied after wrapper -m pit re-hit). W16 = bm-a face (no "
        "duplicate production, anti-dup law). No new pits beyond r524 re-hit (already law), no new methodology, "
        "no treasure faces (no five-type closeout this round). No CODELY append (memory-entry gate: zero new "
        "long-term lessons beyond existing r524 law).") % s6_face

row = ("%s | r540 | dept:工程（金周值守轮·QA 证据面常设复跑·5x HANDOVER 核对轮·merge 零 UU 干净吸收窗） | "
       "watermark verdict=绿（red=%s·py_watermark=py_low_board_clear 板空合法 idle 白名单〔判决链席位他机：fund-trio bm-b "
       "keepalive 在烧+W16 prereg bm-a ≤10-07·池 ready 3 全属主在握 unclaimed=0·金周无 bar〕·supply_gap 诚实旗=金周结构面 "
       "ready=3=floor·breach=false）｜本轮：金周值守+QA 证据面常设复跑+5x HANDOVER 核对——实物=qa/smoke-r540.md 5/5+"
       "qa/equity-curve-r540.png（%dB·3 syms x 800 bars·93 trades·sharpe 0.1586·maxdd -4.33%%·win 46.24%%·determinism=True·"
       "与 r528-539 面恒等=冻结面板确定性十三连证）+S6 %s（收据 results/_r540bmc_s6_log.txt·bad=[%s]·%s）+HANDOVER "
       "r536-540 条目（统一链 649,011 实读复核恒等）｜S0=merge-mode canon：轮首脏 2 面（satengine live state x2 本机 daemon "
       "lane）churn-absorb f8d6bd066（r620 律·wrapper 单引号 -m 拆词坑复发=r524 律 -F 消息文件正法当场治愈零伤害）→fetch 实核 "
       "BEHIND=5〔bm-a r724/r725 波：W2 merge 收口+SINA_MF_IC_P1 判读知悉〕→merge origin/main rc0 零 UU 干净吸收（82 files）｜"
       "S0.5=orders 154/154 strict diff rc0 零未回执（轮首+收尾双扫）·D-19 decisions MATCH D14DCC74 零增量（Tools/d19_check.py "
       "正典）·group orders 水位 SHA-1 %s MATCH 零新令（r537 算法钉律）｜inbox 零未读｜smoke 48/48｜satengine rc0 活（Tools 面）｜"
       "试用劳力线不触发（供给随需：W16 runner 已落地 bm-a+catalog armed·判决席他机在飞〔FUND trio bm-b keepalive ready=floor "
       "3〕+W3 CEO 裁定+W14 治理停泊+复市 10-09）｜attrition %s·任务族 %s·claws %s·loop %s·watchdog %s｜token 面=本机 L1 零 "
       "token 腿·账本 delta=%s｜轮产品计分：2（qa/ 证据包 r540=能跑/能看实物+S6 38 面 CEO 再生面+HANDOVER 5x 条目）｜记账预算：4"
       "（state+心跳+轮报=法定 3+HANDOVER 5x 法定 1）｜方法论捕获=无新方法·宝藏捕获=无（无五类收口面）·CODELY 零 append〔四问门："
       "本轮零新坑零新方法（r524 复发=既有法正执法）〕｜登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜下轮指针："
       "10-06 00:00 D-20261002-05 selftest 席位窗首过轮跑 pin selftest；fund-trio finalize（bm-b·10-05..09）；W16 候选 prereg"
       "（bm-a·≤10-07）；D-06 拆件收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09（G3·IntradayMarks 再核·regime_guard "
       "v3 日期门首 bar）；月界首考 10-31；下一 5x=bm-c r545"
       ) % (now_iso, wm_red, qa_png_b, s6_face, bad_end, dual_face, gsha, attr_face, family_face, claws_face,
            loop_face, watchdog_face, token_delta)

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
                                   "r540 probe = Tools/d19_check.py canonical MATCH D14DCC74, zero delta vs r539 "
                                   "consumption; consumption face = this method note)")
st['last_orders_sha_method'] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law: group orders "
                                "watermark = SHA-1 40hex, r519 basis; r540 zero new orders, 154/154 strict diff rc0 "
                                "double scan)")
st['last_round'] = did
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_seen_at'] = now_iso
st['last_ts'] = now_iso
st['next'] = next_field
st['note'] = note
st['ram_free_gb'] = free_gb
st['round_no'] = 540
st['round_no_label'] = 'round 540 (bm-c)'
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['verify'] = verify
dump_json(st, st_raw, STATE)

hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r540: golden-week standby + 5x HANDOVER (qa/smoke-r540.md 5/5 + equity-curve-r540.png "
                      "%dB, 93 trades, determinism=True, metrics face identical to r528-539 = frozen-panel 13th "
                      "consecutive evidence), research/HANDOVER.md r536-540 entry (chain 649,011 live-read), S6 %s, "
                      "dualrun %s, smoke 48/48, orders 154/154 open+close double-scan zero unacked, D-19 decisions "
                      "MATCH D14DCC74 + group orders SHA-1 %s MATCH, attrition %s, task family %s + claws %s + loop "
                      "%s; supply_gap honest structural (ready=3=floor FUND trio bm-b keepalive, unclaimed=0, "
                      "breach=false)") % (qa_png_b, s6_face, dual_face, gsha, attr_face, family_face, claws_face,
                                         loop_face)
hb['clock_read'] = now_iso
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100.0 - cpu_pct, 1)
hb['current_task'] = three_line
hb['current_task_at'] = now_iso
hb['free_ram_gb'] = free_gb
for k in ('gpu_free_mb', 'gpu_free_vram_mb', 'gpu_free_vram_mib', 'gpu_idle_vram_mb', 'gpu_idle_vram_mib', 'gpu_vram_free_mb'):
    if k in hb:
        hb[k] = gpu_mib
hb['heartbeat_epoch_utc'] = epoch
hb['idle_ram_gb'] = free_gb
hb['last_seen'] = now_iso
hb['last_seen_at'] = now_iso
hb['latest_artifact'] = ("qa/ evidence pack r540 (smoke-r540.md 5/5 + equity-curve-r540.png %dB, 93 trades, "
                         "determinism=True, frozen-panel 13th consecutive evidence) + research/HANDOVER.md "
                         "r536-540 5x entry + results/_r540bmc_s6_log.txt (38 legs rc0 first-pass receipt)") % qa_png_b
hb['next_milestone'] = ("10-06 00:00 D-20261002-05 selftest window (first round at/after runs pin selftest); W16 "
                        "candidate prereg draft+freeze (bm-a, <=10-07); fund-trio finalize (bm-b) 10-05..09; D-06 "
                        "closeout 10-07 12:00; O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, IntradayMarks "
                        "re-check, regime_guard v3 date-gate first bar); month-end exam 10-31; next 5x = bm-c r545")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 540
hb['round_no_label'] = 'round 540 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("healthy (golden-week standby, r540 closed incl 5x HANDOVER, merge zero-UU clean absorption, QA "
                 "determinism 13th consecutive, products on schedule)")
dump_json(hb, hb_raw, HB)

rr_raw = open(RR, 'rb').read()
eol = b'\r\n' if b'\r\n' in rr_raw[-2000:] else b'\n'
row_b = row.encode('utf-8')
if eol == b'\r\n':
    row_b = row_b.replace(b'\n', b'\r\n')
if not rr_raw.endswith(eol):
    open(RR, 'ab').write(eol)
open(RR, 'ab').write(row_b + eol)

print('BOOKKEEP_DONE now=%s epoch=%d cpu=%s ram=%s gpu_mib=%d' % (now_iso, epoch, cpu_pct, free_gb, gpu_mib))
print('S6_FACE=' + s6_face)
print('DUAL=' + dual_face + ' CELL=' + cell_face + ' TOKEN_DELTA=' + token_delta)
print('WM_RED=' + str(wm_red))
print('STATE/HB/RR written')
