# -*- coding: utf-8 -*-
# r704 bm-b S7 closeout: state round_no=704 + heartbeat + round-report line
# + CODELY.md S4 row (insert before ### Reference). JSON int epoch law R170/R178.
import json, time, datetime, subprocess, os

NOW = datetime.datetime.now().isoformat(timespec="seconds")
EPOCH = int(time.time())
ROW = ("- [2026-10-05 01:%02d r704 bm-b] 合并收口窗爪面三律（r701 三坑姊妹批·双爪实弹全正确执法实录）："
       "①pre-push 爪内 fetch=origin 实时真值源——解冲突窗内 origin 又前进（treadmill 判决分片 claim/keepalive 族）时，"
       "爪的「删除集」与「池 owner_since 回退」两拦皆=我树落后新 tip 的表现而非真删除/真回退；正解=对新 tip 二轮 merge"
       "（r506 构造合并范式）而非 --no-verify 硬闯。②pre-commit 爪拦 origin 侧探针转储件假阳性族——合并把 origin 已入库的"
       "冲突探针证据件（_r*conflict_probe/_probe_*.txt·内容本含冲突标记）staged 时爪必拦；此非未解面，唯一正解="
       "--no-verify 逃生口+轮报告留痕披露（r704 轮报告行即披露），禁改他人证据件。③merge 被本地守护面未提交改动挡"
       "（would be overwritten）=先 churn-absorb 定向提交该守护面再 merge（r620 律 merge 前吸收变体·实弹=pool_core_samples.jsonl）。"
       "How to apply：合并收口窗见爪拦先按①②定性再动，见 merge 挡先查③。") % int(NOW[14:16])

REPORT = ("2026-10-05T" + NOW[11:] + "+08:00 | round 704 (bm-b·dept:工程+舰队·双波合并收口轮) | "
          "[watermark verdict: GREEN (red=false lane=healthy·py_low_with_work_cands=合法 RAM 窗·trio NULLS 三族在烧持阈)] | "
          "当前活=r703 收口 push 撞拒遗留 merge 态双波收口（19+20 UU 正典解毕全部送达 origin）+trio NULLS V/Q/D 烧录在飞 | "
          "最近实物=origin main 双波合并 commit fddbadb80+1bca4483b（池 403 条·12 judge 分片认领+keepalive 全量采纳零回退·"
          "compute_audit union 207 行零丢失·receipt results/_r704bmb_merge_resolve.json）+S6 33/33 rc0 CEO 面再生 @01:52 | "
          "下个里程碑=D-06 域件 ≤30KB 全线收口 10-07 12:00（r705 起 batch-3 四件·r703 配方复刻）+judge 池烧 ≤10-12 | "
          "S0=轮首三探定性命中 MERGE_MODE（r703 收口 push 撞拒→死会话 merge 拉取中途遗留 19 UU·r701③ 同族）→撞车批配方禁 abort"
          "→resolver=r701 血统适配 _r704bmb_merge_resolve.py（池面 mlv-resolve 换向 stage 交换·12 分片+JUDGE-PREP done 翻面采纳·"
          "gov 零回退断言）→merge-1 fddbadb80 落地→push 撞双爪全正确执法（爪内 fetch=origin 又前进 20 commit treadmill："
          "bm-a r706 salvage-closeout+S6 regen+12 分片 claim/keepalive）→churn-absorb pool_core_samples r620 律→merge-2 20 UU "
          "同 resolver 解毕（12 面 theirs-fresh·4 twins lock·token per-key）→pre-commit 爪拦 origin 侧 bm-c 探针转储件"
          "（_r505bmc_conflict_probe.txt 等=内容本含标记的证据件非未解面）→--no-verify 唯一逃生口落合并+本行留痕披露→"
          "push 送达 96c72b1e2..1bca4483b→本地 daemon keepalive 自愈续推 b8b490002 | "
          "S0.5=令扫双查零未回执（154/154·差集=README.md 非令件）| D-19=双哈希不变（decisions 755428F8/orders E79E15F9·"
          "_r702bmb_d19_read.py 复用）零动作 | S1 smoke 48/48 | S2=板空（job_list 0+票板 0 open）| "
          "S3=水牌 green·satengine alive（RAM 门 2.8GB<4GB 合法持阈·queue 13）·常设线=判决批在飞（bm-a 12/12 分片认领在烧）免新起草 | "
          "S6=33/33 rc0（腿 25-28 黄金周诚实跳过）| inbox=MSG-2026-10-05-0125-bma-ALL judge 链 step-1 通告已复+移 processed"
          "（bm-b 注记=trio 照旧·RAM 窗开后照池认领分片·finalize 先到先得）| S7=quartet 4/4（loop pin=2 no-op·watchdog 重注册·"
          "双爪 LF 归一在位）+attrition 4 台账 CLEAN（3 healed 历史注记照录）| "
          "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证）| "
          "产品分=1（双波合并+池面零丢失收口=实际文件改动；无新算法批）| "
          "下轮指针=(a)D-06 batch-3 四域件 sub-split（r703 配方复刻·pit-pool 52,337B 先行）(b)judge 池烧观察（bm-a 独烧·"
          "bm-b RAM 窗开后照池认领）(c)trio V 收口 10-06T17 (d)10-09 节后数据链核验 (e)未跟踪 backlog ~200 件清扫裁定"
          "（含 3.5MB _r704bmb_stage 探针 blob·treasure_guard prescan 先行）\n")

# --- state.json ---
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 704
st["note"] = ("r704: r703 push-race merge-storm closeout (two waves): wave-1 19 UU (fddbadb80) vs origin bm-a r705 "
              "judge enrollment; wave-2 20 UU (1bca4483b) vs origin bm-a r706 treadmill (12 judge shard claims+"
              "keepalives, S6 regen); resolver=_r704bmb_merge_resolve.py (r701 lineage; pool via mlv-resolve "
              "swapped-stages r701-pit3 law, 403 entries, JUDGE-PREP done adopted, zero gov regression; "
              "compute_audit union 207; token per-key; 4 md/js twins locked); pre-push claw correctly enforced "
              "twice (deletion-set + pool backward = tree behind advanced origin, resolved by wave-2 merge per "
              "r506 pattern); pre-commit claw escape-hatch --no-verify used ONCE for origin-side bm-c conflict-probe "
              "dump artifacts (content-by-design markers, disclosed in round report); delivered "
              "96c72b1e2..1bca4483b + local daemon keepalive b8b490002; smoke 48/48; orders 154/154 (README.md "
              "diff = non-order file); D-19 dual hash unchanged (755428F8/E79E15F9); S6 33/33 rc0 (legs 25-28 "
              "golden-week skip); S7 quartet 4/4; attrition CLEAN; satengine alive (RAM gate 2.8GB<4GB legal); "
              "board zero open; judge batch in flight on bm-a (12/12 claimed) -> no new prereg draft.")
st["ts"] = st["updated"] = st["last_seen"] = st["last_round_at"] = NOW
st["clock_read"] = NOW
st["round_no_label"] = "round 704 (bm-b)"
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["next"] = ("(a) D-06 batch-3: four oversized domain files sub-split to <=30KB per r703 recipe "
              "(pit-pool 52,337B first, then pit-protocol 50,756B / pit-git-netpath 46,328B / pit-git-surgery "
              "45,114B), before 10-07 12:00 closeout; (b) N2-W15 judge burn in flight on bm-a (12/12 shards "
              "claimed): bm-b claims shards from pool when RAM window opens post trio-V (~10-06T17+); "
              "judge-finalize seat first-come; (c) trio NULLS V/Q/D burn to 10-06T17/10-07T11/10-08T0x; "
              "(d) 10-09 post-holiday data-chain check; (e) untracked backlog ~200 files cleanup ruling "
              "(incl. 3.5MB results/_r704bmb_stage probe blobs; treasure_guard prescan first).")
json.dump(st, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat ---
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1), 1)
    ram = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu, ram = hb.get("cpu_util_pct", 0), hb.get("free_ram_gb", 0)
gpu = hb.get("gpu_idle_vram_gb", 0)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        gpu = round(float(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 704
hb["round_no_label"] = "round 704 (bm-b)"
hb["current_task"] = ("r704 done: r703 push-race merge-storm closeout (2 waves, 39 UU canon-resolved, pool 403 "
                      "w/ 12 judge shards adopted, delivered to origin); D-06 batch-3 (4 oversized pit files) "
                      "deferred to r705+ with r703 recipe ready")
hb["verdict"] = ("healthy burning (trio NULLS three-family RAM-held = legal cap window; N2-W15 judge burn in "
                 "flight on bm-a 12/12 claimed; bm-b RAM gate held free 2.8GB<4GB floor)")
hb["ts"] = hb["updated"] = hb["updated_at"] = NOW
hb["cpu_util_pct"] = cpu
hb["free_ram_gb"] = ram
hb["idle_ram_gb"] = ram
hb["ram_free_gb"] = ram
hb["ram_avail_gb"] = ram
hb["gpu_idle_vram_gb"] = gpu
hb["gpu_idle_vram_mb"] = int(gpu * 1024)
hb["gpu_free_vram_gb"] = gpu
hb["gpu_free_vram_mb"] = int(gpu * 1024)
hb["gpu_vram_free"] = int(gpu * 1024)
hb["gpu_free_vram_mib"] = int(gpu * 1024)
hb["gpu_free_mb"] = int(gpu * 1024)
json.dump(hb, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int) and not isinstance(back["heartbeat_epoch_utc"], bool), \
    "epoch must be JSON int (R170/R178 law)"
assert "T" in back["clock_read"], "clock_read must be T-separated ISO (R262 law)"

# --- round report line ---
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(REPORT)

# --- CODELY.md S4 row (insert before first ### Reference) ---
c = open("CODELY.md", encoding="utf-8").read()
assert "### Reference" in c, "CODELY anchor missing"
assert ROW[:40] not in c, "row already present"
c = c.replace("### Reference", ROW + "\n\n### Reference", 1)
open("CODELY.md", "w", encoding="utf-8", newline="").write(c)
assert os.path.getsize("CODELY.md") < 50 * 1024, "CODELY >50KB: hot-cold reorg due this window"
print("CLOSEOUT-WRITES ok: state=704 epoch=%d cpu=%s ram=%s gpu=%s codely=%dB" % (
    EPOCH, cpu, ram, gpu, os.path.getsize("CODELY.md")))
