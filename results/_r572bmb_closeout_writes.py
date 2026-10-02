import json, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 1) CODELY.md S4 memory line (bytes law r530)
P = 'CODELY.md'
b = open(P, 'rb').read()
t = b.decode('utf-8')
line = ('\n- [2026-10-02 11:4x r572 bm-b] git status porcelain 固定列解析勿先 strip 坑（face 同步脚本实弹·幸运零害自抓）：解析 `XY PATH` 固定列格式前对整行 line.strip() 会剥掉前导状态列空格使 path 切片错位 2 字符（` D fleet/...` → strip → `D fleet/...` → raw[3:] 得 `leet/...`）——checkout 全批 pathspec 不存在 fail-fast（零误 checkout 零害），keep-local 白名单匹配同失效（幸路径错位使危险 checkout 也全败=双反零害）；修复=保留原行按 raw[:2]/raw[3:] 列位切。How to apply：一切解析 git status --porcelain / diff --name-status 等固定列输出的脚本禁先 strip，按列位切片；写后必打印解析样本核位（本例靠 per-file 重试错误信息当场定位）。\n')
if not t.endswith('\n'):
    t += '\n'
t += line.lstrip('\n')
open(P, 'wb').write(t.encode('utf-8'))
print('CODELY appended, size=%.1fKB' % (len(t.encode("utf-8"))/1024))

# 2) round report line (bm-b uses logs/iteration-loop/round_reports.md)
now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
rep = now + ' | r572 | dept:研究/工程 | watermark verdict=绿：py_low_with_work_cands=采样窗跨冻结前闲段（W74 finalize/W76 冻结=git 面非算力面）+W76 烧录在飞=引擎车道合法工作面（engine alive round-zero rc0·点火实证=冻结 commit 后产物增长 r325 律）。当前活=W76 烧录在飞（4/12 落盘·tick 自续）。最近实物=results/perpetual_faces/n1_w74_results.json（W74 FINALIZE one-pass @11:3x·prev 525,148〔W73 bm-a r571 活链头·origin 时序面 r518 律〕+2,200=527,348 净链头·K=160,720·S5 4/4 PASS〔muΔ0.004521/σ−1.15%/p95Δ0.0255/K-lift+0.0002·se_mu 0.000611 收窄链〕·prereg §7/§8 机械回填 r307 两态绿·r538 一过例）+ W76 FREEZE commit 24ec53190（第 65 枚引擎波·bm-b 第 25 枚自有波·双侧算术续带 A 195_004..197_003/B 52_401..52_600 零跳位零分叉==bm-a W75 行 W76+ 投影逐字互证·gate ADMIT 回执 results/_r572bmb_w76_band_gate.py·W77+ 投影 A 197_004..199_003/B 52_601..52_800 双 CLEAN 机证·禁向闸 ADMIT·席位 MSG-20261002-1130-bmb published=reserved·W75 bm-a 烧录在飞=一在飞上游席 FAIL-CLOSED r307）。下个里程碑=W76 12/12 烧毕→finalize one-pass（链序前置=W75 bm-a 落账·窗 ≤48h 随 W75 进度）+W77 冻结（never-dry 常设步·表尾 W76 后首自由号）。实况=D-19 MATCH-unchanged（4FD50184 零动作）；orders 零差集双扫（143/143）；smoke 47/47；S6 全链绿（dualrun streak 17/3 零漂移〔排 compute_audit 前〕·audit rc0 CLEAN burning-healthy·WM rc0·假日无新 bar cutoff 2026-09-30→live.paper/t35_open_fill/t24 触发件合法跳过·REPORT-2026-10-02/LIVE-2026-10-02 再生·月度三件〔science_audit/self_review/briefing〕10-02 晨已跑免双跑·车道 17 项 rc0）；attrition CLEAN（bm-a 4 行 healed 注记照录）；inbox 3 件归档（1108-bmb/1125-bma/1130-bmb）；face 同步=r354 phantom-D 盘点→origin 新面 checkout+pool_core_samples union（origin 775+本机 4 行·dict 全绿 r570 律）+x2_watch 取 origin（本机子集）；外科推送 ×4（W74 shard8/9→shard10/11→finalize 产品+prereg 回填→W76 冻结·diff-based payload+删除集断言四发全过·r519 族零犯）；CODELY.md=124KB 超 50KB 水位照 r504 注记（在役坑律正典·阈值重锚=集团/GM 裁定面）如实披露。验证=commits 062235abe/3dc15cc2e/7bf94fbab/24ec53190 origin ls-tree 送达复核+selftest W2..W76 全链 PASS（缺省波调用 r522 律）+引擎 status 活（heartbeat 51s）+W76 点火 4 分片产物增长实证。本地未达 origin commit 数=0（收尾 push 后复核）。'
with open('logs/iteration-loop/round_reports.md', 'ab') as f:
    if not open('logs/iteration-loop/round_reports.md', 'rb').read().endswith(b'\n'):
        f.write(b'\n')
    f.write((rep + '\n').encode('utf-8'))
print('round report appended')

# 3) state.json r572
epoch = int(time.time())
st = json.load(open('state.json', encoding='utf-8'))
st['round_no'] = 572
st['note'] = ('r572: W74 FINALIZE one-pass landed (prev 525,148 = W73 bm-a r571 head, +2,200 = 527,348 net, K=160,720, S5 4/4, prereg s7/s8 backfill, r538 no-rerun) '
              '+ W76 FREEZE delivered (65th wave, bm-b 25th owned; A 195_004..197_003 / B 52_401..52_600 BOTH SIDES arithmetic continuation zero skip == W75 row projection verbatim; '
              'gate ADMIT results/_r572bmb_w76_band_gate.py; seat MSG-20261002-1130-bmb) + W76 burn in flight (4/12, tick self-ignited post-freeze-commit); '
              'D-19 MATCH-unchanged; orders zero-delta 143/143; smoke 47/47; dualrun 17/3; S6 all-green (holiday no-new-bar, monthly trio already run 10-02 AM); '
              'next = W76 12/12 burn complete + finalize one-pass AFTER W75 bm-a finalize lands (chain order, FAIL-CLOSED r307) + W77 freeze (projection A 197_004..199_003 / B 52_601..52_800 both CLEAN)')
st['last_round_at'] = epoch
st['last_round_ts'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
st['ts'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
st['updated'] = 'r572 bm-b: W74 finalize landed (527,348) + W76 freeze+burn in flight (4/12) + S6 all-green + zero orders delta'
st['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json r572 written, epoch=%d (int check: %s)' % (epoch, isinstance(epoch, int)))

# 4) heartbeat fleet/machines/bm-b.json
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = time.strftime('%Y-%m-%dT%H:%M:%S+0800')
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
hb['current_task'] = 'W74 finalize landed (head 527,348) + W76 frozen (A 195_004..197_003/B 52_401..52_600) + W76 burn in flight 4/12; next: W76 finalize after bm-a W75 finalize; W77 freeze projected'
hb['round_no'] = 572
hb['round_no_label'] = 'r572'
hb['verdict'] = 'healthy: W74 finalize one-pass landed (527,348, K=160,720, S5 4/4), W76 frozen+burning (65th wave, both-sides arithmetic continuation), chain order W75 bm-a pending for W76 finalize'
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written, epoch int verified')
