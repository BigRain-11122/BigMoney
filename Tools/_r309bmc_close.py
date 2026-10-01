"""r309 bm-c: closing bookkeeping -- state 309, heartbeat, CODELY entry,
round report line. One script, exact JSON/EOL control."""
import json
import os
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW_LOCAL = "2026-10-01T10:36:00+08:00"

# ---- 1. state-bm-c.json: round 308 -> 309 ----
sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 309
st["last_round_at"] = NOW_LOCAL
st["last_round_ts"] = NOW_LOCAL
st["updated"] = NOW_LOCAL
st["verify"] = (
    "S1 smoke 47/47; W5 ghost-face dual-flip 12/12 (three-way: shard "
    "products 12/12 + finalize n1_w5_results.json K=11,120 + prereg "
    "sec.7/8 backfill; entry+shard both done, pool diff 63+/26- "
    "surgical r289 mirror); generator _claimable fix (ghost "
    "all-shards-done not live; selftest 4c legs) + N1_BANDS[6] + leg3c "
    "W6 packing/refusal-facts; runner WAVE_CONFIGS[6] + W6 selftest leg; "
    "law sec.4 W6 row + prereg PERPETUAL_N1_W6_PREREG.md frozen pre-run "
    "(gate ADMIT exit0); generator selftest PASS + runner selftest PASS "
    "(W6 leg); supply materialized 12 PERPETUAL-N1-W6-SHARD-0..11 ready; "
    "push 2f34dddd1 after pool union rebase (origin bm-a N3-R1 flips "
    "preserved 6/6 + my W5 flips 12/12 + W6 12/12, r294 domain law); S6 "
    "31 legs rc0 NON-GREEN=NONE")
st["did"] = (
    "r309: W5 wave pool closure (r489 two-layer contract completed by "
    "observing-round flip executor) + never-dry trigger un-deadlocked "
    "(_claimable live count) + N1-W6 wave materialized end-to-end (law "
    "sec.4 W6+ WARNING executed: B arithmetic tail 21_900..22_099 hits "
    "W5 A band -> B re-based to 25_900..26_099 packing at W6 A end+1, "
    "A keeps +2_000 tail 23_900..25_899; machine-proven refusal facts; "
    "NOT a re-pick per R250)")
st["current_task"] = (
    "N1-W6 burn window: 12 shards ready lane=ANY on origin 2f34dddd1, "
    "fleet autofill claims next ticks; finalize --wave 6 (cumulative "
    "K=13,320) after 12/12 + prereg sec.7/8 backfill + predictions "
    "4-check; n_eff anchor note: N3-R1 +28 (bm-a r509 finalize, ledger "
    "375,447) landed between W6 freeze and burn -- disclose at sec.7 "
    "backfill, finalize reads prev from ledger dict (anti-hand-copy law)"
)
st["next"] = (
    "(a) W6 12-shard burn by fleet autofill -> finalize --wave 6 + "
    "predictions reconciliation; (b) T-134 s2 fourth conversion "
    "evidence-scan (p1e_synth 2586.9s vs grid_dualface T54 8-shard "
    "likelihood-first); (c) round 310 = HANDOVER 5-round refresh due; "
    "(d) W7 prereg must re-check B tail law vs W6 A band (law sec.4 "
    "W6 row warning carries forward)"
)
st["last_round"] = (
    "2026-10-01 r309 bm-c: W5 ghost dual-flip + generator claimable fix "
    "+ N1-W6 materialized (12 ready, prereg ADMIT, B skip-over per law) "
    "+ S6 31 legs rc0")
st["last_ts"] = NOW_LOCAL
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=2)
    f.write("\n")

# ---- 2. heartbeat fleet/machines/bm-c.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
try:
    vr = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"], timeout=15)
    gpu_free = int(vr.decode().strip().splitlines()[0])
except Exception:
    gpu_free = hb.get("gpu_free_vram_mib", 0)
hb["last_seen"] = NOW_LOCAL
hb["current_task"] = st["current_task"][:200]
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = 2.3
hb["gpu_free_vram_mib"] = gpu_free
hb["verdict"] = ("W6 supply landed 12 ready (ignition next autofill "
                 "tick); W5 wave closed dual-layer; S6 31 legs rc0")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = NOW_LOCAL
epoch = hb["heartbeat_epoch_utc"]
assert isinstance(epoch, int), "epoch must be JSON int (R170/R178 law)"
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)
    f.write("\n")
json.loads(open(hp, encoding="utf-8").read())
assert isinstance(
    json.loads(open(hp, encoding="utf-8").read())["heartbeat_epoch_utc"],
    int)
print("heartbeat epoch:", epoch, "int OK | gpu_free:", gpu_free)

# ---- 3. CODELY.md pitfall entry ----
cp = os.path.join(ROOT, "CODELY.md")
raw = open(cp, "rb").read()
eol = "\r\n" if b"\r\n" in raw[-200:] else "\n"
entry = (
    "- [2026-10-01 10:3x r309 bm-c] 池 ghost 面死锁供给触发坑（W5→W6 实弹·r489 "
    "姊妹面·r497 park_note 死锁同族）：daemon harvest 只翻 shard 层、entry 层滞留 "
    "ready=烧毕波呈活供假象——生成器 never-dry 触发（live==0）被 12 件已 finalize "
    "的 W5 幽灵 entry 永久堵死，py_watermark「可跑批事实」面同污染=假红；修法=①"
    "观测轮 flip 执行器（三方对账：shard 产物+finalize 件+prereg 回填）entry+shard "
    "双翻（r180 律·本窗 Tools/_r309bmc_w5_entry_flip.py）②生成器 _claimable（全分"
    "片 done=不计活供）进 live 计数与 supply 同面 in-flight 门+selftest 4c 腿。How "
    "to apply：一切「读池判供给/饥饿」面（生成器/审计/水位探针/dispatcher）一律按 "
    "shard 层 claimable 真值计数勿信 entry 层；波收口=烧毕方或观测轮当窗双翻，禁留"
    "隔轮（留隔轮=触发面死锁+假红双害）。"
)
with open(cp, "ab") as f:
    f.write((eol + entry + eol).encode("utf-8"))
print("CODELY appended, size:", os.path.getsize(cp))

# ---- 4. round report line ----
rp = os.path.join(ROOT, "round_reports-bm-c.md")
line = (
    "\n2026-10-01T10:36:00+08:00 | r309 | dept:研究（常供面 N1 供给线·T-133 "
    "s2 faces lane）| watermark verdict=红（09:50 采样 runnable-work-idle-low-"
    "cpu——真根因=W5 闭合后供给真空〔live=0〕+12 件 W5 烧毕幽灵 entry 污染活供计"
    "数〔r489 entry 层滞留〕；本窗三层解=①W5 12 件 entry+shard 双翻〔三方对账："
    "12/12 产物+finalize K=11,120+prereg §7/§8〕②生成器 _claimable 修〔全分片 "
    "done=不计活供·selftest 4c〕③W6 12 分片物化推 origin 2f34dddd1〔ready=12≥"
    "floor3·点火=autofill 下一 tick〕）| 本轮主产出=**N1-W6 供给波全链物化**（法"
    "典 §4 W6 行展行：B 算术尾 21_900..22_099 撞 W5 A 带=钉版警示兑现→同法跳位 "
    "25_900..26_099〔=本波 A 尾+1·打包不变式入 leg3c+refusal facts 机证跳位被迫"
    "性〕·A=23_900..25_899 算术尾原样；prereg PERPETUAL_N1_W6_PREREG.md 跑前冻结"
    "〔N=2,200·累计池 13,320·W5 锚 mu −0.0917/sigma 0.2450/线 1.1492·预测 4 条"
    "写死〕→banned_direction_gate ADMIT exit0→runner WAVE_CONFIGS[6]+W6 守卫腿→"
    "supply 物化 12 分片 ready〔lane=ANY·workers 8×BelowNormal〕）+**W5 波收口"
    "双翻**（r180/r489 律·池 diff 63+/26- 外科）+**生成器 ghost 修复**（never-dry "
    "触发解锁·r497 同族根修）| evidence: S1 47/47；生成器 selftest PASS〔含 3c "
    "W6 packing/4c ghost 腿〕；runner selftest PASS〔W6 腿〕；supply 回执 12 "
    "entries；池终态 W5 done 12/W6 ready 12/N3 done 6〔origin bm-a 侧 N3-R1 翻面"
    "union 保真 6/6〕；S6 31 腿 rc0 NON-GREEN=NONE〔dualrun 先行·审计/水位/日"
    "链全绿·10-01 休市 0 新行·lane 守卫 12 腿诚实 no-op·fund_premium no-op pre-"
    "15:30·host 守卫件 bm-a 新鲜=放行跳〕；attrition CLEAN〔4 healed 历史〕；"
    "orders 双扫差集 EMPTY；D-19 ed4e0eab UNCHANGED（raw-blob）| 实况三行（CEO "
    "过程可见面）：当前活=N1-W6 波 12 分片待机队点火（lane=ANY 首到首得）+W5 波"
    "池面收口完毕｜最近实物=research/PERPETUAL_N1_W6_PREREG.md+池 12 分片条目 "
    "PERPETUAL-N1-W6-SHARD-0..11+生成器 claimable 修复（10:2x·origin 2f34dddd1）"
    "｜下个里程碑=W6 12 分片烧毕→finalize --wave 6〔累计 K=13,320·预测对账 4/4 "
    "面〕+T-134 s2 第四件（窗≤48h·10-03 前）| 产品分=2（能跑实物：冻结 prereg+12 "
    "可烧分片+两修带 selftest）| next: (a) W6 烧批-autofill 接力+finalize+s7/s8 "
    "回填〔n_eff 锚注记：N3-R1 +28 于冻结后落账=§7 回填披露·finalize 读账本真值〕；"
    "(b) T-134 s2 第四件证据扫描（p1e_synth 2586.9s vs grid_dualface T54）；(c) "
    "310 轮=HANDOVER 五轮刷新义务；(d) inbox 095x bma→bmb N3-R1 闭环回执已读留置"
    "（非本机收件）\n")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report appended")
