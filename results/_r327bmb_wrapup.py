# -*- coding: utf-8 -*-
"""r327 bm-b wrapup: CODELY S4 entry + round_reports r327 line + state.json r327 + heartbeat refresh, all UTF-8/LF-safe with self-verify assertions."""
import io, json, time, datetime

now = datetime.datetime.now().astimezone()
ts_hhmm = now.strftime('%H:%M')
ts_iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')  # +0800 -> need colon: 2026-09-27T13:50:00+08:00
clock_read = now.isoformat(timespec='seconds')  # native T-separator with offset
assert 'T' in clock_read, 'clock_read must be T-separated'

# ---------- 1) CODELY.md S4 append (one line, LF) ----------
codely_entry = ("- [2026-09-27 13:5x r327 bm-b] 坑律：**org_chart 表列刷新（KPI/mandate 列）后 town.html 楼栋详情面板须同轮关键词 grep 核对——文档内勘注「详情面板对齐本表」声明不代后续列刷新的实盘同步**——r277 勘注（09-26）与 v6 KPI 列刷新（同日 T-83 s3 GM 亲执）两写手不相见→研究楼详情缺 v6 面（正交成员供给数+五线供给覆盖）1 天无人察觉；r327 grep 零命中实证后最小补一行 dim KPI 行（工程部 KPI 行范式）+内联 JS 提取 node --check 过闸。正典=org_chart 任何列刷新轮=同轮带 town.html 面板 grep 核对面（同族律=r321 skill 双副本同步断链）。指针=results/_r327bmb_town_js_extract.js+round_reports r327 行。\n")
with io.open('CODELY.md', 'ab') as f:
    d = io.open('CODELY.md', 'rb').read()
    if d and not d.endswith(b'\n'):
        f.write(b'\n')
    f.write(codely_entry.encode('utf-8'))
size_after = len(io.open('CODELY.md', 'rb').read())
assert size_after <= 10240, 'CODELY.md over 10KB hard line: %d' % size_after
print('CODELY.md appended, size=%d (<=10KB hard line ok)' % size_after)

# ---------- 2) round_reports.md r327 append (one line, LF) ----------
rr_line = (
 "2026-09-27T13:5x+08:00 | r327 bm-b | dept:舰队+工程 | 水位=绿：red=false@13:30:13 lane healthy；probe 13:45:33 verdict=insufficient_history 窗重置中（n=2·span 10.7min）=诚实披露·板 0 open+bandit 0 open+bars 在位+sina A1 重拉在飞 bm-a 车道 49.0%@13:01 ETA~15:02=合法 idle 白名单 | did: (1) S0 pull --rebase FF 零冲突（bm-c r83 dashpair 修复面落地） (2) 并发体普查：round.lock pid17736=本会话 launcher ancestry 直连·codely 4572=Minigame sibling·零 Bigmoney 双轮 (3) S0.5 轮首双扫 orders 96/96 零未回执（_r327bmb_orders_scan.py·文件名全日期式修正）·决策审核面 firm\\DECISIONS.md 零 09-27 行+集团 ..\\..\\docs\\decisions.md 缺位=诚实 no-op（P-32 先例） (4) S1 smoke 25/25 (5) S2 双板=job_list 0+fleet tasks 0 open（93 票=63 done+30 claimed 他机长活） (6) S3 主题闭环：town.html 详情对齐 org_chart v6 收口——10 楼 mandate 行逐楼审计全对齐·唯一缺口=研究楼详情缺 v6 KPI 面（正交成员供给数·五线供给覆盖 grep 零命中实证）→最小补一行 dim KPI 行（工程部范式）→内联 JS 28725B 提取 node --check PASS+关键词在盘断言（_r327bmb_town_js_extract.js） (7) S6 29/29 rc=0（_r325bmb_s6_chain.ps1 原样复用·链板=_r327bmb_s6_chain.log；周日 no-new-bar 法定形态 live/t35v/t24paper 三条件腿合法跳；regime ORANGE shadow asof 09-24 hs300<MA200+breadth 0.77 双触发如实；t24 promo 0/22 NOT-ELIGIBLE 合法；astock/rev_osc 面板新鲜 no-op；他机车道诚实 no-op 全列） (8) 迁移窗只读探针：v2.2 armed precheck waiting（Tuanjie 三进程+cmd-holder 28696 拦·journal 分钟心跳 13:4x 活）·E:\\Minigame 在·E:\\Fluxgroup 空壳·窗至 09-29 12:00·勿双 arm (9) S4 坑律一条入册（org_chart 列刷新→town 面板同轮核对律·同族=r321） | evidence: node --check PASS+S6 29x rc=0 链板+smoke 25/25+orders 96/96 轮首/收尾双扫 | 下轮: sina 重拉终态窗 ~15:0x→results\\sina_mf_update_status.json complete+N≥250 开工门开（MSG-1210 bm-b 立场正典·r325/r326 报告 N≥50 系笔误勘正）即起草 sina-construct 四档因子族 prereg（PREREG_TEMPLATE 起·三线三判例·机械三件套）；周一 09-28 09:15 T-91 s3 首队列+15:30 T-87 astock 首拉+新 bar 全链接力；10-01 月首轮三件套+REGIME_GUARD v3 日期门；R330 5x HANDOVER\n")
d = io.open('logs/iteration-loop/round_reports.md', 'rb').read()
n_before = d.count(b'\n')
with io.open('logs/iteration-loop/round_reports.md', 'ab') as f:
    if d and not d.endswith(b'\n'):
        f.write(b'\n')
    f.write(rr_line.encode('utf-8'))
n_after = io.open('logs/iteration-loop/round_reports.md', 'rb').read().count(b'\n')
assert n_after == n_before + 1, 'round_reports line delta != +1: %d->%d' % (n_before, n_after)
print('round_reports.md appended, lines %d->%d' % (n_before, n_after))

# ---------- 3) state.json round_no -> 327 ----------
state = json.load(io.open('logs/iteration-loop/state.json', encoding='utf-8'))
assert state['round_no'] == 326, 'unexpected round_no: %r' % state['round_no']
state.update({
    'round_no': 327,
    'did': 'R327: town.html research-building v6 KPI row landed (org_chart v6 face aligned, node --check PASS) + orders 96/96 double-scan + S6 29/29 + smoke 25/25 + migration window read-only probe (v2.2 armed waiting)',
    'verdict': 'green',
    'next': 'sina-construct prereg draft when sina_mf panel complete+N>=250 gate opens (repull ETA ~15:02, MSG-1210 canon; r325/r326 report N>=50 was a typo, corrected); Mon 09-28 T-91 s3 09:15 + T-87 astock 15:30 first pull + new-bar chain; 10-01 monthly trio + REGIME_GUARD v3 date gate; R330 5x HANDOVER',
    'last_round_ts': '2026-09-27T13:5x+08:00',
    'last_result': 'ok',
    'current_task': 'idle (round 327 closed: town v6 KPI alignment + S6 29/29; waiting sina panel complete+N>=250 gate -> sina-construct prereg + Mon T-91/T-87 chain)',
    'updated_at': now.strftime('%Y-%m-%dT%H:%M+08:00'),
    'last_seen': now.strftime('%Y-%m-%dT%H:%M+08:00'),
    'ts': now.strftime('%Y-%m-%d %H:%M:%S'),
})
with io.open('logs/iteration-loop/state.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
chk = json.load(io.open('logs/iteration-loop/state.json', encoding='utf-8'))
assert chk['round_no'] == 327
print('state.json round_no 326->327 written+reparse ok')

# ---------- 4) heartbeat bm-b.json ----------
hb = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
epoch = int(time.time())
hb.update({
    'last_seen': now.strftime('%Y-%m-%dT%H:%M+08:00'),
    'heartbeat_epoch_utc': epoch,
    'clock_read': clock_read,
    'current_task': 'idle (round 327 closed: town.html v6 KPI row landed node-check PASS + S6 29/29; waiting sina panel complete+N>=250 gate -> sina-construct prereg + Mon T-91 s3 09:15 + T-87 15:30 first pull)',
    'cpu_cores': 16,
    'free_ram_gb': 13.3,
    'gpu_free_vram_gb': 6.78,
    'total_ram_gb': 25.7,
    'cpu_util_pct': 1.0,
    'round_no': 327,
    'verdict': 'healthy',
    'cores': 16,
    'idle_ram_gb': 13.3,
    'gpu_free_vram_mb': 6942,
    'idle_ram_mb': 13619,
    'gpu_idle_vram_mb': 6942,
    'gpu_idle_vram_gb': 6.78,
    'cpu_pct': 1.0,
    'round': 327,
    'free_ram_mb': 13619,
    'loop_round': 327,
})
with io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert isinstance(chk2['clock_read'], str) and 'T' in chk2['clock_read'], 'clock_read must be T-separated'
assert chk2['round_no'] == 327 and len(chk2['orders_ack']) == 96
print('heartbeat written+reparse ok: epoch=%d(int) clock=%s round_no=%d ack=%d' % (chk2['heartbeat_epoch_utc'], chk2['clock_read'], chk2['round_no'], len(chk2['orders_ack'])))
print('WRAPUP_ALL_OK')
