# -*- coding: utf-8 -*-
"""r326 bm-b S5/S7 bookkeeping: round report line append + state.json round_no->326 + heartbeat refresh.
Byte-faithful newline='' io (r325 pitlaw); epoch int via python int(time.time()); clock_read ISO-8601 T-separated."""
import io, json, time, datetime, ctypes, ctypes.wintypes

RR = 'logs/iteration-loop/round_reports.md'
ST = 'logs/iteration-loop/state.json'
HB = 'fleet/machines/bm-b.json'

# --- S5 round report line (tail of file is CRLF form; append with \r\n to match) ---
rr = io.open(RR, encoding='utf-8', newline='').read()
assert rr.endswith('\r\n'), 'rr tail form changed'
ts_now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M') + '+08:00'
LINE = (ts_now + ' | r326 bm-b | dept:舰队+工程 | 水位=绿（red=false@13:30:13 lane healthy；probe 13:34:54 verdict=py_low_board_clear 合法 idle 白名单=票 0 open+bandit 0 open+bars 在位+池 done 面；sina A1 深重拉在飞 bm-a 车道 49.0%@13:01 ETA~15:02=供给线合法面·其 complete+N≥250 门开即解禁本机 sina-construct prereg）| did: '
 '(1) S0 轮首 p1d_gates.json 活态产物脏（13:30 autofill tick derive 面·date+elapsed_s 两行纯运行时元数据）→r120 律定向提交 5aee006f→pull --rebase up-to-date 零冲突 '
 '(2) 并发体排摸定谳：codely 四进程 census（3660=MiniGameEngineTick 无头导航〔CPU 活=自车道〕·13160=BiuNiYiXia·17356 已逝·25512=本轮）+python 16348=autofill.py tick 算力面+12352=本机 launcher 持 round.lock=r325 判例复现（sibling Minigame loops+autofill·zero Bigmoney dual-round）→单执行体开工 '
 '(3) S0.5 轮首双扫 orders 96/96 零未回执（python 集合差集双向空）·决策审核面=firm\\DECISIONS.md 零 09-27 行+集团 ..\\..\\docs\\decisions.md 缺位=诚实 no-op（P-32 先例） '
 '(4) S1 smoke 25/25 (5) S2 双板=job_list 0+fleet tasks 0 open（93 票=63 done+30 claimed）·post_review 每 id 最新行口径 0 NO/X·bandit next_pick=claimed-parked MF IC 批等 sina 面板 '
 '(6) S3 主闭环=周一 09-28 bm-b 车道 pre-flight：rev_osc_signal_export selftest ALL LEGS PASS（judged 镜像常量 import 零重实现+BARS 5 字段行+B7b SIG 键契约）+update_astock_daily selftest all guard cases PASS·面板健康双读（astock complete=true 5217/5228 per_files cutoff 2026-09-24〔09-25 中秋法定休市=周内 bar 完备〕周一 15:30 首拉 armed；SIG/BARS-09-24 在位+export_state 幂等锚活〔panel_mtime 1790463118〕）——周一 09:15 T-91 s3 首队列+15:30 新 bar 全链的 bm-b 供给面零风险定谳 '
 '(7) S6 29/29 rc=0（_r325bmb_s6_chain.ps1 谱系原样复用·周日 no-new-bar 法定形态三条件腿依法跳·audit v2.3 py 0.9% 旗 0·market_clock CALL-2026-09-24 cell=O·t24 promo 0/22 NOT-ELIGIBLE 合法·他机车道诚实 no-op 全列·export/scorecard/daily_report 幂等再生 faces=4 token=1） '
 '(8) S4 记忆=零新条目（无新坑·r325 判例复现无增量=复述禁律不入册） '
 '(9) 迁移窗只读探针：v2.2 armed precheck waiting（Tuanjie 三进程 4736/12588/27660+cmd-holder 28696 拦·journal 分钟心跳 13:35:56 活）·E:\\Minigame 在·E:\\Fluxgroup 空壳 0 件·窗至 09-29 12:00·勿双 arm '
 '(10) S7：收尾双扫 orders 96/96 零未回执+inbox 0 open+schtasks 三任务在册（IterationLoop 正在运行=本轮·Watchdog 就绪·Autofill 正在运行）+state round_no→326+心跳三面（epoch int/clock_read T 面/round_no 326） '
 '| evidence: S6 29x rc=0 链板·selftest 2/2 PASS（rev_osc ALL LEGS+astock all guard cases）·smoke 25/25·orders 96/96 双向双扫·decisions 零新行·migration journal 活心跳 '
 '| 下轮: 周一 09-28 09:15 T-91 s3 首队列入场+15:30 T-87 astock 首拉+新 bar 全链接力（daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow〕→t35v→t24×2→aggr→grid→alloc→export→scorecard→daily_report）；sina A1 重拉终态窗 ~15:0x→complete+N≥250 门开即起草 sina-construct prereg（三线三判律·机械三件套）；10-01 月度三件套+REGIME_GUARD v3 日期门；R330 5x HANDOVER\r\n')
rr2 = rr + LINE
io.open(RR, 'w', encoding='utf-8', newline='').write(rr2)
v = io.open(RR, encoding='utf-8', newline='').read()
assert v.endswith('R330 5x HANDOVER\r\n')
assert v.count(LINE) == 1 and len(v.splitlines()) == len(rr.splitlines()) + 1
print('S5 round report appended OK')

# --- S7 state.json round_no->326 ---
s = json.load(io.open(ST, encoding='utf-8-sig'))
assert s['round_no'] == 325, s['round_no']
s['round_no'] = 326
s['did'] = 'R326 maintenance round: Mon 09-28 bm-b-lane pre-flight (rev_osc selftest + astock_daily selftest ALL PASS, panels healthy) + concurrent-body census (zero Bigmoney dual-round) + S6 29/29'
s['verdict'] = 'green'
s['next'] = 'Mon 09-28: T-91 s3 first cohort 09:15 + T-87 astock 15:30 first daily pull + new-bar full chain; sina-construct prereg after sina_mf panel complete+N>=250 gate (repull ETA ~15:02); 10-01 monthly trio + REGIME_GUARD v3 date gate; R330 5x HANDOVER'
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
h['round_no'] = 326; h['round'] = 326; h['loop_round'] = 326
h['last_seen'] = ts_now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock_read
h['current_task'] = 'idle (round 326 closed: Mon 09-28 bm-b-lane pre-flight all-PASS + S6 29/29; waiting Mon T-91 s3 09:15 + T-87 15:30 first pull + new-bar chain)'
h['verdict'] = 'healthy'
h['idle_ram_gb'] = free_ram_gb; h['free_ram_gb'] = free_ram_gb
h['idle_ram_mb'] = int(m.ullAvailPhys // (1024**2)); h['free_ram_mb'] = int(m.ullAvailPhys // (1024**2))
h['n_orders_ack'] = len(h.get('orders_ack', []))
io.open(HB, 'w', encoding='utf-8', newline='').write(json.dumps(h, ensure_ascii=False, indent=1) + '\n')

# self-verification (R170/R178/R262 law: value AND type AND format)
h2 = json.load(io.open(HB, encoding='utf-8-sig'))
assert isinstance(h2['heartbeat_epoch_utc'], int) and not isinstance(h2['heartbeat_epoch_utc'], bool), 'epoch must be JSON int'
assert 'T' in h2['clock_read'] and '+' in h2['clock_read'], 'clock_read must be ISO-8601 T-separated'
assert h2['round_no'] == 326
s2 = json.load(io.open(ST, encoding='utf-8-sig'))
assert s2['round_no'] == 326
print('S7 state+heartbeat OK: round_no 326 | epoch', epoch, 'int | clock', clock_read, '| free_ram', free_ram_gb, 'GB')
