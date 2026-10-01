import json, time, datetime

# --- state-bm-a.json: round_no +1 ---
st = json.load(open(r'state-bm-a.json', encoding='utf-8'))
prev = st.get('round_no', 0)
st['round_no'] = prev + 1
st['last_round_ts'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
st['last_decisions_sha'] = '753F99E81A27DB3E1B4F2C76CD991CA50D52B80AA7FAA63D6412CC2DA1F5FB01'  # verified MATCH this round
json.dump(st, open(r'state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('state round_no:', prev, '->', st['round_no'])

# --- heartbeat fleet/machines/bm-a.json ---
now = datetime.datetime.now().astimezone()
epoch = int(time.time())
h = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
h['last_seen'] = now.isoformat(timespec='seconds')
h['current_task'] = 'r534 W21 engine wave 12/12 burned+finalize closed loop (K=44,120, ledger 410,748)'
h['cpu_cores'] = 32
h['idle_ram_gb'] = None
h['verdict'] = 'healthy: W21 wave complete+finalized same-window; engine idle post-wave; W22 (bm-b) frozen same-window chain-ready'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now.isoformat(timespec='seconds')
json.dump(h, open(r'fleet\machines\bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# self-cert: epoch must be JSON int
h2 = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch not int!'
assert 'T' in h2['clock_read'], 'clock_read missing T separator'
print('heartbeat ok: epoch int', h2['heartbeat_epoch_utc'], 'clock', h2['clock_read'])

# --- round report line ---
line = (f"\n2026-10-01T20:0x+08:00 | r534 | dept:研究/工程 | WM=loaded_ok 绿（引擎烧录窗 py 实测·red=False）"
        f"| **W21 引擎波全链收口（本机 bm-a 第三枚自有波·主实物）**：(1)S0=身份锚 bm-a·0 落后·令差集 NONE·决策水位 MATCH-unchanged (2)S1 smoke 47/47 "
        f"(3)**W21 12/12 分片烧毕→finalize 一次过闭环**：r310 完备性门=origin ls-tree 12/12 后点火·merged **K=44,120**（mu −0.09264/sigma 0.24447/se_mu 0.001164）·账本 **408,548+2,200=410,748 链线性**（prev=r331 bm-c W20 落账头 derive）·S5 四项判定 **4/4 PASS**（mu 漂移 0.0106<0.02/sigma +0.05%<10%/A-p95 差 0.0074<0.05/K-lift −0.0003≤0.02 负向如实）·prereg §7/§8 同窗回填（r307 两态律）·selftest n1 exit0+pf 8/8+attrition CLEAN (4)分片产物三批定向提交（ride 6-10+外科 11+finalize 件）=r310 律履行（daemon 不推产物）(5)**轮窗坑实录三条治愈**：reset --mixed 滞后窗=批量 checkout 65 件一次收敛（排除 6 活写车道件·r512/r524 律）；`finalize --help` 无护栏误触真跑 W2 finalize=1 行元数据 git status 当场抓回 checkout 正典零污染零提交（教训入 CODELY）；checkout 多 pathspec 含 untracked=整批放弃 r326 已知坑过滤重跑一次过 (6)**W22=bm-b 同窗冻结交接已核**（r519 bm-b·A 86_001..88_000 与我 W21 带零重叠·其链序 FAIL-CLOSED 依赖我 W21 finalize 本落账件=现已满足）(7)S6 38 腿全 rc0：dualrun ZERO-DRIFT streak10/3·update_daily 0 新行 cutoff 09-30（国庆假期=无 10-01 bar 合法态）·regime ORANGE d4·CALL-09-30 ORANGE_COOL·车道守卫诚实 no-op x6·paper 锚 OK（enforce 请求=面板末 bar 09-30<日期门 10-01 假期无窗=设计内诚实降级）·t35 PASS 0 例·prospect 22/22 drift0·promotion 0/22 诚实·export-09-30 再生·LIVE-2026-10-01/REPORT-2026-10-01/dscore/build 再生 (8)S7 自愈三件绿（pin8 no-op·watchdog Ready·claw installed）·月度三件套 r496 已兑现零双跑·治理审视槽位已 discharge "
        f"| 验证证据: smoke 47/47+S6 38 rc0+n1/pf selftest 绿+attrition CLEAN+origin 同步 94ae54103+心跳 epoch int 自证 | 当前活: W21 收口毕引擎 idle（W22 bm-b 槽已冻结待烧）; 最近实物: results/perpetual_faces/n1_w21_results.json（K=44,120·20:0x 本轮）+REPORT-2026-10-01.md+LIVE-2026-10-01.md; 下里程碑: 10-09 节后首 bar 窗（REGIME_GUARD v3 enforce 首窗实弹）+W23 槽位 bm-c 轮值+RW-5 外审 10-03,窗 ≤48h | 本地未达 origin commit 数=0 | next: r535=W22 链序观察+板扫+常规轮 [via bm-a]\n")
with open(r'round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended, r534')
