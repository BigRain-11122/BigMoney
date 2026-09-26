# r276 bm-b S4/S5/S7 writeback -- single now() instance for all timestamps (R271 law),
# five-face byte probe per file before write (R255/R257 law), verify after.
import json, datetime, os, re

now = datetime.datetime.now().astimezone()
_off = now.utcoffset() or datetime.timedelta(0)
_sign = '+' if _off >= datetime.timedelta(0) else '-'
_off = abs(_off)
iso_t = (now.strftime('%Y-%m-%dT%H:%M:%S') + _sign
         + '%02d:%02d' % (_off // datetime.timedelta(hours=1),
                          (_off // datetime.timedelta(minutes=1)) % 60))  # T-separated (R262 law)
stamp = now.strftime('%Y-%m-%d %H:%M')
epoch = int(now.timestamp())
assert 'T' in iso_t

def probe(path):
    raw = open(path, 'rb').read()
    return {'bom': raw.startswith(b'\xef\xbb\xbf'), 'crlf': b'\r\n' in raw,
            'nl': raw.endswith(b'\n'), 'text': raw.decode('utf-8-sig')}

def write(path, text, face):
    enc = 'utf-8-sig' if face['bom'] else 'utf-8'
    with open(path, 'w', encoding=enc, newline='') as f:
        f.write(text)

# ---- 1. CODELY.md: append pit law (four-question gate passed: E1 self-caught pit, one line) ----
p = 'CODELY.md'
f = probe(p)
line = ("- [2026-09-26 22:4" + stamp[-1] + "] 坑律（bm-b r276·results/ glob 消费面类型免疫面·r259 __workers__ 家族新参·E1 轮内自捕零外泄）："
        "**共享 results/ 根的 glob 消费者（monitor build_status _backtest_summary 扫 results/*.json）对顶层非 dict JSON 零容忍——探针脚本把 list 顶层 JSON 落 results/ 根=共享 monitor 腿当场 AttributeError（list.get）炸、S6 链 23/24 转红**；"
        "正律=①探针/scratch 产品的 JSON 落盘一律 dict 顶层（或落 results/_rNNN/ 子目录避共享 glob）②共享 glob 消费面 isinstance(d,dict) 门先于 .get（消费面类型免疫=r259 __workers__ 同族）③自产红先自扫源=本机自己 60s 前落的 _r276bmb_myclaims.json，删件+免疫门双修一次性闭环。指针=results/_r276bmb_s6_driver.ps1 monitor 腿+monitor/build_status.py _backtest_summary 修正段")
text = f['text']
if not text.endswith('\n'):
    text += '\n'
text += line + '\n'
write(p, text, f)
print('CODELY.md appended, new size', os.path.getsize(p))

# ---- 2. round_reports.md: append r276 line ----
p = 'logs/iteration-loop/round_reports.md'
f = probe(p)
rr = (f"{iso_t} | r276 (bm-b) | dept:工程 | WM-VERDICT: GREEN py_low_board_clear (probe 22:36 py 0.8% window n=2; board 0 open / bandit 0 / pool 49/49 done; MF_IC_P1 parked bm-a-lane source-blocked; red=false; audit FLAG pool_starvation=weekend supply-gap legal idle per O-1137) | "
       "did: S0 轮首脏=lane products commit d26817a7 后 pull --rebase vs bm-a r272 (9e66d7b8) 3-UU 按技能配方解（post_review.jsonl 行级 union 1506+36→1542 零丢失; autofill launches union 49 cap50 asc 写回序 r245 律+last_tick 22:30 取新整 dict; REPORT-20260926 UNKNOWN 手工定性=r265 同产者律 take-new 22:30:13）resolver=results/_r276bmb_resolve.py; "
       "S0.5 orders 84/84 双扫零差集 + decisions.md 本机三处均不在（C:/Users/Administrator/docs + E:/Minigame 全树 + E:/Fluxgroup 均无）→ P-32 零动作、末知状态经 bm-a r272=D-09/10/11 HQ 面零 BigMoney 例; S1 smoke 25/25; S2 board 0 open / job_list 空; "
       "S3 反重复三连：town.html 已八部门对齐 org_chart v6（队列项过期勿重建）+ Optuna 骨架维持 O-1120 D2 封印（负裁决触发器未满足）+ 本机 11 张 claimed 票全部 parked/未来窗/blocked → 维护轮定谳; "
       "S6 24 腿 → monitor 腿红（_backtest_summary 对 list 顶层 JSON AttributeError，炸源=本机 60s 前落的 scratch _r276bmb_myclaims.json）→ 双修（isinstance 免疫门+删件）复跑 rc=0 432combos/0pass 里程碑 5/7，其余 23 腿全 rc=0 周末面（daily 0 行 cutoff 09-24 / regime ORANGE shadow / clock ORANGE_COOL sleeves=4 activated=0 幂等 / lhb 30min 节流 / heat 周末 / futures cutoff 覆盖零网络 / bm-a 车道 options+mf+sina_mf+ths+ah 与 bm-c 车道 fp 诚实 no-op / fundamental 0.3h 新鲜跳过 / blf 全门过 / aggr+alloc+grid marks 幂等 no-op / t35 export 6 traders 18 pos / dsc 6 traders / daily report faces=4 token=1 / token delta=111）; "
       "S4 坑律 1+ 追加（CODELY 33.3KB<50KB 无整编窗）; migration 面不变：executor v2.2 PID 28696 precheck 等待 3 Tuanjie 编辑器（journal 22:30 仍在推进），旧根唯一真身照跑 | "
       "evidence: S6 逐腿 exit code 在 driver transcript + monitor 复跑 rc=0 + union 计数 1542 断言 + smoke 25/25 + orders diff 空 + CODELY diff 1+ | "
       "next: (1) 09-28 周一窗: T-76 channels run-6/10/4 + jin-gong 260928 验证 + T-78 GRID marks + MF_IC 面板自愈后（bm-a 车道）; (2) 10-01 月首轮三件套+REGIME_GUARD v3 日期门; (3) 每轮 S0 首探新根（在位=五件回执组装+旧根备份清理；ABSENT=journal 尾读+锁活性核 PID 28696 活=继续等待勿双 arm）; (4) 本机 CODELY 33.3KB 头部空间充足")
text = f['text']
if not text.endswith('\n'):
    text += '\n'
text += rr + '\n'
write(p, text, f)
print('round_reports.md appended')

# ---- 3. state.json: round_no 276 + faces ----
p = 'logs/iteration-loop/state.json'
f = probe(p)
d = json.loads(f['text'])
d['round_no'] = 276
d['did'] = ("r276: S0 pull-rebase vs bm-a r272 3-UU resolved per skill (jsonl union 1542 / autofill union cap50 / REPORT take-new; resolver _r276bmb_resolve.py) + orders 84/84 empty + decisions.md absent-on-bm-b zero-action + smoke 25/25 + board 0 open + anti-dup (town aligned / Optuna D2-sealed) -> maintenance round + S6 monitor leg RED self-caught (list-typed scratch json in results/ root crashed _backtest_summary) fixed both faces (isinstance guard + scratch delete) rerun green + 23 legs rc=0 weekend faces")
d['verdict'] = 'green'
d['next'] = ("09-28 Monday window (T-76 channels + T-78 GRID marks + MF_IC panel self-heal bm-a lane); 10-01 month-first trio + REGIME_GUARD v3 date gate; every round S0 first-probe root: new root present -> five-receipt assembly; absent -> journal tail + executor lock liveness (PID 28696 alive = precheck-waiting on 3 Tuanjie editors, do NOT double-arm); window till 09-29 12:00")
d['last_round_ts'] = iso_t
d['last_result'] = 'ok'
d['current_task'] = 'r276 done: maintenance round (S0 rebase-conflict resolution + monitor type-immunity fix); next: 09-28 Monday new-bar chain + 10-01 month-first trio'
d['last_tick'] = stamp[-5:]
d['updated_at'] = iso_t
d['last_seen'] = iso_t
d['ts'] = stamp
d['last_run'] = f'R276 {iso_t}'
d['last_round_at'] = stamp[-5:]
d['updated'] = stamp[-5:]
s = json.dumps(d, ensure_ascii=False, indent=1)
if f['nl']:
    s += '\n'
write(p, s, f)
print('state.json round_no ->', d['round_no'])

# ---- 4. heartbeat bm-b.json ----
p = 'fleet/machines/bm-b.json'
f = probe(p)
h = json.loads(f['text'])
try:
    import psutil
    vm = psutil.virtual_memory()
    free_gb = round(vm.available / 2**30, 1)
    cpu_pct = psutil.cpu_percent(interval=0.3)
except Exception:
    free_gb, cpu_pct = h.get('free_ram_gb'), h.get('cpu_util_pct', 0.0)
h['last_seen'] = iso_t
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = iso_t
h['current_task'] = 'r276: S0 3-UU resolve + monitor type-immunity fix; board 0 open; migration executor v2.2 precheck-waiting (editor-gated)'
h['round_no'] = 276
h['verdict'] = 'loaded_ok'
h['free_ram_gb'] = free_gb
h['cpu_util_pct'] = cpu_pct
h['idle_ram_gb'] = free_gb
h['idle_ram_mb'] = int(free_gb * 1024)
h['cpu_pct'] = cpu_pct
h['n_orders_ack'] = len(h['orders_ack'].split())
s = json.dumps(h, ensure_ascii=False, indent=1)
if f['nl']:
    s += '\n'
write(p, s, f)
h2 = json.loads(open(p, encoding='utf-8-sig').read())
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in h2['clock_read'], 'clock_read must be T-separated (R262 law)'
print('heartbeat epoch int OK:', h2['heartbeat_epoch_utc'], h2['clock_read'])

# ---- 5. S7 second orders scan ----
import glob as _g
ack = set(json.loads(open(p, encoding='utf-8-sig').read())['orders_ack'].split())
files = set(os.path.basename(x) for x in _g.glob('fleet/orders/O-*.md'))
diff = files - ack
print('S7 second orders scan: unacked =', sorted(diff) if diff else 'EMPTY (84/84)')
assert not diff, 'new orders arrived mid-round -> must process before commit'
print('WRITEBACK DONE')
