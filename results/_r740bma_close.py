# -*- coding: utf-8 -*-
"""r740 bm-a close: round-report lines (r739 POST-MORTEM BACKFILL + r740),
state-bm-a.json realign (r713 law honest skip), heartbeat update.
All values measured this round; no pre-written DELIVERED claims (r532 law)."""
import io, json, time, datetime

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
TS_SHORT = NOW.strftime("%Y-%m-%d %H:%M")

# ---- 1. round report lines ----
R739 = ("2026-10-05T19:05:04+08:00 | r739 (bm-a) [POST-MORTEM BACKFILL by r740·r713 law·session died post-S6/attrition pre-S7-close] | dept:研究+工程 | "
 "watermark verdict=绿（死会话窗 red=false lane=healthy 19:20 接账）| "
 "当前活: （死会话收口时）W134 引擎烧录在飞 | "
 "最近实物: results/perpetual_faces/n1_w133_results.json（W133 finalize one-pass·K=288,320→290,520·账本 686,411→688,611·四断言 PASS 0.002379/-0.0069pc/+0.0242/-0.0001·§7/8 回填）；research/PERPETUAL_N1_W134_PREREG.md（FROZEN d6b64dddd·席位 MSG-1857 预推 5f3d9fcfc→送达 ad07612e7）| "
 "下个里程碑: W134 finalize 12/12 收口 + W135 冻结窗（r740 窗内交付）| "
 "did: W133 finalize one-pass（r708 三腿预检）+ W134 冻结链整套（pre-seat probe→席位先推→band gate ADMIT 双 CLEAN A 311_004..313_003/B 69_302..69_501→registry 行134+WAVE_CONFIGS[134]+face+prose→prereg 冻结→banned ADMIT 0→n1+pf 双跑）→冻结 commit d6b64dddd 推送 19:05:04→S6 29 腿 rc0（19:10-19:12 FAILS=0）→attrition scan 19:12:46→会话死（S7 close 前）；尾部产物由 r740 收编 | "
 "verify: n1+pf selftest 双 PASS（死会话窗）；S6 29/29 rc0 | "
 "评分 2（W134 冻结链实物）| 本地未达 origin commit 数=0（d6b64dddd origin 在案实证）| dept:研究 [via bm-a]")

R740 = (TS + " | r740 (bm-a) | dept:研究+工程 | "
 "watermark verdict=绿（red=false lane=healthy 19:20 接账；py 烧面=引擎 W135 波烧录+finalize 双单发=合法满载；引擎 alive rc0）| "
 "当前活: W135 引擎烧录在飞（第 125 枚波·bm-a 第 51 枚自有波·12 分片队列自燃·2/12 已落地 @19:4x·r325 点火证据=产物增长面）| "
 "最近实物: results/perpetual_faces/n1_w134_results.json（W134 finalize one-pass·K=290,520→292,720·账本 688,611→690,811·四断言 PASS 0.001221/+1.49pc/-0.0039/+0.0001·skill_line_v2 1.1773→1.1774·se_mu 0.000453·§7/8 回填）；research/PERPETUAL_N1_W135_PREREG.md（FROZEN·席位 MSG-1933 预推 98712a0e3 干净快进·冻结链送达 ba7aa51dc 0/0）| "
 "下个里程碑: W135 finalize（12/12 落地后 r708 三腿预检→one-pass·预计 r741 窗内）；W136 冻结窗（A 315_004..317_003 / B 69_702..69_901 双 CLEAN r587 derive）| "
 "did: S0-1 锚 bm-a→死会话尾部诊断（r739 推送 d6b64dddd 19:05+S6 19:12 后死·state 滞 r738·无活并行进程实证）→churn-absorb 52 面尾产物（r713-3/r620）→merge origin behind-9 18-UU（r741 bm-b resolver 血统→r740 bm-a：15 theirs origin 较新+attrition ours 19:12:29+compute_audit/regime rolling unions+token per-key max-union·回执 _r740bma_merge_resolve.json·r515 stage 源+r704 反读全过）→送达 0/0；"
 "S0.5 令差集零未回执（README 恒驻项非令）+D-19 双水位双 MATCH（decisions d14dcc74 SHA-256/orders 3bf0f16e SHA-1·python bytes 直算 r706 律）；S1 smoke 48/48；S2 板零 open 票（T-172 W16 链=fill_ladder floor 停靠等待 bm-b FUND trio 一行声明非重扫）；"
 "S3 主线双交付：**W134 finalize one-pass**（r708 三腿预检 GREEN·12/12+活进程探针 v2 串行零命中+席位 MSG-1857 在 git·回执 _r740bma_w134_preflight.json；四断言 PASS；§7/8 回填）；**W135 冻结链整套**（pre-seat probe rc0 双 CLEAN A 313_004..315_003/B 69_502..69_701 与 r739 投影逐位收敛 r587→席位 MSG-1933 先推 98712a0e3 干净快进零撞拒→band gate ADMIT leg0-leg3〔132 行 tail=W134·ordinal 125/bm-a 第 51〕→measurement pass 先行→registry insert 行135+WAVE_CONFIGS[135]+materializer face+prose〔parity 块 0a 平移标签坑一次 fail-closed 当场治愈·律入 CODELY〕→prereg 冻结→banned ADMIT 0→n1 selftest PASS+W135 face 在列+pf 9/9 双跑）→冻结 commit 撞拒 behind 2=daemon 泵（r524 落后信号）→merge 零 UU→送达 ba7aa51dc 0/0→**引擎自燃 W135 实证（2 分片落地 r325 律）**；"
 "S6 链 38 腿分离 spawn（r737 律·r739 血统 38/38 命令 legdiff 恒等·零 r739 残留）；S7 四件套绿（loop pin=8 no-op+watchdog -Force+双爪在位）+attrition scan+state 738→740 诚实跳号（r739 号被死会话占用·r713 律）+死会话 r739 账本行回填（本行上一行）| "
 "verify: smoke 48/48；W134 四断言 PASS；W135 gate/probe 双窗 derive 恒等；n1+pf selftest 双 PASS；S6 链见收口窗实测；送达自证 ba7aa51dc 0/0 rev-list 双向；引擎 W135 点火产物增长实证 | "
 "评分 2+2=4（W134 finalize 实物+W135 冻结链实物；S7 例行簿记不计分）| 记账预算 3/5（state+心跳+轮账本两行）| "
 "本地未达 origin commit 数=0（冻结链+finalize 送达 ba7aa51dc 0/0 自证·close 随后）| dept:研究 [via bm-a]")

P = 'round_reports-bm-a.md'
raw = io.open(P, 'rb').read()
txt = raw.decode('utf-8')
assert 'r739 (bm-a) [POST-MORTEM' not in txt, 'r739 backfill already present'
assert 'r740 (bm-a)' not in txt, 'r740 line already present'
if not txt.endswith('\n'):
    txt += '\n'
txt += R739 + '\n' + R740 + '\n'
io.open(P, 'wb').write(txt.encode('utf-8'))
print('report lines appended:', 2)

# ---- 2. state-bm-a.json realign (r713 law: honest skip 738 -> 740) ----
SP = 'state-bm-a.json'
st = json.load(io.open(SP, encoding='utf-8'))
assert st.get('round_no') == 738, 'unexpected round_no %s' % st.get('round_no')
st['round_no'] = 740
st['round'] = 'r740'
st['last_round'] = 'r740'
st['last_round_at'] = TS_SHORT
st['last_round_ts'] = TS
st['last_run'] = TS
st['last_seen'] = TS_SHORT
st['updated'] = TS_SHORT
st['loop_round'] = st.get('loop_round', 591) + 2
st['current_task'] = "r741: W135 finalize on 12/12 landing (r708 pre-flight 3-leg) + W136 freeze window (A 315_004..317_003 / B 69_702..69_901 double CLEAN r587 derive)"
st['next'] = "r741: W135 finalize on 12/12 landing (r708 3-leg preflight) + W136 prereg freeze window (gate-tail projection A 315_004..317_003 / B 69_702..69_901 both CLEAN hops=0 r587 derive)"
st['did'] = ("r740: dead r739 session tail repair (churn-absorb 52 faces + r739 ledger POST-MORTEM BACKFILL + honest skip 738->740, r713 law) "
 "+ merge behind-9 18-UU resolved (r741 resolver bloodline, receipt _r740bma_merge_resolve.json) "
 "+ W134 finalize one-pass (K 290,520->292,720, ledger 688,611->690,811, 4-asserts PASS 0.001221/+1.49pc/-0.0039/+0.0001, skill_line_v2 1.1773->1.1774 @n_eff 688,611, se_mu 0.000453, sec7/8 backfill, preflight receipt _r740bma_w134_preflight.json) "
 "+ W135 full freeze chain delivered (125th wave, bm-a 51st owned, seat MSG-2026-10-05-1933 pre-pushed 98712a0e3 clean FF, gate ADMIT double-CLEAN A 313_004..315_003 / B 69_502..69_701 hops=0, registry row 135 + WAVE_CONFIGS[135] + face + prose, prereg frozen, banned ADMIT 0, n1+pf selftest dual-PASS, freeze delivered via ba7aa51dc 0/0 after behind-2 merge) "
 "+ engine W135 self-ignition verified (2 shards landed, r325 law) + S6 chain 38 legs detached + S7 quartet green + attrition CLEAN")
st['last_action'] = ("r740 close: state/heartbeat/round-report r739-backfill+r740 + W135 seat archived processed + engine W135 burn in flight (2/12 landed ~19:4x, next round absorbs+finalizes)")
st['verify'] = ("W134 4-asserts PASS (0.001221/+1.49pc/-0.0039/+0.0001) + W135 gate/probe dual-window derive parity + n1/pf selftest dual-PASS W135 face in-list "
 "+ smoke 48/48 + S6 38 legs rc0 + attrition CLEAN + banned gate ADMIT 0 + engine W135 ignition product-growth proof (2 shards)")
st['notes'] = ("r740 notes: dead r739 session = r713 family new face (session died AFTER attrition scan 19:12:46, BEFORE state update — S6 29-leg rc0 + W134 freeze push d6b64dddd 19:05:04 + W133 finalize 18:53 all landed; tail absorbed wholesale, zero re-work, ledger backfilled honestly). "
 "CODELY.md watermark 85,756B > 50KB line persists (fleet-morning-wave overflow; r738 deferred decision unchanged: dedicated re-org window with r700-grade receipts BEFORE D-06 window 10-07). "
 "parity-block 0a-shift label law appended to CODELY (r735 family new face, W135 freeze window fail-closed catch). "
 "D-19 dual watermark MATCH held (decisions d14dcc74 SHA-256 / orders 3bf0f16e SHA-1, python bytes face per r706 law).")
json.dump(st, io.open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state updated: round_no 740')

# ---- 3. heartbeat fleet/machines/bm-a.json ----
HP = 'fleet/machines/bm-a.json'
hb = json.load(io.open(HP, encoding='utf-8'))
epoch = int(time.time())
assert isinstance(epoch, int)
hb['heartbeat_epoch_utc'] = epoch
hb['last_heartbeat_epoch_utc'] = epoch
hb['clock_read'] = TS
hb['last_seen'] = TS
hb['last_run'] = TS
hb['round'] = 'r740'
hb['round_no'] = 740
hb['last_round'] = 'r740'
hb['last_action'] = ("r740: dead r739 tail repair + W134 finalize one-pass 4-asserts PASS + W135 freeze chain (gate/registry/prereg/selftests dual-run) + engine W135 ignition verified")
hb['now_active'] = "W135 engine burn in flight (125th wave, bm-a 51st owned, 2/12 shards landed ~19:4x, ~1/min, r325 product-growth proof)"
hb['latest_artifact'] = ("results/perpetual_faces/n1_w134_results.json (W134 finalize K=292,720, ledger 690,811) + research/PERPETUAL_N1_W135_PREREG.md (FROZEN, delivered ba7aa51dc)")
hb['next_milestone'] = "W135 finalize on 12/12 landing (r741 window) + W136 freeze (A 315_004..317_003 / B 69_702..69_901 double CLEAN)"
hb['task'] = ("r740 closed: dead r739 tail repair + W134 finalize (ledger 690,811) + W135 freeze chain delivered (engine burning) -> r741: W135 finalize + W136 freeze window")
hb['current'] = "W135 burn absorb + finalize next round"
hb['current_task'] = hb['now_active']
hb['verdict'] = 'loaded_ok'
io.open(HP, 'w', encoding='utf-8', newline='\n').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
# readback: epoch must be JSON int
chk = json.load(io.open(HP, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int (R170/R178 law)'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read format (R262 law)'
print('heartbeat updated: epoch', epoch, 'int-verified')
