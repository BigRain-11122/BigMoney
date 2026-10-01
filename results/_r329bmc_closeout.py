# r329 bm-c closeout: state + heartbeat + round-report line, EOL/indent preserving.
import json, io, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+08:00" if now.utcoffset().total_seconds() >= 0 else "-08:00")
epoch = int(time.time())
CPU, RAM, GPU = 11.3, 3.1, 11080

def load(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f: return f.read()
def save(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f: f.write(s)

# --- state-bm-c.json ---
sp = ROOT + r"\state-bm-c.json"
raw = load(sp)
crlf = "\r\n" if "\r\n" in raw else "\n"
st = json.loads(raw)
st.update({
    "round_no": 329, "last_round_at": "r329", "last_round_ts": iso, "updated": iso,
    "cpu_pct": CPU, "idle_ram_gb": RAM, "gpu_free_vram_mib": GPU,
    "verify": "r329: U060 zero-window self-fix (Invoke-SilentExe.ps1 helper + loop/satengine/dispatcher schtasks routed + watchdog no-false-success gate + prompt 4-spot & in-process conversion); S6 37/37 rc0; smoke 47/47; engine alive rc0",
    "did": "r328 adoption closeout (crashed session heal+finalize 6efed57b6 already on origin; state/probe-evidence/inbox-move carried this round) + U060 zero-window engineering on the S7 toolchain (5 Tools files + surgical prompt patch, byte-asserted 1-line diff) + S6 chain 37/37 rc0 (holiday no-bar, all lane guards honest)",
    "current_task": "r329 delivered; next = compute_audit claimed-counter fix (r528 family residual false flag) + s2 eighth pick evidence rescan + W19-yield observation before W20 freeze",
    "next": "(r330)(a) compute_audit fleet_open_tasks counter must exclude claimed_by (r528 family residual: 18:51 audit flagged idle_with_work on 1 open+claimed ticket while watermark probe correctly said board-clear; fix + selftest) (b) T-134 s2 eighth pick evidence-order rescan (t33/t36 natural accrual) (c) W20 engine-wave freeze ONLY after bm-b W19 yield disposition lands on origin (r511/r529 band discipline; W17 A=76_001..78_000 finalized K=35,320) (d) month-bound first-exam checklist (10-31: six members + SYSTEM-V1 + REV-OSC + 27 experimental) (e) HQ-FEEDBACK line: S4U-vs-unelevated principal conflict (watchdog register S4U needs elevation; satengine default-principal precedent same day) -- read file header first, then append",
    "heartbeat_epoch_utc": epoch, "clock_read": iso, "last_seen": iso, "last_ts": iso,
    "note": "r329: U060 round; CEO twice-scolded desktop-flash pain -> all session-invoked register scripts now zero-window in ANY host; iteration prompt now mandates & in-process calls; watchdog S4U false-success gate honest since this round; MSG-183x consumed by r328 (move carried), MSG-184x outbound awaiting bm-b W19 yield",
    "last_round": "2026-10-01 r329 bm-c: U060 zero-window self-fix (helper + 3 registers routed + watchdog gate + prompt 4 spots) + r328 adoption + S6 37/37 rc0",
})
save(sp, json.dumps(st, ensure_ascii=False, indent=2).replace("\n", "\r\n" if crlf == "\r\n" else "\n"))
json.loads(load(sp)); print("state OK round_no=%d epoch=%d(int)" % (st["round_no"], st["heartbeat_epoch_utc"]))

# --- fleet/machines/bm-c.json heartbeat ---
hp = ROOT + r"\fleet\machines\bm-c.json"
raw = load(hp)
crlf2 = "\r\n" if "\r\n" in raw else "\n"
hb = json.loads(raw)
hb.update({
    "cpu_util_pct": CPU, "cpu_pct": CPU, "free_ram_gb": RAM, "ram_free_gb": RAM, "idle_ram_gb": RAM,
    "gpu_free_vram_mb": GPU, "gpu_vram_free_mb": GPU, "gpu_idle_vram_mb": GPU, "gpu_idle_vram_mib": GPU, "gpu_free_vram_mib": GPU,
    "cpu_idle_pct": round(100 - CPU, 1),
    "prod_lanes": "r329: U060 zero-window self-fix (Tools/Invoke-SilentExe.ps1 + 3 register scripts routed + watchdog no-false-success gate + prompt 4-spot & conversion) + S6 37/37 rc0",
    "round_no": 329, "updated_at": iso, "last_seen": iso, "last_seen_at": iso,
    "current_task": "round 329 closeout: U060 zero-window self-fix delivered + verified",
    "heartbeat_epoch_utc": epoch, "clock_read": iso, "health": "ok",
    "activity_now": "idle-legal (holiday no-bar, board clear, engine queue drained W17 12/12 finalized); next = compute_audit claimed-counter fix + s2 eighth pick rescan",
    "latest_artifact": "Tools/Invoke-SilentExe.ps1 zero-window helper + patched register_loop/saturation_engine/dispatcher/watchdog scripts + iteration_prompt.txt U060 conversion (2026-10-01T19:1x)",
    "next_milestone": "compute_audit r528-family counter fix + T-134 s2 eighth conversion, window <=48h",
    "verdict": "healthy: U060 zero-window S7 toolchain landed + verified real-run, engine alive rc0, WM py_low_board_clear legal idle (holiday), S6 37/37 rc0, smoke 47/47",
})
save(hp, json.dumps(hb, ensure_ascii=False, indent=2).replace("\n", "\r\n" if crlf2 == "\r\n" else "\n"))
hbk = json.loads(load(hp))
assert isinstance(hbk["heartbeat_epoch_utc"], int) and "T" in hbk["clock_read"], "F7 fields"
print("heartbeat OK epoch int=%d clock=%s" % (hbk["heartbeat_epoch_utc"], hbk["clock_read"]))

# --- round report line ---
rp = ROOT + r"\round_reports-bm-c.md"
raw = load(rp)
eol = "\r\n" if raw.endswith("\r\n") or "\r\n" in raw[-200:] else "\n"
line = (
    iso + "｜r329｜dept:工程（U060 零窗自修·S7 工具链）｜watermark verdict=绿(py_low_board_clear 板全闭环+bandit 空+假日无新 bar·10-01 国庆休市 cutoff 09-30 正常)｜"
    "S0-1 身份锚定 bm-c·S0 HEAD=origin 6efed57b6 0/0 同步·S0.5 令差集=0（139 全 ack·轮首双扫）·D-19 水位 SHA MATCH-unchanged(753F99E8 raw-blob python 法)·S1 smoke 47/47｜"
    "收养面=r328 猝死会话遗产全收编（其 heal+finalize 外科推送已落 origin 6efed57b6：W17 mirror 行恢复+W19 行按 MSG-184x yield 移除+finalize K=35,320 账本 399,748+2,200=401,948·S5 4/4 PASS·selftests 8/8+36/36 绿——本轮补齐其未落账面：state/轮报告/心跳/探针证物 4 件+MSG-183x inbox move·r322 悬空引用核验=MSG-184x 已在 origin 在场零悬空）｜"
    "主产出=U060 零窗自修五件套（CEO 10-01 两申斥弹窗的工程根治面）：①Tools/Invoke-SilentExe.ps1 新建=CreateNoWindow 原生 exe 通用助手（stdout-only 默认保存在性真值语义+rc 传播+进程内 & 调用）②register_loop/saturation_engine/dispatcher 三脚本裸 schtasks→助手路由（R49 schtasks 存在性正典保持·零语义变更）③register_watchdog_task.ps1 假成功打印根治（S4U 未提权 0x80070005=Register-ScheduledTask 失败后仍打成功行——satengine 头注同族坑·-ErrorAction Stop 诚实化·现有健康任务零触碰）④iteration_prompt.txt 四处 powershell -File 外壳调用→& 进程内（satengine/loop/watchdog/claw·canon 行补零窗包装注记·字节级补丁 1 行外科 diff·EOL 保真 assert 全过）｜"
    "验证=真跑四面（r494 真跑律）：helper 双态探针（存在 rc0 真值/缺任务 rc1 空）+三脚本真跑全 no-op 分支（loop phase ok pin=5·satengine/dispatcher task present no-op）+watchdog 失败复现诚实化+claw 重装 LF 归一+S6 全链 37/37 rc0（批 A 7+批 B 16+批 C 14·reconcile ZERO-DRIFT streak 15·假日车道护栏 no-op 全诚实）｜"
    "诚实发现两条：①compute_audit 18:51 报 idle_with_work+pool_starvation+supply_floor 三旗但其 fleet_open_tasks=1 计 T-141 open+claimed_by 未排=r528 族残留假红面（py_watermark 已修侧正确报 board-clear·watermark verdict 以 probe 为准=绿·r330 修 compute_audit 计数器+selftest）②watchdog 任务 2-min 节奏但 next run 19:20/日志尾 18:50（任务在场 Ready·C1-C7 18:50 pass 全绿·10-min ExecutionTimeLimit 自愈设计内·下轮观察）｜"
    "实况三行（CEO 过程可见面）：当前活=U060 零窗自修已落地·S7 工具链全机零闪窗就绪｜最近实物=Tools/Invoke-SilentExe.ps1+四 register 脚本+prompt 补丁（随轮 commit 上 origin·2026-10-01T19:1x）｜下个里程碑=compute_audit 假红根治+s2 第八件转换（窗 ≤48h）｜产品分=2（可跑零窗工具链+真跑验证产物）｜坑律新增=0（本窗坑均已知律复发·r495 数组传参自纠未入册）｜本地未达 origin commit 数=0（收尾 push+fetch 送达自证）｜"
    "next: (r330)(a) compute_audit claimed 计数器修复（r528 族·live 证据 18:51）(b) T-134 s2 第八件 evidence-order rescan（t33/t36 自然 accrue）(c) W20 冻结等 bm-b W19 yield 落 origin 后（r511/r529 带律·W17 A 带 76_001..78_000 已 finalize）(d) 月界首考清单（10-31）(e) HQ-FEEDBACK S4U-vs-未提权 principal 法面冲突行（先读文件头再 append）"
)
if not raw.endswith(("\n", "\r\n")): raw += eol
save(rp, raw + line + eol)
print("round report line appended, len=%d, eol=%r" % (len(line), eol))
