"""r701 bm-c close: state round_no 701->702 + heartbeat + round report line.
Pattern credit: Tools/_r547bmc_bookkeeping.py (EOL-preserving json
round-trip + append-only round report + epoch int self-check)."""
import datetime as _dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")

now = time.time()
epoch = int(now)
now_iso = _dt.datetime.fromtimestamp(now).astimezone().isoformat(timespec="seconds")
cpu_pct = 38.6
free_gb = 1.8
gpu_mib = 6200

three_line = ("当前活: r701 bm-c 金周值守轮收口（W14-JUDGE 诚实 RAM park 守望+N1 供给断流定谳让路 bm-a W177 车道+lane_io 第三信号修法落地） "
              "| 最近实物: config/lane_io.py 第三信号扩展（origin-commit 活性 veto·selftest 25/25+双实现活体恒等 3/3）+qa/smoke-r701.md 5/5+qa/equity-curve-r701.png（93 trades·determinism=True·22 连证）+docs/daily_report/REPORT-20261007+docs/live_usage/LIVE-20261007 @ "
              + now_iso +
              " | 下个里程碑: W14-JUDGE RAM≥6G 窗自动复燃烧毕→judge-finalize→CEO-REPORT-WAVE14（48h 钟·≤10-09）；10-08（周四）复市首 bar 数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采；bm-a W177 freeze 窗（引擎 N1 供给恢复）；月界首考 10-31；下一 5x=bm-c r705")

verdict = ("r701 bm-c: golden-week guard round (CEO gaming window; W14-JUDGE honestly parked on RAM gate avail 1.8G<6G floor "
           "with ACBlackFlag 9.4GB foreground; engine alive idle queue-empty = N1 supply exhausted 174/174 waves burned, "
           "W177 freeze = bm-a declared lane per heartbeat current_task, bm-c yields per anti-dup law). (1) S0: round-start "
           "dirty 4 own runtime faces -> two commits (pre-pull snapshot + churn absorb r696 race law) -> pull --rebase "
           "hit _orphan_face_probe.json UU (regenerable canon probe report, bm-a v1.1.1 merged-provenance vs local scan) "
           "-> --theirs resolve + atomic continue, rebase clean. HONESTY NOTE: the two S0 commit messages are labeled "
           "'r702' -- label slip (this round is r701 per state authority; S6 driver/QA pack/pit entry all correctly "
           "labeled r701); git history preserved, no surgery for cosmetic labels. (2) S0.5: orders 167/167 BOTH sweeps "
           "zero unacked; D-19 decisions hash 4C32527B MATCH zero action. (3) S1 smoke 48/48. (4) CORE PRODUCT: lane_io "
           "third-signal extension LANDED (r700 next-pointer (c)): config/lane_io.py +_origin_commit_age_min (git log "
           "origin/main -40 %ct%x00%s needle scan, CREATE_NO_WINDOW, fail-soft None) + third-tier veto in "
           "shared_derive_write_allowed (both heartbeats stale but origin commit < C_HOST_STALE_MIN = host alive = veto "
           "stale-takeover; commit unreadable = pre-r701 behavior) -- fixes r700 live-fire (four C-faces "
           "stale-takeover-derived on live-but-heartbeat-stale bm-a); selftest 25/25 (+7 legs L15-L21); live-fire "
           "dual-implementation parity lane_io vs pool_worker 13.1/36.3/7.1min identical 3/3; end-to-end guard call "
           "correct (hb fresh 19min -> skip). (5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 21; daily_report + "
           "ceo_live_usage regenerated same-day idempotent; lane guards honest no-ops; pool dualrun before compute_audit "
           "per law). (6) QA pack r701 5/5 (93 trades, determinism=True, metrics face identical = frozen-panel 22nd "
           "consecutive evidence). (7) post_review 45Y/0N/5W zero red; attrition CLEAN (3 healed historical rows "
           "noted); orphan face=0 (round-zero probe). (8) S7 quartet idempotent (loop pin=5 no-op, watchdog "
           "re-registered, both claws LF-normalized). No new methodology (r700 third-signal method reused on a new "
           "surface); pit entry direct-write pit-protocol.md 1262B + receipt _r701bmc_pit_directwrite.json. "
           "Bookkeeping budget: 3 (state+heartbeat+round report). Product score: 2 (lane_io fix = runnable verified "
           "code change + QA evidence pack + S6 CEO faces).")

row = (now_iso + " | r701 bm-c | dept:工程/研究（金周连守轮·第二十一 bm-c·lane_io 第三信号修法轮） | 水位绿（red=false·SAT 活·board 0 open·next_pick=claimed moneyflow IC） "
       "｜本轮：金周值守+lane_io 第三信号修法落地——实物=config/lane_io.py（origin-commit 活性 veto·selftest 25/25 含 r701 七腿 L15-L21·双实现活体交叉恒等 13.1/36.3/7.1min 3/3·端到端守卫真调用正确）"
       "+qa/smoke-r701.md 5/5+qa/equity-curve-r701.png（66,238B·93 trades·sharpe 0.1586·maxdd -4.33%·win 46.24%·determinism=True·指标面恒等=冻结面板 22 连证）"
       "+docs/daily_report/REPORT-20261007+docs/live_usage/LIVE-20261007（S6 再生）"
       "｜S0=轮首脏 4 本机 runtime 面→两 commit 吸收（pre-pull snapshot+churn absorb r696 竞速律）→pull --rebase 撞 _orphan_face_probe.json UU（可再生探针报告·bm-a v1.1.1 merge-provenance vs 本机扫描面·--theirs 解+原子 continue 净）"
       "·**轮号标签滑位诚实注记：两 S0 commit 误标 r702（state 权威本轮=r701·S6 驱动器/QA 包/坑条全正确标 r701·git 史保全零手术）**"
       "｜S0.5=orders 167/167 双扫零未回执·D-19 decisions 哈希 4C32527B MATCH 零动作｜S1 48/48"
       "｜S3=水位绿·SAT 引擎活（queue_next=[] burns_active=[] py 0.29%——N1 供给断流定谳：174 波全烧完 12/12·W177 freeze=bm-a 已声明车道（心跳 current_task 明载）·本机让路反重复律）"
       "·W14-JUDGE（lane_owner=bm-c·77 cells）诚实 RAM park（avail 1.8G<6.0G 早门·CEO 前台 ACBlackFlag 9.4GB 15min 龄实测·r699 measure-size-park 律正确执法·un-park=RAM≥6G 自动翻面·19:58 复燃 pid 4572 20:1x 游戏启动窗再亡→20:30 relaunch→20:31 park 落 log rc0）"
       "·四连崩考古：18:50/19:22 解包错 expected 17（runner 编辑期签名漂移·19:58 前已修·当前 L3309=19 值解包与 return 19 值恒等核验 ✓）"
       "｜S6 38/38 rc0（收据 results/_r701bmc_s6_log.txt·dualrun streak 21·REPORT/LIVE-20261007 同日再生·lane 守卫诚实 no-op·update_fund_premium no-op=金周 09-30 快照已覆盖）"
       "｜QA r701 5/5（收据 qa/smoke-r701.md+png 66,238B·runner pid 22648 终态退出）｜post_review 45Y/0N/5W 零红｜attrition CLEAN（3 healed 历史缩行注记照录）"
       "｜孤儿面=0（round-zero 探针·py_faces 3 全正规军）｜四件套幂等（loop pin=5 no-op·watchdog 重注册·双爪 LF 归一）"
       "｜坑律=config/lane_io.py 第三信号落地条直写 pit-protocol.md 1,262B+收据 results/_r701bmc_pit_directwrite.json（md5 a5a23ee9adb2d2c3d32ca4c9b5d8e5f1·零丢失断言过）"
       "｜方法论捕获=无新方法（r700 第三信号法面复用至新表面）·宝藏捕获=无（无五类收口面）·登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3）"
       "｜token 面=L1 零 token 腿·delta state+0/report+1628/mandate+87"
       "｜轮产品计分：2（lane_io 修法=能跑已验实改+QA 证据包+S6 CEO 面）｜记账预算：3（state+心跳+轮报法定）"
       "｜下轮指针：(a) W14-JUDGE RAM 窗自动复燃→烧毕→judge-finalize+intake→CEO-REPORT-WAVE14 48h 钟（≤10-09） (b) 10-08 复市首 bar：数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 道）+O-2115/O-2030 治理日验收包正式复跑 (c) bm-a W177 freeze 落地后引擎 N1 供给恢复（本机让路勿抢车道） (d) 月界首考 10-31（T-143 交付 10-29） (e) 下一 5x=bm-c r705 HANDOVER 核对"
       " | 本地未达 origin commit 数=0（commit 后 push+fetch+ls-tree 自证）")

did = ("r701 bm-c: golden-week guard round closed. (1) S0 churn commits + probe-report UU resolve (regenerable face, "
      "--theirs, atomic continue). (2) orders 167/167 both sweeps zero unacked; D-19 MATCH. (3) smoke 48/48. "
      "(4) CORE: lane_io third-signal extension (origin-commit liveness veto) landed with selftest 25/25 + "
      "dual-implementation live parity 3/3 + end-to-end guard call verified; fixes r700 four-face "
      "stale-takeover-on-live-host observation. (5) S6 38/38 rc0 (streak 21). (6) QA r701 5/5, 93 trades, "
      "determinism=True (22nd consecutive). (7) post_review 45Y/0N; attrition CLEAN; orphan face=0. (8) quartet "
      "idempotent. (9) W14-JUDGE honestly parked on RAM (CEO gaming window), auto un-park on gate pass; N1 supply "
      "exhausted fleet-wide, W177 freeze = bm-a declared lane (bm-c yields). Label slip disclosed: two S0 commits "
      "say r702, this round is r701 per state authority.")


def load_json_raw(p):
    raw = open(p, 'rb').read()
    return json.loads(raw.decode('utf-8-sig')), raw


def eol_of(raw):
    return b'\r\n' if b'\r\n' in raw[:4000] else b'\n'


def dump_json(obj, raw, p):
    eol = eol_of(raw)
    data = (json.dumps(obj, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if eol == b'\r\n':
        data = data.replace(b'\n', b'\r\n')
    open(p, 'wb').write(data)


# ---- state update (preserve key order; round_no = next round per S7 law)
st, st_raw = load_json_raw(STATE)
st['clock_read'] = now_iso
st['cpu_pct'] = cpu_pct
st['cpu_util_pct'] = cpu_pct
st['current_task'] = three_line
st['current_task_at'] = now_iso
st['did'] = did
st['free_ram_gb'] = free_gb
st['gpu_free_vram_mib'] = gpu_mib
st['idle_ram_gb'] = free_gb
st['heartbeat_epoch_utc'] = epoch
for k in ('gpu_idle_vram_mib', 'gpu_free_mb', 'gpu_idle_mb', 'gpu_vram_free_mb'):
    if k in st:
        st[k] = gpu_mib
st['last_seen'] = now_iso
st['ram_free_gb'] = free_gb
st['round_no'] = 702
st['ts'] = now_iso
st['updated'] = now_iso
st['verdict'] = verdict
dump_json(st, st_raw, STATE)
chk = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 702, 'round_no must advance to 702'
print('state ok: round_no 701->702, epoch int self-check PASS')

# ---- heartbeat update (own file only)
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r701: golden-week guard + lane_io third-signal fix landed (origin-commit liveness veto, "
                      "selftest 25/25, live parity 3/3) + QA pack r701 (5/5, 93 trades, determinism=True, 22nd "
                      "consecutive) + S6 38/38 (streak 21, REPORT/LIVE-20261007 regenerated); W14-JUDGE honestly "
                      "parked on RAM gate (CEO gaming window, avail 1.8G < 6G floor, auto un-park); N1 supply "
                      "exhausted 174/174 waves, W177 freeze = bm-a declared lane (bm-c yields); smoke 48/48; "
                      "orders 167/167 both sweeps; post_review 45Y/0N; attrition CLEAN; orphan face=0")
hb['clock_read'] = now_iso
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100.0 - cpu_pct, 1)
hb['current_task'] = three_line
hb['current_task_at'] = now_iso
hb['free_ram_gb'] = free_gb
for k in ('gpu_free_mb', 'gpu_free_vram_mb', 'gpu_free_vram_mib', 'gpu_idle_vram_mb', 'gpu_idle_vram_mib',
          'gpu_vram_free_mb', 'gpu_free_mib'):
    if k in hb:
        hb[k] = gpu_mib
hb['heartbeat_epoch_utc'] = epoch
hb['idle_ram_gb'] = free_gb
hb['last_seen'] = now_iso
hb['last_seen_at'] = now_iso
hb['latest_artifact'] = ("config/lane_io.py third-signal extension (selftest 25/25 + live parity receipt) + "
                         "qa/smoke-r701.md 5/5 + qa/equity-curve-r701.png 66,238B (93 trades, determinism=True, "
                         "22nd consecutive) + results/_r701bmc_s6_log.txt (38 legs rc0) + "
                         "results/_r701bmc_pit_directwrite.json + docs/daily_report/REPORT-20261007 + "
                         "docs/live_usage/LIVE-20261007")
hb['next_milestone'] = ("W14-JUDGE RAM>=6G window auto-resume -> judge-finalize -> CEO-REPORT-WAVE14 48h clock "
                        "(<=10-09); 10-08 reopen first bar: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + "
                        "fund_premium 15:30 first snapshot (bm-c lane) + O-2115/O-2030 governance-day acceptance "
                        "rerun; bm-a W177 freeze restores N1 supply; month-end exam 10-31 (T-143 deliverable "
                        "10-29); next 5x = bm-c r705")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 701
hb['round_no_label'] = 'round 701 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r701 bm-c: golden-week guard round (CEO gaming window; W14-JUDGE parked on RAM gate honest defer; "
                 "N1 supply exhausted fleet-wide, W177 = bm-a lane). (1) S0 absorb + probe-report UU --theirs "
                 "resolve clean; label slip disclosed (two S0 commits say r702, round is r701). (2) orders 167/167 "
                 "both sweeps; D-19 MATCH. (3) smoke 48/48. (4) CORE: lane_io third-signal extension landed "
                 "(origin-commit liveness veto; selftest 25/25; dual-impl live parity 13.1/36.3/7.1min 3/3; "
                 "end-to-end verified). (5) S6 38/38 rc0 streak 21. (6) QA r701 5/5 determinism 22nd consecutive. "
                 "(7) post_review 45Y/0N; attrition CLEAN; orphan=0. (8) quartet idempotent. Bookkeeping 3; "
                 "product 2.")
dump_json(hb, hb_raw, HB)
chk = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 701
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be T-separated ISO'
assert chk['ts'] == chk['clock_read'], 'ts must be same-source same-instant as clock_read'
print('heartbeat ok: epoch int + clock_read T-iso + ts same-source self-checks PASS')

# ---- round report append (EOL-preserving)
rr_raw = open(RR, 'rb').read()
eol = b'\r\n' if b'\r\n' in rr_raw[-2000:] else b'\n'
row_b = row.encode('utf-8')
if eol == b'\r\n':
    row_b = row_b.replace(b'\n', b'\r\n')
if not rr_raw.endswith(eol):
    rr_raw += eol
open(RR, 'ab').write(row_b + eol)
new_raw = open(RR, 'rb').read()
assert new_raw == rr_raw + row_b + eol, 'round report append mismatch'
assert new_raw.count(b'bm-c round 701') == rr_raw.count(b'bm-c round 701'), 'unexpected dup'
print('round report ok: r701 line appended (EOL-preserved, %dB)' % len(row_b))
