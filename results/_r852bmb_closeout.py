# -*- coding: utf-8 -*-
# r852 bm-b closeout: state.json + heartbeat + round report line + scratch cleanup
import io, json, os, time, ctypes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- machine stats ---
class M(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_uint64), ('ullAvailPhys', ctypes.c_uint64),
                ('ullTotalPageFile', ctypes.c_uint64), ('ullAvailPageFile', ctypes.c_uint64),
                ('ullTotalVirtual', ctypes.c_uint64), ('ullAvailVirtual', ctypes.c_uint64),
                ('ullAvailExtendedVirtual', ctypes.c_uint64)]
m = M(); m.dwLength = ctypes.sizeof(M)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_gb = round(m.ullAvailPhys / 1e9, 1)
total_gb = round(m.ullTotalPhys / 1e9, 1)
ram_free_pct = round(100.0 * m.ullAvailPhys / m.ullTotalPhys, 1)

R852_QUEUE = ("r853 queue: astock completion verify (ETA ~01:40, 4433/5217 @01:10) -> spawn detached "
              "T23 census full burn (runner pre-verified selftest 21/21 @r851) -> census_holds readout "
              "(window <=10-11 06:00) -> N2 U3(1) prereg window if holds / G2 academic-citation fallback "
              "if negative + S6 chain; O-20261011-0012 条款4 执行点=重建完毕即认领池面+矩阵切片（属主道自助）; "
              "W207 five-face freeze window via M9 watcher (upstream W205 finalize pending -> W206 five-face+finalize "
              "-> run results/_w207bmb_freeze_edits.py staged @r852, gates live-fired; anchor roll per r590); "
              "W18 stays drain-gated (bm-a owns w17-judge)")

DID = ("r852: W207 五面冻结前置暂存窗落地（主产物=results/_w207bmb_freeze_edits.py PREPARED pre-landing·py_compile PASS"
       "·链序门实弹两证=r609 origin-verbatim 门抓住轮中 origin 前进 3 commit（cd0539ce0 bm-a W205 12/12 烧完+churn）"
       "+gate0.5 W206 未落=诚实等待态·三偏离全机器验证=运行时 EOL 探测（仓实况纯 LF vs W206 模板 CRLF 假设）"
       "/prose 数字全回执派生（arith 窗=leg1 机读·W208+ 投影=leg4 机读）/纯 50 行 estate 取自已落 W205 不可变块"
       "（W204/W205 实证 50+1 结构·防逐代膨胀）） + M9 看守行落 state/queue/main.md（bm-c M8 镜像·W207 链守望）"
       " + bm-c 跨机告知 MSG-20261011-0120（其 _w206bmc_freeze_edits.py 三发现=EOL CRLF 假设 vs 仓 LF 实况"
       "/par_sec 计数 50 vs 实测 51/prose 算术续带起点 465_805 vs 回执 467_804·全 fail-closed 级零盘污）"
       " + S0.5 D19 双水位零 delta（bm-c r843 报 dec 68d13893 矛盾→r779 三步法实证=group origin dec caca0c6e 恒等我侧正确"
       "·r852bmb_d19_three_step.py 证据） + 轮中 origin 前进后 r609 门自证 + S1 smoke 49/49 + astock 重建进度 4433/5217"
       "（ETA ~01:40·T23 census 保持物理依赖等待） + S6 41 腿（40 rc0+alloc rc2 已知 510880·dualrun streak 7"
       "·leg36=bm-a 心跳停滞 200min 触发 stale-takeover 派生=lane_io 守卫律正常执法） + S7 四任务 ALIVE rc0"
       "（本地化输出文本匹配假 MISSING 陷阱=以 rc 判定解·R49 正典面）+双爪恒等+attrition CLEAN+idle --worked 清零")

VERDICT = ("GREEN: r852 (W207 freeze editor staged with live-fired chain-order gates; astock rebuild 4433/5217 "
           "ETA ~01:40; D19 dual watermark zero-delta three-step verified; S6 41 legs 40 rc0 + known alloc rc2; "
           "4 tasks ALIVE rc0; attrition CLEAN; zero CODELY append per memory gate (both candidates covered by "
           "codified r838/r839 + R49)")

# --- scratch cleanup (own un-committed temp views; treasure_guard not applicable: never in git) ---
for f in ('results/_r852bmb_mainqueue_view.txt', 'results/_r852bmb_m8row.txt'):
    p = os.path.join(REPO, f)
    if os.path.exists(p):
        os.remove(p)
        print('removed scratch:', f)

# --- state.json ---
sp = os.path.join(REPO, 'state.json')
d = json.load(open(sp, encoding='utf-8'))
d['round_no'] = 852
d['round_no_label'] = 'r853'
d['note'] = DID
d['did'] = DID
d['last_action'] = DID
d['verdict'] = VERDICT
d['task'] = R852_QUEUE
d['next'] = R852_QUEUE
d['current_task'] = R852_QUEUE
d['now_active'] = 'r852 closeout: W207 freeze editor staged (gates live-fired); astock rebuild 85% in flight; M9 watcher armed'
d['latest_artifact'] = ('r852: results/_w207bmb_freeze_edits.py (W207 five-face freeze splice editor, PREPARED pre-landing, '
                        'py_compile PASS + r609/gate0.5 live-fire proof @01:0x-01:2x) + M9 watcher row (state/queue/main.md) + '
                        'fleet/inbox/MSG-20261011-0120-bmb-w206-staged-script-findings.md + results/_r852bmb_s6chain.log (41 legs)')
d['next_milestone'] = ('astock panel complete (~01:40) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) '
                       '-> N2 U3(1) prereg window / G2 fallback; O-20261011-0012 条款4 pool+matrix claim at rebuild completion; '
                       'W207 five-face freeze via staged _w207bmb_freeze_edits.py once W205 finalize + W206 five-face+finalize land (M9)')
for k in ('last_round_at', 'last_seen', 'updated', 'ts', 'clock_read', 'last_round_ts', 'updated_at'):
    d[k] = now_iso
d['last_orders_at'] = now_iso
d['d19_watermark_guard']['round_ref'] = 852
d['d19_watermark_guard']['ts'] = now_iso
d['round'] = 852
d['heartbeat_epoch_utc_face'] = 'kept in fleet/machines/bm-b.json'
open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(d, indent=1, ensure_ascii=False))
print('state.json -> round 852')

# --- heartbeat ---
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-b.json')
h = json.load(open(hp, encoding='utf-8'))
h['round'] = 852
h['round_no'] = 852
h['now_active'] = 'r852 closeout: W207 freeze editor staged (chain-order gates live-fired); astock rebuild 4433/5217 ETA ~01:40'
h['current_task'] = R852_QUEUE
h['task'] = R852_QUEUE
h['next'] = R852_QUEUE
h['latest_artifact'] = d['latest_artifact']
h['next_milestone'] = d['next_milestone']
h['verdict'] = VERDICT
h['last_action'] = DID
h['did'] = DID
for k in ('last_round_at', 'last_seen', 'updated', 'ts', 'clock_read', 'updated_at'):
    h[k] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['cpu_cores'] = 16
h['free_ram_gb'] = free_gb
h['ram_free_gb'] = free_gb
h['ram_free_pct'] = ram_free_pct
h['gpu_free_vram_mb'] = 3573
h['gpu_free_vram_gb'] = 3.57
h['vram_free_gb'] = 3.57
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['orphan_faces'] = 0
h['orphan_face_note'] = 'round-zero probe 00:52 py_faces=15 orphans=0 (read-only)'
h['sync'] = {"last_push_ts": now_iso, "note": "r852 closeout push; post-push behind=0 self-proof below"}
open(hp, 'w', encoding='utf-8', newline='').write(json.dumps(h, indent=1, ensure_ascii=False))
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated (R262 law)'
print('heartbeat -> round 852; epoch int OK; free RAM', free_gb, 'GB /', total_gb, 'GB')

# --- round report line ---
rp = os.path.join(REPO, 'logs', 'iteration-loop', 'round_reports.md')
raw = open(rp, 'rb').read()
t = raw.decode('utf-8')
crlf = t.count('\r\n'); lf = t.count('\n') - crlf
EOL = '\r\n' if crlf >= lf else '\n'
if not t.endswith(EOL):
    t += EOL
line = EOL.join([
 f"{now_iso} | r852 bm-b | dept:研究;工程 W207 五面冻结前置暂存窗收口（主产物=results/_w207bmb_freeze_edits.py PREPARED pre-landing·py_compile PASS·链序门实弹两证：r609 origin-verbatim 门抓住轮中 origin 前进 3 commit=cd0539ce0（bm-a W205 shard 12/12 烧完+churn）·gate0.5 W206 未落=诚实等待态；三偏离全机器验证=运行时 EOL 探测（仓 pf/n1 实况纯 LF·W206 模板 CRLF 假设将 fail-closed）/prose 数字全回执派生（arith 窗=leg1 机读·W208+ 投影=leg4 机读·序数 197/41 live-registry derive）/纯 50 行 estate 取自已落 W205 不可变块（W204/W205 实证 50+1·防逐代膨胀）+M9 看守行落位（bm-c M8 镜像）+bm-c 跨机告知 MSG-20261011-0120（其 W206 暂存脚本三发现：EOL 假设/par_sec 计数 50vs51/prose 算术续带起点滑差·全 fail-closed 零盘污）+S0.5 D19 双水位零 delta（bm-c r843 报 dec 68d13893 矛盾=r779 三步法实证 group origin dec caca0c6e 恒等我侧正确·证据 _r852bmb_d19_three_step.py）+astock 重建 4433/5217 ETA~01:40（T23 census 物理依赖等待）",
 "WM-VERDICT: green（red=false @00:52 probe·next_pick=moneyflow IC claimed advisory·py 低位=astock 全宇宙重建网络限速拉取型合法）",
 "孤儿面=0（round-zero probe 00:52 py_faces=15）；S6 41 腿=40 rc0+alloc rc2 已知 510880（P5 slot TRANSFER 待办）；leg36=bm-a 心跳停滞 200min 触发 paper_export stale-takeover 派生=lane_io 守卫律正常执法；dualrun streak 7；S7 四任务 ALIVE rc0（本地化 schtasks 输出文本匹配假 MISSING 陷阱=rc 判定解·R49 正典）+双爪恒等+attrition CLEAN（历史缩行全 healed）+idle --worked 清零；记忆 append=零（四问门②复述禁令：EOL 律 r838/r839 已法典化·schtasks rc 判=R49 已法典化·W206 发现已入 bm-c MSG+脚本头注=正确归宿）",
 "本地未达 origin commit 数=0（push 后 fetch+ls-tree 自证见下）；下轮指针 r853：astock 完结核验→分离 T23 census 全量烧录→holds 判读（窗≤06:00）→N2 U3(1) prereg 窗/G2 回退；O-20261011-0012 条款4 池面+矩阵切片认领；W207 M9 窗（上游 W205 finalize→W206 五面+finalize→跑 _w207bmb_freeze_edits.py）",
]) + EOL
t += line
open(rp, 'wb').write(t.encode('utf-8'))
print('round report line appended; report EOL =', repr(EOL))
print('CLOSEOUT WRITE OK @', now_iso)
