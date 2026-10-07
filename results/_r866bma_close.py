import json, datetime, time, io

# 1) heartbeat update (own file only)
hb = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
now = datetime.datetime.now(datetime.timezone.utc).astimezone()
hb['last_seen'] = now.isoformat(timespec='seconds')
hb['round'] = 866
hb['current_task'] = ('T-2026-10-08-177 REGIME-5 labeler s1 landed (O-20261007-2215 @bm-a 1); '
                      'next: validation prereg s2 + bull-supply scan leg 2')
hb['cpu_cores'] = 32
hb['ram_free_gb'] = 54.1
hb['gpu_free_vram_gb'] = 5.6
hb['verdict'] = 'green (red=false lane healthy; engine alive idle queue0, W182 seat reserved)'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now.isoformat(timespec='seconds')
hb['ts'] = now.isoformat(timespec='seconds')
hb['orphan_faces'] = 1
hb['orphan_killed'] = 1
with io.open(r'fleet\machines\bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')
# post-write self-check: epoch must be JSON int (R170/R178 law)
chk = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in chk['clock_read'], 'clock_read not T-separated'
print('heartbeat ok, epoch', chk['heartbeat_epoch_utc'])

# 2) round report row (canonical ROOT face per r863/r864 heal)
row = ("2026-10-08T06:52:00+08:00 | r866 | bm-a | dept:research | "
       "WM-VERDICT: green (red=false lane healthy; engine alive, W181 burned 05:28-05:39 12 shards, W182 seat reserved, queue0) | "
       "当前活: O-20261007-2215 @bm-a ① REGIME-5 五态判别器 slice-1 全落地——scripts/regime5_labeler.py (CEO 判据方向 verbatim 数值化, "
       "selftest 15/15, run K=3289 cutoff 2026-09-30: BULL=201/CHOP=2103/GRIND=103/BEAR=780/SUPPORT=102), "
       "标签面 results/regime5_labels/REGIME5-2026-09-30.json 契约三键 (bm-c regime_style_matrix awaiting_upstream 解除在望), "
       "冻结件 research/REGIME5_LABELER_V1.md (冻结先于收益验证; v1.0 面效度修正 SUPPORT_DIST_MAX 0.03→0.15 收录 2015-07-06 正典救市, "
       "修正时点=零收益面消费, 如实留痕); "
       "最近实物: results/regime5_labels/REGIME5-2026-09-30.json + scripts/regime5_labeler.py (06:50) | "
       "下个里程碑: REGIME-5 验证批预注册 (各阶段收益差+显著性+N_CONF 校准+过渡成本, PREREG_TEMPLATE/science_gates) + 牛市进攻供给扫描 leg2, ≤10-14 12:00 大限 | "
       "did: S0-1 孤儿探针双轮同靶 (pid 41108 BigDomain frontdoor, 三面确认) → 刀2 kill 首射收编击杀 (kill receipt 在件); "
       "S0 pull --rebase 1 commit (bm-c r736 regime_style_matrix skeleton); S0.5 双扫 51/51 零未回执; "
       "DEC/ORD changed-hash consumed (ee659451/2bb2ee75: D-20261008-01② F-20261007-01 司面状态列自翻 executed + CEO 物理件区零涉本司新行); "
       "O-2215 bm-a 回执落令件 + 票 T-2026-10-08-177 认领即开工 (O-1730 即时律); "
       "S6 37 faces rc0 (pre-open no-ops, dualrun streak 52); attrition guard CLEAN; hooks byte-equal; "
       "inbox W182 seat MSG (self r865) 处理归档 processed/; 孤儿面=1 (killed=1) | "
       "本地未达 origin commit 数=0 (push 后自证)")
with io.open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(row + '\n')
print('report row appended')
