# r1054 closeout: state + heartbeat + round report (fresh read-modify-write per r1006 law)
import json, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

idle = json.load(open(ROOT + r'\results\idle_trigger.bm-a.json', encoding='utf-8'))

DID = ("r1054: (1) bm-b 解锁递送验证 CLOSED（r1053 next①）：r1004/r1005 closeout 已落 origin（9877424b4f+2722a044b5·estate dac9a725 lineage delivered 'r1054 criterion met'）+心跳新鲜 11:27:38+O-0948 ack+MSG-1035 rootfix 三腿全执行（13 TIMEOUT 清账+v2 采纳）=fast-path 死锁解锁全链闭环；rootfix 回执窗双机全闭（bm-c r1087 11:02:27 ack+432 清账+MiniGame 同修 df88bb98a）"
       "(2) MSG-0845 收件 8/8：Downloads 全扫捕获（tailscale file get CLI=静默 no-op=r1044 双面坑二次实录）+批1字节 4/4 恒等+WAV 头 44.1k/16bit/stereo 验过+SHA256 拷贝对账 8/8+落位 CEO 看片通道 media\\drama-pilot-in\\audition-mix-20261018\\（8件+README）+回执 MSG-20261018-1145 已落"
       "(3) 全流程梳理令（组 orders 11:3x 行）本司 24h 补行同轮执行：council C-20261018-02 §六 BigMoney 司流程清单行 BM-1..BM-8+3 在册治理面供证·CAS 外科直投 origin edc8332778（40hex 校验+tip/blob 双验过+零树触碰·r1049 正法）"
       "(4) D-19 ord a62af296→9a1771f3 advance（11:28 漫剧3D转向行=非本司面零义务+11:3x 梳理行=本司补行已执行）·dec 0ad85a30 hold"
       "(5) W268 守门：W267=bm-c own seat（prereg df55e3fab9 11:0x ALL GATES PASS）但 splice/self-burn/finalize 未落 → W268 GATED 零抢跑维持（upstream waits-face 非空）"
       "(6) S6 43/43 rc0 bad=0（r1053 面 verbatim 克隆·MF day-11 数据点随链）(7) smoke 49/49+satengine ALIVE idle+watermark red=false+orphan 0/24+双爪重装+loop pin=8 no-op（watchdog S4U flip 拒=carried C-20261016-04）(8) idle green_idle 达档·claimable=1=行14 bm-b 专属车道零领单→实际产出工 --worked 清零")

NEXT = ("r1055: (1) W268 守门（W267 splice/finalize=bm-c 下窗节奏；finalize 落地+席面点名 bm-a → live re-derive FIRST ACTION）；(2) MF 封锁周一裁决 <=10-19（day-8/9/10/11 链 armed）；(3) 委员会 12:00 班对 §六 供证收取观察（首轮裁决表 <=10-20 12:00）；(4) bm-b r1005 leftover MemoryBudgetGate first-fire 面（bm-b 自域观察）")

VERDICT = ("GREEN: r1054: bm-b 解锁递送验证闭环（estate 已达 origin+回执窗双机全闭）+ MSG-0845 收件 8/8 字节恒等落 CEO 看片通道 + 全流程梳理令本司 24h 补行同轮 CAS 落位（council §六 BM-1..8）+ D-19 ord advance 9a1771f3 + W268 GATED 零抢跑维持（W267 chain 未闭合）+ S6 43/43 rc0 + smoke 49/49 + orders 双扫 CLEAN + idle --worked")

VERIFY = ("Downloads 8 件字节/头格式/SHA256 对账 8/8 + CAS_PUSHED edc8332778（tip 恒等+blob 恒等断言）+ d19 advance 读回 full-string equality + origin ls-tree（W267 prereg 在/n1_w267 缺=zero skip-claim 证据）+ S6 chain 43 rc0 bad=0（results/_r1054bma_s6chain_rc.log）+ smoke 49/49 + satengine ALIVE queue0 + orphan 0/24 + idle --worked 回执 + bm-b/bm-c origin 心跳面 ack_0948 双真")

ART = ("media\\drama-pilot-in\\audition-mix-20261018\\ 8件+README + council C-20261018-02 §六（origin edc8332778）+ MSG-20261018-1145 + results/_r1054bma_s6chain_rc.log + _r1054bma_s6chain.ps1")

# --- state file ---
sp = ROOT + r'\state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st.update({
    'round_no': 1055, 'round': 1054, 'last_round': 'r1054', 'loop_round': 1054,
    'last_round_at': NOW, 'last_round_closed': NOW, 'last_run': NOW, 'last_seen': NOW,
    'now_active': NOW, 'updated': NOW, 'updated_at': NOW, 'ts': NOW,
    'current': DID, 'did': DID, 'last_action': DID, 'last_action_at': NOW,
    'current_task': NEXT, 'task': 'r1054: bm-b unlock verify + MSG-0845 pickup + council §六 + S6 closeout',
    'next': NEXT,
    'last_artifact': ART, 'latest_artifact': ART, 'recent_artifact': ART,
    'verdict': VERDICT, 'verify': VERIFY,
    'next_milestone': 'W268 波窗（候 bm-c W267 finalize·≤48h）+ MF 封锁周一裁决 <=10-19 + 委员会 §六 供证收取',
    'last_orders_sha': '9a1771f3c8398ff085d9d73994a8c4463db90326b9c92741f0238f804c380364',
    'last_orders_seen': 'r1054: ord a62af296->9a1771f3 advance consumed (11:28 漫剧3D转向=非本司零义务 + 11:3x 全流程梳理=本司 24h 补行已同轮执行 council §六 CAS edc8332778)',
    'last_orders_at': NOW, 'last_orders_ts': NOW, 'last_orders_read_at': NOW,
    'last_decisions_seen': 'r1054: dec 0ad85a30 hold (probe zero-delta)',
    'last_decisions_at': NOW, 'last_decisions_ts': NOW, 'last_decisions_read_at': NOW,
    'heartbeat_epoch_utc': EPOCH, 'heartbeat_epoch_utc_type_int': True,
    'last_heartbeat_epoch_utc': st.get('heartbeat_epoch_utc', EPOCH),
    'clock_read': NOW,
    'idle_rounds': 0, 'agenda_starved': False,
    'orphan_face': 0, 'orphan_faces': 0,
    'cpu_pct': idle.get('cpu_pct', 28.5), 'cpu_load_pct': idle.get('cpu_pct', 28.5),
    'ram_free_gb': idle.get('ram_free_gb', 51.5), 'free_ram_gb': idle.get('ram_free_gb', 51.5),
    'gpu_free_vram_mb': idle.get('gpu_free_vram_mb', 7414),
    'last_round_label': 'r1054',
    'round_no_label': 'r1054',
})
st['notes_r1054'] = ("r1054: (1) bm-b fast-path 解锁递送验证改判据实锚（r1053 addendum 正法）：成功判据=bm-b closeout push 落 origin 非 repo_heads==bm-a-sha——bm-b r1004 S0 即在 c6fcd9fc2a（bm-a r1053 tip）上 r1032-law 重放自身 live faces+estate 9877424b4f=r1004 closeout、r1005 复扫轮已入常规节奏（11:27 新鲜）；O-0948 双机回执窗全闭=rootfix 账户 CLOSED。"
                     "(2) tailscale CLI get 双面坑二次实录：`file get -wait=false <dir>` 静默 no-op 零落盘而 GUI 物化面 8/8 落 Downloads 08:41-42——r1044 律（收件必扫 Downloads）第二次实弹；哈希对账后落 media\\drama-pilot-in\\（CEO 看片通道正位）。"
                     "(3) council C-20261018-02 §六 供证=BigMoney 司流程清单行 8 条+3 在册治理面；CAS 一次过（无竞速·fetch 后 origin 未进）——组仓活跃会话窗（记忆治理席 11:3x 落账两 CEO 行）零树触碰共存验证。"
                     "(4) W267 席位链勘定：seat MSG-1025 owner=bm-c（86th own wave·chain-order law bm-a 让位）+prereg df55e3fab9 已落但五面 splice/自燃/finalize 未落=W268 upstream waits-face 非空→GATED 维持；bm-a 预置 _w267bma probe 不复用（band 归 W267 已注册面·W268 derive 须候 W267 finalize 后全新 live walk）。"
                     "(5) watchdog S4U flip 拒绝访问=carried C-20261016-04（提权窗待）。")
st['orders_ack_note'] = 'r1054: fleet/orders 零新令（origin delta=O-2315/O-0948 回执节他机追加·本机 ack 面不变）；D-19 组面 ord advance 9a1771f3（两 CEO 行已消费·11:3x 行本司义务同轮执行）'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
j = json.load(open(sp, encoding='utf-8'))
assert isinstance(j['heartbeat_epoch_utc'], int), 'epoch must be int'

# --- heartbeat ---
hp = ROOT + r'\fleet\machines\bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
hb.update({
    'machine_id': 'bm-a', 'last_seen': NOW, 'ts': NOW,
    'clock_read': NOW, 'heartbeat_epoch_utc': EPOCH,
    'round_no': 1055, 'round': 1054, 'last_round': 'r1054',
    'idle_rounds': 0, 'agenda_starved': False,
    'current': DID[:600], 'did': DID[:600], 'last_action': DID[:600],
    'current_task': NEXT[:500], 'next': NEXT[:500],
    'last_artifact': ART, 'latest_artifact': ART,
    'verdict': VERDICT, 'verify': VERIFY,
    'now_active': "bm-a 循环 r1054 收口（MSG-0845 收件 8/8 落 CEO 看片通道+全流程梳理本司补行 council §六+S6 43 腿全绿）",
    'next_milestone': 'W268 波窗（候 bm-c W267 finalize·≤48h）+ MF 封锁周一裁决 <=10-19',
    'updated_at': NOW,
})
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
j2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(j2['heartbeat_epoch_utc'], int), 'hb epoch must be int'

# --- round report (ROOT canonical per r899) ---
rp = ROOT + r'\round_reports-bm-a.md'
prev_tail = open(rp, encoding='utf-8', errors='replace').read().splitlines()[-1][:120]
line = "%s | r1054 | bm-b 解锁递送验证闭环（estate 9877424b4f 已达 origin+O-0948 双机回执窗全闭+心跳 11:27 新鲜）+ MSG-0845 收件 8/8（Downloads 全扫按 r1044 律·批1字节 4/4 恒等+WAV 头验过+SHA256 8/8·落位 media\\drama-pilot-in\\audition-mix-20261018\\+回执 MSG-1145）+ 全流程梳理令本司 24h 补行同轮（council C-20261018-02 §六 BM-1..8+3 治理面·CAS origin edc8332778 tip/blob 双验）+ D-19 ord advance 9a1771f3（11:28 漫剧3D=非本司零义务/11:3x 梳理=补行已执行·dec hold）+ W268 GATED 维持（W267=bm-c 席 prereg 落但 splice/finalize 未落=waits 非空零抢跑）+ S6 43/43 rc0（MF day-11 点随链） | Downloads 哈希对账 8/8+CAS_PUSHED edc8332778+d19 读回恒等+origin ls-tree W267 证据+smoke 49/49+satengine ALIVE+orphan 0/24+idle --worked | r1055: W268 守门候 bm-c finalize+MF 周一裁决 <=10-19+委员会 §六 收取观察\n" % NOW
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)
print('STATE+HEARTBEAT+REPORT OK  prev_tail=%s' % prev_tail)
print('epoch=%d now=%s' % (EPOCH, NOW))
