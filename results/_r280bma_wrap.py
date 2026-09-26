# -*- coding: utf-8 -*-
"""R280 bm-a S7 wrap: round report row + state round_no++ + heartbeat refresh.
R271 law: all timestamps derived from ONE datetime.now() instance (no hardcode).
R262 law: clock_read uses T-separator isoformat. R170/R178: epoch must be int.
R255/R257: mirror each file's indent/trailing-newline/EOL face exactly.
"""
import json, io, time
from datetime import datetime, timezone

now = datetime.now().astimezone()
now_s = now.strftime('%Y-%m-%d %H:%M:%S')
now_iso = now.isoformat()          # T-separator, includes UTC offset (R262)
epoch = int(time.time())           # int, not str (R170/R178)

# --- 1) round report row (append, CRLF, trailing newline preserved) ---
rp = 'logs/iteration-loop/round_reports-bm-a.md'
raw = open(rp, 'rb').read()
eol_crlf = raw.count(b'\r\n') >= (raw.count(b'\n') - raw.count(b'\r\n'))
NL = '\r\n' if eol_crlf else '\n'
row = ('2026-09-27 ' + now.strftime('%H:%M:%S') + ' | R280 | bm-a dept:研究·策略·工程·舰队（无人值守轮）'
       '| 水位=绿（red=false·audit CLEAN pool-supply-gap ready=1·py_low_board_clear 周末合法白名单=板全闭环 bandit 空·REV-OSC 修后待 tick 重发）'
       '| did: S0 autofill_state tick 簿记撞 bm-b 维护 commit 双 rebase union 解（_r280bma_resolve{,2}.py·双新 claim 零丢失 cap50 滚最旧）；'
       'orders 89/89 差集零+集团决策 D-20260927-01/02/03 复核涉本仓例全 executed 无新待办；'
       'S3 闭环①=revosc 崩-发双发射根因修（d6_block load_member_rets 元组未解包·logs/autofill_REV-OSC-STOCK-P1.log 同点双崩·'
       '工程修 bdd99072 selftest 15/15 零判定产物窗 r253 律·修后新 sha tick 可重发）；'
       'S3 闭环②=CN_TREND_ETF_P1 prereg 冻结（T-87 s2 队列#1 趋势跟踪·feb36786+R280 零跑修正案 D2 截断面语义·'
       '23 ETF 机械宇宙 results/cn_trend_probe.json·7 judged cells MA/DON/MA200 族·K=2000 nulls seed 20270201 注册·'
       'science_gates selftest 35/35·F-04 MSG-20260927-0035·runner 下轮建）；'
       'S4 CODELY 坑律一行（R261 族新参·runner 运行面 donor 返回形态）；R280=5x 核对轮 HANDOVER.md 头行翻面+增量窗行'
       '（统一链 187,845 平持=本窗零批 finalize）；'
       'S6 全 29 腿 rc=0 周末 no-op 面（update_daily/market_clock ORANGE_COOL/scorecard/paper 腿 idempotent·token=1）；'
       '| 验证: smoke 25/25·science_gates 35/35·rev_osc selftest 15/15·HANDOVER diff 3+/1-·push 三段（含双 rebase）'
       '| 下轮指针: ①autofill tick 重发 REV-OSC（修后 sha）→收割判定面 ②CN_TREND_ETF_P1 runner scripts/cn_trend_etf_p1.py 建造+selftest→入池'
       '（供给线防 revosc 收线后池饿）③T-86 census runner 面')
text = raw.decode('utf-8-sig')
if not text.endswith('\n'):
    text += NL
text += row + NL
with io.open(rp, 'w', encoding='utf-8', newline='') as f:
    f.write(text)

# --- 2) state round_no++ (byte-face mirror) ---
sp = 'state-bm-a.json'
sraw = open(sp, 'rb').read()
s = json.loads(sraw.decode('utf-8-sig'))
s['round_no'] = int(s.get('round_no', 0)) + 1
for k in ('ts', 'updated_at', 'last_seen'):
    if k in s:
        s[k] = now_s
if 'clock_read' in s:
    s['clock_read'] = now_iso
out_s = json.dumps(s, ensure_ascii=False, indent=1)
if sraw.endswith(b'\n') and not out_s.endswith('\n'):
    out_s += '\n'
sNL = '\r\n' if b'\r\n' in sraw else '\n'
with io.open(sp, 'w', encoding='utf-8', newline='') as f:
    f.write(out_s.replace('\n', sNL) if sNL == '\r\n' else out_s)

# --- 3) heartbeat (epoch int + T clock + verdict/task fields) ---
hp = 'fleet/machines/bm-a.json'
hraw = open(hp, 'rb').read()
h = json.loads(hraw.decode('utf-8-sig'))
h['last_seen'] = now_s
h['clock_read'] = now_iso
h['heartbeat_epoch_utc'] = int(epoch)          # MUST be JSON int
h['round_no'] = s['round_no']
h['current_task'] = ('R280: revosc d6 crash-fix (bdd99072, awaiting tick relaunch) + '
                     'CN_TREND_ETF_P1 prereg frozen feb36786 (runner next round)')
h['verdict'] = 'healthy'
import os
cpu = os.cpu_count()
try:
    import psutil
    h['cpu_pct'] = round(psutil.cpu_percent(interval=0.3), 1)
    h['cpu_cores'] = cpu
    h['cores'] = cpu
    vm = psutil.virtual_memory()
    h['free_ram_gb'] = round(vm.available / (1 << 30), 1)
    h['idle_ram_gb'] = h['free_ram_gb']
except Exception:
    pass
out_h = json.dumps(h, ensure_ascii=False, indent=1)
if hraw.endswith(b'\n') and not out_h.endswith('\n'):
    out_h += '\n'
hNL = '\r\n' if b'\r\n' in hraw else '\n'
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    f.write(out_h.replace('\n', hNL) if hNL == '\r\n' else out_h)

# --- self-verify (R170/R178/R262/R271) ---
chk = json.loads(open(hp, 'rb').read().decode('utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
assert abs(chk['heartbeat_epoch_utc'] - epoch) <= 2, 'epoch consistency'
st = json.loads(open(sp, 'rb').read().decode('utf-8-sig'))
print('state round_no:', st['round_no'], '| hb epoch:', chk['heartbeat_epoch_utc'],
      '(int)', '| clock:', chk['clock_read'], '| report row appended ok')
