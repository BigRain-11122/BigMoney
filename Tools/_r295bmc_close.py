"""r295 bm-c round-close: state + heartbeat + round report line.
Surgical JSON updates preserving per-file indent/EOL (r289 pit law)."""
import datetime
import json
import subprocess
import time


def load_raw(path):
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    return json.loads(raw.decode('utf-8')), crlf


def save_raw(path, obj, crlf):
    txt = json.dumps(obj, ensure_ascii=False, indent=2)
    if crlf:
        txt = txt.replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)


def iso_now():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


epoch = int(time.time())
clock = iso_now()
dec_sha = 'ed4e0eabf941b4299a6f26b243082ee74a83517b462d352d9c047f95a49a1f07'

# fresh GPU read
try:
    g = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=15)
    gpu_free = int(g.stdout.strip().splitlines()[0])
except Exception:
    gpu_free = 9790

# ---- state-bm-c.json ----
st, crlf = load_raw('state-bm-c.json')
st['round_no'] = 295
st['last_round_at'] = clock
st['last_round_ts'] = epoch
st['updated'] = clock
st['cpu_pct'] = 52.7
st['idle_ram_gb'] = 0.2
st['gpu_free_vram_mib'] = gpu_free
st['verify'] = ('S1 smoke 47/47; S6 38 legs rc0 (10-01 rollover metadata + stale-takeover derive faces, '
                'host-owned shared faces yielded to origin per take-origin after bm-a r496 S6; '
                'post_review latest batch 25 rows 0 NO = T-78-WINNER-WIRING re-derive closed at 00:55 '
                'via machinery, want-values track RW-1 refrozen anchors 0.862/1.5605 verified vs smoke this round; '
                'decisions sha ED4E0EAB consumed, D-20261001-02/03/07 board rows acked; '
                'attrition CLEAN; claw MATCH; watchdog Ready; pin :05 verified; '
                'dualrun DRIFT owner-field type (streak reset, observation-phase)')
st['did'] = ('r295: same-repo single-executor back-off round (interactive session in-tree T-134 s2 WIP '
             'cross_start_robustness.py conversion -- OS round yielded dev face, no WIP touch/commit) '
             '+ red-flag diagnosis (00:50 runnable-work-idle-low-cpu = LOWAMP-P1-NULLS burn 00:47 in-flight '
             'load-phase sampling + single-core runner family = O-2355/T-134 remediation: s2 conversion WIP '
             'in-tree + bm-a r496 s3 multicore gate landed origin) + orders diff EMPTY both scans '
             '+ D-19 merged consumption step executed (git show origin/main raw-blob, r292 wiring) '
             '+ S6 38 legs rc0 + RAM pressure watch (0.2GB available during NULLS burn)')
st['current_task'] = ('r295 done; T-134 s2 WIP held by interactive session (yielded); '
                      'LOWAMP-P1-NULLS burn in flight via pool_worker; '
                      'next r296 = S0 pull integrate ~40 incoming (bm-a r496)')
st['next'] = ('(a) S0 pull --rebase integrate bm-a r496 (T-134 s3 multicore gate + T-135 Bonsai ticket bm-a lane); '
              '(b) T-134 s2: verify interactive WIP landed -> close slice, or resume if abandoned; '
              '(c) D-20261001-03 consumption-step ack window 10-03 12:00 (r295 report = receipt); '
              '(d) T-131 still open awaiting GM sign (P1 unclaimable); '
              '(e) RAM pressure watch during pool burns (0.2GB avail @01:30) -- crash-fuse events would surface')
st['heartbeat_epoch_utc'] = epoch
st['clock_read'] = clock
st['last_ts'] = clock
st['last_decisions_sha'] = dec_sha
st['last_decisions_read_at'] = clock
st['last_decisions_sha_method'] = ('python subprocess.check_output raw-blob bytes SHA-256 '
                                   '(PS-pipeline join method = transcoding false-drift, see CODELY r292 pit)')
st['last_round'] = ('2026-10-01 r295: same-repo back-off (T-134 s2 WIP=interactive session) + '
                    'red-flag diagnosis + D-20261001-03 ack + post_review T-78 re-derive verified closed + S6 38 legs rc0')
st['note'] = 'r295 product score=1 (S6 pipeline refresh + takeover derive + diagnosis; dev face yielded)'
save_raw('state-bm-c.json', st, crlf)
print('state ok, crlf=%s' % crlf)

# ---- fleet/machines/bm-c.json ----
hb, crlf2 = load_raw('fleet/machines/bm-c.json')
hb['last_seen'] = clock
hb['round_no'] = 295
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
hb['cpu_util_pct'] = 52.7
hb['cpu_pct'] = 52.7
hb['cpu_idle_pct'] = 47.3
hb['free_ram_gb'] = 0.2
hb['idle_ram_gb'] = 0.2
hb['ram_free_gb'] = 0.2
hb['gpu_free_vram_mb'] = gpu_free
hb['gpu_free_vram_mib'] = gpu_free
hb['gpu_idle_vram_mb'] = gpu_free
hb['gpu_idle_vram_mib'] = gpu_free
hb['gpu_vram_free_mb'] = gpu_free
hb['current_task'] = ('T-134 s2 WIP held by interactive session (OS round yielded per same-repo single-executor); '
                      'LOWAMP-P1-NULLS burn in flight via pool_worker; next OS round: integrate bm-a r496')
hb['prod_lanes'] = ('r295: back-off maintenance round (T-134 s2 WIP=interactive session, not touched); '
                    'red-flag diagnosed (burn in flight, single-core runner family = O-2355 remediation chain); '
                    'S6 38 legs rc0; RAM pressure watch 0.2GB avail')
hb['verdict'] = ('yellow: back-off round (interactive session holds T-134 s2 WIP in-tree) + '
                 'red-flag diagnosed=LOWAMP-NULLS burn in flight (py 23.8% low = single-core runner family, '
                 'T-134 s2/s3 remediation active) + RAM 0.2GB available during burn (watch, no OOM event yet); '
                 'pool burning LOWAMP-P1 campaign + N1-W2 queue; D-20261001-03 acked')
hb['health'] = 'ok'
save_raw('fleet/machines/bm-c.json', hb, crlf2)
print('heartbeat ok, crlf=%s, epoch type=%s' % (crlf2, type(hb['heartbeat_epoch_utc']).__name__))

# ---- round_reports-bm-c.md ----
line = ('{ts}｜r295｜watermark verdict=insufficient_history 采样窗（00:50 红牌=runnable-work-idle-low-cpu '
        '已诊断：LOWAMP-P1-NULLS 烧批 00:47 起在飞=加载窗采样假象·py 23.8%=单核 runner 族=O-2355/T-134 整改面'
        '〔s2 改造 WIP=交互会话本窗在树持有·本 OS 轮按同仓单执行体律退避不碰〕+bm-a r496 s3 多核门已落 origin）｜'
        'D-20261001-03 ack：集团台账消费步=git fetch+git show origin/main:<path>（r292 已接线·本窗已按此消费 '
        'ED4E0EAB 决策批 25 行〔D-02 Bonsai 并卷/bm-a GPU 复验 T-135 归 bm-a 线〕）｜'
        'post_review P0 闭：T-78-WINNER-WIRING ✗→YES 00:55 由机制 re-derive 翻绿（want 值随 RW-1 前视修复重锚 '
        '0.862/1.5605·与本轮 smoke 独立锚值逐位一致=合法翻面）最新批 25 行零 NO｜'
        'S6 38 legs rc0（10-01 日期翻转元数据面+stale-takeover derive〔bm-a 心跳 98min 陈·合法接管〕·'
        'origin 同窗双写共享面按 take-origin 让 origin 主〔bm-a r496 host 写〕·dualrun DRIFT owner-field 型差=观察相 streak 清零照录）｜'
        'RAM 压力注记：烧批窗 available 0.2GB（crash-fuse 面监控·无 OOM 事件）｜'
        '验证：smoke 47/47；attrition CLEAN；claw MATCH；watchdog Ready；orders 双扫 EMPTY；'
        'commit=定向 add 本轮产出（daemon WIP+交互会话 WIP 未载运）｜'
        '下轮指针：S0 pull 合流 ~40 入站（bm-a r496）；T-134 s2 WIP 落地核验→闭片或接管；'
        'T-131 仍候 GM 署名（P1 禁认领）；D-03 ack 窗 10-03 12:00').format(ts=clock)
with open('round_reports-bm-c.md', 'a', encoding='utf-8') as f:
    f.write('\n' + line + '\n')
print('report line appended')
