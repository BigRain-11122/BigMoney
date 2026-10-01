# r528 bm-a closeout writes: state, heartbeat, round report, CODELY lesson
import json, time, datetime, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')          # T-separated, +08:00 offset
epoch = int(time.time())
assert 'T' in iso, 'clock_read must be T-separated'


def write_json_crlf(path, obj):
    b = json.dumps(obj, ensure_ascii=False, indent=2).replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(b)
    # self-proof: parses back
    json.loads(open(path, encoding='utf-8').read())


# ---- 1) state-bm-a.json ----
sp = 'state-bm-a.json'
st = json.loads(open(sp, encoding='utf-8').read())
st['round_no'] = 529                              # next round number
st['last_round'] = 528
st['did'] = ('r528 bm-a: py_watermark _scan_tickets claim-lock fix (status=open+claimed_by '
             'shape no longer counted as this-machine work candidate -- T-141 precedent fed '
             'chronic false py_low_with_work_cands red r522..r527; selftest leg added '
             '(T-4 claimed-by fixture), ALL PASS; live probe now py_low_board_clear honest; '
             'watchdog C7 reads probe-recorded open_tickets so red face self-clears on next '
             'trailing window) + S0 integrations (bm-c r326 heal closeout, bm-b r516 W16 '
             'shards 12/12 surgical) + S6 33 legs rc0 holiday no-op honest + governance '
             'waiting lines one-line declaration')
st['verify'] = ('selftest ALL PASS + live probe open_tickets=0/verdict=py_low_board_clear + '
                'smoke 47/47 post-patch + dualrun ZERO-DRIFT 306 entries streak 6/3 + '
                'attrition CLEAN + claw MATCH + loop pin=8 Running + watchdog Ready')
st['next'] = ('r529: governance rulings watch (T-142 LOWAMP-P2 / W14 grammar-family -- '
              'one-line declaration type, no re-scan) > W17=bm-c freeze observation > '
              'W18 wave gate self-check > 10-03 RW-5 unfreeze -> T-126 REEVAL18 prereg')
st['last_round_at'] = iso
st['current_task'] = ('r528 close: WM probe claim-lock fix landed; governance holds '
                      '(T-142/W14/N2-W15) unchanged; engine W18 gated on bm-c W17')
st['updated'] = iso
st['last_round_ts'] = iso
st['notes'] = ('r528: watermark probe fix = root-cure of chronic false-red (contributing '
              'pressure factor in r526 W14 mis-ignition); red file self-clears as trailing '
              'window turns over (MinRedSamples=3)')
write_json_crlf(sp, st)

# ---- 2) heartbeat fleet/machines/bm-a.json ----
hp = 'fleet/machines/bm-a.json'
hb = json.loads(open(hp, encoding='utf-8').read())
hb['last_seen'] = iso
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = epoch
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['current_task'] = ('r528 close: py_watermark claim-lock fix (chronic WM false-red root-cure) '
                      'landed + S6 33 legs rc0; governance holds: T-142 LOWAMP-P2 verdict + '
                      'W14 293-candidate disposition + N2-W15 self-held (await GM); next N1 '
                      'engine wave = W18 (after bm-c W17); 10-03 RW-5 -> T-126 prereg')
hb['verdict'] = 'probe-fix-landed-governance-hold'
hb['round_no'] = 528
hb['last_round'] = 528
hb['cpu_pct'] = 6.0
hb['free_ram_gb'] = 59.0
hb['gpu_free_vram_gb'] = 5.4
hb['task'] = hb['current_task']
hb['notes'] = ('r528: WM probe fix -- claimed tickets excluded from work-candidates '
               '(T-141 shape); live verdict py_low_board_clear; red self-clears next '
               'watchdog window')
write_json_crlf(hp, hb)
# F7 self-proof
chk = json.loads(open(hp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('heartbeat epoch int self-proof OK:', chk['heartbeat_epoch_utc'])

# ---- 3) round report append ----
report = ('2026-10-01T18:0x+08:00 | r528 | dept:工程 | '
          'WM=红→自愈中（17:40 red 系修复前旧样本；本轮根治=py_watermark._scan_tickets 增 claimed_by '
          '排除——T-141 形态（status=open+claimed_by=bm-b）自 r522 起每轮喂假 work-cand 假红，本轮修后 live probe '
          'open_tickets=0·verdict=py_low_board_clear 诚实合法闲；watchdog C7 读探针记录面，尾窗翻转后 red 文件自清）｜'
          '当前活=治理三线守望（T-142 LOWAMP-P2 处置/W14 语法族裁定/N2-W15 自持——均待 GM，一行声明不重扫）+W17/bm-c '
          '冻结观察（尚无 prereg 落 origin）+W18 波门自查（前置=W17，未到窗）｜'
          '最近实物=scripts/py_watermark.py claim-lock 修复+selftest 新腿（17:5x·live probe 自证 board_clear）+'
          'S6 33 腿 rc0 全息假日 no-op（REPORT-2026-10-01/LIVE-2026-10-01/scorecard/dashboard 全再生·dualrun '
          'ZERO-DRIFT 306 entries streak 6/3）｜'
          '下个里程碑=10-03 RW-5 解冻→T-126 REEVAL18 prereg（窗≤48h from 解冻）+W17 落 origin 后 W18 冻结窗（轮值律·窗随 '
          'bm-c 节奏）+GM 裁决落地→T-142 P3 ExitPatch prereg/W14 293 候选去向｜'
          'did: (1) S0-1 机器身份锚定 bm-a+S0 fetch（0 behind 起点）+S0.5 双扫 orders 139/139 零未回执+D-19 决策面 '
          'sha 753F99E8 MATCH 零新决策（temp partial clone raw-bytes 法）；(2) **主产品=py_watermark 假红根治**：'
          'T-141（引擎票·claimed_by=bm-b·status=open）被 _scan_tickets 按 status==open 计入本机 work-cand=与自身 '
          'docstring「Open (unclaimed)」相悖的实装 bug——r522..r527 连续 6 轮 WM-red 手工再定性均源于此（r526 假红压力'
          '更间接喂了 W14 违规点火面）；修复=claimed_by 非空即排除+selftest T-4 fixture 腿（claimed_by=bm-b 形态）+'
          'live 验证 open_tickets 0/verdict=py_low_board_clear；作用面=三机共用探针全队受益（红牌噪声归零·轮报告省每日'
          '假红解释账）；(3) S0 收编 bm-c r326 治愈 closeout（r526 stale-sweep 第三犯 13 W14 产品件复原+CODELY union）'
          '与 bm-b r516 W16 外科（12/12 分片在场·finalize 判据修收养）；(4) S1 smoke 47/47+池面核：0 ready·0 本机欠账分片'
          '·W14 entry 层治理三字段停泊照旧（r527 承诺零触碰 W14 任何腿）·引擎活（heartbeat 26s·队列空=W15 草案/RETAIL '
          '闸内）·MiniGame 可视化面另一执行体 X1619 在飞（17:49 commit）按单执行体律零介入；(5) S6 33 腿 rc0（假日全合法：'
          'update_daily 0 新行 cutoff 09-30·采集器 no-op×N·车道守卫诚实 no-op×6·月度三件套他机今日已跑齐跳过·'
          'compute_audit 旗=pool_starvation+supply_floor 如实（供给四面全法内阻塞=T-142/W14 裁定+10-03 门+W17 序列，'
          '非违令·日报首行已载））；(6) S7 自愈三件套（loop pin=8 Running·watchdog Ready 重注册幂等·claw MATCH）+'
          'attrition CLEAN（4 healed 注记）+orders 收尾双扫 139/139 零未回执 | '
          'evidence: py_watermark selftest ALL PASS（含新腿）+live probe jsonl 两采样 open_tickets=0+smoke 47/47 '
          'post-patch+心跳 epoch int json.loads 自证+S6 log results/_r528bma_s6_log.txt 33 腿 rc 逐条 | '
          '计分：2 分（py_watermark 修复=能跑实物·三机受益；S6 再生气=文件改动）·记账 4 处（state/心跳/轮报告/CODELY 一行） | '
          '本地未达 origin commit 数=commit 后自证 | [via bm-a]')
with open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(report + '\r\n')

# ---- 4) CODELY.md one-line lesson ----
lesson = ('- [2026-10-01 18:0x r528 bm-a] 水位探针 claimed 票假 work-cand 假红坑（r522..r527 六轮实弹·r526 假红压力面'
          '成因根治）：py_watermark._scan_tickets 按 status==open 计数但 docstring 自称「Open (unclaimed)」——'
          'T-141 形态（status=open+claimed_by=他人机）被恒计入本机 work-cand → 全队每轮假 WM-red 手工再定性；'
          '且假红压力曾间接喂 r526 W14 违规点火判断面（r526 主错序仍在本机·此条=压力源根治）。修=claimed_by 非空即排除'
          '（fleet README §4 claim 锁语义对齐）+selftest claimed-by fixture 腿+live 自证。How to apply：一切「扫板判'
          '可跑批」类探针/守卫的候选面=unclaimed 面（claim=锁），禁只看 status 字段；假红根因先查计数器语义再人工再定性。')
with open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write(lesson + '\r\n')

print('closeout writes done at', iso)
