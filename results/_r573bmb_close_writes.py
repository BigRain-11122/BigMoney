import json, time, datetime, glob, os

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')

# --- fresh W79 shard count ---
w79 = len(glob.glob(r'results\p2cal_ext\n1_w79\shard-*.json'))

# --- state.json (bm-b) ---
state = json.load(open('state.json', encoding='utf-8'))
state['round_no'] = 573
state['note'] = (
    "r573: W76 FINALIZE one-pass landed (prev 529,548 = W75 bm-a r572 head, +2,200 = 531,748 net, "
    "K=165,120, S5 4/4, skill_line 1.1646, r538 no-rerun; prereg s7/s8 backfilled r307 two-state, "
    "backfill tool results/_r573bmb_w76_backfill.py) + W79 FREEZE delivered (SIXTY-EIGHTH wave, bm-b "
    "26th owned; A 201_004..203_003 / B 53_401..53_600 BOTH SIDES arithmetic continuation zero skip "
    "== W78 row W79+ projection verbatim; gate ADMIT results/_r573bmb_w79_band_gate.py; seat "
    "MSG-20261002-1151-bmb PUSHED to origin BEFORE freeze per r565 early-visibility; banned gate 0 "
    "matched; full selftest W2..W79 + pf 8/8; MSG-0640 FIX-A/B/C pure-insertion verified) + W79 burn "
    "in flight (shard-0 self-ignited pre-commit per r359 law face, %d/12 at close) + D-19 "
    "MATCH-unchanged (4FD50184) + orders zero-delta 143/143 both scans + smoke 47/47 + dualrun "
    "ZERO-DRIFT streak 18/3 + S6 all-green (holiday no-new-bar no-op faces; host-guarded faces "
    "honest skip) + chain now W1..W77 ALL LANDED head 533,948 K=167,320 (W77 finalize bm-a r573 "
    "landed mid-round) + next = W79 12/12 burn complete + finalize one-pass AFTER W78 bm-c finalize "
    "lands (chain order FAIL-CLOSED r307) + W80 freeze (projection A 203_004..205_003 / B "
    "53_601..53_800 both CLEAN per gate)" % w79)
state['last_round_at'] = int(time.time())
state['last_round_ts'] = datetime.datetime.now().astimezone().isoformat('T', 'seconds')
state['ts'] = state['last_round_ts']
state['updated'] = ("r573 bm-b: W76 finalize landed (531,748) + W79 freeze+burn in flight (%d/12) + "
                    "chain W1..W77 head 533,948 (bm-a W77) + S6 all-green + zero orders delta" % w79)
state['updated_at'] = state['last_round_ts']
json.dump(state, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json written round 573, w79 shards =', w79)

# --- heartbeat bm-b.json ---
hb = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
epoch = int(time.time())
hb['last_seen'] = datetime.datetime.now().astimezone().isoformat('T', 'seconds')
hb['current_task'] = ('W79 burn in flight (%d/12, engine tick lane); W76 finalize + W79 freeze '
                      'landed r573' % w79)
hb['cpu_cores'] = 16
hb['idle_ram_gb'] = 5.4
hb['gpu_idle_vram_mb'] = 2235  # 8GB - 5765MB used per compute_audit r573 sample
hb['verdict'] = 'healthy-burning (W79 engine lane saturated, py75% audit CLEAN)'
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = datetime.datetime.now().astimezone().isoformat('T', 'seconds')
json.dump(hb, open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert isinstance(hb['heartbeat_epoch_utc'], int)
print('heartbeat written epoch=', epoch)

# --- round report line (bm-b file) ---
rr = r'logs\iteration-loop\round_reports.md'
raw = open(rr, 'rb').read()
t = raw.decode('utf-8')
eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
line = (
    "2026-10-02T11:59+08:00 | r573 | dept:研究+工程 | watermark 绿（red=false·lane healthy·py_low_with_work_cands=W79 烧录在飞合法态·板 0 open/bandit 0/池 ready 0 由引擎线回应） | "
    "做了：①W76 FINALIZE one-pass（prev 529,548 W75 bm-a+2,200=531,748 净链头·K=165,120·S5 4/4·skill_line 1.1646·r310 完备性门 12/12 ls-tree 过·prereg §7/§8 回填 r307 两态）②W79 席位公示先推 origin（MSG-1151-bmb·r565 early-visibility）→W79 FREEZE 五面（68th 波·bm-b 26th 自有·A 201_004..203_003/B 53_401..53_600 双侧算术续带零跳位==W78 行投影逐字·gate ADMIT+banned 0+selftest W2..W79+pf 8/8+FIX-A/B/C 纯增量）③引擎 tick 自燃起烧 W79（shard-0 冻结 commit 前已落=r359 律面·%d/12 收轮时）④S6 全链绿（dualrun 18 连零漂移·audit CLEAN·smoke 47/47·假日 no-new-bar 面）⑤inbox 4 件处理归档（bm-a W75/W77 回执+bm-c 双让路回执+W78 修正单） | "
    "验证：git push 全送达（多轮 ride+rebase·活烧窗 r523 律一次收敛零 abort）·ls-tree origin 12/12 W76+shard 增长面 | "
    "CEO 三行：当前活=W79 引擎烧录 %d/12 在飞；最近实物=results/perpetual_faces/n1_w76_results.json（11:5x·链头 531,748）+W79 冻结包（6a7e0df21）；下里程碑=W79 12/12 烧毕+W78 bm-c 落账后 finalize one-pass（本窗 ≤2h）| "
    "本地未达 origin commit 数=N=0（push+fetch+ls-tree 自证送达）| "
    "下轮指针：W79 12/12 烧毕核验→W78 bm-c finalize 落账后 W79 finalize one-pass（r538 禁重跑·r518 origin 时序）→W80 席位公示+冻结（投影 A 203_004..205_003/B 53_601..53_800 双 CLEAN·W79 行投影）"
    % (w79, w79))
t = t.rstrip('\r\n') + eol + line + eol
open(rr, 'wb').write(t.encode('utf-8'))
print('round report line appended, eol=', repr(eol))
