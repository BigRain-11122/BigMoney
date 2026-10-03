# -*- coding: utf-8 -*-
# r431 bm-c S7 wrap: state-bm-c.json + heartbeat + round report ledger line.
import json, time, datetime, psutil, sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
STATE = REPO + r'\state-bm-c.json'
HEART = REPO + r'\fleet\machines\bm-c.json'
REPORT = REPO + r'\round_reports-bm-c.md'

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('%z')[:-2] + ':' + now.strftime('%z')[-2:]
epoch = int(time.time())
cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
vm = psutil.virtual_memory()
idle_ram = round(vm.available / 1e9, 1)

DID = ("r431 bm-c: WM 绿（red=false lane healthy·21:37 probe）。(1) D-06 POST-SPLIT INCREMENT SWEEP + FLOW-SINK DELIVERED"
 "（T-144(c) 主产出）：4 热层坑律 verbatim 入域件（pit-spawn +2：r422 三代执行体连环斩首收养律/r426 多子进程链驱动器"
 "禁经 CreateNoWindow 包装器点火律；pit-git +1：r423 merge 窗三连坑〔origin 残留 marker 全仓扫+porcelain UU 全量扫+"
 "push 前三 fetch 复核〕；pit-tooling +1：r629 rehearsal/harness 镜像=调用点守卫复刻律）+ r628 bm-b §4 回执流水下沉"
 " archive 202610.md r431 节+冷层指针行（r444 范式）+3 域指针 receipt 扩展；CODELY.md 30442->25418B=首次低于 D-06 "
 "≤30KB 主件目标线；byte recon delta 5024==removed 5793−ext 503−coldptr 266；zero-loss 独立复核 10/10+utf-8 strict"
 "+lone-CR=0；surgical numstat CODELY 4+/8-·pit-git 3+/0-·pit-tooling 3+/0-·pit-spawn 5+/1-（r625 no-newline 位序对"
 "·内容字节恒等）·archive 6+/0-；receipt results/_r431bmc_pit_sweep.json+脚本 _r431bmc_sweep.py；+1 pit-ps 直写"
"（包装器多行输出单一字符串项坑·本窗实弹）_r431bmc_ticket_ps.py；T-144 progress_r431_bmc 落账。(2) W2 FINALIZE "
"BURN POLL：PID 31276 alive（本轮 cpu 6848->7565s·mem 254MB）·harness probe AWAITING exit 3 诚实回执（adoption "
"at landing per r422 law·deadline <=10-06·O-2115 acceptance 10-08）。(3) S0：churn-absorb commit 9fd331a03+rebase"
" bm-a r643 x3；S0.5 orders 152/152 零差集；D-19 4167B784 MATCH；GORDERS 68947C17 MATCH（零消费）。(4) S1 smoke "
"47/47 PASS；satengine rc=0 活；S6 canonical 37/37 rc=0（NON-ZERO none·dualrun ZERO-DRIFT streak 32·daily_report "
"REPORT-2026-10-03 五面+LIVE-2026-10-03 双子落盘·fund_premium 周末诚实 no-op）。(5) S7：attrition CLEAN rc0·"
"claws/loop/watchdog 自愈 4/4；呈报：pit-git 107KB 超 D-06 域件 ≤30KB 目标=收口窗子拆分裁定议程。剩余=D-06 收口"
"（10-07）：10-03 午后增量批（r627/r630/r631-bma/r631-bmb/r632·r633=活跃案留热层）+pit-data CRLF 裁定+流水下沉余面"
"+终局对账。本地未达 origin commit 数=0（push 后 fetch 自证）。")

VERIFY = ("sweep receipts (_r431bmc_pit_sweep.json + 独立复核 10/10 + numstat surgical 5 件全对账 + pit-spawn hunk "
"-17/+17,5 r625 位序对内容恒等实证)；smoke 47/47；W2 probe AWAITING exit 3 (PID 31276 alive cpu=7565s mem=254MB)；"
"S6 37/37 rc0 NON-ZERO none (log _r431bmc_s6_log.txt·dualrun streak 32)；orders 152/152·D19 4167B784 MATCH·"
"GORDERS 68947C17 MATCH；attrition CLEAN rc0；S7 4/4 自愈（loop pin=5·watchdog·pre-commit/pre-push claws）；"
"epoch int 实证+clock T 分隔实证")

NEXT = ("(a) r432+: poll burn via python results/_r430bmc_w2_adopt.py probe -> if w2_judge.json landed: ADOPTION-RECEIPT "
"-> adapt _r426bmc_close.py template (count->replace->target-line-assert trio per r429 pit) + idempotent finalize "
"no-op check -> commit product + deferred burn log atomically, deadline <=10-06; O-2115 acceptance evidence pack "
"10-08; (b) D-06 closure 10-07: 10-03 午后热层增量批 sweep (r627/r630/r631-bma/r631-bmb/r632; r633 active-case stays) "
"+ pit-data CRLF-face decision + pit-git 107KB sub-split ruling + flow-sinking remainder + final reconciliation; "
"(c) T-143 assembly window post-10-09 (deliverable 10-29); (d) moneyflow GM ruling watch (MSG-1452/1543); "
"(e) W14 lane zero-touch pending GM dual-ruling; (f) bm-a heartbeat staleness watch (fresh 21:02; >3h = GM report).")

CURTASK = ("r431: D-06 increment sweep delivered (4 pits + r628 flow-sink, CODELY 25418B < 30KB); W2 burn poll AWAITING "
"(PID 31276 alive); next: r432+ probe poll -> adopt at landing (deadline <=10-06); D-06 closure 10-07")

# --- state ---
st = json.loads(open(STATE, 'rb').read().decode('utf-8'))
st.update(dict(clock_read=ts, cpu_pct=cpu_pct, current_task=CURTASK, did=DID, idle_ram_gb=idle_ram,
    heartbeat_epoch_utc=epoch, last_round="r431 bm-c: D-06 post-split increment sweep + flow-sink (CODELY 25418B <30KB); W2 burn poll AWAITING; S6 37/37 rc0 streak 32",
    last_round_at=ts, last_round_ts=ts, last_seen=ts, last_ts=ts, round_no=431, updated=ts, updated_at=ts,
    last_decisions_read_at=ts, verify=VERIFY, next=NEXT))
out = json.dumps(st, ensure_ascii=False, indent=1)
json.loads(out)
open(STATE, 'wb').write(out.encode('utf-8'))
chk = json.loads(open(STATE, 'rb').read().decode('utf-8'))
assert chk['round_no'] == 431 and chk['heartbeat_epoch_utc'] == epoch and isinstance(chk['heartbeat_epoch_utc'], int)
assert 'T' in chk['clock_read'] and '+' in chk['clock_read']
print('STATE r431 written (epoch=%d int-verified, clock=%s)' % (epoch, ts))

# --- heartbeat ---
hb = json.loads(open(HEART, 'rb').read().decode('utf-8'))
hb.update(dict(activity_now="r431: D-06 increment sweep delivered (4 pits->pit-spawn/git/tooling + r628 flow-sink->archive; CODELY 25418B below 30KB target) + W2 burn poll AWAITING (PID 31276 alive cpu 7565s)",
    clock_read=ts, cpu_pct=cpu_pct, cpu_util_pct=cpu_pct, cpu_idle_pct=round(100 - cpu_pct, 1),
    current_task=CURTASK, free_ram_gb=idle_ram, idle_ram_gb=idle_ram, ram_free_gb=idle_ram,
    heartbeat_epoch_utc=epoch, last_seen=ts, last_seen_at=ts, updated_at=ts,
    latest_artifact="results/_r431bmc_pit_sweep.json (D-06 sweep receipt: 4 pits + r628 flow-sink, CODELY 30442->25418B) + commit e416635f2 @ " + ts,
    next_milestone="w2_judge.json landing -> adoption same round (harness _r430bmc_w2_adopt.py + close-template trio), deadline <=10-06; O-2115 acceptance 10-08; D-06 full closeout 10-07",
    prod_lanes="MASS_TRIAL_W2-JUDGE finalize burn in flight (PID 31276); adoption harness staged; D-06 closure work in progress (10-03 increment batch done, remainder r627/r630/r631x2/r632 + CRLF + flow-sinking)",
    round_no=431, health="ok", verdict="healthy"))
out = json.dumps(hb, ensure_ascii=False, indent=1)
json.loads(out)
open(HEART, 'wb').write(out.encode('utf-8'))
chk = json.loads(open(HEART, 'rb').read().decode('utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int) and chk['round_no'] == 431
assert 'T' in chk['clock_read']
print('HEARTBEAT r431 written (epoch=%d int-verified)' % epoch)

# --- round report ledger line ---
line = ts + '\t| r431 bm-c\t| ' + DID + '\r\n'
raw = open(REPORT, 'rb').read()
if raw and not raw.endswith(b'\n'):
    raw += b'\r\n'
open(REPORT, 'ab').write(raw.endswith(b'\n') and line.encode('utf-8') or (b'\r\n' + line.encode('utf-8')))
tail = open(REPORT, 'rb').read()
assert ('r431 bm-c' in tail.decode('utf-8', errors='replace').split('\n')[-2] if not tail.endswith(b'\n') else tail.decode('utf-8', errors='replace').split('\n')[-2])
print('REPORT ledger line appended (%dB)' % len(line))
print('S7 WRAP CORE DONE')
