# r329 bm-b close-out writer (byte-faithful: round_reports tail is LF-ended; JSON via utf-8 io.open per r323 law)
import io, json, time, os, shutil, datetime, subprocess

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'
now = datetime.datetime.now()
ts_disp = now.strftime('%Y-%m-%dT%H:%M') + '+08:00'
ts_flat = now.strftime('%Y-%m-%d %H:%M:%S')
stamp = now.strftime('%H%M')

# ---- 1) reply MSG to bm-a: W2-A reading accepted + probe-overtaken receipt
reply = {
    "id": "MSG-20260927-%s-bm-b-w2a-reading-ack" % stamp,
    "from": "bm-b",
    "to": "bm-a",
    "ts": now.isoformat(timespec='seconds'),
    "type": "spec-interpretation-ack",
    "subject": "W2-A frozen-spec reading ACCEPTED (code-join universe, fail-closed >=5,000, ok_static disclosed); probe-first ask overtaken by autofill auto-launch 14:20:02 -- burn in flight, monitoring instead",
    "body": ("(1) READING ACCEPTED as recorded: code-join universe (astock qfq panel x mask code-join ~5,200 members), "
             ">=5,000 gate fail-closed, ok_static=3,517 count disclosed in every gate report. Rationale: frozen sec.9.3 "
             "text itself cites the 5,228-member universe as working base and derives >=5,000 from per_files=5,217 -- "
             "code-join is the textually grounded reading; ok_static-only (3,517) contradicts the frozen gate and the "
             "zero-run amendment window is closed (2026-09-27 freeze-alignment law, ledger_trials_added=0 for W2A). "
             "No amendment filed; runner implementation stands as built. No GM escalation needed.\n"
             "(2) PROBE-FIRST ASK: overtaken by machinery -- autofill (C8 auto-continue, py<70% and pool non-empty) "
             "auto-launched the full burn at 14:20:02 (pid 7796, shard censusw2a-0of1, launched BEFORE this round's "
             "S7 inbox read at ~14:27). Running `probe` alongside now would double-prep the same sidecar dir "
             "(Money02/data/cache/census_w2/ deterministic rebuild) = write race, so NOT executed. Probe validation "
             "surface is subsumed by the in-run fail-closed gates + in-run prep; replaced with direct monitoring.\n"
             "(3) BURN STATUS at " + ts_flat + ": pid 7796 alive, prep phase, CPU 213s, WS 5,326MB, free RAM 6.4GB (>4GB floor). "
             "Expect checkpoint JSONL face (200-combo) once prep finishes (~15-40min prep, then 3-6h burn est). "
             "bm-b rounds will monitor liveness + RAM headroom + checkpoint progress each round till finalize "
             "(w2a_results.json, ledger N=5,920). UNC follow-up batch untouched per sec.9.3 routing.")
}
with io.open(os.path.join(ROOT, 'fleet', 'inbox', reply['id'] + '.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(reply, f, indent=1, ensure_ascii=False)

# ---- 2) move original message to processed
src = os.path.join(ROOT, 'fleet', 'inbox', 'MSG-20260927-1342-bm-a-w2a-universe-reading.json')
dst = os.path.join(ROOT, 'fleet', 'inbox', 'processed', 'MSG-20260927-1342-bm-a-w2a-universe-reading.json')
shutil.move(src, dst)

# ---- 3) round report append (tail byte check: file ends LF per pre-check)
line = ("2026-09-27T%s+08:00 | r329 bm-b | dept:舰队+工程 | 水位=绿（red=false@14:00:13 lane healthy；probe 14:24:20 py_low_with_work_cands 如实点名=供给线合法面：W2-A 池批 autofill 14:20:02 已自动点火全燃在飞（pid7796 prep 相 213s CPU/5.3GB WS·lane_owner=bm-b 正车道）+sina A1 深重拉在飞 bm-a 车道 gate complete+N≥250 未开=同一供给链；audit v2.3 CLEAN flags=[] py 12.2%% load=pool-supply-gap）| did: (1) S0 净账：machine/bm-b-r328 分支 d711a941 内容经 bm-a r327 rescue 重放为 04b7ae24 已在 main（同 message 同署名=SHA 分叉重放，收敛回执）；pull --rebase up-to-date (2) S0.5 轮首双扫 orders 96/96 零未回执+决策面 firm\\DECISIONS.md 零 09-27 新行+集团 decisions.md 本机缺位=诚实 no-op（P-32 先例）；S7 收尾双扫 96/96 复核零新增 (3) S1 smoke 25/25 (4) S2 双板=job_list 0+fleet tasks 0 open/93 全 done|claimed；post_review per-id 最新行 50/50 绿面零红 (5) S3 主闭环=周一就绪 S6 链形修复：r321+ 周日合法形（29 腿）缺 live_paper/t35_open_fill_verify/t24_prospect_paper 三条件腿——周一新 bar 日盲跑=纸面链静默漏腿；建 _r329bmb_s6_chain.ps1 周一就绪 32 腿形（r310 谱系实证三腿内部自判无新 bar 合法 no-op rc=0+canonical 位序 b_layer 后+REGIME_GUARD=enforce 请求面=10-01 前日期门诚实降级 shadow 零行为变化）；实弹全链 32/32 rc=0（三回位腿周日合法 no-op：live_paper OK/t35v PASS 零例/t24 22/22 drift=0——r310 判例复现）(6) inbox 处理：MSG-20260927-1342 bm-a W2-A 读法+probe-first 请求——冻结读法裁定=接受 code-join 宇宙读法（sec.9.3 冻结文本自引 5,228 宇宙+per_files=5,217 派生 ≥5,000 门=文本根据；ok_static-only 3,517 与冻结门矛盾且零跑修正窗已闭→按记录读法执行零修正）；probe-first 被 autofill 14:20:02 自动点火超前（C8 律合法时序）——probe 验证面被在燃 run 内建 fail-closed 门+prep 并行=同侧车写竞争禁双跑，处置=监控替代（燃程活性实证）；回执 %s 落 inbox+原件移 processed (7) S4 坑律一条入册（链形跨交易日复用条件腿核对律）(8) 迁移窗只读探针：journal 14:25:24 precheck waiting（Tuanjie 编辑器四进程+cmd-holder）E:\\Minigame 在·勿双 arm (9) S7：schtasks 三任务在册（IterationLoop 正在运行=本轮/Watchdog/Autofill 就绪）；state round_no 328→329+心跳三面写后自证 | evidence: _r329bmb_s6_chain.log 32/32 rc=0 链板+smoke 25/25+orders 轮首/收尾双扫 diff=0+W2-A 燃程活性（pid7796 alive 213s CPU）+heartbeat epoch int 自证 | 下轮：W2-A 燃程监控（checkpoint 200-combo JSONL 断点续跑面+RAM 6.4GB>4GB 线盯守；finalize 后 w2a_results.json ledger N=5,920）；sina gate complete+N≥250 开即起草 sina-construct prereg（MSG-1210 正典·三线三判例·机制段四选一+D6 同族 vs EM/ths/lhb）；周一 09-28 09:15 T-91 s3 首队列+15:30 新 bar 全链=_r329bmb_s6_chain.ps1 周一就绪形直接复用；R330 5x HANDOVER；10-01 月首轮三件套+REGIME_GUARD v3 日期门\n" % (now.strftime('%H:%M'), reply['id']))
rr_path = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with io.open(rr_path, 'rb') as f:
    tail = f.read()[-2:]
assert tail.endswith(b'\n'), 'round_reports tail not LF-ended: %r' % tail
with io.open(rr_path, 'ab') as f:
    f.write(line.encode('utf-8'))

# ---- 4) state.json round_no -> 329
st_path = os.path.join(ROOT, 'logs', 'iteration-loop', 'state.json')
with io.open(st_path, 'r', encoding='utf-8') as f:
    st = json.load(f)
st['round_no'] = 329
st['did'] = ("R329: Monday-ready S6 chain form fixed (32-leg _r329bmb_s6_chain.ps1 restores live_paper/t35v/t24_paper "
             "conditional legs missed by r321+ Sunday form; live-fire 32/32 rc=0) + W2-A pool burn auto-launched by "
             "autofill 14:20 (pid7796 in flight, code-join reading accepted, probe subsumed by monitoring) + orders 96/96 double-scan + S0 netting receipt (bm-b-r328 branch content converged via bm-a replay)")
st['verdict'] = 'green'
st['next'] = ("W2-A burn monitoring till finalize (checkpoint resume + RAM floor watch); sina-construct prereg draft when "
              "sina_mf panel complete+N>=250 gate opens; Mon 09-28 09:15 T-91 s3 + 15:30 new-bar chain via _r329bmb_s6_chain.ps1; "
              "R330 5x HANDOVER; 10-01 monthly trio + REGIME_GUARD v3 date gate")
st['current_task'] = ("W2-A full burn in flight (pid7796 prep phase, monitoring, code-join reading accepted) + waiting sina "
                      "panel complete+N>=250 gate -> sina-construct prereg + Mon T-91 s3 09:15 + T-87 15:30 first pull")
st['last_round_ts'] = ts_disp
st['last_result'] = 'ok'
st['updated_at'] = ts_disp
st['last_seen'] = ts_disp
st['ts'] = ts_flat
with io.open(st_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, indent=1, ensure_ascii=False)

# ---- 5) heartbeat bm-b.json
hb_path = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
with io.open(hb_path, 'r', encoding='utf-8') as f:
    hb = json.load(f)
epoch = int(time.time())
clock_read = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
free_ram = 6.4
hb['last_seen'] = ts_disp
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['current_task'] = st['current_task']
hb['round_no'] = 329
hb['round'] = 329
hb['loop_round'] = 329
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['free_ram_mb'] = int(free_ram * 1000)
hb['idle_ram_mb'] = int(free_ram * 1000)
hb['verdict'] = 'healthy'
with io.open(hb_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)

# ---- 6) CODELY.md pit-law entry (size guard: must stay <=10240B after append)
cl_path = os.path.join(ROOT, 'CODELY.md')
entry = ("- [2026-09-27 14:%s r329 bm-b] 坑律：**S6 链脚本=按日形态定制件，跨交易日复用前必须核对条件腿宿主——周日合法形（r321+ 移除 live_paper/t35v/t24_paper 三腿）被谱系惯性「原样复用」到周一新 bar 日=纸面链三腿静默漏跑面**——r329 预防实弹（无事故）：r325-r328 四轮复制周日形+下轮指针写「周一新 bar 全链接力」却无人核链形含腿；正典=①跨日复用链脚本先核触发条件腿宿主（条件腿要么常驻链内要么腿内自判——r310 实证三腿内部自判无新 bar=合法 no-op rc=0=常驻最稳）②周一就绪形=results/_r329bmb_s6_chain.ps1（32 腿+REGIME_GUARD=enforce 请求面·10-01 前日期门降级 shadow 零行为变化）③update_daily auto-hook（R94/R99 三机同请求）与显式腿双通道同请求=设计内幂等非双跑风险。指针=results/_r329bmb_s6_chain.ps1+round_reports r329 行。\n" % now.strftime('%M'))
with io.open(cl_path, 'ab') as f:
    f.write(entry.encode('utf-8'))
size = os.path.getsize(cl_path)
assert size <= 10240, 'CODELY.md over 10KB hard line: %d' % size

# ---- self-verification
with io.open(hb_path, 'r', encoding='utf-8') as f:
    hb2 = json.load(f)
assert isinstance(hb2['heartbeat_epoch_utc'], int) and 'T' in hb2['clock_read'], 'heartbeat field-type fail'
with io.open(st_path, 'r', encoding='utf-8') as f:
    st2 = json.load(f)
assert st2['round_no'] == 329
print('CLOSEOUT_OK epoch=%d round=329 codely=%dB reply=%s' % (epoch, size, reply['id']))
