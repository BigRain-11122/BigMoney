import json, time, datetime

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def eol_of(raw):
    crlf = raw.count(b'\r\n')
    lf = raw.count(b'\n') - crlf
    return '\r\n' if crlf > lf else '\n'

def write_bytes(path, text, eol):
    t = text.replace('\r\n', '\n').replace('\n', eol)
    with open(path, 'wb') as f:
        f.write(t.encode('utf-8'))

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S%z')
ts_iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

# ---- 1) round report line (output first) ----
rp_path = 'round_reports-bm-a.md'
raw = read_bytes(rp_path)
eol = eol_of(raw)
line = (
    ts + ' | round 612 | dept:工程/研究 | 水位 verdict=绿（red=false·probe py_low_with_work_cands=池面合法在飞态：本机 autofill 06:50:07 claim FUND-QUALITY-P1-CELL-QUALITYROE-X2+06:50:18 32 workers 点火升温窗·2 未领条目=NULLS/SENS 排队后继 tick·审计旗 supply_gap 如实照录非违令）'
    ' | 当前活：MSG-0640 律提案受理（reland 属主面执行时点实取律）+FUND-QUALITY-P1-X2 池面烧录看护'
    ' | 最近实物：基本面 quality faces 数据本地性首次投产——本机 autofill claim QUALITY-ROE-X2 cell 烧录在飞（T-152 交付件消费·06:50:07 认领/06:50:18 点火/32 workers BelowNormal）+ E16 方法论卡+iteration_prompt S0 律行扩展+pit-git.md 增量行+MSG-0700-bma-bmb 回执'
    ' | 下个里程碑：QUALITY 四分片烧毕（bm-b 烧 VALUE-NULLS+QUALITY-X1·本机烧 X2·NULLS/SENS 待领）→FUND-QUALITY-P1 与 FUND-VALUE-P1 judged verdict finalize（窗≤10-04 晚）'
    ' | did: (1) S0-1 锚定 bm-a+S0 纯 FF 348b6adf3→2621524d1（behind 3=bm-b r606 FUND-QUALITY-P1 FREEZE+池注册 4 条目+autofill ticks·脏面=本机 daemon 活写件零交集）'
    ' (2) S0.5 双扫 orders 150/150 差集 0·D-19=K: 缺席诚实 skip（S4U 无头车道 r597 律·水位键 937A373D 不动）'
    ' (3) S1 smoke 47/47 (4) S2 双板：job_list 空·任务板零 open 票（T-145/T-151 本机链闭·T-152/153 他机占）'
    ' (5) S3 水位绿+引擎活（idle）+在飞判决批双条（VALUE-NULLS+QUALITY-X1 bm-b）=试用期常设线免起草'
    ' (6) inbox 双件处理：MSG-0630 自机回执归 processed+MSG-0640（bmb→bma·r609 环重放陈旧 probe 快照=对 bm-b r604 修正镜像 revert 事故+律提案）受理=律三面落地：E16 卡（执行时点 rev-parse+show 实取/恒等断言·禁环早先 fetch 缓存基座树面直 commit·多环环 2+ 树面仍陈旧=重放即 revert）+iteration_prompt.txt S0 律行扩展（三机同窗起消费）+research/pit-git.md post-split direct-write 行+回执 MSG-2026-10-03-0700-bma-bmb 落 inbox'
    ' (7) 池面实况：本机 autofill claim FUND-QUALITY-P1-CELL-QUALITYROE-X2（T-152 交付 quality faces 本机在位=数据本地性合法·r608 origin-ref 前读双查门内·daemon 管禁手工代烧）·bm-b 在烧 VALUE-NULLS+QUALITY-X1·FUND-QUALITY NULLS/SENS 两分片待后继 tick 认领'
    ' (8) S6 34 腿 rc0（dualrun ZERO-DRIFT streak 5/3·watermark py_low_with_work_cands 合法定性·REPORT/LIVE 幂等·黄金周数据腿全 no-op）'
    ' (9) S7 自愈 5/5（attrition CLEAN 4 healed 注记·loop pin=8 no-op·watchdog 重注册·双爪字节级装）+orders 收尾再扫差集 0'
    ' (10) 心跳 epoch int 自证+state 611→612'
    ' | 验证证据：smoke 47/47+S6 34×rc0+attrition CLEAN+iteration_prompt rg MSG-0640 命中=1+E16/E15 行对自证+心跳 json.loads isinstance(epoch,int) 通过'
    ' | 计分：1（律三面=实际文件改动支撑面·X2 cell 烧录在飞=产品管线产出烧毕 daemon 自交下窗验）'
    ' | 本地未达 origin commit 数：见收尾自证行'
    ' | next: QUALITY 四分片烧毕→FUND-QUALITY-P1 judged verdict finalize；VALUE-NULLS 烧毕→FUND-VALUE-P1 judged finalize；两家族 verdict 后基本面族线 leg(d) 收口（千人题库面） | [via bm-a r612]'
)
tail_ok = raw.endswith(b'\n')
with open(rp_path, 'ab') as f:
    if not tail_ok:
        f.write(eol.encode())
    f.write(line.replace('\n', eol).encode('utf-8') + eol.encode())
print('round report appended, eol=', repr(eol))

# ---- 2) state update ----
st_path = 'state-bm-a.json'
raw = read_bytes(st_path)
eol = eol_of(raw)
st = json.loads(raw.decode('utf-8'))
st['round_no'] = 612
st['did'] = ('r612 bm-a: MSG-0640 law proposal ADOPTED three faces (E16 reland-owner-face execution-time fetch law + iteration_prompt S0 extension '
             '+ pit-git.md direct-write) + FUND-QUALITY-P1-CELL-QUALITYROE-X2 pool shard claimed by local autofill 06:50:07 (T-152 delivered quality '
             'faces consumed locally, data-locality legal) burn in flight 32 workers + S6 34 legs rc0')
st['verify'] = ('smoke 47/47; S6 34 legs rc0; attrition CLEAN (4 healed noted); dualrun ZERO-DRIFT streak 5/3; orders 150/150 double-scan zero unacked; '
                'D-19 S4U honest skip (K: absent, watermark 937A373D untouched); watermark probe py_low_with_work_cands = legal in-flight (claim+burn ramp)')
st['next'] = ('QUALITY 4 shards burn-out -> FUND-QUALITY-P1 judged verdict finalize; VALUE-NULLS burn-out -> FUND-VALUE-P1 judged finalize; then fund-family leg(d) closeout')
st['current_task'] = 'FUND-QUALITY-P1-X2 cell burn in flight (autofill-managed); MSG-0640 E16 law landed three faces; awaiting NULLS/SENS claim by fleet ticks'
st['last_round_at'] = ts
st['updated'] = ts
write_bytes(st_path, json.dumps(st, ensure_ascii=False, indent=1), eol)
print('state bumped to', st['round_no'])

# ---- 3) heartbeat update (bump last) ----
hb_path = 'fleet/machines/bm-a.json'
raw = read_bytes(hb_path)
eol = eol_of(raw)
hb = json.loads(raw.decode('utf-8'))
hb['last_seen'] = ts
hb['clock_read'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['round_no'] = 612
hb['current_task'] = ('r612: E16 reland owner-face execution-time fetch law landed (MSG-0640 adoption: E16 card + iteration_prompt S0 + pit-git); '
                      'FUND-QUALITY-P1-X2 cell burn in flight (autofill 06:50 claim, 32 workers); QUALITY NULLS/SENS queued for fleet ticks')
hb['verdict'] = 'loaded_ok'
write_bytes(hb_path, json.dumps(hb, ensure_ascii=False, indent=1), eol)

# self-check: epoch int + ISO parseable
hb2 = json.loads(read_bytes(hb_path).decode('utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
datetime.datetime.fromisoformat(hb2['clock_read'])
print('heartbeat ok epoch=%d clock=%s' % (hb2['heartbeat_epoch_utc'], hb2['clock_read']))
print('ALL-BOOKKEEPING-OK ts=%s' % ts)
