"""r499 bm-b round-close face writes: round report line, state.json,
heartbeat, CODELY.md memory append. Format-mirrored (r289 family law)."""
import json
import time
import datetime

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())


def detect_crlf(path):
    with open(path, 'rb') as fh:
        raw = fh.read(8192)
    return b'\r\n' in raw


def append_line(path, text):
    crlf = detect_crlf(path)
    with open(path, 'ab') as fh:
        data = text.encode('utf-8')
        if crlf:
            data = data.replace(b'\n', b'\r\n')
        fh.write(data + (b'\r\n' if crlf else b'\n'))


# ---- 1. round report line (bm-b ledger) ----
report = (
    "{ts} | r499 bm-b re-fire（猝死遗产收编·r495/r498 判例三度适用）dept:工程/研究 | "
    "[watermark verdict: RED=runnable-work-idle-low-cpu（py_tail 0.7-1.1% 空闲+池空——N1 族 W1-W4 全烧尽 W4=法典尾行、"
    "唯一 open 票 T-131=GM 署名门禁开、bandit 空=合法 idle 白名单成立；供给侧整改=N3/N2/N4 新面 runner+波级 prereg 待建"
    "（试用劳动力常设线·supply_floor breach 382min 已燃灯）；O-1612 GM waiver 面如实携带）] | "
    "本轮主产出（实物）：(1) 猝死 r499 会话遗产整批收编落地=commit 21090ae6a 已推 origin"
    "（三波 rebase 撞车 33+8+1 件全按 bigmoney-conflict-resolve 正典：AA 产品 12 件 r481 信封断言全等取 origin、"
    "finalize 件浮点尾差 1e-14 级人工裁定取 origin 保账本链一致〔r481 升级判例〕、池/compute_audit 等 7 面 "
    "merge_lane_views 工具合并+格式镜像 indent2 CRLF、runner/W4 prereg/仪表面取 origin 孪生侧、"
    "r305 假拒绝首波复发=commit -C 手工落 pick+quit+update-ref 净路 r507 律）；"
    "遗产实物=N1-W3 finalize 判决面（K=6720 mu=-0.0904 sigma=0.2479 se_mu 0.003024·skill_line +0.0082·ledger 371,019）"
    "+N1-W4 波物化（origin r507p2 孪生）+PORTFOLIO-BOOK 双层翻面+格式战 indent2 多数派正典收口；"
    "(2) 两枚 r499 push rider 滞留 stash 裁定弃置（rider2=bm-a 车道件 18k 行格式翻转=车道违禁噪声+rider1=活态已超越）| "
    "验证：S1 47/47；三波后 origin/main==main@21090ae6a 推送实证；"
    "S6 本轮 31 腿 rc0（reconcile DRIFT=done_at 孪生态观察相照录·flip 门 streak 重置、holiday 全腿合法 no-op、"
    "REPORT/LIVE 当日再生）+遗产自带 S6 35 腿 rc0；orders 133/133 双扫 EMPTY（134=133+README 文档件）；"
    "D-19 ED4E0EAB UNCHANGED（raw-bytes+大小写归一 r503 律）；attrition CLEAN；schtasks 双任务健康（pin=2 no-op+S4U）；"
    "merge_lane_views selftest 0 FAIL+池面 201 条 W3/W4 双层全 done 实证 | "
    "下轮指针：(1) 供给侧新面=N3 邻域鲁棒 runner+波级 prereg（法典 §4 台账取带·冻结语法·banned-gate 例外三件套预写 r494 律）"
    "＝试用劳动力常设线下轮默认开工（板空+池饿+无在飞判决批三条件全中）"
    "(2) r305 假拒绝本窗首波复发/二三波 continue 正常=间歇性实锤，恢复序照 r507 泛化律不变"
    "(3) 观察：daemon rebase-merge 自守卫+r351 yield 全窗零污染实证（手术窗 2min tick 6 次全 no-op）"
    "(4) GM 双裁定待件照旧（MSG-0400/048x 亲启非本机） | "
    "executive 三行面：当前活=供给链 N1 族燃尽收口、待 N3 新面开建；"
    "最近实物=21090ae6a@origin（N1-W3 finalize 判决面+遗产全量）+docs/live_usage/LIVE-2026-10-01.md@{t16} 再生；"
    "下个里程碑=N3 面 runner+prereg 落地→池面回填 12 分片（窗 ≤48h·下轮起）"
).format(ts=ts, t16=ts[:16])
append_line('logs/iteration-loop/round_reports.md', report)
print('report line appended')

# ---- 2. state.json ----
st = json.load(open('state.json', encoding='utf-8'))
st['round_no'] = 499
st['note'] = (
    'r499 re-fire: dead r499 heritage adopted+landed 21090ae6a on origin (3-wave rebase 33+8+1 conflicts '
    'all per conflict-resolve canon: 12 AA products r481-assert take-origin, finalize float-tail (1e-14 '
    'accumulation-order) adjudicated take-origin for ledger-coherence, 7 faces merge_lane_views+indent2 '
    'mirror, r305 false-refusal wave-1 recurrence -> commit -C manual path r507 law); stranded r499 '
    'push-rider stashes adjudicated+dropped; N1 family exhausted (W1-W4 all done, W4=tail row), supply '
    'side needs N3/N2/N4 face runner+prereg = next-round default line; watermark py_low_with_work_cands = '
    'legal idle (T-131 GM-gated, bandit empty, pool all-burned); orders 133/133 EMPTY, D-19 UNCHANGED'
)
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at'):
    st[k] = ts
st['last_decisions_at'] = st.get('last_decisions_at', ts)
raw = json.dumps(st, ensure_ascii=False, indent=1)
if detect_crlf('state.json'):
    raw = raw.replace('\n', '\r\n')
with open('state.json', 'w', encoding='utf-8', newline='') as fh:
    fh.write(raw + ('\r\n' if detect_crlf('state.json') else '\n'))
json.load(open('state.json', encoding='utf-8'))
print('state.json round_no=499 written')

# ---- 3. heartbeat ----
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['current_task'] = (
    'r499 re-fire done: dead-session heritage adopted+landed 21090ae6a on origin '
    '(3-wave rebase 33+8+1 per canon, finalize float-tail adjudication, r305 manual path), '
    'stranded stashes adjudicated, S6 31 legs rc0, smoke 47/47'
)
hb['round_no'] = 499
hb['loop_round'] = 499
hb['round'] = 499
hb['cpu_util_pct'] = 16.0
hb['free_ram_gb'] = 4.9
hb['idle_ram_gb'] = 4.9
hb['ram_free_gb'] = 4.9
hb['gpu_free_vram_gb'] = 2.1
hb['gpu_idle_vram_gb'] = 2.1
hb['gpu_free_vram_mb'] = 2124
hb['verdict'] = (
    'healthy: heritage landed 21090ae6a (smoke 47/47, S6 31 legs rc0 + heritage 35 legs, orders 133/133 '
    'EMPTY, D-19 UNCHANGED, attrition CLEAN); watermark py_low_with_work_cands=legal idle (T-131 '
    'GM-gated, pool all-burned N1 W1-W4 done); three-line face: active=N1 family exhausted, supply-side '
    'N3 face build queued as next-round default; latest=21090ae6a@origin (N1-W3 finalize verdict face '
    'K=6720 skill_line +0.0082) + LIVE-2026-10-01.md regen @' + ts[:16] + '; next milestone=N3 face '
    'runner+prereg -> 12 pool shards refill (window<=48h)'
)
raw = json.dumps(hb, ensure_ascii=False, indent=1)
if detect_crlf('fleet/machines/bm-b.json'):
    raw = raw.replace('\n', '\r\n')
with open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='') as fh:
    fh.write(raw + ('\r\n' if detect_crlf('fleet/machines/bm-b.json') else '\n'))
back = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(back['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('heartbeat written, epoch int verified:', back['heartbeat_epoch_utc'])

# ---- 4. CODELY.md memory append (one entry, four-gate checked) ----
mem = (
    '- [2026-10-01 r499 bm-b] r481 升级判例·AA finalize 汇总件浮点尾差裁定面（三波撞车实弹）：冻结确定性批的 finalize 汇总件'
    '（n1_w3_results.json null_pool_cumulative）跨机双烧时数值面可差在浮点累加序（同数不同求和顺序→1e-14~1e-17 相对差，'
    'headline 全等：K/n_values/取整 mu·sigma 双 commit 全同）——r481 单层精确断言对此类恒 FAIL=假阳性拒解；正解=断言失败先做'
    '分层复证（信封键剥离→浮点键 1e-9 相对容差→整数/字符串键精确），容差过+headline 同→人工裁定取 origin 侧'
    '（账本/skill_line 回填已消费 origin 面，取本地浮点变体=打破落地链一致）+resolver 留痕入档。'
    'How to apply：未来一切 finalize/汇总类 AA 断言一律三层判据，禁单层 == 全键恒等。'
)
append_line('CODELY.md', mem)
print('CODELY.md memory line appended')
print('CLOSE-FACES-OK', ts)
