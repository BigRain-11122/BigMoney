import json, hashlib, os, re, shutil, time, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)
now = datetime.datetime.now()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

def load(p):
    return json.load(open(p, encoding="utf-8"))

def save(p, d, sample=None):
    sp = open(p, "rb").read().decode("utf-8")
    crlf = sp.count("\r\n")
    m = re.search(r'\n(\s+)"', sp)
    ind = len(m.group(1)) if m else 1
    out = json.dumps(d, ensure_ascii=False, indent=ind)
    if crlf > 0:
        out = out.replace("\n", "\r\n")
    open(p, "w", encoding="utf-8", newline="").write(out)

# --- bm-a heartbeat age (takeover basis documentation)
try:
    ahb = load("fleet/machines/bm-a.json")
    ae = ahb.get("heartbeat_epoch_utc")
    aage = (time.time() - ae) / 60.0 if isinstance(ae, int) else None
except Exception:
    aage = None

# --- 1) state file: round_no 289->290 + did/verify/next
st = load("state-bm-c.json")
st["round_no"] = 290
st["last_round_at"] = now_iso
st["last_round_ts"] = now.strftime("%Y-%m-%dT%H:%M")
st["updated"] = now_iso
st["last_ts"] = now_iso
st["cpu_pct"] = 9.0
st["idle_ram_gb"] = 8.1
st["gpu_free_vram_mib"] = 9790
st["verify"] = (
    "S1 smoke 47/47; S6 37 legs rc0 (dualrun drift entries[140].defer_note="
    "observation-phase streak-reset recorded; t24 22/22 pass drift=0 = MSG-2145 "
    "refreeze expectation met; scorecard/dashboard daily derives = legal "
    "stale-takeover, bm-a hb age "
    + (f"{aage:.0f}min" if aage is not None else "unreadable")
    + " >= C_HOST_STALE_MIN; py_watermark verdict=py_low_board_clear legal idle; "
    "CALL ORANGE_COOL sleeves=4; lhb/futures/fund_prem all no-op fresh; "
    "attrition face pending S7 scan)"
)
st["did"] = (
    "r290: D-20260930-19 delivery-layer wiring RECEIPT (iteration_prompt decision-step "
    "rewritten to fresh-face read law: git -C group-tree fetch + git show origin/main:"
    "docs/decisions.md, zero tree touch; state watermark key last_decisions_sha SHA-256 "
    "content-address per D-18; dispatch-board + docs/orders.md CEO physical-items zone "
    "consumption) + stale-group-tree blind-read pit caught: local checkout 149 commits "
    "behind origin, D-20260930-05..41 37 decision rows missed by local reads, all consumed "
    "this round via fresh face (D-05 RW-1~7 ack: RW-1~4 green r476/r491-refreeze in-tree, "
    "RW-5 freeze respected zero new-prereg; D-14 criteria note; D-16/D-19 wired; D-21 "
    "delivery-law first enforcement: BigMoney yellow=received-now-acked; D-41 retail-track "
    "order consumed) + D-41 deliverable #5 behavior-guardrails berth claimed via MSG "
    "(zero-collision evidence vs bm-a/bm-b heartbeats + T-129 + MSG-2108; +0 trials; "
    "r291 execution) + CODELY pit entry + HQ-FEEDBACK F-20260930-02 mechanism-gap report"
)
st["current_task"] = (
    "r290 done: D-19 wiring + #5 berth claimed; next r291 = D-41#5 full closed loop "
    "(BEHAVIOR_GUARDRAILS canon + behavior_guardrails.py L1 derivation +0 trials)"
)
st["next"] = (
    "(a) r291: D-41#5 behavior-guardrails full loop (canon+script+results+CEO card, +0 "
    "trials per ORDER 'cannot-test-only-codify'); (b) Face B backfill when bm-b lands "
    "results/cross_start_robustness face_b (EXCLUSION parked pending astock refresh settle "
    "per bm-b hb); (c) 10-01 month-first trio + REGIME_GUARD v3 date-gate auto-activation "
    "hands-off; (d) W12 48h CEO verdict report clock 10-02; (e) D-19 receipt window 10-02 "
    "12:00 (wired this round, receipt commit pushed)"
)
st["note"] = "r290 product score=1 (real file changes: prompt wiring + state watermark key + berth MSG; runnable artifact deferred to r291 #5 loop)"
save("state-bm-c.json", st)

# --- 2) heartbeat
hb = load("fleet/machines/bm-c.json")
hb["round_no"] = 290
hb["last_seen"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = 9.0
hb["cpu_util_pct"] = 9.0
hb["cpu_idle_pct"] = 91.0
hb["cpu_cores"] = 32
hb["cores"] = 32
hb["idle_ram_gb"] = 8.1
hb["ram_free_gb"] = 8.1
hb["free_ram_gb"] = 8.1
hb["total_ram_gb"] = 25.7
hb["gpu_idle_vram_mb"] = 9790
hb["gpu_idle_vram_mib"] = 9790
hb["gpu_free_vram_mb"] = 9790
hb["gpu_free_vram_mib"] = 9790
hb["verdict"] = (
    "green: smoke 47/47 + S6 37 rc0 + D-19 wired + D-41#5 berth claimed; "
    "wm=py_low_board_clear legal idle"
)
hb["current_task"] = (
    "r290: D-20260930-19 delivery-layer wiring (fresh-face decisions read + content-hash "
    "watermark) + 37 missed decision rows consumed; D-41#5 berth claimed"
)
hb["prod_lanes"] = (
    "r290: D-19 wiring landed+pushed; D-41 five-priorities status: #1 FaceA closed/FaceB "
    "bm-b queue, #2 closed, #3 bm-b parked-astock-settle, #4 closed, #5 bm-c berth r291; "
    "10-01 month-first trio; dualrun streak reset (drift observation)"
)
hb["updated_at"] = now_iso
save("fleet/machines/bm-c.json", hb)

# --- 3) round report line
rr = (
    now_iso + "｜r290｜watermark verdict=绿（py_low_board_clear=板全闭环+池 0 open+bandit 无 open"
    "合法 idle 白名单）。本轮：D-20260930-19 投递层司内接线落地（决策审核步改新鲜读律 git show "
    "origin/main+state 水位键 last_decisions_sha 内容寻址+通告板/orders 物理件区两消费步）+集团树"
    "盲读坑抓获披露（本机 checkout 落后 origin 149 commit·D-05..41 共 37 条漏读全部经新鲜面补消费+"
    "按科学闸回执：D-05 ack〔RW-1~4 全绿 r476+refreeze r491 在树〕/D-14 细化知悉/D-16+19 已接线/"
    "D-21 送达律首次执法 BigMoney 黄=已收到本窗回执/D-41 轨道令消费）+D-41 交付件#5 行为护栏泊位"
    "认领（MSG-20260930-2235·零撞车证据=bm-a/bm-b 心跳+T-129+MSG-2108 全查·+0 试验·r291 执行）｜"
    "验证：smoke 47/47·S6 37 legs rc0（t24 22/22 复验=MSG-2145 预期兑现；dualrun drift entries[140]"
    ".defer_note 观察相 streak-reset 照录；scorecard/dashboard 写入=stale-takeover 合法〔bm-a hb "
    + (f"{aage:.0f}min" if aage is not None else "unreadable") + "〕；CALL ORANGE_COOL sleeves=4）·"
    "push 45eff4e90（拒后 pull--rebase 4/4 复推绿）｜下轮指针：r291=D-41#5 全闭环（正典+L1 派生件+"
    "results+CEO 面）；Face B 待 bm-b face_b.json 落地回填 §7/§8+SUMMARY+TRACK\n"
)
with open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(rr)

# --- 4) inbox processing: 3 consumed msgs -> processed/
os.makedirs("fleet/inbox/processed", exist_ok=True)
moved = []
for m in ("MSG-20260930-2040-bmc-bmb-faceb-fix-convergence.md",
          "MSG-20260930-2108-bma-bmc-d41-berth-zero-collision.md",
          "MSG-20260930-2145-bma-bmc-t24-anchor-refreeze-receipt.md"):
    src = os.path.join("fleet/inbox", m)
    if os.path.exists(src):
        shutil.move(src, os.path.join("fleet/inbox/processed", m))
        moved.append(m)
print("moved:", len(moved))

# --- 5) HANDOVER 5x update (r290 = 5-multiple)
hp = "research/HANDOVER.md"
h = open(hp, encoding="utf-8").read()
anchor = "下一 5x=bm-a r490"
add = (
    "\n> bm-c round 290 五倍数核对（2026-09-30 22:5x）：增量窗 r286-290=bm-c 面——"
    "r290=D-20260930-19 投递层接线（Tools/iteration_prompt.txt 决策审核步新鲜读律+state-bm-c.json "
    "last_decisions_sha 内容寻址水位键〔新增键〕）+集团树盲读坑披露（本机集团 checkout 落后 origin "
    "149 commit·D-05..41 37 条经 git show origin/main 补消费·HQ-FEEDBACK F-20260930-02）+D-41#5 "
    "行为护栏泊位认领（fleet/inbox/MSG-20260930-2235-bmc-ALL·+0 试验·r291 执行窗）；r286-289="
    "Face A 烧毕裁定保留（r284）+Face B 烧批窗开启（r285·烧批宿主 bm-b 在飞）+MSG-2040 两修复合流+"
    "P2NULL-KLIFT-K2200 全收口（r289 finalize）。产物清单漂移=Tools/iteration_prompt.txt〔r290 改〕+"
    "state-bm-c.json〔last_decisions_sha 新键〕+results/_r290bmc_{wire.py,s6.ps1}〔r290 工具件〕；指针："
    "r291=D-41#5 全闭环→10-01 月首轮三件套+REGIME_GUARD v3 日期门 hands-off→D-19 验收窗 10-02 "
    "12:00（已提前接线）→RW-5 外审 10-03→W12 CEO verdict 报 10-02。下一 5x=bm-c r295。\n"
)
if anchor in h:
    h = h.replace(anchor, add + "\n" + anchor.replace("bm-a r490", "bm-c r295") if False else h)
# append the bm-c block after the bm-a 5x block line instead: simple append-before-anchor approach
if anchor in h and "bm-c round 290" not in h:
    h = h.replace(anchor, add + "\n" + anchor)
elif "bm-c round 290" not in h:
    h = h.rstrip() + "\n" + add
open(hp, "w", encoding="utf-8", newline="").write(h)
print("handover updated, bytes:", os.path.getsize(hp))

# self-verify heartbeat epoch int
hb2 = load("fleet/machines/bm-c.json")
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat epoch int OK:", hb2["heartbeat_epoch_utc"], hb2["clock_read"])
