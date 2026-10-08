"""r873 bm-a closeout writes: state round bump + heartbeat (epoch int
law R170/R178, clock_read T-format R262) + round report row (ROOT
canonical per r844 law)."""
import json
import time
import datetime

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

# --- state bump ---
sp = r"state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 873, f"round_no anchor drift: {st['round_no']}"
st["round_no"] = 874
st["round"] = 873
st["ts"] = iso
st["clock_read"] = iso
st["last_round"] = 873
st["last_round_at"] = iso
st["current_task"] = ("W184 registry FREEZE chain inherit (freeze push + tick ignition 12 shards, "
                      "r872 candidate 21,446B) + W16 reform-face derive slice (prereg sec.4 caliber, "
                      "first live reform implementation) + pool supply refill (W17 prereg draft)")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
st2 = json.load(open(sp, encoding="utf-8"))
assert st2["round_no"] == 874
print("state -> r874 ok")

# --- heartbeat ---
hp = r"fleet\machines\bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["clock_read"] = iso
hb["ts"] = iso
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["idle_ram_gb"] = 57.2
hb["ram_free_gb"] = 57.2
hb["idle_vram_gb"] = 5.3
hb["gpu_idle_vram_gb"] = 5.3
hb["gpu_free_vram_gb"] = 5.3
hb["cpu_pct"] = 4.8
hb["cpu_util_pct"] = 4.8
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["round_no"] = 874
hb["round"] = 873
hb["last_round"] = 873
hb["now_active"] = ("r873 W16-JUDGE false-crash closure + verdict backfill "
                    "(claim umbrella + dual-face tombstone + daemon harvest flip "
                    "09:36:03 = crash-loop dead; prereg sec7/8 one-shot; attrition "
                    "2 rows retrofill 37+40)")
hb["current_task"] = ("W184 registry FREEZE chain inherit (r872 candidate: freeze push + "
                      "tick ignition 12 shards) + W16 reform-face derive slice (first live "
                      "reform impl, prereg sec.4 caliber, 48h CEO report due 10-10 04:48) + "
                      "pool supply refill W17 (supply_floor breach honest)")
hb["last_action"] = "r873 closeout: S6 full chain rc0 + quartet green + W16 closure DELIVERED"
hb["latest_artifact"] = ("research/TRIAL_LABOR_W16_PREREG.md sec7/sec8 backfill @2026-10-08 09:5x "
                         "+ results/gate_attrition.json W16 rows (39 history)")
hb["verdict"] = ("green (W16-JUDGE closure DELIVERED same-round: false-crash tombstoned both fuse "
                 "faces + entry/shard harvest-done 09:36:03 + sec7/sec8 one-shot backfill + attrition "
                 "2 rows retrofill; verdict = old-caliber 0/40 fail + intake lawful-zero, reform-face "
                 "derive = next-round P0; watermark red=false lane healthy; supply_floor flag = "
                 "pool empty post-W16, W17 draft next; engine ALIVE rc0 idle queue0)")
hb["orphan_faces"] = 0
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in hb2["clock_read"], "clock_read must be T-separated (R262)"
print("heartbeat ok: epoch-int", hb2["heartbeat_epoch_utc"], "| clock", hb2["clock_read"])

# --- round report row (ROOT canonical r844 law) ---
rp = r"round_reports-bm-a.md"
row = (
    iso + " | r873 | bm-a | dept:策略+工程/舰队 | WM-VERDICT: 绿 (red=false lane=healthy; engine ALIVE "
    "rc0 idle queue0; supply_floor flag=pool empty post-W16 closure -- W17 draft = next-round supply "
    "refill, streak 11.6min fresh) | 当前活=W16-JUDGE 伪崩收口+判决面回填全链 | 最近实物=research/TRIAL_LABOR_W16_"
    "PREREG.md §7/§8 一次定稿回填 + results/gate_attrition.json W16 双行 (09:4x, 39 history) | 下个里程碑=W184 "
    "freeze push+点火 12 shards (r872 候选继承, 窗≤今晚) + W16 改革面 derive (首落实现, 48h CEO 呈报 due 10-10 "
    "04:48) | did: S0-1 孤儿面=0; S0 pull-rebase 风暴 (push 拒×2→churn absorb 自家 daemon 面→rebase 3/3→DELIVERED "
    "a9f5897a7 not-at-origin=0); orders 双扫 0 未回执 (O-*.md 口径); DEC/ORD 水位 python raw-bytes 双恒等 "
    "ee659451/bc1a85af 零动作; smoke 49/49; W16 三件套收口: ①worker-claim 伞 (runner log 'judge shard 0of1 "
    "complete' 40/40 rc0 04:24:08 实证, 30-min confirm 伪崩 04:52 = r860 坑律 W16-SCREEN 同晨复刻) ②fuse 双面 "
    "墓碑 (r824/r860 范式, reason=完成实证, sigs 78/cleared 65) ③daemon 收镰翻面 entry+shard done 09:36:03 (commit "
    "9e1c97241+c34041d01) = fuse 停摆 122 拒绝计数死; 判决面: 10,000→distinct 173 (1.73% ∉[2%,12%] MISS 供给弱化警 "
    "报) →screen 40/173 (null p95 0.511572 带内第九连) →judge 40/40 fail (最佳 0.7272 < 判线 1.1437) →G2 0→intake "
    "合法零; 账本 802,278+40=802,318 链连续; §7/§8 回填含改革面缺口披露 (r722 血统复制丢 W14 改革块=旧口径保守面非 "
    "终判, derive 切片=下轮 P0); attrition 双行 retrofill (SCREEN 373+JUDGE 40, shared+bm-a 车道, guard scan "
    "CLEAN 4 files); S6 28 腿全 rc0 (dualrun streak 51 ZERO-DRIFT; 采集器 pre-15:30 合法 no-op; moneyflow 分离 "
    "rank pass spawn; scorecard 6/28/7; REPORT-2026-10-08+LIVE-2026-10-08+build_status 再生; token L2 0 today; "
    "纸盘腿=无新 bar 合法跳); 四件套绿 (loop pin8 no-op, watchdog Ready, 双爪 CR-normalized MATCH); idle --worked "
    "| 验证: commits 1499a55e7+a9f5897a7 (rebase 后) + attrition guard CLEAN + heartbeat epoch-int 自证 | 下轮指针: "
    "W184 freeze+点火 → W16 改革面 derive → W17 prereg\n"
)
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(row)
with open(rp, encoding="utf-8") as f:
    assert "r873 | bm-a" in f.read().splitlines()[-1]
print("round report row ok (ROOT canonical)")
