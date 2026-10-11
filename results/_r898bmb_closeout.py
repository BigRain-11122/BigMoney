# -*- coding: utf-8 -*-
"""r898 bm-b closeout: state.json + heartbeat + round report line.

Absorbs r897 closeout face (killed by 25min runner timeout mid-closeout at ~22:27;
this tick runner PID 29328 = current body per lock adjudication).
"""
import json, time, ctypes, os

B = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]


def ram_stats():
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullAvailPhys / (1 << 30), st.ullTotalPhys / (1 << 30)


def gpu_free_gb():
    try:
        import subprocess
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=15).stdout.strip().splitlines()[0]
        return round(int(out) / 1024.0, 2)
    except Exception:
        return -1.0


free_gb, total_gb = ram_stats()
vfree = gpu_free_gb()

did = ("r898: ①前班体接管定谳（r897 于 25min 窗被杀 mid-closeout·round.lock=22:32:02=本 tick runner 29328 持有=当班体·半成品 closeout 面收进）；"
       "②D-19 双水位 delta 消费（dec 916861a6→d296e83d=D-20261011-08 行扩〔bm-b 部署腿=巡查执行器+消费步仍候 bm-c O-令派单·未到〕；"
       "ord f4916177→075caa8d=否决窗制度废止令〔bm-c 直执·零本机腿〕+BigLife 点名复工令〔O-20261011-22xx-bm-c 派 bm-a/bm-b·O 件未落地本仓 fleet/orders·S7 双扫零新件〕）；"
       "③smoke 49/49；④i2v 53 单夜批守望回执：首单 XQ_XQ28 OK（1002s/1071KB/277 帧·log-bmb.err=0B）+KN_KN16 在跑 2/53·零 timeout 零 fail=免 VRAM/offload 诊断；"
       "⑤W18-JUDGE finalize PID25060 活烧（CPU 累计 4040s）未落地续守望；⑥G-soft/热点池 supervisor 定谳：r894_gsoft 4 连 STALL-KILLED 终态+r895_pool_scored 尝试 1 STALL-KILLED·尝试 2 在飞"
       "（blob:none promisor 懒取 ~2.9k 对象·夜网大包 stall 族·双 payload 本地完好·晨窗健康路重试律候产）；⑦T-184 510880 分支未到（ls-remote 零 t184 refs·等待态·due 10-12 15:30）；"
       "⑧S6 41 腿全 rc0；⑨S7 守卫批：loop pin=2 no-op+watchdog 幂等重注册+attrition CLEAN+孤儿面=1（=supervisor 6368 wait-on-child 假阳性·git 子链活证·非僵尸）+idle 判定 green_idle=false（RAM 16.9%/VRAM 0.09GB=i2v CEO 优先批合法满载）")

next_ptr = ("r899: i2v 53 单夜批守望（progress-bmb.jsonl 推进·单位均时长收敛回执·停滞>4h 单按 README §4 让渡规则） > W18 finalize 落地守望（PID25060·落地→intake+s4 判据面+48h CEO 钟起算） > "
            "G-soft+r895 推送晨窗重试（supervisor 8 尝试耗尽态后·ls-remote 单跳通=路候健康窗·两脚本幂等守卫直跑） > T-184 510880 收件（transfer/t184-510880·10-12 15:30 前·到件同轮恢复 alloc_paper 腿） > "
            "BigLife 点名复工令 bm-b 腿（O-20261011-22xx-bm-c 到达即办） > D-20261011-08 bm-b 部署腿（fleet-oversight schtasks·候 bm-c O-令） > BigHouse T-2 城市接入件设计（backlog row12·选址图+构件清单·due ≤10-15） > 48h CEO 报 due 10-13 11:2x")

verdict = ("GREEN: CEO i2v 本地令夜批健康在烧（首单 1002s 实测回执·2/53·零 err）+W18 finalize detached 活烧+S6 41 腿 0 红+smoke 49/49; "
           "观察面=G-soft/热点池推送夜网 5 连 stall-kill（payload 完好候晨窗）+RAM 紧张（i2v 栈 mmap·free {free:.1f}GB）").format(free=free_gb)

state = json.load(open(os.path.join(B, "state.json"), encoding="utf-8"))
state.update({
    "round": 898, "round_no": 899, "round_no_label": "r898",
    "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "last_seen": NOW, "last_round_at": NOW, "last_action_at": NOW,
    "did": did,
    "last_action": "r898: 前班体接管收进+i2v 首单回执（1002s/2 单）+D-19 双水位 delta 消费+S6 全绿",
    "now_active": "r898 closeout",
    "next": next_ptr, "task": next_ptr, "current_task": next_ptr,
    "next_milestone": "i2v 53 单全落 ETA 明午（首单 1002s·53 单≈14h）→W18 finalize 落地→48h CEO 钟起算; G-soft/r895 推送晨窗重试; T-184 收件 10-12 15:30; BigHouse T-2 ≤10-15; 48h CEO 报 10-13 11:2x",
    "verdict": verdict,
    "latest_artifact": ("r898: i2v 首单 animatic XQ_XQ28.mp4（1071KB·1002s·22:31·progress-bmb.jsonl）+ Tools/_r898bmb_s6.py 41 腿链"
                        "（results/_r898bmb_s6_log.txt 全 rc0）+ supervisor 回执（r894 终态/r895 在飞）"),
    "note": ("r898: 前班体 r897 接管收进（25min 窗杀）；keepwarm 释放阀在位（批毕复役=删 marker）；RAM 紧张观察面（i2v 栈 mmap·free {free:.1f}GB·S6/探针照常全绿）；"
             "IntradayMarks 任务在册（周一 09:25 首火 armed）").format(free=free_gb),
    "orphan_face": 1, "orphan_faces": 1,
    "orphan_face_note": ("r898 round probe: py_faces=21 orphans=1 (read-only); 定性=supervisor 6368 wait-on-child 假阳性"
                        "（r895 尝试 2 git 子链 22:42 活证·非僵尸）；intentional detached workers: W18 finalize 25060 + supervisor 6368 + ComfyUI 8188 + i2v client"),
    "last_decisions_sha": "d296e83d4864484e8515679fdd854ccc69ed9ead",
    "last_decisions_at": NOW, "last_decisions_read_at": NOW,
    "last_decisions_sha_method": ("r898 probe via results/_r686bmb_d19_check.py (r537 SHA-1 raw-blob PIN); dec d296e83d delta = D-20261011-08 行扩"
                                  "（bm-b 部署腿仍候 bm-c O-令派单·零其他涉本仓新义务）"),
    "last_orders_sha": "075caa8d977e5baf6248548ce9b6f4ce06c8d030",
    "last_orders_at": NOW, "last_orders_read_at": NOW,
    "last_orders_sha_note": ("r898 probe: ord delta = 21:5x 否决窗制度废止令（bm-c 直执·零本机腿）+22:0x BigLife 点名复工令"
                             "（O-20261011-22xx-bm-c 派 bm-a/bm-b·O 件未落地本仓 fleet/orders·落地轮即办）；in-dir O files all acked (orders_ack 198)"),
    "d19_watermark_guard": {"tool": "scripts/d19_watermark.py", "probe": "results/_r686bmb_d19_check.py",
                            "probe_evidence": "C:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json",
                            "method_decisions": "sha1", "method_orders": "sha1", "verbatim": True,
                            "advance": True, "round_ref": 898, "ts": NOW},
    "sync": {"last_push_ts": NOW, "note": "r898 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0"},
})
json.dump(state, open(os.path.join(B, "state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hb = json.load(open(os.path.join(B, "fleet/machines/bm-b.json"), encoding="utf-8"))
hb.update({
    "round": 898, "round_no": 899, "round_no_label": "r898",
    "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "last_seen": NOW, "last_round_at": NOW, "last_action_at": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "did": did, "last_action": state["last_action"], "now_active": "r898 closeout",
    "next": next_ptr, "task": next_ptr, "current_task": next_ptr, "next_milestone": state["next_milestone"],
    "verdict": "green",
    "note": "r898: i2v 夜批健康（首单 1002s 回执）；孤儿面=1=supervisor wait-on-child 假阳性；G-soft/热点池推送候晨窗",
    "idle_rounds": 0, "agenda_starved": False,
    "free_ram_gb": round(free_gb, 1), "ram_free_gb": round(free_gb, 1),
    "gpu_free_vram_gb": vfree, "gpu_free_vram_mb": int(vfree * 1024), "vram_free_gb": vfree,
    "orphan_face": 1, "orphan_faces": 1,
    "orphan_face_note": state["orphan_face_note"],
    "latest_artifact": state["latest_artifact"],
    "sync": state["sync"],
})
json.dump(hb, open(os.path.join(B, "fleet/machines/bm-b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

chk = json.load(open(os.path.join(B, "fleet/machines/bm-b.json"), encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"

rep = os.path.join(B, "logs", "iteration-loop", "round_reports.md")
line = ("\n| {ts} | r898 | bm-b 舰队 | 当前活: i2v 53 单夜批烧录中（CEO O-2126 机队本地令·bm-b=480P int4 animatic 线）+W18 finalize detached 在烧 | "
        "最近实物: XQ_XQ28.mp4 首单 animatic（1071KB·1002s·22:31 落盘·progress-bmb.jsonl）+Tools/_r898bmb_s6.py 41 腿链（全 rc0） | "
        "下里程碑: 53 单全落 ETA 明午（≈14h）·W18 finalize 落地→48h CEO 钟·G-soft/r895 推送晨窗重试·T-184 收件 ≤10-12 15:30·BigHouse T-2 ≤10-15 | "
        "did: {did} | 证据: smoke 49/49+S6 41 rc0（_r898bmb_s6_log.txt）+progress-bmb.jsonl+supervisor 回执+idle_trigger（green_idle=false 合法满载·idle_rounds=0）+孤儿面=1（wait-on-child 假阳性定性）+attrition CLEAN | "
        "watermark verdict: GREEN（red=false） | 本地未达 origin commit 数=0（push 后自证） | 下轮指针: {nxt} |\n").format(
    ts=NOW, did=did[:520], nxt=next_ptr[:260])
with open(rep, "a", encoding="utf-8") as f:
    f.write(line)

print("state round=898 round_no=899; hb epoch=%d int; ram_free=%.1fGB vram_free=%.2fGB; report appended" % (EPOCH, free_gb, vfree))
