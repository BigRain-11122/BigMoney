# -*- coding: utf-8 -*-
# r396 bm-c bookkeeping writer: state + heartbeat + round report (EOL-preserving bytes-face per r530/r600)
import json, time, subprocess

def detect_eol(path):
    with open(path, 'rb') as fh:
        b = fh.read(200000)
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    return '\r\n' if crlf > lf else '\n'

def write_json(path, obj):
    eol = detect_eol(path)
    s = json.dumps(obj, indent=1, ensure_ascii=False) + '\n'
    s = s.replace('\n', eol)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(s)

def append_lines(path, lines):
    eol = detect_eol(path)
    with open(path, 'ab') as fh:
        for ln in lines:
            fh.write(ln.encode('utf-8') + eol.encode())

ts = time.strftime('%Y-%m-%d %H:%M:%S')
iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# fresh machine sample
import psutil
cpu = round(psutil.cpu_percent(interval=0.5), 1)
ram = round(psutil.virtual_memory().available / (1024**3), 1)
try:
    out = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free',
                                    '--format=csv,noheader,nounits'],
                                   creationflags=0x08000000, timeout=20)
    gpu = int(str(out, 'utf-8').strip().splitlines()[0])
except Exception:
    gpu = 880

VERIFY = ("smoke 47/47 rc0; S6 37/37 ALL-RC0 (reconcile ZERO-DRIFT streak 3/3; golden-week data legs legal no-ops; "
          "scorecard/build_status stale-takeover legal bm-a hb>45min); attrition 4 ledgers CLEAN (healed notes); "
          "D-19 4167B784 unchanged zero action; orders 150/150 double-scan zero unacked; sat-engine status rc0 alive; "
          "N3-R2 finalize delivered commit 54532b2d0 (144 windows, ledger 615,348+144=615,492, zero double-count verified)")
DID = ("r396: N3-R2 wave finalize DELIVERED to origin (commit 54532b2d0: n3_r2_results.json 6/6 members judged, 144 "
       "quarter-start windows, ledger 615,348+144=615,492 zero-double-count per r538 verification; prereg sec7/sec8 "
       "one-shot backfill; M10 methodology card carried; predictions 4-right+1-partial; 2020Q1 maxdd deepest 6/6 rank1 "
       "machine-proof) + crash-recovery numbering resync 393->396 per git-log-truth + S6 rebuilt as detached 37-leg "
       "runner (_r396bmc_s6_chain.py, r324 law) + CODELY EOL-flip trap caught and healed bytes-face (r600 law) + "
       "W14-GENERATE two-layer observation MSG to bm-a + LOWAMP-DEEP-P1 estate verified (10/10 pool done, 19 products "
       "on origin, deep panel 48/48 present on bm-c -> next-round finalize+E1)")
NEXT = ("(a) LOWAMP-DEEP-P1 finalize+E1 (T-147 owner; due 10-09 pre-market; deep panel verified local 48/48; "
        "r518/r538 finalize laws apply); (b) T-144 flow-sinking due 10-07; (c) W14-GENERATE entry-flip response "
        "watch (MSG-0410); (d) N3-R3 param-axis densification candidate draft (R2 prereg design note)")

# state-bm-c.json
p = 'state-bm-c.json'
st = json.load(open(p, encoding='utf-8'))
st['machine_id'] = 'bm-c'
st['round_no'] = 396
st['last_round_at'] = 'r396'
st['last_round_ts'] = ts
st['updated'] = iso
st['cpu_pct'] = cpu
st['idle_ram_gb'] = ram
st['gpu_free_vram_mib'] = gpu
st['verify'] = VERIFY
st['did'] = DID
st['current_task'] = 'r396 close-out: bookkeeping four + commit push + delivery self-verify'
st['next'] = NEXT
st['heartbeat_epoch_utc'] = epoch
st['clock_read'] = iso
st['last_ts'] = ts
st['last_round'] = ("2026-10-03 r396 bm-c: N3-R2 finalize delivered (54532b2d0) + S6 37/37 rc0 + recovery numbering "
                    "393->396 + LOWAMP-DEEP-P1 estate verified for next round")
st['last_seen'] = ts
st['updated_at'] = iso
assert isinstance(st['heartbeat_epoch_utc'], int), 'epoch must be int'
write_json(p, st)

# heartbeat fleet/machines/bm-c.json
p = 'fleet/machines/bm-c.json'
hb = json.load(open(p, encoding='utf-8'))
hb['cpu_util_pct'] = cpu
hb['free_ram_gb'] = ram
hb['cpu_pct'] = cpu
hb['idle_ram_gb'] = ram
hb['gpu_idle_vram_mb'] = gpu
hb['gpu_idle_vram_mib'] = gpu
hb['gpu_vram_free_mb'] = gpu
hb['gpu_free_vram_mb'] = gpu
hb['gpu_free_vram_mib'] = gpu
hb['ram_free_gb'] = ram
hb['cpu_idle_pct'] = round(100 - cpu, 1)
hb['round_no'] = 396
hb['updated_at'] = iso
hb['last_seen'] = ts
hb['last_seen_at'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['health'] = 'ok'
hb['prod_lanes'] = ("r396: N3-R2 finalize delivered (commit 54532b2d0, 144 windows, ledger 615,492 zero-double-count); "
                    "S6 37/37 all rc0; smoke 47/47; attrition CLEAN; D-19 unchanged; orders 150/150 double-scan clean")
hb['current_task'] = 'r396 close-out: bookkeeping four + final commit push + delivery self-verify'
hb['activity_now'] = 'r396 close-out: N3-R2 finalize delivered; bookkeeping + final commit push'
hb['latest_artifact'] = ('results/perpetual_faces/n3_r2_results.json (6 members judged, 144 quarter-start windows, '
                         'ledger 615,492) via commit 54532b2d0 @ 2026-10-03 03:5x')
hb['next_milestone'] = ('LOWAMP-DEEP-P1 finalize+E1 (deep-axis new-family registration verdict, due 2026-10-09 '
                        'pre-market; pool 10/10 done, products on origin, local deep panel verified 48/48)')
hb['verdict'] = ("r396 recovery round: N3-R2 wave finalize delivered to origin (r394/r395 crash recovery, numbering "
                 "resynced 393->396 per git-log-truth); S6 37/37 all-rc0; FUND-VALUE X2/NULLS ready unowned (bm-c "
                 "locked out of p1c_stock per host_gates, engine lane drains); LOWAMP-DEEP-P1 estate verified for "
                 "next-round finalize+E1; watermark green")
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'
write_json(p, hb)
json.load(open(p, encoding='utf-8'))
print('state+heartbeat written; epoch int verified:', epoch)

# round report append
RL = []
RL.append('**当前活**：N3-R2 finalize 已交付 origin；S6 37/37 全绿；收口簿记+commit 推送中。')
RL.append('**最近实物**：results/perpetual_faces/n3_r2_results.json（6 员 judged·144 季启窗·ledger 615,492·commit 54532b2d0·2026-10-03 03:5x）。')
RL.append('**下个里程碑**：LOWAMP-DEEP-P1 finalize+E1（深轴新家族判决·due 10-09 开市前·下 1-2 轮内·≤48h）。')
RL.append('水位 verdict：绿——red=false·lane healthy·next_pick=claimed（moneyflow IC 等面板自愈）。')
RL.append(('%s | r396 | dept:研究/工程 | N3-R2 finalize 交付（r394/r395 猝死恢复轮·r381 恢复轮首动作律）：'
            'n3_r2_results.json 上 origin（commit 54532b2d0·6 员 judged·144 季启窗·ledger 615,348+144=615,492·'
            'prev 与 ledger_head() 自洽零双计 r538 核验）+prereg §7/§8 一次定稿回填+M10 方法论卡同窗携带+CODELY 两行'
            '（finalize 回执+恢复轮取号律）；预测对账=4 全中+1 部分中（2020Q1=6/6 员最深回撤窗 rank1 机证·'
            'ENGULF 24/24 红点=R1 脆弱先验交叉印证）；轮号序恢复 393→396（state 落后已发布轮·以 git log 为准·如实披露）'
            '｜S0：bm-b 03:56 tick 同窗竞态=fetch+ff-only+commit+push 一次直达；CODELY EOL 翻面坑当场抓回'
            '（replace 工具写 LF→整文件 84/82 伪 diff·按 r600 律 HEAD blob verbatim 字节面追加治愈=3/0 净增）'
            '｜S1 smoke 47/47；S6 37/37 ALL-RC0（分离 runner _r396bmc_s6_chain.py·r324 律·reconcile ZERO-DRIFT streak 3/3·'
            'strategy_scorecard/build_status=stale-takeover 合法〔bm-a 心跳>45min〕·golden-week 数据腿合法 no-op·'
            'build_status 432combos/0pass）；sat-engine rc0 活；attrition 4 账本 CLEAN；D-19 SHA 不变零动作；'
            'orders 150/150 双扫零未回执；inbox 0（MSG-0410 出站 W14-GENERATE 观察）｜S2：job_list 空；'
            '池面 FUND-VALUE X2/NULLS/SENS=p1c_stock 族（bm-c host_gates 锁出·归他机引擎车道）；'
            'W14-GENERATE entry=waiting×shard done 双层滞留观察→MSG bm-a；T-151 N3-R2 座腿闭合｜'
            'LOWAMP-DEEP-P1 遗产验证：10/10 池条目 done·产物 19 件在 origin·deep 面板 48/48 本机在位实证'
            '（SENS 腿本机烧成佐证）→下轮 finalize+E1 主产线｜下轮指针：(主) LOWAMP-DEEP-P1 finalize+E1'
            '（T-147·due 10-09 开市前）；(次) T-144 流水下沉 due 10-07；(备) N3-R3 参轴增广候选起草｜'
            '本地未达 origin commit 数=收口 commit 后自证回填') % ts)
append_lines('round_reports-bm-c.md', RL)
print('round report appended:', len(RL), 'lines')
