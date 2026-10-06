# -*- coding: utf-8 -*-
"""r773 CEO-order O-20261006-1207 execution package: D-19 watermark update +
task ticket T-2026-10-06-173 open+claim + heartbeat orders_ack + CODELY line +
round-report addendum."""
import hashlib
import json
import subprocess
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
CREAT = 0x08000000
now_iso = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def blob_sha(path):
    out = subprocess.run(["git", "-C", GRP, "show", f"origin/main:{path}"],
                          capture_output=True, creationflags=CREAT).stdout
    return hashlib.sha256(out).hexdigest()

dec_sha = blob_sha("docs/decisions.md")
ord_sha = blob_sha("docs/orders.md")
assert dec_sha.startswith("a44c39e0") and ord_sha.startswith("30155db5"), (dec_sha, ord_sha)

# --- state watermarks ----------------------------------------------------------
s = json.load(open("state-bm-a.json", encoding="utf-8"))
s["last_decisions_sha"] = dec_sha
s["last_orders_sha"] = ord_sha
s["last_decisions_at"] = now_iso
s["last_orders_at"] = now_iso
json.dump(s, open("state-bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
print("watermarks: dec", dec_sha[:8], "ord", ord_sha[:8])

# --- task ticket T-2026-10-06-173 (CEO direct order, immediate) ----------------
ticket = {
    "id": "T-2026-10-06-173",
    "priority": "P1",
    "type": "theme-deepening-research-batch",
    "immediate": True,
    "spec": ("CEO direct order O-20261006-1207 (addendum to O-20261001-2103/2106; "
             "canonical group-repo row d1b52cf; local copy fleet/orders/O-20261006-1207-bm-a.md). "
             "THREE FACES, honest-law full enforcement (D-41 s1.3 full start-point "
             "distribution / s1.4 trial counting + luck correction / single-start "
             "conclusions invalid / folk sayings numerified first): (1) 引入溯源面 -- "
             "16-event library expansion + per-event introduction-mechanism taxonomy "
             "(overseas-mapping[ChatGPT->AI] / policy-driven[一带一路/中特估/国企改革] / "
             "industry-cycle[新能源/涨价] / native-tech[DeepSeek] / event-catalyzed), "
             "cross-measure introduction-type x persistence, R1 '国外发酵非必要' refined "
             "per-type not overturned; (2) 散户最优波面 -- 43-wave-segment library, "
             "per-wave-position (first/second/third+) retail-executable follow rules with "
             "real numbers: entry = wave-start real-time-determinable line (+20% break-line "
             "family), exit = wave-end determination line, cost x2, T+1, FULL START-POINT "
             "DISTRIBUTION, pre-registered frozen criteria; wave-position x follow-rule = "
             "falsifiable hypothesis; negative verdict closes THAT wave position only "
             "('不能一棒子打死' enforcement: every position judged independently, negatives "
             "reported positives kept); (3) 配合面 -- theme heat / wave signals vs registered "
             "book via two paths: core-book position gate (theme ebb de-risk, regime gate C1 "
             "theme leg) + risk on/off overlay; both via prereg, ETF universe frozen per law, "
             "no self-expansion. DELIVERABLE: 《题材引入机制与散户最优波》 plain-language "
             "numbers report, 48h first version from order issue (12:07 -> due 10-08 ~12:00), "
             "positive AND negative columns both reported."),
    "status": "claimed",
    "claimed_by": "bm-a",
    "claimed_at": now_iso,
    "created_by": ("bm-a (OS iteration loop r773; CEO order intake via the r773 closeout "
                   "merge absorb a0e34658b; same-round open+claim per O-20260924-1730 "
                   "immediate law)"),
    "progress": ("r773 bm-a: INTAKE + CLAIM same round (order landed 12:07 via bm-a GM "
                 "session, local registry copy absorbed by the r773 merge). Next steps: "
                 "(a) prereg drafting from research/PREREG_TEMPLATE.md for BOTH faces with "
                 "the 16-event + 43-wave-segment libraries ENUMERATED DATA-GROUNDED (dates/"
                 "instruments per verified sources, folk sayings numerified first, no "
                 "memory-cited references -- 1512.01602 lesson); (b) D6 mechanism-section "
                 "alpha-face choice + same-family correlation gate (max|corr|>=0.7 reject); "
                 "(c) batch execution via the pool/engine lane per O-20260924-2100 "
                 "execution-face separation; (d) 48h report first version by 10-08 ~12:00. "
                 "Scheduling note: W158 freeze window (never-dry engine line) proceeds in "
                 "parallel next tick; this ticket owns the research-batch lane."),
    "result_ref": None,
}
json.dump(ticket, open("fleet/tasks/T-2026-10-06-173-P1.json", "w", encoding="utf-8",
                       newline="\n"), ensure_ascii=False, indent=1)
print("ticket T-2026-10-06-173 opened + claimed")

# --- heartbeat orders_ack ------------------------------------------------------
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
ack = h.get("orders_ack", [])
assert "O-20261006-1207-bm-a.md" not in ack
ack.append("O-20261006-1207-bm-a.md")
h["orders_ack"] = ack
h["current_task"] = ("O-20261006-1207 theme-deepening batch claimed (T-2026-10-06-173, 48h "
                     "report due 10-08 noon) + W158 freeze window queued next tick")
json.dump(h, open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
h2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert "O-20261006-1207-bm-a.md" in h2["orders_ack"]
print("heartbeat orders_ack += O-20261006-1207-bm-a.md")

# --- CODELY execution record (one line) ----------------------------------------
LINE = ("- [2026-10-06 12:1x r773 bm-a] O-20261006-1207 题材深化批令执行记录（CEO 直令·O-20261001-2103/2106 "
        "追加·正典 d1b52cf·本仓副本经 r773 closeout merge 吸收 a0e34658b）：同窗认领=T-2026-10-06-173-P1 票 "
        "opened+claimed（immediate·三面=引入溯源 16 事件分类学×持续性/散户最优波 43 波段逐位全起点分布/配合面 "
        "两配径预注册）·D-41 §1.3/1.4 诚实律全执法·交付=48h 首版白话数字报告（due 10-08 午·正负双列）·"
        "D-19 双水位更新 dec a44c39e0/ord 30155db5（消费定性：dec 零新行动=集团分卷/核销批·ord 一件涉本司即本令）。")
c = open("CODELY.md", encoding="utf-8").read()
anchor = "### Feedback\n"
i = c.find(anchor)
j = c.find("\n", i) + 1
c2 = c[:j] + LINE + "\n" + c[j:]
open("CODELY.md", "w", encoding="utf-8", newline="\n").write(c2)
assert LINE in open("CODELY.md", encoding="utf-8").read()
print("CODELY order-execution line appended,", len(LINE), "bytes")

# --- round-report addendum -----------------------------------------------------
import io
RR = "round_reports-bm-a.md"
ADD = (f"\n2026-10-06T{now_iso[11:16]}+08:00 | round 773 addendum (bm-a, dept:研究·O-20261006-1207 "
       "题材深化批令同窗认领) | [watermark verdict: 绿（red=false）] | 做了什么: CEO 直令 O-20261006-1207 "
       "（引入溯源 16 事件分类学+散户最优波 43 波段逐位+配合面两配径·48h 首版报告 due 10-08 午·正负双列）经 "
       "closeout merge 吸收后同窗开票认领 T-2026-10-06-173-P1（immediate·same-round open+claim per "
       "O-20260924-1730）·下一步=PREREG_TEMPLATE 起草双面预注册+事件/波段库数据锚定枚举（folk 先数值化·"
       "1512.01602 记忆引用教训）+D6 同族相关性门；D-19 双水位更新（dec a44c39e0 零新行动=集团分卷/核销批19·"
       "ord 30155db5 一件涉本司=本令）·heartbeat orders_ack 已加本令 | verify: fleet/tasks/"
       "T-2026-10-06-173-P1.json + state-bm-a.json 水位键 + orders_ack 枚举 | 下轮指针: r774 = (a) W158 "
       "冻结窗四件套（席位/门/xform 已备）→ 双 selftest → 冻结 commit+push → 引擎点火；(b) T-173 预注册起草 "
       "开动（双面+两库枚举数据锚定）；(c) 10-07 12:00 wrapper Step1 回执窗+D-06 收口窗\n")
rr = io.open(RR, encoding="utf-8").read()
io.open(RR, "w", encoding="utf-8", newline="\n").write(rr.rstrip("\n") + "\n" + ADD.lstrip("\n"))
print("round 773 addendum appended")
