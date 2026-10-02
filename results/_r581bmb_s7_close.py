# -*- coding: utf-8 -*-
# r581 bm-b S7 closeout: state + heartbeat + round report + CODELY lesson + inbox archive
import json, os, shutil, time, datetime

NOW = datetime.datetime.now()
TS = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
R = 581

# 1. state.json
st = json.load(open('state.json', encoding='utf-8'))
st['machine_id'] = 'bm-b'
st['round_no'] = R
st['note'] = ('r581: dead-r579/r580 diagnosis (state stopped 578 + git self-labeled r580 = r529 law, '
              'round skipped to 581); W97 FREEZE five-face landed + pushed (87th engine wave, bm-b 33rd owned; '
              'A 237_004..239_003 arithmetic CLEAN + B 58_001..58_200 D-20261002-05 pin at im_ic_pair=58_000 '
              'median 99/199, W68-B anchor; seat MSG-20261002-1545-bmb pushed before freeze per r565); '
              'engine self-ignited W97 (tick, burn in flight at close); W93 finalize one-pass landed '
              '(prev 566,948 W92 bm-c unblocked + 2,200 = 569,148, K=202,520, K-lift -0.0002 honest negative, '
              'S5 4/4 PASS, sec7/8 backfilled) -> unblocks W94 bm-a; W95 (own) next finalize pending W94; '
              'W95 12/12 shard products delivered to origin (r310); r580 estate adopted (3 CODELY lessons + tools); '
              'S0 double surgery under live writers (CODELY union per r580 clobber-trap lesson, deletion-set '
              'empty x2); D-19 MATCH-unchanged 937A373D')
st['last_round_at'] = EPOCH
st['last_round_ts'] = TS
st['ts'] = TS
st['updated'] = 'r581 bm-b: W97 freeze + ignition + W93 finalize landed + S6 all-green'
st['updated_at'] = TS
st['last_decisions_at'] = st.get('last_decisions_at') or TS
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json -> r581')

# 2. heartbeat fleet/machines/bm-b.json
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = TS
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = TS
hb['current_task'] = ('W97 burn in flight (engine tick, 6+/12 shards); W93 finalize landed (chain 569,148); '
                      'W95 finalize pending W94 bm-a')
hb['cpu_cores'] = 16
hb['round_no'] = R
hb['round_no_label'] = 'r581'
hb['verdict'] = ('healthy-burning (W97 self-ignited post-freeze; W93 finalize one-pass chain-linear; '
                 'supply line relay W98 seat bm-a published; D-19 unchanged)')
import psutil
hb['cpu_util_pct'] = psutil.cpu_percent(interval=0.5)
vm = psutil.virtual_memory()
hb['free_ram_gb'] = round(vm.available / 1024**3, 1)
hb['idle_ram_gb'] = hb['free_ram_gb']
hb['ram_free_gb'] = hb['free_ram_gb']
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('heartbeat -> r581, epoch int OK, cpu=%s ram=%s' % (hb['cpu_util_pct'], hb['free_ram_gb']))

# 3. round report line (bm-b lineage file)
REPORT_LINE = (
    TS + " | r581 bm-b | dept:研究/工程 | [watermark verdict: 15:37 probe insufficient_history n=2（15min 窗重置态·非红如实）"
    "+audit FLAG:supply_floor=池饿 0 ready+本机引擎队列空（W95 12/12 烧毕）=never-dry 供给律触发·本轮治愈=W97 冻结+自燃在烧] | "
    "本轮主产出（实物）：(1) **W97 FREEZE 五面落地+推 origin**（第 87 枚引擎波·bm-b 第 33 自有·A 237_004..239_003 算术 CLEAN+"
    "B 58_001..58_200 **D-20261002-05 钉=SEED_REGISTRY im_ic_pair=58_000 中位 99/199 越 hit 起窗**·W68-B 50_501..50_700 同构正断言锚·"
    "席位 MSG-20261002-1545-bmb 先推 origin r565 律·ADMIT 回执 results/_r581bmb_w97_band_gate.py rc0 单态·banned gate ADMIT 0·"
    "pf selftest 9/9+n1 缺省波 selftest PASS·W98 投影 A 239_004..241_003/B 58_201..58_400 双 CLEAN）"
    "**引擎 tick 自燃实证**（收轮时 6/12 在烧 pid55900·r325 产物增长律）"
    "(2) **W93 finalize one-pass 落账**（prev=566,948=W92 bm-c r372 解锁·链序正·+2,200=**569,148**·K=202,520·"
    "w93-only mu=−0.0969452 σ=0.2428347·merged mu=−0.0927304·K-lift **−0.0002** 正负交替如实报负·se_mu 链 0.000563→…→0.000544·"
    "§5 四门全过（Δmu 0.0042<0.02/σ −2.3%<±10%/A p95 差 0.0274<0.05/K-lift 门内）·§7/§8 机械回填+stdout 留档+"
    "ledger 块在产物内持久化 r509 幻影面零）→**解锁 W94 bm-a finalize**（12/12 产品已在 origin）"
    "(3) W95 12/12 分片产品补推 origin（r310 完备性·shard-0 由 r580 冻结 commit 携带+1-11 本轮）+"
    "r580 猝死会话遗产收编（CODELY 三条教训验证收编+S6 链工具/收尾脚本入档 r471 律）"
    "(4) S0 双外科整合（15885fc29→36a530dca 两推·**CODELY union=防他机行顶替** r580 教训执行面·删集空断言×2·"
    "pre-push 爪两救=origin 三机并发窗快进面·n1_w97 在飞产品按律排除 ride-next） | "
    "smoke 47/47；S6 28 腿全绿假期 no-op（dualrun streak 25/3 零漂移）；D-19 MATCH 937A373D 零动作；"
    "orders 143/143 双扫 EMPTY；月度三件套晨间已落（BRIEF/SELF-REVIEW-202609 05:26+science_audit 05:09）；"
    "attrition CLEAN；本地未达 origin commit 数=0 | "
    "下轮：候 W94 bm-a finalize 落账→**W95 finalize（本机波）**；W97 12/12 烧毕收官+产品推 origin\n"
)
with open('logs/iteration-loop/round_reports.md', 'ab') as f:
    f.write(REPORT_LINE.encode('utf-8'))
print('round report appended')

# 4. CODELY S4 lesson (one entry, two coupled pitfalls from this window)
LESSON = (
    "- [2026-10-02 16:1x r581 bm-b] 冻结 PASS 片段锚=拼接短语不可假设连续＋手术 my_files∩their_mod 整文件面=CODELY 顶替复发面（W97 冻结+S0 双外科实弹）："
    "①freeze 生成器第 5 面（PASS 片段）锚取「短语级拼接文本」（如 law sec.4 W96 row, r581 bm-a] \"）在他机把尾段分写两行字串面（bm-a W96 分写为『law sec.4 W96 』+『row, r581 bm-a] 』两行字串）时 find 恒空——"
    "锚必须取片段尾行**单行字面量**+post-anchor guard（『+ T-141 s2』在场）；幂等重跑治愈（1-4 面 SKIP 面设计）。"
    "②r580 手术工具 my_files 无条件 hash-object 整文件——本窗 my committed delta 与 origin delta 在 CODELY.md 相交（我加 3 条 r580 教训 vs bm-a r582 加 2 条 r581 坑律）时整文件面=结构性顶替他机行（r580 W94-heal 教训的手术工具自犯面）；"
    "修=手术前对 my_files∩their_mod∩append-only 类逐件 union（origin blob 底+我 diff-added 行尾插·_r581bmb_s0_surgery.py union_codely 范式）+树内断言（bm-a/bm-c 尾行在场+r580 行在场双验）。"
    "How to apply：W98+ 冻结生成器第 5 面锚一律取尾行单行字面量；手术/重放工具遇 my_files∩their_mod 且该件为 append-only 台账（CODELY/登记簿类）必先 union 后入 payload，纯 derive 面（S6 共享 JSON）整文件取任一侧皆可（下轮重 derive 自愈）。\n"
)
with open('CODELY.md', 'ab') as f:
    f.write(LESSON.encode('utf-8'))
print('CODELY lesson appended')

# 5. archive processed inbox seat MSGs
os.makedirs('fleet/inbox/processed', exist_ok=True)
for m in ['MSG-20261002-1531-bma-w96-seat.md', 'MSG-20261002-1545-bmb-w97-seat.md',
          'MSG-20261002-1603-bma-w98-seat.md']:
    src = os.path.join('fleet/inbox', m)
    dst = os.path.join('fleet/inbox/processed', m)
    if os.path.exists(src):
        shutil.move(src, dst)
        print('archived', m)
    elif os.path.exists(dst):
        print('already archived', m)
print('CLOSEOUT_Writes_OK')
