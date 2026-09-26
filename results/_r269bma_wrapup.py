"""R269 bm-a: S5/S7 wrap-up — round report line + state round_no bump +
heartbeat refresh. Byte faces probed: all three = no BOM / CRLF /
indent=1 / ensure_ascii=False / no trailing newline (round report file
ends WITH newline; state+heartbeat end WITHOUT).
"""
import datetime as dt
import json
import psutil

now = dt.datetime.now()

# ---- S5 round report line (file ends with newline; append one line) ----
line = (
    "2026-09-26 21:4x | R269 (bm-a GM session) | watermark verdict: GREEN "
    "py_low_board_clear（board 0 open·pool 49/49 done·next_pick=MF_IC_P1 "
    "source-blocked=合法 idle 白名单；compute_audit pool_starvation 旗如实披露 "
    "152min ready=0——全线 done/阻断/分析型，O-1137 §二禁造数凑烧适用，09-28 新 "
    "bar 链+grid 首跑窗为下一真实载体） | S0.5 orders 84/84 零差集；集团决策 "
    "D-20260926-05..11 扫毕，涉本仓=D-10 IntradayMarks E2 就此闭口回执（工具面"
    "归 HQ 本司零动作） | S3 T-83 s3 GM 七件套 slice1 落地（件①②④）：firm/"
    "JUDGMENT_MATRIX.md v1.0 判决体系总图（9 判据面路由·薄法指针零阈值复制·三线"
    "三判律成文·s2-D1 SINA_MF 采集道合法裁定）+ firm/ACCOUNT_LIFECYCLE.md v1.0 "
    "账户生命周期正典（五环串明+8 账户族×环覆盖×报告归属表）+ org_chart v6 KPI 刷"
    "新（研究部五线供给面+总经办战报面）；件③⑤⑥⑦ 续作指针入票 progress_r269 | "
    "evidence: post_review 行 T-83-S3-GM-DELIVERABLES 登记（11 检查全锚稳定产物"
    "件）+复审器实跑 YES=30/NO=0/WAIT=5；smoke 25/25 PASS；S6 25 腿 rc=0（周末 "
    "no-op·MF/AH spawn 节流自愈·alloc/fund_premium 车道护栏诚实 no-op·t24 晋升门 "
    "0/22 诚实腿败） | next: O-2000 迁移执行器 v2.1 armed（PID 35344 活·journal "
    "21:23:50 precheck 等 CEO 关 Code.exe；本轮短促配合 drain 自协调）；件③⑤⑥⑦ "
    "GM slice2；MF_IC_P1 待面板源恢复；09-28 新 bar 链\n"
)
with open(r"logs/iteration-loop/round_reports-bm-a.md", "ab") as fh:
    fh.write(line.encode("utf-8"))

# ---- state round_no bump (no trailing newline) ----
p = r"state-bm-a.json"
d = json.load(open(p, encoding="utf-8-sig"))
d["round_no"] = 269
txt = json.dumps(d, ensure_ascii=False, indent=1)
with open(p, "wb") as fh:
    fh.write(txt.encode("utf-8").replace(b"\n", b"\r\n"))

# ---- heartbeat (no trailing newline; epoch int; clock T-separated) ----
p = r"fleet/machines/bm-a.json"
d = json.load(open(p, encoding="utf-8-sig"))
import time
d["last_seen"] = now.strftime("%Y-%m-%d %H:%M")
d["round_no"] = 269
d["current_task"] = ("R269 closed (T-83 s3 GM slice1 件①②④ landed: JUDGMENT_"
                     "MATRIX + ACCOUNT_LIFECYCLE + org_chart v6 KPI refresh); "
                     "migration armed waiting CEO editor close")
vm = psutil.virtual_memory()
d["free_ram_gb"] = round(vm.available / 2**30, 1)
d["cpu_pct"] = psutil.cpu_percent(interval=1)
try:
    import subprocess
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True).stdout.strip()
    free_mb = float(o.splitlines()[0])
    d["gpu_free_vram_gb"] = round(free_mb / 1024, 1)
except Exception:
    pass
d["verdict"] = ("GREEN R269: T-83 s3 GM slice1 (件①②④) delivered+reviewed "
                "YES (30/0/5), smoke 25/25, S6 25 legs rc=0 weekend no-ops, "
                "orders 84/84, board 0 open, pool starvation flag disclosed "
                "as legal idle, migration v2.1 armed PID 35344")
d["heartbeat_epoch_utc"] = int(time.time())
d["clock_read"] = now.astimezone().isoformat()
assert isinstance(d["heartbeat_epoch_utc"], int)
d["task"] = ("R269: s3 slice1 closed; next = GM slice2 (件③ doc-hierarchy / 件⑤ "
             "orders index+supersession / 件⑥ s2 candidates adjudication / 件⑦ "
             "line-status single-source), 09-28 new-bar chain, MF_IC_P1 on panel "
             "recovery, migration receipt assembly post-move")
txt = json.dumps(d, ensure_ascii=False, indent=1)
with open(p, "wb") as fh:
    fh.write(txt.encode("utf-8").replace(b"\n", b"\r\n"))

# post-write self-verification (R170/R178/R262: value+type+format)
d2 = json.load(open(r"fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(d2["heartbeat_epoch_utc"], int)
assert "T" in d2["clock_read"]
d3 = json.load(open(r"state-bm-a.json", encoding="utf-8-sig"))
assert d3["round_no"] == 269
print("wrap-up written: report line + state 269 + heartbeat "
      f"epoch={d2['heartbeat_epoch_utc']} clock={d2['clock_read']}")
