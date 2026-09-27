import json
import time
import io

now = time.strftime('%Y-%m-%d %H:%M:%S')
iso = time.strftime('%Y-%m-%dT%H:%M:%S') + time.strftime('%z')
iso = iso[:-2] + ':' + iso[-2:]  # +08:00 form

# --- 1. round report line (bm-a file, LF) ---
rr = 'logs/iteration-loop/round_reports-bm-a.md'
line = (
    "2026-09-27 17:09 | r338 | 水位绿(lane=healthy red=false py尾 0.3/0.2/1 池 SINA done-flip 后 ready=0 board 0 open=法定idle带; "
    "bandit advisory=claimed moneyflow IC 等 EM 面板 self-heal 16:31 spawn 在途) | 做了: S0 pull--rebase 快进 bcdd81b8(bm-c r87-89+addendum 折叠态) "
    "+ bm-c-r87/88/89 内容子集核验(entry级 CODELY=stub↔全文双形态 archive零缺行=已折叠; bm-c r90 同窗已GC三分支) + bm-a-r336 自有分支内容核验后GC(D-20260925-01③ fold后GC义务) | "
    "S0.5: orders 96/96 零未回执(轮首) + decisions 尾读 D-09 已闭口(BigMoney 回执在案)/D-10 HQ即办/C-20260927-01 委员会件=第3席财务资源席意见已出(F-20260927-02) 零新动作 | "
    "S1 smoke 25/25 | S3 主闭环=SINA-CONSTRUCT-P1 判定面收口: 普查双燃(16:40 pid41360 target_met=True + 16:50 pid44968 pre-flip盲窗重复=r312 keep-last/T19 r80 先例; 链恒等286546→286551单计) "
    "**全族判负 5/5 REJECT**(V1 |IS IC|0.0033-0.0078<0.02地板/V2 |IS IR|0.051-0.094≪0.30/V3仅TIER_r2/D6 EM-mf跨族拒TIER_r2/r3/MAIN 0.7016-0.738/OOS全负) "
    "→ prereg §7/§8 一次定稿回填+gate_attrition entries 第60行+池done翻面(r312律)+T-46 progress_r338+census产物入git(results/shortline/sina_construct_p1.json+行级csv) "
    "latent_repull_defect_note=R222修正案已收口面零新待办 | §5预测对账: ①MAIN方向量级对(IR/OOS错)②r3反向对③梯度对④null带对=先验兑现效应量不足批级判负 | "
    "S4 CODELY 坑律新条(共享JSON面写者格式复刻律)+二十批外迁(9716→9534B r332bmb/r335bma 两全文入archive行级零丢失) | "
    "S6 33/33 rc=0 周日no-op族合法(update_moneyflow rank self-heal spawn 16:31 节流在途) | "
    "验证: smoke 25/25+S6 33/33+ledger_head=286551+archive断言True×2+push 8b2a424a clean | 下轮指针: 池ready=0 供给面=bandit advisory moneyflow IC 批等 EM 面板 self-heal 完成后 prereg+开烧; 池饿第七旗 30min 窗观察(16:54 起); bm-c r90 折叠回执待其轮报告收口\n"
)
with io.open(rr, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report appended')

# --- 2. state-bm-a.json: round_no 337 -> 338 (LF, preserve shape) ---
sp = 'state-bm-a.json'
st_raw = open(sp, 'rb').read()
eol = '\r\n' if st_raw.count(b'\r\n') > 0 else '\n'
st = json.loads(st_raw.decode('utf-8'))
print('state before: round_no=', st.get('round_no'))
st['round_no'] = 338
st['last_round_at'] = now
if isinstance(st.get('tasks'), dict):
    pass
st['current_task'] = 'r338 closed: SINA-CONSTRUCT-P1 judgment face (ALL 5 REJECT) + 20th-batch archival; next=pool supply (bandit advisory moneyflow IC awaits EM panel self-heal)'
s = json.dumps(st, ensure_ascii=False, indent=1)
tail = eol if st_raw.endswith((b'\n', b'\r')) else ''
open(sp, 'wb').write((s + tail).replace('\n', eol).encode('utf-8') if eol == '\r\n' else (s + tail).encode('utf-8'))
st2 = json.load(open(sp, encoding='utf-8'))
print('state after: round_no=', st2['round_no'])

# --- 3. heartbeat fleet/machines/bm-a.json ---
hp = 'fleet/machines/bm-a.json'
h_raw = open(hp, 'rb').read()
heol = '\r\n' if h_raw.count(b'\r\n') > 0 else '\n'
h = json.loads(h_raw.decode('utf-8'))
h['last_seen'] = now
h['current_task'] = 'r338 closed SINA-CONSTRUCT-P1 judgment (5/5 REJECT); idle-legal (board 0 open, pool ready=0, bandit advisory claimed-await-panel)'
h['verdict'] = 'healthy'
# cpu cores + RAM + GPU: light snapshot (no psutil dependency assumption -> reuse prior fields if present)
epoch = int(time.time())
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = iso
assert isinstance(h['heartbeat_epoch_utc'], int)
s = json.dumps(h, ensure_ascii=False, indent=1)
tail = heol if h_raw.endswith((b'\n', b'\r')) else ''
open(hp, 'wb').write(s.replace('\n', heol).encode('utf-8') if heol == '\r\n' else (s + tail).encode('utf-8'))
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int) and 'T' in h2['clock_read']
print('heartbeat written: epoch=', h2['heartbeat_epoch_utc'], 'clock=', h2['clock_read'])
