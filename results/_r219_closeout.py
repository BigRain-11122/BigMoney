# R219 closeout: state file + heartbeat + round report line (bm-a)
import json, time, datetime, psutil

now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- 1) state-bm-a.json ---
state = json.load(open("state-bm-a.json", encoding="utf-8-sig"))
state["round_no"] = 219
state["did"] = ("R219: S0 撞车正典解 (autofill_state 1-UU vs bm-b r224, bigmoney-conflict-resolve 二次实弹: "
    "launches union 50+50->50 零丢失 + last_tick 同秒 tie->HEAD r140 + CRLF 镜像 r223 + parse-verify/isinstance, rebase 落定) "
    "+ 技能装订面漂移自捕 re-sync (.codely-cli/skills 16例旧版 -> Tools/skills 18例三律版, 18/18 ALL GREEN) "
    "+ T-72 s2 巡逻 (first-pull pid 29132 健康 done 602/5228 ETA ~10:20) + S6 21 腿全绿 + CODELY 坑律 1 条")
state["verdict"] = "GREEN"
state["next"] = ("T-72 s2 完成轮验收 derive (coverage>=5000/5222+自坍缩零违规面+同日重跑幂等+num 上限冻结+请求预算归账; ETA ~10:20); "
    "09-28 Monday 新 bar 全链接力; mf/AH EM-block 自愈窗续巡; bm-c rebuild-or-retire 09-26 11:52 GM face; "
    "10-01 月界三件套+REGIME_GUARD v3 日期门; T-70 中期判读 10-09")
state["ts"] = now_iso
state["last_round_ts"] = "2026-09-26T04:45:38"
state["updated_at"] = now_iso
state["current_task"] = ("r219 done: S0 collision resolved via skill dogfood#2 + skill-install re-sync 18/18; "
    "next: T-72 s2 acceptance derive on first-pull completion (~10:20) / 09-28 new-bar relay")
state["last_run"] = now_iso
state["last_round_at"] = now_iso
json.dump(state, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- 2) heartbeat fleet/machines/bm-a.json (own file only) ---
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
vm = psutil.virtual_memory()
hb["machine_id"] = "bm-a"
hb["last_seen"] = now_iso
hb["current_task"] = "r219 done: S0 autofill_state UU resolved (skill dogfood#2) + skill-install re-sync 18/18; T-72 s2 first-pull patrol healthy (602/5228); next: T-72 s2 acceptance derive on completion"
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["cpu_pct"] = round(psutil.cpu_percent(interval=1), 1)
hb["free_ram_gb"] = round(vm.available / 1e9, 1)
hb["gpu_free_vram_gb"] = 5.4
hb["verdict"] = "GREEN"
hb["heartbeat_epoch_utc"] = epoch  # JSON int (R170/R178 law: int not str)
hb["clock_read"] = now_iso
hb["round_no"] = 219
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- post-write self-assert (smoke F7 contract) ---
re = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(re["heartbeat_epoch_utc"], int), "epoch not int after write-back (R170/R178 law)"
rs = json.load(open("state-bm-a.json", encoding="utf-8-sig"))
assert rs["round_no"] == 219
print(f"state 219 + heartbeat epoch {re['heartbeat_epoch_utc']} int-verified + clock {re['clock_read']}")

# --- 3) round report line ---
line = ("R219 | " + now_iso + " | bm-a (dept:工程/舰队·S0 撞车正典解+技能装订面 re-sync) | "
 "verdict: GREEN (WM probe 05:03 py_low_board_clear 合法闲置 0 open/0 bandit/bars present·pool_ready 2=bm-b lane-pin P-1e 域不越权; "
 "watermark_red red=false lane healthy; compute_audit CLEAN flags[] py 0.7%; smoke 25/25; orders 74/74 双扫零差集) | "
 "did: S0 轮首脏=本机 watchdog 04:50 tick 定向提交后 pull --rebase 撞 bm-b r224 closeout 同窗双推 1-UU (autofill_state) "
 "-> bigmoney-conflict-resolve 技能二次实弹 dogfood: 分类器首判 mixed-dict+ledger -> 探针 (launches 50+50 集合恒等零差集; "
 "last_tick 双 04:50:01 同秒 tie; base CRLF/inc LF 分化) -> results/_r219_resolve.py 按配方解 (launches union 50 零丢失; "
 "last_tick tie->HEAD=base r140 律整 dict 赋值 R203 律; CRLF 生产者镜像 r223 律; parse-verify r185 + isinstance 断言) "
 "-> rebase continue 落定 3c00e3e7; S3 主闭环=**技能装订面漂移自捕+re-sync**: 实跑分类器输出配方缺 cap50/r140-tie/CRLF 三律 "
 "-> 源 (Tools/skills 18 例版, bm-b r223/r224 更新) vs 装订 (.codely-cli/skills 16 例版 R218 装订后未再同步) 字节差实锤 "
 "-> re-sync 装订面 -> selftest 18/18 ALL GREEN 三律入位; T-72 s2 巡逻: first-pull 健康 (pid 29132 存活 04:33 起, "
 "done 602/5228 ~4.4s/股, ETA ~10:20 完成轮验收); J 队列 J10/J12/J13/J18b 全 done·Optuna gated 6<8·余项全日期门控; "
 "S0.5 首扫 74/74 零未回执 + decisions 09-26 批 4 行零涉本仓待执项 (D-01 涉本司=SLA 注记已 executed; D-02/03/04 执行司=FluxVerse/HQ); "
 "S6 21 腿全绿: audit CLEAN + wm probe 合法 idle + daily 0 新行 cutoff 09-24 (周末·09-28 新 bar) + regime ORANGE d2 shadow "
 "(hs300<MA200 #10 + breadth 0.77) + lhb <30min 节流 no-op + heat 周末 no-op + futures/options 零网络覆盖 no-op "
 "+ mf 分离 rank pass spawn (EM-block 自愈续) + ths 同日幂等 no-op + ah spawn 节流 29min<30min 自愈续 + fp=bm-c 车道诚实 no-op "
 "+ fundamental 7.6h fresh skip + blf 全门绿 + bar 条件腿 (live.paper/t35v/t24x2/aggr/alloc) 0 新 bar 合法跳过 "
 "+ export-09-24 6 员 18 持 equity 5,996,645 幂等 + scorecard 6 员 + build_status (10 factors/432combos/0pass/traders 6) "
 "+ token delta +2; S4 坑律 1 条入册 (技能源!=装订面·漂移律·四问门过); "
 "S7 schtasks 三任务健康 (Loop Running 本轮实火/Watchdog Ready 05:20/Autofill Ready 05:10) + inbox 0 未读 + 收尾 orders 双扫 74/74 | "
 "ev: results/_r219_probe.py + results/_r219_resolve.py + rebase 落定 3c00e3e7 + 装订面 selftest 18/18 实跑 + CODELY 坑律行 "
 "+ state 219 + 心跳 epoch int 自证 + 本轮 commit | "
 "next: T-72 s2 完成轮验收 derive (coverage>=5000/5222+自坍缩零违规面+同日重跑幂等+num 上限冻结+请求预算归账·ETA ~10:20); "
 "09-28 Monday 开盘新 bar 全链接力 (daily->live.paper REGIME_GUARD v3->t35v->t24x2->aggr->export->scorecard); "
 "mf/AH EM-block 自愈窗续巡; bm-c rebuild-or-retire 09-26 11:52 GM face; 10-01 月界三件套+REGIME_GUARD v3 日期门; T-70 中期判读 10-09\n")
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
