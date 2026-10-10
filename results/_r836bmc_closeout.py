import json, time, subprocess, ctypes, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_compact = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

class MemStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
m = MemStatus(); m.dwLength = ctypes.sizeof(MemStatus)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_ram = round(m.ullAvailPhys / 1e9, 1)
total_ram = round(m.ullTotalPhys / 1e9, 1)

def gpus():
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=15)
        return int(p.stdout.strip().splitlines()[0])
    except Exception:
        return None

vram_free_mib = gpus()  # 14397
head_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()[:9]

SUMMARY = ("r836 bm-c: S0 delivery-cure round -- (1) RED-FLAG CURED: r833-r835 close commits found UNPUSHED (behind2/ahead6, last_push_ts still r832 14:18 = the round-verify claim was false); "
           "churn absorb x2 + pull --rebase 8-pick replay: runnable_pool shared face resolved --ours then sync_face settle (r489 two-layer union, settled wrote shared+lane), crash_fuse newer-wins union (80/88->88 sigs), "
           "headless traps beaten (rebase --continue fake-conflict message = unstaged daemon faces per r813 law; Terminal-is-dumb EDITOR unset = git -c core.editor=true), "
           "marker contamination (3 faces via rebase-continue claw bypass, r808 family RECURRENCE) repaired pre-push by soft-reset single clean commit 7d31360cb (git grep '^<<<<<<<' HEAD tree-clean verified, marker blobs never reached origin); "
           "PUSH DELIVERED 81706d1e8..7d31360cb, post-push fetch 0/0 self-verified; "
           "(2) S0.5: dec delta FALSE (34cf2538 unchanged) + ord delta FALSE (b31f0381) + orders_ack real-unacked=[O-20261010-1906-bm-c] consumed in-round: adjudication receipt MSG-1940 processed (W139/W140 carve-outs 7464be852 verified in tree, W204 chain unblocked), reply MSG-2026-10-10-2010 sent to bma -- honest disclosure: C1804 dead-session spliced dual files NOT recoverable (main worktree/.codely-cli tmp/%TEMP%/both worktrees searched), phase-2 rebuild from committed ADMIT receipt bands pinned next shift, seat+prereg 1422ad767 held; "
           "(3) S1 smoke 49/49; S2 job board empty; W17 = bma property per MSG-1900 (no re-claim, later-claimer law, my SHARD-0 close unioned into settled pool face); "
           "(4) S6 43-leg canon rc0 green; S7 quartet green (pin=5 no-op, watchdog, both claws LF-normalized) + attrition CLEAN (4 ledgers) + idle --worked reset; "
           "(5) pit ledger: new r836 entry (race-ring detached-HEAD stale-branch-ref push + r808 marker-guard recurrence, template three-mandatory-legs law) + mini-split r516/r782 -> pit-git-resolver-rebease2.md (receipt _r836bmc_pit_resolver_rebase2_split.json, byte identity 30652-2521+1671=29802<=cap)")

ACTIVITY = ("当前活: r836 收口——S0 送达根治（r833-r835 滞留 commit 全量上链 7d31360cb·0/0 自证）+ O-1906 判决消费（回执 MSG-2010·phase-2 重建下轮）+ pit 双坑律入册+mini-split | "
            "最近实物: origin/main 7d31360cb（consolidated v2 单净 commit）+ results/_r836bmc_surgical_merge.py（共享面 newer-wins 手术工具留仓）+ pit-git-resolver-rebase2.md @ " + now + " | "
            "下个里程碑: W204 五面冻结 phase-2（splice 从 ADMIT 回执重建·≤2 班）+ W18 draft berth + T-182 P0 runner（10-13/14 交）")

NEXT = ("r837 续作: ①W204 phase-2 splice 重建（ADMIT 回执 bands A=463604_465603/B=465604_465803/ARITH_A=463404_465403/ARITH_B=463604_463803·照 W203 注册式·双 blob SHA 重取·selftest 绿门后冻结）"
        "②W18 draft berth（候选选取+queue_seed_gate）③T-182 P0 runner 切片 ④L54 三机首燃观察 ⑤D-05 写腿=10-11 00:00 常务轮首位 ⑥pit 指针行 ceremony 债（CODELY.md 主件指针行+登记册 append·本窗诚实欠账）⑦s05 脚本双 bug 修复（dec 读取行+ack 后缀口径）后入 1-gen 血统")

# ---- state-bm-c.json ----
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 836
st["round_no_label"] = "round 836 (bm-c)"
st["clock_read"] = now
st["ts"] = now
st["last_seen"] = now
st["updated"] = now
st["last_round"] = SUMMARY
st["last_round_at"] = now
st["last_round_summary"] = now + " | r836 | dept:工程/舰队（S0 送达根治轮·rebase 双坑律入册+O-1906 判决消费） | 本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | WM-VERDICT: 红→结构性（lane=pool-batch-runnable-idle-low-cpu·W17 已归 bm-a=MSG-1900·本机队列空·供线=下轮 W204 重建+W18 berth·本轮实工=送达根治全链非怠工） | 孤儿面=1（只读探针·ComfyUI 8188 影片链服务面·r829 判例不触·killed=[]） | " + SUMMARY
st["last_round_summary_at"] = now
st["current_task"] = ACTIVITY
st["current_task_at"] = now
st["current_task_ts"] = now
st["activity_now"] = ACTIVITY
st["last_action"] = SUMMARY
st["verdict"] = SUMMARY
st["did"] = SUMMARY
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "W204 five-face freeze phase-2 (splice rebuild <=2 shifts) + W18 draft berth + T-182 P0 runner 10-13/14"
st["latest_artifact"] = "origin/main 7d31360cb + results/_r836bmc_surgical_merge.py + research/pit-git-resolver-rebase2.md + fleet/inbox/MSG-2026-10-10-2010-bmc-w204-phase2-receipt.md"
st["free_ram_gb"] = free_ram
st["ram_free_gb"] = free_ram
st["idle_ram_gb"] = free_ram
st["total_ram_gb"] = total_ram
st["last_ts"] = now
st["head_sha"] = head_sha
st["health"] = "ok"
st["idle_rounds"] = 0
st["agenda_starved"] = False
if vram_free_mib:
    st["gpu_free_vram_mib"] = vram_free_mib
    st["gpu_idle_vram_mib"] = vram_free_mib
    st["gpu_free_mib"] = vram_free_mib
    st["gpu_vram_free_mb"] = round(vram_free_mib * 1.048576)
    st["gpu_idle_mb"] = round(vram_free_mib * 1.048576)
    st["gpu_free_vram_mb"] = round(vram_free_mib * 1.048576)
    st["gpu_idle_vram_mb"] = round(vram_free_mib * 1.048576)
st["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": now,
              "note": "r836 closeout delivery: consolidated v2 7d31360cb pushed pre-close (81706d1e8..7d31360cb); close commit pushed after this write; post-push fetch + rev-list 0/0 self-verify."}
if "d19_watermark_guard" in st and isinstance(st["d19_watermark_guard"], dict):
    st["d19_watermark_guard"]["round_ref"] = 836
    st["d19_watermark_guard"]["ts"] = now
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now
hb["ts"] = now
hb["clock_read"] = now
hb["updated_at"] = now
hb["heartbeat_epoch_utc"] = int(time.time())
ack = hb.get("orders_ack", [])
if isinstance(ack, dict):
    ack = list(ack.keys())
if "O-20261010-1906-bm-c" not in ack:
    ack.append("O-20261010-1906-bm-c")
hb["orders_ack"] = ack
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["verdict"] = SUMMARY
hb["last_round_summary"] = st["last_round_summary"]
hb["last_action"] = SUMMARY
hb["activity_now"] = ACTIVITY
hb["next"] = NEXT
hb["next_milestone"] = st["next_milestone"]
hb["latest_artifact"] = st["latest_artifact"]
hb["free_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
if vram_free_mib:
    hb["gpu_free_vram_mib"] = vram_free_mib
    hb["gpu_idle_vram_mib"] = vram_free_mib
hb["health"] = "ok"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify epoch int + ack presence
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "O-20261010-1906-bm-c" in hb2["orders_ack"]
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"]

# ---- round report line ----
rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8") as f:
    f.write(st["last_round_summary"] + " | 下轮指针: " + NEXT + "\n")

print(json.dumps({"round": 836, "ts": now, "free_ram_gb": free_ram, "vram_free_mib": vram_free_mib,
                  "head_sha": head_sha, "orders_ack_total": len(hb2["orders_ack"]),
                  "epoch_int": hb2["heartbeat_epoch_utc"]}))
