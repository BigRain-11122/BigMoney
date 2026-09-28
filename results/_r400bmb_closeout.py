# -*- coding: utf-8 -*-
"""r400 bm-b closeout: round report append + state.json + heartbeat + CODELY.md + inbox move.
Read-only-degraded round (S0 collision + Fluxgroup migration execution segment).
All writes = bm-b own-lane files only."""
import json, time, shutil, os, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------- 1. round report append (bm-b lane file) ----------
report_line = (
    f"{ts} | r400 | dept:工程/舰队 (S0 冲突降级只读维护轮·Fluxgroup 迁移窗末班) | "
    "WM-VERDICT: 红牌 red=true @23:17:19 lane=runnable-work-idle-low-cpu·定性=迁移执行段暂停的诚实信号非违令"
    "(Bigmoney-Autofill 等 19 任务被 O-20260926-2000 执行器 v2.2 全禁保护·journal waiting@23:31 实证·GM waiver O-1612·"
    "迁移 enable-all 后 autofill 恢复领 grid shard 自愈)·probe verdict=insufficient_history(n=1 迁移窗扰动) | "
    "did: (1) S0-1 bm-b 锚定;轮首 git status 脏=死会话遗留(r399 池就绪翻转+21:46 S6 产物+autofill tick)→进程面实探零本仓并发会话"
    "(本机=19756 唯一 Bigmoney 会话·其余 codely=Minigame 车道)→按 r398 e10ced42 脱水先例收口 8cb7dd66(runner 7359d47b7 同车)→"
    "pull --rebase 撞 28-UU 共享快照面族→OS 轮令+bigmoney-conflict-resolve 技能双确认=S0 禁解→abort 转只读维护;"
    "origin 活机实证=bm-a r404 在飞(S0 commit 23:20:51+轮中再进 8094f0dec)=竞态风险实锤→S7 正典序列 push 拒→retry 撞→abort→"
    "fallback 分支 origin machine/bm-b-r400 承运滞留产物(runner+池就绪+脱水件 fleet 可见化·D-20260925-01③ 新 ref 零竞态);"
    "(2) S0.5 双扫:本地面 0 差集+origin 面新令 O-20260928-2210 CEO 算力共享令已回执(供给侧三律理解入库+orders_ack 122);"
    "其即时票 T-2026-09-28-113(open·四切片 s1 claim-by-file 协议/s2 pool_worker/s3 ledger/s4 onboarding)本轮禁认领——"
    "认领 commit 达不到 main=机群不可见锁=反重复铁律风险+bm-a r404 在飞持干净通道=天然认领方;暂缓事由=git 写通道物理依赖留痕本行;"
    "下轮 origin 若仍 open 且无人认领则 bm-b 新根首轮认领执行;T-112=bm-c 车道不碰;decisions 尾 D-20260928-05/-06 不涉本仓零动作,"
    "D-02/-03 已由 bm-a r395 落地回执在案; (3) S1 smoke 26/26 PASS 零修红; (4) 迁移实探三件套=schtasks Bigmoney-IterationLoop=已禁用"
    "+last-run=本实例+lock 23:19:35+journal waiting 循环=O-20260926-2000 执行段已启动,本轮=旧根末班轮,未提交产物随 robocopy 迁往"
    " E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney; (5) S6 写面链腿只读轮跳过披露:23:3x 全采集窗关闭=零数据损失(bm-a r403 22:41 S6 36 腿 rc=0 "
    "已覆盖共享面·bm-b 专属采集腿窗关 no-op 等价·paper/marks 幂等面 09-28 bar 已处理);token_meter 跳过披露; (6) S7 自愈脚本"
    "(register_loop_task/register_watchdog)迁移保护窗禁跑(勿双arm·19 任务 XML 由迁移 enable-all 恢复指新根·Abort 路径自动恢复同律);"
    "HANDOVER 5 倍轮核对顺延至新根首绿轮(树即将 robocopy·同步后核对才有意义·r405 补) | "
    "evidence: origin machine/bm-b-r400 分支在位(runner 7359d47b7+脱水 8cb7dd66+本轮收尾件);smoke 26/26;"
    "schtasks=已禁用 running=本实例;journal C:\\Users\\Administrator\\fluxgroup-migration-journal.log waiting@23:31:50;"
    "watermark_red.json red=true @23:17:19 | "
    "next: 迁移完成新根首轮(E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney·实探律 E:\\Fluxgroup\\MiniGame 在=新根开工):"
    "S0 同步+28-UU 批正典解收口(活机退场后按 bigmoney-conflict-resolve 配方)+T-113 认领判定+grid shard autofill 恢复烧"
    "+CEO 48h 千人试用期报告窗 09-29 22:45"
)
with open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"), "a", encoding="utf-8") as f:
    f.write("\n" + report_line + "\n")

# ---------- 2. state.json (bm-b lane) ----------
sp = os.path.join(ROOT, "state.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 400
state["note"] = ("r400: S0-collision degraded read-only round (28-UU shared-snapshot batch vs live bm-a r404 mid-flight -> "
                 "forbidden-to-resolve per OS order, aborted) + Fluxgroup migration execution segment discovered mid-round "
                 "(19 tasks disabled protection, journal waiting, lock 23:19:35) = last round in old root; stranded r399 "
                 "products (GRID_DUALFACE_P1 runner 7359d47b7 + pool ready-flip) carried to origin machine/bm-b-r400 per "
                 "D-20260925-01(3); CEO O-2210 compute-sharing order receipted, immediate ticket T-113 claim deferred "
                 "(claim commit cannot reach main this round = invisible lock anti-dup hazard; natural claimant = live bm-a; "
                 "next round claims if still open); smoke 26/26; unpushed tail travels with robocopy to new root")
state["last_round_at"] = ts
state["last_round_ts"] = ts
json.dump(state, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 3. heartbeat (bm-b lane, epoch MUST be int) ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
free_ram_gb = round(float(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_AVAILPHYS")) / 1e9, 2) if os.name != "nt" else None
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1e9, 2)
    cpu_pct = psutil.cpu_percent(interval=1)
except Exception:
    free_ram_gb, cpu_pct = hb.get("free_ram_gb", 0), hb.get("cpu_pct", 0)
gpu_free = hb.get("gpu_free_vram_gb")
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    gpu_free = round(int(out.stdout.strip().splitlines()[0]) / 1024.0, 2)
except Exception:
    pass
hb.update({
    "last_seen": ts,
    "heartbeat_epoch_utc": epoch,
    "clock_read": ts,
    "current_task": ("r400 read-only degraded round done: S0 28-UU collision (live bm-a r404) -> abort + fallback branch "
                     "machine/bm-b-r400 carries stranded GRID_DUALFACE_P1 runner+pool-ready; CEO O-2210 receipted, T-113 "
                     "claim deferred (invisible-lock hazard, next round claims if open); migration execution segment active "
                     "-> next: new-root first round (E:\\Fluxgroup\\FluxGroup\\quant\\bigmoney) sync + canonical 28-UU resolve + T-113"),
    "cpu_cores": 16,
    "free_ram_gb": free_ram_gb,
    "gpu_free_vram_gb": gpu_free,
    "cpu_util_pct": cpu_pct,
    "round_no": 400,
    "round": 400,
    "loop_round": 400,
    "verdict": ("degraded-healthy: smoke 26/26; WM red=true @23:17:19 = migration task-disable honest signal (GM waiver "
                "O-1612, autofill resumes post enable-all -> grid shard burn self-heals); S0 collision per OS order = "
                "read-only round + fallback branch; orders ack 122/122 (O-2210 added)"),
})
if "O-20260928-2210-bm-a.md" not in hb.get("orders_ack", []):
    hb.setdefault("orders_ack", []).append("O-20260928-2210-bm-a.md")
hb["n_orders_ack"] = len(hb["orders_ack"])
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 4. CODELY.md one memory line (四问门通过: 教训/复用/不复述/单条) ----------
codely_line = (
    f"- [2026-09-28 23:4x] r400 bm-b 坑律（S0 冲突降级轮 playbook·三活实证）：①轮首脱水收口（r398 先例）后 pull --rebase 仍撞="
    "脱水件含可再生 S6 快照面且 origin 已被活机推进→冲突质量放大（28-UU 实测）；活机判据=origin/main HEAD 落龄<10min 且轮次 commit 在推"
    "→S0 禁解成立，S7 收尾正典序列 push 拒→retry 撞→abort→fallback 分支 origin machine/bm-b-r400（D-25-01③ 新 ref 零竞态）承运滞留产物"
    "优于硬等同步；②CEO 即时票在降级轮禁认领：认领 commit 达不到 main=机群不可见锁=反重复风险，天然认领方=持干净通道在飞活机，暂缓事由="
    "物理通道依赖须轮报告留痕；③Fluxgroup 迁移执行段实证三件套=schtasks 已禁+journal waiting 循环+lock 在位→此窗 S7 自愈脚本禁跑（勿双arm）、"
    "水位红牌=迁移暂停诚实信号非违令（GM waiver O-1612）。How to apply：轮首撞 S0 冲突先探 origin HEAD 落龄定活机，活机在飞=降级只读+分支承运，"
    "勿抢无人认领的 CEO 票。\n"
)
cp = os.path.join(ROOT, "CODELY.md")
if os.path.getsize(cp) < 50 * 1024:
    with open(cp, "a", encoding="utf-8") as f:
        f.write(codely_line)

# ---------- 5. inbox MSG -> processed ----------
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260928-2110-bmb-all-t104s2-grid-prereg-freeze.md")
dst_dir = os.path.join(ROOT, "fleet", "inbox", "processed")
os.makedirs(dst_dir, exist_ok=True)
if os.path.exists(src):
    shutil.move(src, os.path.join(dst_dir, os.path.basename(src)))

# ---------- self-verify (R170/R178 epoch-int + R262 clock-T laws) ----------
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"][10], "clock_read must be ISO T-separated"
st2 = json.load(open(sp, encoding="utf-8"))
assert st2["round_no"] == 400
print("CLOSEOUT OK | epoch=%d int | round=400 | orders_ack=%d | free_ram=%s gpu=%s cpu=%s"
      % (hb2["heartbeat_epoch_utc"], hb2["n_orders_ack"], free_ram_gb, gpu_free, cpu_pct))
