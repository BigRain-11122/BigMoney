# r939 bm-b closeout: state.json + heartbeat + round report line (atomic, owner-content audit per r936 law)
import json, time

TS = '2026-10-14T16:21:00+08:00'
EPOCH = int(time.time())
RPT = 'logs/iteration-loop/round_reports.md'
STATE = 'state.json'
HB = 'fleet/machines/bm-b.json'

did = ('r939 bm-b product round (48h CEO W19 report landed 48h early): '
       '(1) MAIN PRODUCT research/W19-TRIAXIS-CEO-REPORT-V1.md -- W19 lawful-zero verdict (112 judged, g1_pass 0, E[FP] 5.6 vs 0, best 0.7515 < skill_line 1.1512 live) '
       '+ three-axis X/S/T adjudication table (W17 344 exit-face deltas all 0.0 / W18 188 sizing deltas ~0 / W19 112 timing +0.0942 p=0.01 & -0.2808 n.s.; 644 judged, 0 registrations, E[FP] nominal 32.2 vs 0) '
       '+ W20 census verdict (45 faces 0 survivors, tick-stock-panel source closed) + supply route decision points ((a) stock-universe burn face = P1 CEO-signed-ticket gate; (b) sec.5 sources lane self-drive); '
       'due 2026-10-16T13:49 clock intact, landed 2026-10-14 r939; '
       '(2) same-round prereg sec.7 erratum (paired-deltas informative n misquote 45/128 -> judged-block 21/35, machine-read authoritative, medians/p unchanged) + T-186 progress_r939 receipt; '
       '(3) S0 clean (origin zero new; daemon-face checkpoints bbc5124ab+8ad412fe9); S0.5+S7 double-scan 0 unacked orders; D-19 dual hash EQUAL zero-action (raw-bytes probe); '
       '(4) smoke 49/49; SatEngine alive (verdict idle, queue 0); watermark red=false (py_low_board_clear legal idle whitelist); '
       '(5) S6 full chain rc0 (dualrun streak 24 ZERO-DRIFT; sina 10-14 bar not yet published -> cutoff stays 2026-10-13, live.paper/t35_open_fill/t24_prospect legs honest-skip pending bar catch self-heal; REPORT-2026-10-14 + LIVE-2026-10-14 written ORANGE_COOL cap 50%); '
       '(6) CODELY main-file mini-split debt discharged same-window (32,679B -> 30,697B <= 30,720 cap; r933/r936 -> pit-git-resolver-rebase2, r938 -> pit-encoding, r939 new law direct-write pit-protocol-judge [backfill-counts machine-read law]; '
       'receipt results/_r939bmb_codely_minisplit.json, zero-loss assertions PASS, prescan rc3 authorized face; standing debt disclosed: pit-ps.md 32,451B overage for next maintenance window); '
       '(7) S7 loop/watchdog/claws green + attrition CLEAN; orphan probe 16:20 py_faces=17 orphans=0')

verdict = ('GREEN: r939 48h CEO W19 report landed 48h early (three-axis X/S/T adjudication + W20 census verdict + supply route decision points); '
           'S6 full chain rc0; smoke 49/49; attrition CLEAN; orders 0 unacked; D-19 dual hash EQUAL; '
           'flags = supply_floor/pool_starvation standing WITH VERDICT (route closed; refill = P1 stock-universe ticket or sec.5 sources) '
           '+ GPU PSU-deferred standing (MODE=pause) + sina 10-14 daily-bar catch pending (self-heal) + pit-ps.md 32,451B domain overage standing debt (next maintenance window)')

next_r940 = ('r940: (a) sina 10-14 daily bar catch -> live.paper REGIME_GUARD=enforce + t35_open_fill_verify + t24_prospect legs when landed; '
             '(b) supply refill route (b) self-drive watch (sec.5 sources: REFINE_BENCH variants / T-86 surviving-factor leg); '
             '(c) standing: GPU PSU-swap MODE=pause, backfill_ext_slots monitor, bili-reply CEO cookie gap, pit-ps.md sub-split next maintenance window, scorecard guard-face governance audit pointer')

# --- state.json ---
st = json.load(open(STATE, encoding='utf-8'))
assert st['round_no'] == 938, 'unexpected prior round %s' % st['round_no']
assert st['machine_id'] == 'bm-b'
st['round_no'] = 939; st['round'] = 939; st['round_no_label'] = 'r939'
st['clock_read'] = TS; st['ts'] = TS; st['updated'] = TS; st['updated_at'] = TS; st['last_seen'] = TS
st['last_round_at'] = TS; st['last_round_ts'] = TS; st['last_action_at'] = TS
st['last_decisions_at'] = TS; st['last_decisions_read_at'] = TS; st['last_orders_at'] = TS; st['last_orders_read_at'] = TS
st['last_decisions_sha_method'] = 'r939: probe rerun raw-bytes (results/_r686bmb_d19_check.py) dec d9d8aa72 / ord a7bb50ea BOTH EQUAL vs stored -> zero-action'
st['last_orders_sha_note'] = 'r939: orders sha1 EQUAL (raw-bytes verify); round-start + S7 double-scan zero new O-*.md; zero scan delta'
st['did'] = did
st['last_action'] = 'r939: 48h CEO W19 report landed + prereg sec.7 erratum + CODELY mini-split (main 30,697B <= cap) + S6 full chain rc0'
st['latest_artifact'] = 'research/W19-TRIAXIS-CEO-REPORT-V1.md + results/_r939bmb_codely_minisplit.json @ ' + TS
st['current_task'] = 'r940: sina 10-14 bar catch -> live legs when landed; supply route (b) self-drive watch'
st['task'] = st['current_task']
st['next'] = next_r940
st['next_milestone'] = 'W19 report due 10-16 13:49 (landed 48h early); sina 10-14 bar catch next rounds; supply refill route (b); pit-ps sub-split next maintenance window'
st['now_active'] = 'r939 W19 triaxis CEO report landed; SatEngine ticking; CPU lanes green; sina 10-14 daily bar catch pending; GPU MODE=pause PSU-deferred standing'
st['note'] = 'r939: main-file mini-split debt discharged same-window (r933/r936/r938 migrated + r939 backfill-counts law direct-write); pit-ps.md overage disclosed standing; prereg sec.7 informative-n erratum same-round'
st['verdict'] = verdict
st['orphan_face'] = 0; st['orphan_faces'] = 0
st['orphan_face_note'] = 'r939 probe 16:20: py_faces=17 orphans=0 killed=[]'
st['sync'] = {'last_push_ts': TS, 'note': 'r939 closeout commit+push follows this write; behind=0 self-proof post-push'}
json.dump(st, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- heartbeat ---
hb = json.load(open(HB, encoding='utf-8'))
assert hb['machine_id'] == 'bm-b' and hb['round_no'] == 938
hb['round_no'] = 939; hb['round'] = 939; hb['round_no_label'] = 'r939'
hb['clock_read'] = TS; hb['ts'] = TS; hb['last_seen'] = TS; hb['last_action_at'] = TS; hb['last_round_at'] = TS
hb['heartbeat_epoch_utc'] = EPOCH
hb['current_task'] = 'r940: sina 10-14 bar catch -> live legs when landed; supply route (b) self-drive watch'
hb['task'] = hb['current_task']
hb['did'] = 'r939 bm-b: 48h CEO W19 report landed 48h early (W19-TRIAXIS-CEO-REPORT-V1.md) + CODELY mini-split debt discharged (main 30,697B <= cap) + S6 full chain rc0; smoke 49/49'
hb['last_action'] = 'r939: W19 triaxis CEO report + sec.7 erratum + mini-split; sina 10-14 daily bar catch pending (live legs skip honest)'
hb['latest_artifact'] = 'research/W19-TRIAXIS-CEO-REPORT-V1.md + results/_r939bmb_codely_minisplit.json @ ' + TS
hb['next'] = next_r940
hb['next_milestone'] = 'W19 report due 10-16 13:49 (landed early); sina bar catch; supply refill route (b); pit-ps sub-split next window'
hb['now_active'] = 'r939 W19 triaxis CEO report landed; SatEngine ticking; bar catch pending; GPU MODE=pause standing'
hb['note'] = 'r939: W19 report + mini-split receipt landed; supply_floor/pool_starvation flags carry verdict (route closed); pit-ps 32,451B overage standing debt'
hb['verdict'] = verdict
hb['orphan_face'] = 0; hb['orphan_faces'] = 0
hb['orphan_face_note'] = 'r939 probe 16:20: py_faces=17 orphans=0 killed=[]'
hb['idle_rounds'] = 0; hb['agenda_starved'] = False; hb['green_idle'] = False
hb['idle_ram_pct'] = 27.0; hb['ram_free_pct'] = 27.0
hb['idle_ram_gb'] = 6.5; hb['ram_free_gb'] = 6.5; hb['free_ram_gb'] = 6.5
hb['gpu_free_vram_mb'] = 3540; hb['gpu_free_vram'] = '3540 MiB'
hb['gpu_free_vram_gb'] = 3.5; hb['gpu_idle_vram_gb'] = 3.5; hb['vram_free_gb'] = 3.5
hb['sync'] = {'last_push_ts': TS, 'note': 'r939 closeout commit+push follows'}
json.dump(hb, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# owner-content audit (r936 law): reload and assert bm-b own round/clock/verdict
st2 = json.load(open(STATE, encoding='utf-8'))
hb2 = json.load(open(HB, encoding='utf-8'))
assert st2['round_no'] == 939 and st2['machine_id'] == 'bm-b' and st2['clock_read'] == TS
assert hb2['round_no'] == 939 and hb2['machine_id'] == 'bm-b' and hb2['clock_read'] == TS
assert isinstance(hb2['heartbeat_epoch_utc'], int) and hb2['heartbeat_epoch_utc'] == EPOCH
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read']

# --- round report line ---
line = ('| ' + TS + ' | r939 | bm-b [dept:research/strategy] | 48h CEO W19 报告提前 48h 落地（本轮主产出）: 当前活=W19 三轴收官呈报落稿; '
        '最近实物=research/W19-TRIAXIS-CEO-REPORT-V1.md @ ' + TS + '（三轴 X/S/T 判决表=W17 344/W18 188/W19 112 合计 644 judged·0 注册·E[FP] 名义 32.2 vs 实过 0；'
        'W20 普查 45 面 0 幸存源关闭；供给路线决策点=(a) 股票宇宙烧面 P1 级 CEO 署名门 (b) sec.5 源车道自驱）+ T-186 progress_r939 回执 + prereg §7 勘误'
        '（配对差分 informative n 误引 45/128→judged 块内实读 21/35·机读件权威·中位差/p 原值正确）; '
        '下个里程碑=W19 报告 due 10-16 13:49 已提前落地·sina 10-14 bar catch 后续轮（live.paper/t35/t24 三腿候 bar 落自愈）·月界首考 10-31 | '
        'watermark: GREEN (red=false; py_low_board_clear=板闭环+池空合法 idle 白名单; supply_floor/pool_starvation 旗=既有定谳面 route closed) | '
        'orphan-faces=0 (r939 probe 16:20: py_faces=17 orphans=0) | '
        'S0 pull 零新增（daemon 面双 checkpoint bbc5124ab+8ad412fe9）+S0.5/S7 收尾双扫 0 未回执+D-19 双水位 raw-bytes EQUAL 零动作+smoke 49/49+SatEngine 活（verdict idle·queue 0）| '
        'S6 链全 rc0（dualrun streak 24 零漂移; 10-14 bar 未发布=cutoff 10-13·三 live 腿合法跳过; REPORT+LIVE 10-14 已写·ORANGE_COOL cap 50%）| '
        'CODELY 主件越帽 mini-split 债当窗处置（32,679→30,697 ≤30,720; r933/r936→pit-git-resolver-rebease2·r938→pit-encoding·r939 新律直写 pit-protocol-judge〔回填计数机读实读律〕; '
        'receipt=results/_r939bmb_codely_minisplit.json·零丢失断言过·prescan rc3 授权面; 存量债披露=pit-ps.md 32,451B 越帽候下维护窗 sub-split）| '
        'S7 循环/看门狗/双爪全绿+attrition CLEAN | 本地未达 origin commit 数=0（收口 push 后自证）'
        + '\n')
data = open(RPT, 'rb').read()
if not data.endswith(b'\n'):
    data += b'\n'
open(RPT, 'ab').write(line.encode('utf-8'))
print('CLOSEOUT OK: state r939, heartbeat epoch=%d (int), report line appended (%dB)' % (EPOCH, len(line.encode('utf-8'))))
