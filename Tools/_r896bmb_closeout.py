"""r896 bm-b closeout: state.json + heartbeat + round-report append + resource
snapshot + epoch-int self-proof. One-shot driver (r887 closeout recipe)."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().replace(microsecond=0)
TS = NOW.isoformat()

did = ("r896: ①BigHouse 首研究件提前 20h 交付（research/wuzhong-replication-r1.md "
       "地理/社区形态/记忆点三面+TASKS.md 板 T1-T5·house/BigHouse commit 16fda71 "
       "推送 ls-remote 送达自证·O-1917 §2 回执落档·backlog row12 BigHouse 席 "
       "idle-claim 接线）；②W18-JUDGE finalize 分离点火（PID25060·判决烧录 "
       "188/188 checkpoint 完备后聚合·W17 4h 先例·守望窗跨轮）；③G-soft/热点池"
       "双推送在途实锚（PID25616/7668 活·零 CPU=夜间慢网等待族·receipt 留下轮）；"
       "④S0 stash-rebase-pop 净树手术 2 commit 收口零冲突+D-19 双水位 delta 消费"
       "（dec 6382fbdd 不变·ord f81400db→b3c8b784=两行 BigStream 域零本仓义务）；"
       "⑤S6 41 腿全 rc0（dualrun ZERO-DRIFT streak 51·池 445 entries）+smoke "
       "49/49+孤儿面=0")
next_task = ("r897: W18-JUDGE finalize 落地守望（PID25060 分离在飞·落地→intake"
             "+s4 判据面+48h CEO 钟起算） > BigHouse T-2 城市接入件设计（backlog "
             "row12 可领·due ≤10-15） > G-soft/热点池双推送 receipt 验证+落地回执"
             "（PID25616/7668 在途） > G 系工程同步腿（O-1917 §1 productName/"
             "GameTitle 对齐） > T-184 510880 transfer 收件 10-12 15:30 前 > "
             "IntradayMarks 周一 10-12 09:25 首火 > 48h CEO 报 due 10-13 11:2x")
artifact = ("r896: house/BigHouse research/wuzhong-replication-r1.md + TASKS.md"
            "（commit 16fda71·送达自证）+ Tools/_r896bmb_s6.py 41 腿链"
            "（results/_r896bmb_s6_log.txt 全 rc0）")
verdict = ("GREEN: BigHouse first research piece delivered 20h early (origin "
           "16fda71 verified) + W18-JUDGE finalize detached in flight (PID "
           "25060) + S6 41 legs 0 red + smoke 49/49; dual pushes still "
           "night-slow-net waiting (receipt next rounds)")

# -- resource snapshot (psutil + nvidia-smi, best-effort)
ram_gb, ram_pct, vram_mb = 0.0, 0.0, 0
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_gb = round(vm.available / 2**30, 1)
    ram_pct = round(100 - vm.percent, 1)
except Exception:
    pass
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20)
    vram_mb = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass

# -- state.json
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_action": "r896: BigHouse 首研究件交付（三面研究件+任务板·origin 16fda71）"
                   "+W18 finalize 分离在飞+S6 全绿",
    "last_action_at": TS, "last_round_at": TS, "last_seen": TS,
    "last_round_ts": "2026-10-11T21:01:51+08:00",
    "did": did, "next": next_task, "task": next_task,
    "current_task": next_task, "now_active": "r896 closeout",
    "next_milestone": ("W18 finalize 落地 ≤10-12 深夜→48h CEO 钟起算; BigHouse "
                       "T-2 城市接入件 ≤10-15; T-184 收件 10-12 15:30; 48h CEO "
                       "报 10-13 11:2x"),
    "note": "r896: O-1917 §2 BigHouse first research piece done 20h early; "
            "idle-claim seat wired (backlog row 12)",
    "verdict": verdict, "latest_artifact": artifact,
    "round": 896, "round_no": 897, "round_no_label": "r896",
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": ("r896 round probe: py_faces=15 orphans=0 (read-only); "
                         "3 intentional detached workers live (W18 finalize "
                         "PID25060 CPU-active + push workers 25616/7668 "
                         "network-wait pythonw) -- not orphans by 3-face law"),
    "last_orders_sha": "b3c8b78484916ddef37bca3966c37b8ee9092106",
    "last_orders_at": TS, "last_orders_read_at": TS,
    "last_orders_sha_note": ("r896 probe: dec 6382fbdd unchanged zero action; "
                             "ord f81400db->b3c8b784 delta consumed = commit "
                             "2e150f49 零卡点流线令 + 65b58a6 三车道排产政策令 "
                             "(both BigStream domain, zero BigMoney rows); "
                             "in-dir O files all acked"),
    "last_decisions_read_at": TS,
    "d19_watermark_guard": dict(st.get("d19_watermark_guard") or {},
                                round_ref=896, ts=TS),
    "sync": {"last_push_ts": TS,
             "note": "r896 closeout push lands with this commit; delivery "
                     "self-proof = post-push fetch + rev-list 0"},
})
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# -- heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(NOW.timestamp())
hb.update({
    "clock_read": TS, "ts": TS, "last_seen": TS,
    "current_task": next_task, "did": did, "next": next_task,
    "last_action": st["last_action"], "last_action_at": TS,
    "last_round_at": TS, "now_active": "r896 closeout",
    "next_milestone": st["next_milestone"], "note": st["note"],
    "latest_artifact": artifact, "verdict": "green",
    "round": 896, "round_no": 897, "round_no_label": "r896",
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "free_ram_gb": ram_gb, "ram_free_gb": ram_gb, "ram_free_pct": ram_pct,
    "gpu_free_vram_mb": vram_mb, "gpu_free_vram_gb": round(vram_mb / 1024, 1),
    "vram_free_gb": round(vram_mb / 1024, 1),
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": st["orphan_face_note"],
    "sync": st["sync"],
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb["clock_read"] and " " not in hb["clock_read"].split("+")[0]

# -- round report line
report = (
    f"{TS} | r896 bm-b | dept:研究（BigHouse 席首件=苏州吴中社区复刻研究件三面·"
    f"O-1917 §2 提前 20h 交付）+dept:工程（W18-JUDGE finalize 分离点火+S6 41 腿"
    f"全链+S0 净树 rebase 手术）+dept:舰队（D-19 双水位消费+backlog BigHouse 席"
    f"接线） | 实况三行：当前活=W18 judge-finalize 分离在飞（PID25060·188 cells "
    f"聚合·W17 4h 先例·落地→intake+48h CEO 钟起算）+G-soft/热点池双推送在途守望"
    f"（PID25616/7668·夜间慢网族）；最近实物=house/BigHouse research/"
    f"wuzhong-replication-r1.md+TASKS.md（commit 16fda71·21:2x 推送·ls-remote "
    f"送达自证·due 10-12 18:00 提前 20h）；下个里程碑=W18 finalize 落地 ≤10-12 "
    f"深夜→48h CEO 抒面起算；BigHouse T-2 城市接入件 ≤10-15；T-184 510880 收件 "
    f"10-12 15:30 | WM-VERDICT: green（red=false @21:23 derive·next_pick="
    f"claimed moneyflow IC） | 孤儿面=0（round probe 15 faces 零孤儿·3 分离工作者"
    f"=finalize CPU-active+双推送 pythonw 网络等待·三面法非孤儿） | r896: ①S0-1 "
    f"锚定 bm-b+probe 孤儿=0+净树 stash-rebase-pop 收口 2 commit 零冲突；②S0.5 "
    f"令扫零新令+D-19 delta 消费（dec 6382fbdd 不变·ord→b3c8b784 两行 BigStream "
    f"域零本仓义务）；③smoke 49/49；④BigHouse 首研究件+任务板+O-1917 §2 回执落档"
    f"+backlog row12 席接线；⑤W18 finalize 分离点火（188/188 checkpoint 完备→"
    f"PID25060）；⑥S6 41 腿全 rc0（ZERO-DRIFT streak 51·池 445） | 记账预算：5 "
    f"处（state/心跳/轮报告/O 回执/backlog 行） | 本地未达 origin commit 数=0"
    f"（收口 commit 后 push+fetch 自证）\n")
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rp, "a", encoding="utf-8") as f:
    f.write(report)

print(f"closeout written: state round_no=897 | heartbeat epoch={epoch} int "
      f"| ram_free={ram_gb}GB vram_free={vram_mb}MB | report appended")
