# -*- coding: utf-8 -*-
# r538 bm-a: closeout bookkeeping -- state round_no++, heartbeat refresh, round-report append line
import json, time, datetime, psutil, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')  # +0800 form, T separator per F5
epoch = int(time.time())
vm = psutil.virtual_memory()

# --- state-bm-a.json ---
sp = r'state-bm-a.json'
raw = open(sp, encoding='utf-8').read()
crlf = '\r\n' in raw
st = json.loads(raw)
st['last_round'] = st.get('round_no', 537)
st['round_no'] = 538
st['round'] = 537
st['did'] = ('r538: town.html org_chart v2 alignment closure (11th building alloc renamed 资产配置研究组, dept re-anchored 组合与资金部 O-2311, '
             'stale v5-independent-dept references purged x5 incl footer; O-1145 v5 row deleted from org_chart at v6 ten-dept regroup r277, town never caught up) '
             '+ S6 28 legs rc0 holiday no-ops (host faces regen REPORT/LIVE/dscore/build_status)')
st['verify'] = ('align gate 10/10 PASS (residual 0, 11 depts all map org_chart v2 canonical set, id/drawAlloc unique) + node --check scripts-block rc0 '
                '+ Edge headless dump-dom render (new name x5, old name x0, canvas live); smoke 47/47; dualrun ZERO-DRIFT streak 14; WM py_low_board_clear legal idle; attrition CLEAN')
st['next'] = ('W23 finalize (bm-c, unblocked since W22 landed 20:05 chain head 412,948) -> bm-a W24 finalize next round once W23 results.json on origin '
              '(12/12 shards already delivered); W27 freeze waits W26 (bm-c seat); T-140/T-142/W14-GENERATE stay GM-ruled')
st['last_round_at'] = iso
st['current_task'] = 'r538 closed: town.html org_chart v2 alignment (alloc building re-anchored); awaiting bm-c W23 finalize -> W24 finalize'
st['updated'] = iso
out = json.dumps(st, ensure_ascii=False, indent=1)
if crlf:
    out = out.replace('\n', '\r\n')
open(sp, 'w', encoding='utf-8', newline='' if crlf else '\n').write(out)
print('state written, round_no=', st['round_no'], 'crlf=', crlf)

# --- heartbeat fleet/machines/bm-a.json ---
hp = r'fleet\machines\bm-a.json'
raw = open(hp, encoding='utf-8').read()
crlf_h = '\r\n' in raw
h = json.loads(raw)
h['last_seen'] = iso
h['current_task'] = st['current_task']
h['cpu_pct'] = round(psutil.cpu_percent(interval=None), 1)
h['free_ram_gb'] = round(vm.available / (1024**3), 1)
h['task'] = 'r538 town.html org_chart v2 alignment closure (alloc->组合与资金部挂靠, gate 10/10, render-verified)'
h['verdict'] = ('healthy: r538 town.html org_chart v2 alignment closure (gate 10/10 + Edge render-verified) + S6 28 legs rc0 holiday no-ops; '
                'engine alive queue0 idle-legal (W23 finalize=bm-c unblocked on W22 landed; W24 finalize=next once W23 on origin; W26=bm-c seat); '
                'board clean, pool drained (W14-GENERATE GM-park only), audit pool_starvation flag=GM-ruled supply gap disclosed')
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = iso
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be int'
out = json.dumps(h, ensure_ascii=False, indent=1)
if crlf_h:
    out = out.replace('\n', '\r\n')
open(hp, 'w', encoding='utf-8', newline='' if crlf_h else '\n').write(out)
print('heartbeat written, epoch=', h['heartbeat_epoch_utc'], 'int-ok, crlf=', crlf_h)

# --- round report append ---
rp = r'round_reports-bm-a.md'
line = ('%s | r538 | town.html org_chart v2 对齐收口：alloc 楼正名资产配置研究组+dept 锚回组合与资金部 O-2311（O-1145 v5 行已于 r277 v6 十部门改组删除，town 5 处引用全清）；'
        'S6 28 legs rc0 假日 no-op（host 面再生成）| 验证：align gate 10/10（残留 0·11 dept 全映射 v2 正典集）+node --check rc0+Edge dump-dom 真渲染（新名5/旧名0）；'
        'smoke 47/47；dualrun 连绿14；WM py_low_board_clear 合法闲置；attrition CLEAN | 下轮：bm-c W23 finalize 已解锁（W22 落 20:05）→落账后 bm-a 跑 W24 finalize（12/12 分片已在 origin）；'
        'W27 冻结候 bm-c W26；T-140/T-142/W14-GENERATE 归 GM 裁\n') % iso
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended')
