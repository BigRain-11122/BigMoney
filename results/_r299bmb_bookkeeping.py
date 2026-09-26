"""r299 bm-b bookkeeping: heartbeat + state.json + round report line.
Follows r298 pattern (bookkeeping script, write-then-verify).
Epoch int law (R170/R178) + clock_read T-separator law (R262) enforced.
"""
import json
import time
import datetime
import psutil

now_local = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
assert isinstance(epoch, int)

# ---- heartbeat ----
hb = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
vm = psutil.virtual_memory()
cpu_pct = psutil.cpu_percent(interval=0.3)
hb.update({
    "last_seen": now_local,
    "heartbeat_epoch_utc": epoch,
    "clock_read": now_local,
    "current_task": "r299 maintenance round done: T-87 probe#12 on_track 81.2pct ETA 06:41:59 + S6 30/30 rc=0 + S0 autostash-pop autofill_state canonical resolve (bm-a r295 FUSION_GRID_P1 freeze pair integrated)",
    "cpu_cores": psutil.cpu_count(logical=True),
    "cpu_util_pct": cpu_pct,
    "cpu_pct": cpu_pct,
    "free_ram_gb": round(vm.available / 1e9, 1),
    "free_ram_mb": int(vm.available / 1e6),
    "idle_ram_gb": round(vm.available / 1e9, 1),
    "idle_ram_mb": int(vm.available / 1e6),
    "gpu_free_vram_gb": 6.8,
    "gpu_free_vram_mb": 6949,
    "gpu_idle_vram_gb": 6.8,
    "gpu_idle_vram_mb": 6949,
    "total_ram_gb": round(vm.total / 1e9, 1),
    "round_no": 299,
    "round": 299,
    "verdict": "green",
    "n_orders_ack": 91,
})
with open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO (R262)"
print("heartbeat ok: epoch=%d clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))

# ---- state.json ----
st = json.load(open(r"logs\iteration-loop\state.json", encoding="utf-8"))
st.update({
    "round_no": 299,
    "did": "r299 维护轮：S0 pull--rebase autostash pop 1-UU autofill_state(r298 同型第2连)按冻结配方解决(_r299bmb_resolve.py: union |50| 全重叠 cap50/last_tick take-newer 05:20:01/LF 镜像/stash drop/车道件还原 unstaged r290 律)+bm-a r295 对集成(FUSION_GRID_P1 prereg FREEZE+wrap)；S0.5 orders 91/91 双扫零未ack(本地+fetch 远端面)+decisions.md 直扫不可达诚实注记；S1 smoke 25/25；S2 板 32 票全 claimed 零 open+pool entries 0+WM red=false；S3 T-87 probe#12 on_track 81.2%(4243/5228)@12.61/min ETA 06:41:59<窗零形状缺陷+迁移 precheck 注记(cwd-holder pid29440=T-87 刷新进程自证)；S6 30/30 legs rc=0(audit CLEAN/WM py_low_board_clear 合法/regime ORANGE shadow/paper 族幂等 no-op)；S7 inbox T-85 冻结宣告已归档+state/heartbeat 299 epoch int 自证",
    "current_task": "r299 maintenance round (T-87 probe#12 + S6 30/30 + S0 autostash pop canonical resolve)",
    "next": "T-87 完成态探针(ETA 06:41:59 后 gate 自动收尾)；FUSION_GRID_P1 runner/池条目(bm-a)入池后 autofill 自动烧分片(池分片法·勿手碰科学面)；09-28 周一首新 bar 全链；迁移 v2.2 armed editor-gated 窗至 09-29 12:00(勿双 arm)",
    "verdict": "green",
    "last_result": "ok",
    "last_round_ts": now_local,
    "updated_at": now_local,
})
with open(r"logs\iteration-loop\state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk2 = json.load(open(r"logs\iteration-loop\state.json", encoding="utf-8"))
assert chk2["round_no"] == 299
print("state ok: round_no=299")

# ---- round report line ----
line = (
    "%s | r299 bm-b | dept:工程/数据 | WM-VERDICT: 绿 red=false lane healthy; py_low_board_clear 合法闲置(板 0 open 全闭环/pool entries 0/bandit claimed 面); "
    "S0 pull--rebase autostash pop 1-UU autofill_state(r298 同型第2连)->冻结配方 _r299bmb_resolve.py(union |50| 全重叠 cap50/last_tick take-newer 05:20:01/LF 镜像/stash drop/车道件还原 unstaged r290 律)+bm-a r295 对集成(FUSION_GRID_P1 prereg FREEZE T-85 s2/s3); "
    "S0.5 orders 91/91 双扫零未ack(本地+fetch 远端面·decisions.md 直扫不可达诚实注记 R291 面); S1 smoke 25/25; S2 板 32 票全 claimed 零 open+pool 0; "
    "S3 T-87 probe#12 on_track 81.2%%(4243/5228)@12.61/min ETA 06:41:59<窗 header/ohlc 零缺陷(difflib delta=6 仅轮号面)+迁移 precheck 等待注记(cwd-holder pid29440=T-87 刷新进程自证,~06:42 自退,editor 仍拦); "
    "S6 30/30 legs rc=0(_r299bmb_s6_chain.log: audit CLEAN flags=[]/WM py_low_board_clear 合法/regime ORANGE shadow breadth 0.77/astock lock-alive no-op/paper 族幂等 no-op/daily_report faces=4); "
    "S7 inbox MSG-T85-FUSION-GRID-P1 已归档处理(bm-a 冻结宣告零 bm-b 动作,池分片法后继面)+state/heartbeat 299 epoch int 自证 "
    "| 下轮指针: T-87 完成态探针(ETA 后 gate 自动收尾面)+FUSION_GRID_P1 入池后 autofill 自动烧分片+09-28 周一首新 bar 全链+迁移 v2.2 armed editor-gated 窗至 09-29 12:00\n"
) % now_local
with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("report line appended:", line[:80], "...")
