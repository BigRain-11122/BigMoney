"""r702 bm-c close: state round_no 702->703 + heartbeat + round report line.
Pattern credit: Tools/_r701bmc_close.py (EOL-preserving json round-trip +
append-only round report + epoch int self-check)."""
import ctypes
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
cpu_pct = 46.0
free_gb = 6.2
gpu_mib = 309

three_line = ("当前活: r702 bm-c 崩会恢复轮收口（S0 rebase E42 卡死逃逸+丢件 verbatim 重建+W14-JUDGE 复燃活体确认） "
              "| 最近实物: qa/smoke-r702.md 5/5+qa/equity-curve-r702.png（93 trades·determinism=True·23 连证）+results/_r702bmc_w14_watch.json（burn alive pid 18900·RAM gate 6.2G pass·checkpoint lock face 3.6min 新鲜）+results/_r702bmc_s6_log.txt（38/38 rc0·dualrun streak 22）+docs/daily_report/REPORT-20261007+docs/live_usage/LIVE-20261007 @ "
              + now_iso +
              " | 下个里程碑: W14-JUDGE 77-cell 烧毕（ETA ~22:50·r700 fill_latency ~85min 律）→judge-finalize+intake→CEO-REPORT-WAVE14（48h 钟·≤10-09）；10-08（周四）复市首 bar 数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 道）；下一 5x=bm-c r705 HANDOVER 核对")

verdict = ("r702 bm-c: crashed-session recovery round (prior r702 attempt died mid-rebase in the E42 family; "
           "this session recovered per r835 canon + r700 precedent). (1) Round-zero orphan probe=0 (5 py faces all "
           "regular). (2) S0 RECOVERY: diagnosed stuck rebase (stopped pick a7c4ad2ac on regenerable "
           "results/_orphan_face_probe.json UU, 4 churn-absorb picks remaining); verified stopped-pick content "
           "already at HEAD (2189a866d, mislabeled message, content-faithful, file-set + line counts match); "
           "treasure_guard restore classification rc0 all 12 dropped paths; escape = rebase --quit + symbolic-ref "
           "detached self-check + branch -f main HEAD + checkout main (r624); dropped-pick non-daemon files "
           "restored VERBATIM from pick blobs (Tools/_r702bmc_s0b..s0h.py + 5 facts jsons); ONE fresh rebuild "
           "absorb; pull --rebase onto e0150d762 with exactly the two predicted probe-file stops resolved "
           "canon-side (2189a866d stop --ours=origin canon / rebuild-absorb stop --theirs=fresh 21:20 local "
           "scan, r701 precedent); rebase clean 6/6; push e0150d762..e3e95f0b1; behind=0/ahead=0 self-verified. "
           "HONESTY NOTE: the s0j pre-rebase amend raced the autofill daemon's tick-claim commit, so tail churn "
           "faces ride under the 'autofill tick claim judge-0of1' message at origin tip e3e95f0b1 -- label "
           "slip disclosed, content complete and bm-c-lane only, no surgery for cosmetic labels (r701 "
           "precedent). (3) S0.5 round-start sweep: DEC 4C32527B / ORD A8B02C8A both MATCH zero-delta; orders "
           "167/167 zero unacked; inbox zero unread. (4) S1 smoke 48/48. (5) S3: watermark green; SAT engine "
           "alive rc0 (queue_next=[] burns_active=[]); post_review 45Y/0N/5W zero red; board 0 open; job_list 0. "
           "W14-JUDGE RE-IGNITED and alive (RAM gate passed: CEO gaming window closed, avail 8.5G->6.2G >= 6G "
           "floor; autofill tick claim judge-0of1 owner=bm-c; runner pid 18900 trial_labor_w14.py judge "
           "--shard 0 --shards 1 since 21:25:23; checkpoint lock face 3.6min fresh; 77 cells, G-manifest "
           "PASS 48 members; watch receipt results/_r702bmc_w14_watch.json). (6) S6 38/38 rc0 (dualrun "
           "ZERO-DRIFT streak 22, 406 entries; lane guards honest no-ops; REPORT/LIVE-20261007 regenerated "
           "same-day idempotent; fund_premium no-op = golden-week 09-30 snapshot covers). (7) QA pack r702 "
           "5/5 (93 trades, determinism=True, equity 1,017,839 cross-round identical = frozen-panel 23rd "
           "consecutive evidence). (8) S7 quartet idempotent (loop pin=5 no-op, watchdog re-registered 21:31, "
           "both claws LF-normalized); attrition CLEAN (3 healed historical rows noted). Bookkeeping budget: "
           "3 (state+heartbeat+round report). Product score: 2 (S0 recovery = repo unstuck + pushed with "
           "receipts + W14-JUDGE re-ignition watch receipt + QA evidence pack + S6 CEO faces).")

row = (now_iso + " | r702 bm-c | dept:工程（金周连守轮·第二十二 bm-c·崩会恢复轮·S0 E42 逃逸轮） | 水位绿（red=false·SAT 活·board 0 open·next_pick=claimed moneyflow IC） "
       "｜本轮：崩会恢复+复燃确认——实物=qa/smoke-r702.md 5/5+qa/equity-curve-r702.png（66,334B·93 trades·sharpe 0.1586·maxdd -4.33%·win 46.24%·determinism=True·equity 1,017,839 跨轮恒等=冻结面板 23 连证）"
       "+results/_r702bmc_w14_watch.json（W14-JUDGE 复燃活体收据：pid 18900·21:25:23 起·trial_labor_w14.py judge --shard 0 --shards 1·RAM gate 8.5→6.2G pass·checkpoint lock face 3.6min 新鲜·G-manifest PASS 48 员·ETA ~22:50）"
       "+results/_r702bmc_s6_log.txt（38 腿 rc0）+docs/daily_report/REPORT-20261007+docs/live_usage/LIVE-20261007（S6 同日幂等再生）"
       "｜S0=前 r702 会话 rebase 中途猝死（E42 族卡死态：stopped pick a7c4ad2ac 撞可再生 _orphan_face_probe.json UU·余 4 churn-absorb picks）→诊断（rebase-merge todo/done/message/stopped-sha 四件+HEAD 内容核对：stopped pick 内容已在 HEAD 2189a866d〔消息误标·内容忠实·文件集+行数恒等〕）→treasure_guard restore 12 路全 rc0→r835 正典逃逸（rebase --quit+symbolic-ref 游离自证+branch -f main HEAD+checkout main〔r624 律〕）→丢件 verbatim 重建（Tools/_r702bmc_s0b..s0h.py+5 facts json 自 pick blobs 字节精确恢复·daemon 活面 newest-wins 不回放）→单次 fresh rebuild absorb→pull --rebase onto e0150d762 两处预测内 probe 停点按典解（2189a866d 停 --ours=origin 典面/rebuild absorb 停 --theirs=21:20 本机新扫描·r701 判例）→6/6 净→push e0150d762..e3e95f0b1→behind=0/ahead=0 自证"
       "·**诚实注记：s0j 术前 amend 与 autofill 守护 claim commit 竞速→尾段 churn 内容乘在 origin tip e3e95f0b1 的『autofill tick claim』消息下（标签滑位披露·内容完备且纯 bm-c 车道·r701 判例零手术）**"
       "｜S0.5=orders 167/167 零未回执·D-19 DEC 4C32527B/ORD A8B02C8A 双 MATCH 零动作（收收尾双扫）｜S1 48/48"
       "｜S3=水位绿·SAT 引擎活 rc0（queue_next=[] burns_active=[]）·post_review 45Y/0N/5W 零红·板 0 open·job_list 0·**W14-JUDGE 复燃**（autofill tick claim judge-0of1 owner=bm-c·RAM gate pass=CEO 游戏窗关〔ACBlackFlag 进程消失·8.5G 实测〕·r699 measure-size-park 律 un-park 面正确自动翻面·试炼劳动常设线=在飞判决批满足）"
       "｜S6 38/38 rc0（dualrun ZERO-DRIFT streak 22·406 entries·lane 守卫诚实 no-op·update_fund_premium no-op=金周 09-30 快照覆盖·REPORT/LIVE-20261007 同日再生）"
       "｜QA r702 5/5（收据 qa/smoke-r702.md+png 66,334B·runner pid 18312 终态退出·determinism=True 23 连证）｜post_review 45Y/0N/5W｜attrition CLEAN（3 healed 历史缩行注记照录）"
       "｜孤儿面=0（round-zero 探针·py_faces 5 全正规军）｜四件套幂等（loop pin=5 no-op·watchdog 重注册 21:31·双爪 LF 归一 IN-PLACE）"
       "｜方法论捕获=无新方法（r835/r700 逃逸正典复用）·宝藏捕获=无（无五类收口面）·登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3）"
       "｜token 面=L1 零 token 腿（token_meter 腿 rc0·固定语境 ~13067+8744 粗估照录）"
       "｜轮产品计分：2（S0 恢复=仓体解锁已推+收据·W14 复燃收据·QA 证据包+S6 CEO 面）｜记账预算：3（state+心跳+轮报法定）"
       "｜下轮指针：(a) W14-JUDGE 77-cell 烧毕（ETA ~22:50）→judge-finalize+intake→CEO-REPORT-WAVE14 48h 钟（≤10-09） (b) 10-08 复市首 bar：数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 道） (c) bm-a W177 freeze 烧毕后引擎 N1 供给恢复 (d) 月界首考 10-31（T-143 交付 10-29） (e) 下一 5x=bm-c r705 HANDOVER 核对"
       " | 本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证）")

did = ("r702 bm-c: crashed-session recovery round closed. (1) S0: stuck-rebase quit-escape per r835 canon "
       "(stopped-pick content verified already at HEAD; 12 dropped paths treasure_guard rc0; s0b-s0h tools+facts "
       "restored verbatim from pick blobs; fresh rebuild absorb; pull --rebase onto e0150d762 with 2 canon-side "
       "probe resolutions; push e0150d762..e3e95f0b1 behind=0). Amend-vs-daemon label slip disclosed (tail churn "
       "under autofill-claim message). (2) S0.5 orders 167/167 zero unacked; DEC/ORD hash MATCH. (3) smoke 48/48. "
       "(4) W14-JUDGE re-ignited and alive (pid 18900, RAM gate passed, checkpoint lock fresh; ETA ~22:50) -> "
       "judge-finalize next round. (5) S6 38/38 rc0 streak 22. (6) QA r702 5/5, 93 trades, determinism=True 23rd "
       "consecutive. (7) post_review 45Y/0N; attrition CLEAN; orphan face=0. (8) quartet idempotent.")


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
st['round_no'] = 703
st['ts'] = now_iso
st['updated'] = now_iso
st['verdict'] = verdict
dump_json(st, st_raw, STATE)
chk = json.loads(open(STATE, 'rb').read().decode('utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 703, 'round_no must advance to 703'
print('state ok: round_no 702->703, epoch int self-check PASS')

# ---- heartbeat update (own file only)
hb, hb_raw = load_json_raw(HB)
hb['activity_now'] = ("r702: crashed-session recovery round: S0 stuck-rebase quit-escape per r835 canon "
                      "(dropped s0b-s0h tools+facts restored verbatim, fresh rebuild absorb, rebase onto "
                      "e0150d762 clean, push behind=0; amend-vs-daemon label slip disclosed) + W14-JUDGE "
                      "re-ignited and alive (pid 18900, RAM gate 8.5->6.2G pass, checkpoint lock fresh, ETA "
                      "~22:50) + QA pack r702 5/5 (93 trades, determinism=True, 23rd consecutive) + S6 38/38 "
                      "(streak 22, REPORT/LIVE-20261007 regenerated); smoke 48/48; orders 167/167; "
                      "post_review 45Y/0N; attrition CLEAN; orphan face=0")
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
hb['latest_artifact'] = ("qa/smoke-r702.md 5/5 + qa/equity-curve-r702.png 66,334B (93 trades, determinism=True, "
                         "23rd consecutive) + results/_r702bmc_w14_watch.json (W14-JUDGE burn alive receipt, pid "
                         "18900) + results/_r702bmc_s6_log.txt (38 legs rc0) + results/_r702bmc_s0i_facts.json "
                         "(S0 recovery receipts) + docs/daily_report/REPORT-20261007 + docs/live_usage/"
                         "LIVE-20261007")
hb['next_milestone'] = ("W14-JUDGE 77-cell burn completion (ETA ~22:50) -> judge-finalize + intake -> "
                        "CEO-REPORT-WAVE14 48h clock (<=10-09); 10-08 reopen first bar: data-chain re-arm + "
                        "REGIME_GUARD v3 first-bar enforce + fund_premium 15:30 first snapshot (bm-c lane); "
                        "month-end exam 10-31 (T-143 deliverable 10-29); next 5x = bm-c r705")
hb['ram_free_gb'] = free_gb
hb['round_no'] = 702
hb['round_no_label'] = 'round 702 (bm-c)'
hb['ts'] = now_iso
hb['updated'] = now_iso
hb['updated_at'] = now_iso
hb['verdict'] = ("r702 bm-c: crashed-session recovery round (prior r702 attempt died mid-rebase E42-family; "
                 "this session: quit-escape + dropped-pick verbatim rebuild + canon rebase onto e0150d762 + "
                 "push behind=0; label slip on tail churn disclosed). W14-JUDGE re-ignited and alive (RAM "
                 "gate passed, pid 18900, ETA ~22:50). S6 38/38 streak 22; QA r702 5/5 determinism 23rd "
                 "consecutive; smoke 48/48; orders 167/167; post_review 45Y/0N; attrition CLEAN; orphan=0; "
                 "quartet idempotent. Bookkeeping 3; product 2.")
dump_json(hb, hb_raw, HB)
chk = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 702
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
print('round report ok: r702 line appended (EOL-preserved, %dB)' % len(row_b))
