# r704 bm-a S7 close: state + heartbeat + round report + CODELY pit line
import json, io, time, hashlib, subprocess, os

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

# --- D-19 full shas (fresh read via group real-path origin blob, r660 raw-bytes law) ---
G = 'C:/Users/sjs20/Desktop/FluxGroup'
subprocess.run(['git', '-C', G, 'fetch', 'origin'], capture_output=True)
def gsha(f):
    b = subprocess.run(['git', '-C', G, 'show', 'origin/main:' + f], capture_output=True).stdout
    return hashlib.sha256(b).hexdigest()
DSHA = gsha('docs/decisions.md')
OSHA = gsha('docs/orders.md')

# --- state-bm-a.json (round_no 700->704 skip dead r701-703 session labels per r687 precedent; type-preserving int) ---
sp = 'state-bm-a.json'
st = json.load(io.open(sp, encoding='utf-8'))
assert isinstance(st['round_no'], int), 'round_no type drift: %r' % type(st['round_no'])
st['round_no'] = 704
st['round'] = 'r704'
st['updated'] = NOW
st['last_round'] = 'r704'
st['last_round_at'] = NOW
st['current_task'] = ('r704 salvage-adoption: dead-r703 session closed out (died ~00:33 post-merge-commits, state/hb/report unwritten) -- '
                      'products landed (D-20261005-05(1) OH receipt slice group-delivered 5761978 + HQ-FEEDBACK F-20261005-01 line + S6 38/38 rc0 + origin 8-commit double-wave merge, claw-caught pool resolver aliasing bug fixed)')
st['did'] = ('r704: orders 154/154 zero-unacked + D-19 decisions CHANGED consumed (4E5BE321->' + DSHA[:12].upper() +
             ' D-20261005-01..05, BigMoney row 05(1) receipt closed via dead-r703 OH slice) + smoke 48/48 + satengine alive rc0 idle + '
             'S6 38/38 rc0 + self-heal 4/4 + attrition CLEAN 4 ledgers')
st['last_action'] = ('r704: absorb+merge origin 7+1 waves (5 UU faces canonical, pool keepalive per-entry theirs-fresh in-place mutation; '
                     'pre-push claw caught resolver aliasing bug -> owner_since regression blocked -> fixed + amended pre-push, zero origin harm)')
st['last_decisions_sha'] = DSHA
st['last_decisions_at'] = NOW
st['last_decisions_ts'] = NOW
st['last_decisions_src'] = 'group-tree origin/main raw-bytes sha256 via local real-path fetch+show (python subprocess bytes, r209/r631 law; K: absent S4U window)'
st['last_orders_sha'] = OSHA
st['last_orders_at'] = NOW + ' (r704 fresh read: 755428F8 window consumed, D-20261005-01..05 all BigMoney rows acked/closed)'
st['next'] = ('r705: N2 screen 12/12 verdict-gate (SHARD-2=bm-b RAM window ~10-06/07, seat MSG-2215 stands); W3 judge product adoption probe --live (bm-c ETA passed 02:00->verify); '
              'moneyflow EM source-blocked (conn fuse, panel 53/5222) -> IC prereg gated; trio NULLS finalize watch 10-05..09 (bm-b canonical)')
st['verify'] = 'smoke 48/48; push_verify DELIVERED 160a33ba1 (absorb+merge+merge-2, behind=0 post-push fetch); attrition guard CLEAN 4 ledgers (healed 5 rows recorded); state reparse + hb epoch int proof'
io.open(sp, 'w', encoding='utf-8', newline='\n').write(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
rt = json.load(io.open(sp, encoding='utf-8'))
assert rt['round_no'] == 704 and isinstance(rt['round_no'], int)
print('state written: round_no 704, D-19 sha', DSHA[:12].upper(), 'orders', OSHA[:12].upper())

# --- heartbeat fleet/machines/bm-a.json ---
hp = 'fleet/machines/bm-a.json'
hb = json.load(io.open(hp, encoding='utf-8'))
hb['last_seen'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['verdict'] = 'GREEN watch-state: adoption round closed; engine alive; board clear golden-week'
hb['current_task'] = 'r704 salvage-adoption + origin 8-commit merge + S6 38/38 green'
hb['round_no'] = 704
io.open(hp, 'w', encoding='utf-8', newline='\n').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
ht = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(ht['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in ht['clock_read'], 'clock_read must be T-separated (R262 law)'
print('heartbeat written: epoch int', ht['heartbeat_epoch_utc'], 'orders_ack', len(hb.get('orders_ack', [])))

# --- CODELY.md pit line (S4: claw-caught resolver aliasing bug; one-line compact per entry-gate) ---
cp = 'CODELY.md'
ct = io.open(cp, encoding='utf-8').read()
pit = ('\n- [2026-10-05 00:5x r704 bm-a] merge resolver per-entry 替换别名坑（pre-push claw 实弹拦截·爪设计正向首实证）：UU 池面解冲突时 '
       '`om={e[\"id\"]:e for e in o[\"entries\"]}; om[i]=tm[i]` 只改 side-dict 键绑定·o[\"entries\"] 列表原对象未动→落地=ours 旧面整存'
       '（FUND-DIVLOWVOL owner_since 00:36:12→00:26:12 回退 10min）——pre-push 爪按 backward 拦 push=正确执法非误伤（MSG-0612 族+r648 律）。'
       '正法=for idx,e in enumerate(o[\"entries\"]): o[\"entries\"][idx]=tm[e[\"id\"]]（原位列表元素替换）+写盘后反读断言关键时间戳==theirs 侧恒等。'
       'How to apply：一切 per-entry/per-face merge resolver 写盘前必带反读==预期侧断言；爪拦截先查实况勿急 --no-verify。')
if 'per-entry 替换别名坑' not in ct:
    io.open(cp, 'a', encoding='utf-8', newline='\n').write(pit + '\n')
    print('CODELY pit line appended; new size', len(ct) + len(pit) + 1)
else:
    print('CODELY pit line already present, skip')
print('S7 BOOKKEEPING DONE')
