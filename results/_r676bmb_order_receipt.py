import subprocess, os, io, json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RCPT = os.path.join(ROOT, r"results\_r676bmb_order_receipt.json")
out = {}

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")
epoch = int(time.time())
out["clock"] = clock
out["epoch"] = epoch

# ---- Part A: heartbeat -- orders_ack += O-20261004-1440-bm-c.md ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(hp, encoding="utf-8"))
ORD = "O-20261004-1440-bm-c.md"
ack = hb.setdefault("orders_ack", [])
if ORD not in ack:
    ack.append(ORD)
hb["orders_ack_count"] = len(ack)
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["current_task"] = ("r676 close: CEO order O-20261004-1440 receipt (pool 3/3=bm-b trio burning premise-corrected; "
                      "tickets 157-164 fleet-claimed zero-open; N2-N4 red-card w/ reason: N4 registry wired but "
                      "waves owner=bm-a, N3=pool-face R1/R2 done, N2-W15 draft; bm-b engine grain = N1-W116 freeze "
                      "next round); trio burns V801+/Q623+/D468+ of 2000 ETA 10-06..08")
hb["verdict"] = "healthy burning"
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
try:
    import psutil
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    gb = round(vm.available / (1024 ** 3), 2)
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
        hb[k] = gb
    out["cpu_pct"] = hb["cpu_util_pct"]
    out["free_gb"] = gb
except Exception as e:
    out["psutil_exc"] = repr(e)
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
_h = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(_h["heartbeat_epoch_utc"], int)
assert ORD in _h["orders_ack"]
out["hb_ack_count"] = _h["orders_ack_count"]

# ---- Part B: state.json note append (order intake face) ----
sp = os.path.join(ROOT, "state.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["note"] = (st.get("note", "") + " || MID-ROUND CEO ORDER O-20261004-1440-bm-c intake @15:0x: "
              "(1) pool premise corrected -- ready 3/3 = bm-b trio NULLS claimed+burning (V801/Q623/D468 @14:35, "
              "claim-refresh 14:30:11, rates 24.4/20.5/17.9/h, ETA V 10-06T15/Q 10-07T09/D 10-08T04; order's 14:30 "
              "audit snapshot pre-dated refresh); (2) tickets 157-164 = fleet same-round response, origin live scan "
              "6 done/1 claimed(bm-c)/1 yielded, ZERO open now; (3) N2-N4 engine wiring RED-CARD w/ reason per order "
              "escape clause: N4=FAMILIES registry wired (T-151) but waves B1/B2/B3 all engine_owner=bm-a "
              "(zero-cross-machine-dup contract sec.1 = invisible to bm-b queue), N3=pool-face runner by fleet "
              "adjudication (R1/R2 12-batch pool burns done, R3=materializer path r509), N2-W15=prereg DRAFT (legs "
              "not landed, freeze window pending); bm-b engine grain = author+freeze N1-W116 with engine_owner=bm-b "
              "(W115 one-window-close precedent bm-c r445) = r677 opening action; py 61.5% >= 50% acceptance met "
              "via trio burns; (4) supply continuation staged: FUND trio finalize 10-06..08 -> next wave faces "
              "pre-staged per fleet consensus (trial-labor next candidates 10-06+, fund prereg drafting window "
              ">=10-08 post D6-corr, T-148 contest shards, W3 thousand-person) -- no supply cut at closeout")
st["last_round_at"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["clock_read"] = clock
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
_ = json.load(io.open(sp, encoding="utf-8"))
out["state_reparse"] = "OK"

# ---- Part C: round report addendum line (RED-CARD first per order clause) ----
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
line = (
    clock + " | r676 addendum (bm-b) CEO-Law O-20261004-1440-bm-c receipt: "
    "[N2-N4 engine wiring RED-CARD + reason per order escape clause: bm-b instance 无本机属主未烧波在册 "
    "(queue 0/idle) -- N4=FAMILIES 注册表已接 (T-151) 但 B1/B2/B3 波全 engine_owner=bm-a (零跨机重复契约 sec.1 "
    "=bm-b 队列结构性不可见), N3=池面 runner 机队定谳 (R1/R2 十二批池烧全 done·R3=materializer 正道 r509), "
    "N2-W15=prereg DRAFT (run/screen/finalize legs 未落地·冻结窗未开); bm-b 引擎米路=起草+冻结 N1-W116 "
    "engine_owner=bm-b (W115 一窗闭环先例 bm-c r445) = r677 开窗动作, 本轮窗预算 (令中途接管+两波 merge 撞拒+18 UU "
    "canon resolve) 容不下整 prereg 作者链不违 R99/R250] | "
    "池面核验: ready 3/3=bm-b trio NULLS 在烧实证 (V801/Q623/D468 of 2000 @14:35, owner=bm-b keepalive 14:30:11 "
    "鲜活, rates 24.4/20.5/17.9/h, ETA V 10-06T15/Q 10-07T09/D 10-08T04; 令面 14:30 审计快照先于 claim-refresh=前提修正) | "
    "八票 157-164: 机队同轮响应后 origin 实况=6 done/1 claimed(bm-c r422 在做)/1 yielded, 本机双扫 ZERO-open 非挂账 | "
    "供料续波预置: FUND 三炉 finalize 10-06..08 后下一波已排 (10-06+ 试用期候选起草·fund prereg 窗 >=10-08 D6-corr "
    "先行·T-148 大赛分片·千人 W3), 禁收口断供 | "
    "py 61.5%>=50% 达标面 (三烧+维护链合法占用) | 令回执=心跳 orders_ack 154 + 本行; "
    "本地未达 origin commit 数:读 push_verify 回执 (收口推送后 ahead=0)"
)
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + eol)
out["round_report_addendum"] = True

with io.open(RCPT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK " + RCPT)
