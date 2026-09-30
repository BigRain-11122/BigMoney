# r300 bookkeeping: round report line + state-bm-c.json + heartbeat (format-preserving)
import json, time, datetime, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# 0) probe formats (r289 shared-JSON rewrite law)
def probe(path):
    raw = io.open(path, 'rb').read()
    crlf = raw.count(b'\r\n'); lf = raw.count(b'\n') - crlf
    eol = '\r\n' if crlf >= lf else '\n'
    j = json.loads(raw.decode('utf-8'))
    ind = None
    for l in raw.decode('utf-8').split(eol):
        if l.startswith('  "'):
            ind = 2; break
    return eol, (2 if ind == 2 else None)

# 1) round report line (append, byte mode, CRLF)
rr_line = (
    now + '｜r300｜watermark verdict=红（runnable-work-idle-low-cpu：池 ready=2 均 bm-b lane〔host gate=astock 面板本机不可烧〕'
    '，本机零可烧批=合法 idle 白名单如实披露；供给线 W3=等 GM 裁定 PERPETUAL_FACES §1 v1.1〔bm-b MSG-20261001-0400〕，一行声明不重扫）｜'
    '当前活=T-134 s1 普查分类器修正+r299 cross_start WIP 验证收口｜'
    '最近实物=scripts/multicore_census.py v1.1（库内间接臂+注释跳过·selftest 10/10）+ results/multicore_census.json 刷新'
    '（真实面 38 multiprocess/38 single_core·hard-law live 面归零）+ cross_start_robustness.py selftest 22/22（S9 全起确定性+BS6c 池==内联）@04:1x｜'
    '下个里程碑=GM 裁定 v1.1 后 W3 物化恢复供给 ready≥3（≤48h 内随裁定落地）；bm-b astock 刷新完窗（~06:45）后 EXCLUSION+FACEB 两批自动烧｜'
    '产品分=2（能跑实物：分类器+普查工件+WIP 验证）｜'
    'S1 47/47；S6 33 legs rc0（dualrun ZERO-DRIFT streak 2/3·CALL-2026-09-30=ORANGE_COOL·scorecard/buildstat=合法 stale-takeover 写'
    '·token crash-fuse 拒发 522 已 parked per bm-b r491 heal）；'
    'orders 133/133 差集 EMPTY；D-19 ED4E0EAB UNCHANGED（raw-blob）；attrition CLEAN；'
    'MSG-0235=本机出站件留置（收件 bm-a/bm-b）；MSG-0400=GM 裁定件（W3 hold 遵从·不越权）；'
    'r293 陈 stash 已核=dispatcher 态瞬态 1 件已弃（stash 清零）；loop Running/pin:05 no-op；watchdog Ready（幂等重装）；claw 装机；'
    'RAM 0.7GB 低水位观察续；每月三件 r294 已 discharge 不双跑\r\n'
)
with io.open('round_reports-bm-c.md', 'ab') as f:
    f.write(rr_line.encode('utf-8'))

# 2) state-bm-c.json (format-preserving rewrite)
sp = 'state-bm-c.json'
eol, _ = probe(sp)
s = json.load(io.open(sp, encoding='utf-8'))
s['round_no'] = 300
s['last_round_at'] = now
s['last_round_ts'] = epoch
s['updated'] = now
s['cpu_pct'] = 8.2
s['idle_ram_gb'] = 0.7
s['gpu_free_vram_mib'] = 12834
s['verify'] = ('S1 smoke 47/47; S6 chain 33 legs rc0 (lane no-ops honest, no-new-bar holiday legs honest-skip, '
               'monthly trio discharged r294 no-double-run); orders 133/133 diff EMPTY; D-19 ED4E0EAB UNCHANGED (raw-blob); '
               'attrition CLEAN; claw installed; watchdog Ready (idempotent reinstall); loop pin :05 no-op; '
               'stash list cleared (r293 transient dropped after inspection); dualrun ZERO-DRIFT streak 2/3')
s['did'] = ('r300: T-134 s1 CENSUS CLASSIFIER FIXED -- house parallel_runner indirection arm + comment-skip '
            'mechanism (multicore_census.py selftest 10/10); live census regen: TRUE face 38 multiprocess / 38 single_core '
            '(was false 65/11 -- 27-runner mass false-negative cured: trial_labor_w1..w14 family + aggressive_lab + '
            'mass_trial etc all real ProcessPool via tl1); hard-law live face now EMPTY (EXCLUSION/FACEB/W14 all '
            'verified-converted); r299 cross_start WIP verification closed (selftest 22/22: S9 all-start determinism '
            'double-run + BS6c face-B pool==inline); pool workers_plan for both live burns code-verified 8-worker ProcessPool')
s['current_task'] = ('T-134 s1->s2 verification loop (census = accurate now); supply line W3 held pending GM ruling on '
                     'PERPETUAL_FACES v1.1 (bm-b MSG-20261001-0400); zero burnable lane-free work on bm-c = legal idle disclosed')
s['next'] = ('(a) GM ruling on PERPETUAL_FACES v1.1 -> W3 materialization restores ready>=3 (floor breach ready=2<3 disclosed); '
             '(b) bm-b astock refresh window ~06:45 -> EXCLUSION+FACEB auto-burn on bm-b lane; '
             '(c) T-134 s4 efficiency face = bm-a next-round delivery (CEO acceptance = 10-01 morning report); '
             '(d) RAM watch 0.7GB low; (e) remaining 38 single_core runners have NO live pool entries (new-entry ban only, '
             'convert-on-demand when next re-pooled)')
s['heartbeat_epoch_utc'] = epoch
s['clock_read'] = now
s['last_ts'] = now
s['last_decisions_sha'] = 'ed4e0eabf941b4299a6f26b243082ee74a83517b462d352d9c047f95a49a1f07'
s['last_decisions_read_at'] = now
s['last_decisions_sha_method'] = 'python subprocess.check_output raw-blob bytes SHA-256 (PS-pipeline join method = transcoding false-drift, see CODELY r292 pit)'
s['last_round'] = ('2026-10-01 r300: census classifier fix (indirection arm, 10/10 selftest) + true-face regen 38/38 + '
                   'hard-law live face EMPTY + cross_start WIP verification closed 22/22 + S6 33 legs rc0 + stash cleared')
s['note'] = 'r300 product score=2 (census classifier runnable + refreshed census artifact + WIP verification closed)'
with io.open(sp, 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(s, ensure_ascii=False, indent=2).replace('\n', eol))

# 3) heartbeat fleet/machines/bm-c.json
hp = os.path.join('fleet', 'machines', 'bm-c.json')
eol2, _ = probe(hp)
h = json.load(io.open(hp, encoding='utf-8'))
h['last_seen'] = now
h['current_task'] = 'r300 done: T-134 s1 census classifier fix + WIP verify closed; idle (zero lane-free burnable, W3 held pending GM ruling)'
h['cpu_cores'] = 32
h['idle_ram_gb'] = 0.7
h['gpu_free_vram_mib'] = 12834
h['verdict'] = 'legal_idle_disclosed: pool ready=2 both bm-b-lane (astock host gate), W3 supply held pending GM ruling (MSG-20261001-0400), board closed'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(h, ensure_ascii=False, indent=2).replace('\n', eol2))

# 4) self-verify heartbeat epoch is JSON int (R170/R178 law)
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
chk2 = json.load(io.open(sp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'state epoch must be int'
print('bookkeeping ok: state round', chk2['round_no'], '| epoch int verified', chk['heartbeat_epoch_utc'])
print('clock_read T-sep ok:', 'T' in chk['clock_read'])
