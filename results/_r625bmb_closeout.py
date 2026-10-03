# r625 bm-b closeout: state.json round_no+1, round report line, heartbeat.
# UTF-8 source; ASCII-only console output (GBK console law).
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())
STAMP = NOW[:16]  # 2026-10-03T17:3x

NOTE = ("r625: D-06 increment sweep executed -- 6 hot pit entries verbatim migrated to domain files "
        "(pit-git +4: r619/r620/r621/r624 rebase-race family; pit-ps +1: r618 tool-signature+D-19 channel; "
        "pit-spawn +1: r618 croc relay garbage-bytes), zero-loss PASS (cores 3800+733+827B, 3 md5, "
        "root CODELY 24238->19386B, ptr clauses x3); orders 151/151 double-scan zero unacked; "
        "D-19 watermark identical 4167b784 zero action; smoke 47/47; S6 33 legs rc0 golden-week no-ops; "
        "burns alive Q184/V288/D84 of 2000 (k holes under _done_keys self-heal); S7: watchdog needlessly "
        "rebuilt (r618 tool-signature pit re-offense: -FilePath vs real -Exe, idempotent-harmless, "
        "re-verified present), claws ok, attrition CLEAN")

REPORT = (STAMP + "+08:00 | R625 bm-b (dept:工程·D-06 收编执行轮) | watermark verdict: GREEN "
          "(red=false; WM loaded_ok py~75% local_batch_running; audit CLEAN flags=0 zombies=0; "
          "dualrun ZERO-DRIFT streak 15; smoke 47/47) | 当前活: FUND 三件 NULLS 烧在飞 "
          "(Q184/V288/D84 行·k 空洞=_done_keys 自愈面在护·finalize have==2000 硬门) | "
          "最近实物: D-06 增量回扫 6 条坑律入域件——research/pit-git.md +4 条 (r619/r620/r621/r624 rebase "
          "竞态族·核 3800B·md5 2f7ab9fc…) + research/pit-ps.md +1 条 (r618 工具签名漂移+D-19 通道备胎复合条·核 733B) + "
          "research/pit-spawn.md +1 条 (r618 croc relay 垃圾字节面·核 827B)·根件 24238→19386B·零丢失断言 PASS·"
          "回执+迁移脚本 results/_r625bmb_d06_sweep_receipt.json 17:1x 落地 | 下个里程碑: NULLS 三件 have==2000 "
          "finalize 判决 (约 10-06); D-06 全线收口窗 10-07 (bm-b 自有增量已清·余=bm-a r631 热条归域+流水下沉集团裁定) | "
          "did: S0 churn-absorb r625+rebase clean; S0.5 orders 151/151 双扫零未回执; D-19 水位恒等 4167b784=零动作; "
          "S1 47/47; S2 双板空+零开放票; S3 饱和引擎 exit0 活 (py 71.8%/queue 0); 烧验收看护=三件推进 +14~17 行/轮; "
          "S6 33 腿全 rc0 (golden-week 诚实 no-op·cutoff 09-30); S7 自愈=loop pin=2 no-op·watchdog 无谓重建 "
          "(r618 工具签名坑再犯实录·-FilePath 撞真签名 -Exe·幂等无害·正签名复验在位)·precommit/prepush 双爪 ok·"
          "attrition CLEAN·orders 复扫 151 恒等 | 本地未达 origin commit 数=0 (push+fetch 自证) | "
          "下轮指针: NULLS 验收看护+finalize 门在位巡检; bm-a r631 热条归域随属主扫勿代劳\n")

# --- state.json (bm-b face) ---
s = json.load(open('state.json', encoding='utf-8'))
s['round_no'] = 625
s['note'] = NOTE
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at', 'last_seen'):
    s[k] = NOW
s['last_decisions_at'] = s.get('last_decisions_at') or NOW
s['round_no_label'] = 'r625'
json.dump(s, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- round report (bm-b uses shared iteration-loop ledger) ---
p = 'logs/iteration-loop/round_reports.md'
b = open(p, 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') >= b.count(b'\n') - b.count(b'\r\n') else b'\n'
if b.endswith(b'\r\n') or b.endswith(b'\n'):
    add = REPORT.encode('utf-8').replace(b'\n', eol)
else:
    add = eol + REPORT.encode('utf-8').replace(b'\n', eol)
open(p, 'ab').write(add)

# --- heartbeat fleet/machines/bm-b.json ---
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['round_no'] = 625
hb['round_no_label'] = 'round 625 (bm-b)'
hb['current_task'] = ('r625 done: D-06 increment sweep 6 entries into pit-git/ps/spawn zero-loss PASS; '
                      'next: NULLS burn acceptance watch + finalize (~10-06)')
hb['verdict'] = ('active: r625 D-06 sweep delivered; burns alive (NULLS trio); WM loaded_ok; '
                 'audit CLEAN; dualrun streak 15')
for k in ('ts', 'updated', 'updated_at'):
    hb[k] = NOW
hb['cpu_util_pct'] = 44.0
for k in ('free_ram_gb', 'idle_ram_gb', 'ram_free_gb', 'ram_avail_gb'):
    hb[k] = 3.28
hb['gpu_idle_vram_gb'] = 2.29
hb['gpu_idle_vram_mb'] = 2292
for k in ('gpu_free_vram_gb', 'gpu_free_vram_mb', 'gpu_vram_free'):
    hb[k] = 2.29 if 'gb' in k else 2292
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# self-verify: epoch int type + clock T separator (R170/R178/R262 law)
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be ISO8601 T-form'
st = json.load(open('state.json', encoding='utf-8'))
assert st['round_no'] == 625
print('CLOSEOUT_OK stamp=%s epoch=%d' % (STAMP, EPOCH))
