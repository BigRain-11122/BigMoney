import json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# 1. state.json: round_no 976->977 + watermark keys
st = json.load(open('state.json', encoding='utf-8'))
st['round_no'] = 977
st['last_decisions_sha'] = '578804c1'
if 'last_orders_sha' in st:
    st['last_orders_sha'] = '0d7b4fe2'
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no->977, decisions_sha->578804c1')

# 2. round report append (binary-safe append-only, r962 law)
line = (
    "2026-10-15 12:2x | r976(续,11:32轮被杀后12:02重开) | 完成包落地窗主段: S6全链38腿0bad CHAIN_DONE(r947树毁后首跑绿,results/_r976bmb_s6_log.txt)+smoke 49/49绿+attrition CLEAN+饱和引擎活(idle)+孤儿探针17面/1孤儿(i2v XQ05族观察面) | D-19双sha变更消费:decisions 6910a9ed->578804c1/orders 46c60d47->0d7b4fe2,delta=O-20261015-1200 CEO直接令token治理包(委员会牵头/HQ收口窗执笔/O-1055 MV线明示不影响/无@bm-b腿=零动作+水位键更新) | 完成包394件git add -A全量暂存(含D-staged恢复工件消解,余11 D面=本机恢复窗日志件,爪安全)+MSG-2015翻案移processed | catchup实况:本地HEAD(r958)非origin祖先,origin已含bm-c吸收的r959-r975面(S6 43/43 absorbed实证),behind=68,冲突交集246件 | 本地未达origin commit数=0(本轮零commit,暂存面候下轮收口=O-20261001-1108送达门诚实) | 下轮P0指针:25min全窗做commit->push(拒)->pull --rebase(union resolver备CODELY.md)->push或树手术add-only onto origin tip(r957律ls-tree tip:dir+mktree --missing),r953树杀软帽全程 | RAM 2.6GB(<4GB门=重活禁,astock refresh 5222股在飞pid8380+i2v animatic burning pid28900+backfill szse pid1388=O-1055 CEO令三活照常)\n"
)
with open('logs/iteration-loop/round_reports.md', 'ab') as f:
    f.write(line.encode('utf-8'))
print('round report appended')

# 3. heartbeat
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = now_iso
hb['task'] = 'r976(cont): completion-package staging window - S6 38/38 first green + 394-file stage + D-19 O-1200 consumed (zero-action, non-bm-b leg)'
hb['did'] = ("r976(cont): (a) S6 chain 38 legs 0 bad CHAIN_DONE first-run-green post-r947 (evidence=results/_r976bmb_s6_log.txt: dualrun ZERO-DRIFT streak 33, compute_audit idle-starvation honest, "
             "watermark green, all lane-guards honest no-op, aggr 20/20 + alloc 7 + grid 5/5 marked through 2026-10-14, t35 export 10-14, daily_report 10-15, ceo_live_usage ORANGE cap50% written, build_status refreshed) "
             "(b) smoke 49/49 PASS fresh (c) attrition 4 ledgers CLEAN (d) saturation engine alive (verdict=idle) (e) orphan probe 17/1 (i2v XQ05 family watch face, same as r975) "
             "(f) D-19 delta consumed: decisions 6910a9ed->578804c1 + orders 46c60d47->0d7b4fe2, delta rows = D-20261015-03 + O-20261015-1200 CEO token-governance package (committee-led, HQ closeout window, O-1055 MV line explicitly unaffected, no @bm-b leg) = zero action + watermark keys updated "
             "(g) completion package: git add -A 394 files staged (D-staged recovery artifacts dissolved, 11 remaining D faces = own bmb recovery-window logs, claw-safe) + MSG-2015 triaged to processed/ "
             "(h) catchup verdict: local HEAD(r958) NOT ancestor of origin/main; origin already contains bm-c-absorbed r959-r975 faces (S6 43/43 absorbed); behind=68; intersection 246 files "
             "(i) HONEST SKIP: commit+push+catchup deferred to next round full 25-min window (r951 two-phase law: no long git op near watchdog kill; 11:17 staging law) "
             "(j) three live lines verified alive: astock refresh (pid 8380) + i2v animatic (pid 28900) + backfill szse march (pid 1388) = O-1055 CEO leg continuation")
hb['free_ram_gb'] = 2.6
hb['gpu_free_vram_mb'] = 73
hb['verdict'] = ("GREEN-completion-pending: S6 38/38 first green + smoke 49/49 + 394-file package staged; catchup 68-behind = next-round P0 full-window (commit->push->rebase or tree-surgery); "
                 "recent artifact = results/_r976bmb_s6_log.txt CHAIN_DONE 12:0x + docs/daily_report/REPORT-2026-10-15.md + docs/live_usage/LIVE-2026-10-15.md; "
                 "next milestone: r977 lands completion package commit+push to origin main (<=25min)")
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['ts'] = now_iso
assert isinstance(hb['heartbeat_epoch_utc'], int)
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('heartbeat written, epoch int verified:', epoch)
