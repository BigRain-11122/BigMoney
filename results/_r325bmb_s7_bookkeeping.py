# -*- coding: utf-8 -*-
"""r325 bm-b S5/S7 bookkeeping: round report line append + state.json round_no->325 + heartbeat refresh.
Byte-faithful newline='' io; epoch int via python int(time.time()); clock_read ISO-8601 with T separator."""
import io, json, time, datetime, ctypes, ctypes.wintypes, platform, os

RR = 'logs/iteration-loop/round_reports.md'
ST = 'logs/iteration-loop/state.json'
HB = 'fleet/machines/bm-b.json'

# --- S5 round report line (tail of file is CRLF form; append with \r\n to match) ---
rr = io.open(RR, encoding='utf-8', newline='').read()
assert rr.endswith('\r\n'), 'rr tail form changed'
ts_now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M') + '+08:00'
LINE = (ts_now + ' | r325 bm-b | dept:舰队+工程 | 水位=绿（red=false@13:00:13 lane healthy·watermark_red red=false；probe 13:15:04 verdict=insufficient_history 窗重积中=诚实态·前 3 连 py_low_board_clear〔12:32/12:43/13:04〕·板 0 open+池 77/77 done+bandit next_pick=claimed-parked MF IC 批等 sina 面板=合法 idle 白名单）| did: '
 '(1) S0 轮首 p1d_gates.json 活态产物脏（13:08 r324 尾 watchdog derive 面）→r120 律定向提交 ce15575f→pull --rebase up-to-date FF 零冲突〔注：r322-324 惯例=stash-dance 保 unstaged 设计态·本轮回 r120 律定向提交=双正典并存面·FF 零冲突零实损如实注记〕 '
 '(2) S0.5 轮首双扫 orders 96/96 零未回执（python 集合差集）·集团 ..\\..\\docs\\decisions.md 缺位=诚实 no-op（P-32 先例） '
 '(3) S1 smoke 25/25 (4) S2 双板=job_list 0+fleet tasks 0 open（93 票全 claimed/done）·post_review 现行红面 r324 已证 0·本轮零新注册 '
 '(5) S3 主闭环=R325 5x HANDOVER 核对轮：_r295bmb_ledger_scan 复跑 79 件 INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0·HEAD=DECISION_CHAIN_E2E_P1 286,541 实读平持（本窗零批 finalize）'
 '+HANDOVER line4 级联刷新（r325 prepend/r320 降级/r280 剪枝〔EOF 增量行全保〕）+文末 r321-325 增量窗行 append·**实弹新坑律首捕：python 文本模式 universal-newlines read 把 CRLF 正典件静默 LF 化=写回全文件假 diff 232 行**'
 '（首跑 git diff 全重写被行数断言当场拦→git checkout 还原→newline=\'\' 字节保真重做 PASS·最终 diff 2+/1-·CRLF 231→232 保真） '
 '(6) S4 坑律入册+水位律当窗热冷整编：r325 坑律条入 CODELY+r312/r320×2 三条旧律 verbatim 外迁 research/memory-archive/202609.md 十三批节（multiset 零丢失断言 PASS·CODELY 9226→7712B ≤10KB 硬线）'
 '——本轮整编脚本断言三连自捕（终结符键不一致×2+方向反×1）全在写后自验面零外泄 '
 '(7) S6 29/29 rc=0（_r325bmb_s6_chain.ps1=r324 谱系 delta=header-only·周日 cutoff 09-24 法定 no-new-bar 形态·live.paper/t35v/t24paper 三条件腿依法跳；audit py 1.2% 旗=[pool_starvation]=供给缺口白名单〔sina 深面板重拉在飞 bm-a 车道〕SUPPLY-NO-BREAK 照办；astock 面板新鲜 no-op=周一 15:30 首拉 armed；t24 promo 0/22 NOT-ELIGIBLE 合法；rev_osc/sina_mf/ths/ah/fp 他机车道诚实 no-op；export-09-24/scorecard/daily_report 幂等再生 faces=4 token=1）'
 '(8) 迁移窗只读探针：v2.2 armed precheck waiting（Tuanjie 编辑器三进程 4736/12588/27660+cmd-holder 28696 拦·journal 分钟心跳 13:13 活）·E:\\Minigame 在·E:\\Fluxgroup 空壳·窗至 09-29 12:00·勿双 arm '
 '(9) S7：S7 收尾双扫 orders 96/96 零未回执+inbox 0 open+state round_no→325+心跳三面（epoch int/clock_read T 面）+schtasks 双源健康（IterationLoop 正在运行=本轮·Watchdog 就绪） '
 '| evidence: HANDOVER 断言 PASS（锚点 8 项）·CODELY multiset PASS（13th batch·7712B）·S6 29x rc=0 板（_r325bmb_s6_chain.log）·ledger 79 件 0 fail 0 dup·smoke 25/25·orders 96/96 双扫 '
 '| 下轮: 周一 09-28 09:15 T-91 s3 首队列入场（SIG/BARS-09-28 到位即 replay）+新 bar 全链接力（daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow〕→t35v→t24×2→aggr→grid 首拍→alloc→export→scorecard→daily_report）+T-87 astock 15:30 首拉实弹；sina 面板 complete+N≥250 门开后 sina-construct prereg 起草（三线三判律）；10-01 月度三件套+REGIME_GUARD v3 日期门；R330 5x\r\n')
rr2 = rr + LINE
io.open(RR, 'w', encoding='utf-8', newline='').write(rr2)
v = io.open(RR, encoding='utf-8', newline='').read()
assert v.endswith('R330 5x\r\n')
assert v.count(LINE) == 1 and len(v.splitlines()) == len(rr.splitlines()) + 1
print('S5 round report appended OK')

# --- S7 state.json round_no->325 ---
s = json.load(io.open(ST, encoding='utf-8-sig'))
assert s['round_no'] == 324, s['round_no']
s['round_no'] = 325
s['did'] = 'R325 5x HANDOVER check (ledger 79 files 0-fail, line4 cascade refresh, EOF increment row) + CODELY 13th-batch hot archival + S6 29/29 + new pitlaw (universal-newlines CRLF)'
s['verdict'] = 'green'
s['next'] = 'Mon 09-28: T-91 s3 first cohort 09:15 + new-bar full chain; T-87 astock 15:30 first daily pull; sina-construct prereg after panel complete+N>=250 gate; 10-01 monthly trio + REGIME_GUARD v3 date gate'
s['last_round_ts'] = ts_now
s['last_seen'] = ts_now
s['updated_at'] = ts_now
io.open(ST, 'w', encoding='utf-8', newline='').write(json.dumps(s, ensure_ascii=False, indent=1) + '\n')

# --- S7 heartbeat refresh (epoch int, clock_read ISO-8601 with T) ---
h = json.load(io.open(HB, encoding='utf-8-sig'))
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.wintypes.DWORD), ('dwMemoryLoad', ctypes.wintypes.DWORD),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_ram_gb = round(m.ullAvailPhys / (1024**3), 1)
epoch = int(time.time())
clock_read = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
h['round_no'] = 325; h['round'] = 325; h['loop_round'] = 325
h['last_seen'] = ts_now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock_read
h['current_task'] = 'idle (round 325 closed: 5x HANDOVER check + CODELY 13th-batch archival; waiting Mon 09-28 T-91 s3 auto-fire + new-bar chain)'
h['verdict'] = 'healthy'
h['idle_ram_gb'] = free_ram_gb; h['free_ram_gb'] = free_ram_gb
h['idle_ram_mb'] = int(m.ullAvailPhys // (1024**2)); h['free_ram_mb'] = int(m.ullAvailPhys // (1024**2))
h['n_orders_ack'] = len(h.get('orders_ack', []))
io.open(HB, 'w', encoding='utf-8', newline='').write(json.dumps(h, ensure_ascii=False, indent=1) + '\n')

# self-verification (R170/R178/R262 law: value AND type AND format)
h2 = json.load(io.open(HB, encoding='utf-8-sig'))
assert isinstance(h2['heartbeat_epoch_utc'], int) and not isinstance(h2['heartbeat_epoch_utc'], bool), 'epoch must be JSON int'
assert 'T' in h2['clock_read'] and '+' in h2['clock_read'], 'clock_read must be ISO-8601 T-separated'
assert h2['round_no'] == 325
s2 = json.load(io.open(ST, encoding='utf-8-sig'))
assert s2['round_no'] == 325
print('S7 state+heartbeat OK: round_no 325 | epoch', epoch, 'int | clock', clock_read, '| free_ram', free_ram_gb, 'GB')
