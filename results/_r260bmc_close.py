# r260 bm-c closeout: S6-chain wait + round report line + HANDOVER 5x row
# + state 259->260 flip + heartbeat (R170/R178 epoch-int law, self-verified).
import io, json, time, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---- 1) wait for detached S6 chain (max 180s), parse non_green
LOG = r"logs\iteration-loop\s6_r260_bmc_chain.log"
chain_non_green = "PENDING-TIMEOUT (detached, next round collects)"
for _ in range(36):
    try:
        txt = io.open(LOG, encoding="utf-8").read()
    except FileNotFoundError:
        txt = ""
    if "S6 chain done" in txt:
        last = [l for l in txt.splitlines()
                if l.startswith("S6 chain done")][-1]
        chain_non_green = last.split("non_green=", 1)[-1].strip()
        break
    time.sleep(5)
print("chain non_green:", chain_non_green)

DID = ("r260 (freeze window): SLOT-9 CROWD-VOTE-P1 freeze steps 1-5 ALL "
       "LANDED per W5/W6/W7 mirror -- (1) FROZEN flip: prereg banner+status "
       "BERTH->FROZEN + sec.4 seed annotation + sec.9 freeze record append "
       "(judgment lines zero-touch, sec.5 predictions zero-change); "
       "(2) G-ANCHOR bit-exact: berth probe re-run git-face ZERO-DIFF "
       "(file-level) + freeze probe face-by-face ALL GREEN "
       "(results/_r260bmc_w9_d6_cells_probe_facts.json: 1616 decidable / "
       "first 2020-02-06 / votes 1525/1599/715/824 / crowd_ge3 860 / "
       "crowd_eq4 571 / recover 660 / asym flips 71 / sym flips 77, cutoff "
       "2026-09-29 unmoved zero incremental segment); (3) SEED "
       "innovation_quota_w9_crowd=20326000 registered (science_gates."
       "SEED_REGISTRY single key) + three-step law ALL GREEN "
       "(results/_r260bmc_w9_seed_law_facts.json: 141-key full import view, "
       "137 existing int bases zero-collision, first_el 1323286491 distinct, "
       "bands clean, rg 12 hits classifiable; +500 above W8 20325500, W13 "
       "trio registered bm-a r461 clear); (4) threshold-constant zero-drift "
       "PASS (author-verbatim, zero calibration); (5) D6 cells probe landed "
       "(batch-internal ASYM vs SYM 0.9169 variant-face burn-both; vs T33 "
       "max 0.4561 all<0.7 merge-clause ZERO; vs registered six 0.1767 "
       "disclose-only; REGIME_GUARD non-cell boundary stands, T0 untouched); "
       "construction single source crowd_positions/cell_returns defined in "
       "the freeze probe (r456 paradigm; r261 runner verbatim-import); "
       "step-6 runner = next round per W7 r255->r256 timeline mirror. "
       "Catalog SLOT-9 flipped frozen (entry prereg_ref/runner_note + "
       "registry state/evidence/verified). MSG-20260930-0925 dual-signal. "
       "S6 37-leg chain detached (r462 bm-a paradigm) non_green="
       + chain_non_green + ". Orders 122/122 zero-diff (123rd file=README "
       "non-order), inbox zero unread, tasks zero open, WM red=false, "
       "decisions zero new lines. Smoke 26/26.")
VERIFY = ("smoke 26/26; seed law ALL GREEN facts in-tree; d6 cells probe "
          "facts in-tree (G-ANCHOR reverify pass + threshold constants pass "
          "+ d6 face); berth probe re-run git-status clean (bit-exact "
          "file-level); catalog/prereg FROZEN flips in-tree; heartbeat "
          "epoch int self-verified; S6 chain non_green=" + chain_non_green)
NEXT = ("(a) r261 SLOT-9 step-6 runner build: scripts/innovation_quota_w9.py "
        "(W1-W7 skeleton parameterization reuse; single-source import "
        "crowd_positions/cell_returns from results/_r260bmc_w9_d6_cells_"
        "probe.py; G-ANCHOR battery constants from berth+freeze facts; "
        "BATCH_CELLS=2004, nulls K=2000 / starts 1000 / splits 100 seed "
        "20326000) -> selftest -> read-only verify real-panel bit-exact -> "
        "catalog runner_note BUILT flip -> pool enqueue (enqueue_gates "
        "prereg_frozen PASS + runner_exists PASS -> two-gate law satisfied) "
        "-> autofill burn -> judged verdict results/innovation_quota/"
        "CROWD-VOTE-P1.json (<=48h window, judged-negative mainline "
        "prediction); (b) SLOT-8 W8 COV-SHRINK-AB-P1 burn landed on ledger "
        "this window (live head 357,383) -- harvest face (verdict + prereg "
        "s7/s8 backfill + pool done flip + attrition check + 48h CEO face) "
        "= observing harvest round work per r244 landed-marker law; "
        "(c) 10-01 month-first trio (science_audit + monthly_briefing + "
        "self_review) + REGIME_GUARD v3 date-gate auto-activation hands-"
        "off; (d) SLOT-7 48h CEO clock due 2026-10-02 07:26 (O-1116 "
        "dual-column); (e) supply floor: SLOT-9 pool-ready after r261 "
        "runner = second ready line.")

# ---- 2) round report line
report = (
    now + " | r260 bm-c (dept:研究+工程·SLOT-9 冻结轮+5x HANDOVER) | "
    "WM-VERDICT: 绿 (red=false@watermark_red.json lane=healthy; 冻结窗交付"
    "非闲置; S6 chain detached r462 范式 non_green=" + chain_non_green +
    ") | CEO 可见面: 当前活=INNOVATION-QUOTA-SLOT-9 冻结步①-⑤ 全落地（泊位 "
    "r259→冻结 r260·W5/W6/W7 镜像）; 最近实物=research/INNOVATION_QUOTA_W9_"
    "PREREG.md FROZEN（横幅+状态行+§4 seed 注记+§9 冻结窗实录）+results/_r260bmc_"
    "w9_seed_law_facts.json（三步律 ALL GREEN·141 键零撞）+results/_r260bmc_w9_"
    "d6_cells_probe_facts.json（G-ANCHOR 逐位 PASS+阈值常量零漂移+D6 cells 批内 "
    "0.9169/vs T33 max 0.4561 零合并/vs 六员 0.1767 披露）+Tools/fill_ladder_"
    "catalog.json SLOT-9 frozen 翻面（同窗 commit·MSG-0925 双信号）; 下个里程碑="
    "SLOT-9 步⑥ runner scripts/innovation_quota_w9.py 建毕→selftest→verify→"
    "池化→autofill 烧批→judged 判决面（窗 ≤48h·judged-negative 主通道预判·r261）"
    "+SLOT-8 W8 收割面（落账 357,383 已观测·归收割轮） | did: " + DID +
    " | verify: " + VERIFY + " | next: " + NEXT)
with io.open(r"logs\iteration-loop\round_reports-bm-c.md", "a",
             encoding="utf-8") as f:
    f.write("\n" + report + "\n")
print("round report line appended")

# ---- 3) HANDOVER 5x row (r260 = 5x window)
hrow = (
    "- 【第五节·产物清单核对（新增与删改）】**round 260 bm-c（5x 核对本轮）**："
    "2026-09-30 09:2x 核对；对账区间=增量 bm-c r256-260（基线=round 255 bm-c 行·"
    "bm-a r460/r463 行已收讫），统一链 **355,271→357,383 实读（活链头="
    "COV-SHRINK-AB-P1.json live-read·+2,112=SLOT-8 W8 判决批落账）**；本窗新增="
    "W9 冻结窗件（prereg FROZEN 翻面+seed law facts+D6 cells probe facts+"
    "catalog frozen 翻面）+S6 分离驱动器+close 件；删改=零；下个 5x 窗=r265。")
with io.open(r"research\HANDOVER.md", "a", encoding="utf-8") as f:
    f.write("\n" + hrow + "\n")
print("HANDOVER 5x row appended")

# ---- 4) state-bm-c.json 259->260
with io.open(r"state-bm-c.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 260
st["last_round_at"] = "r260"
st["last_round_ts"] = now
st["updated"] = now
st["did"] = DID
st["verify"] = VERIFY
st["next"] = NEXT
st["current_task"] = ("r260 closed (SLOT-9 freeze steps 1-5 ALL GREEN); "
                      "next = r261 step-6 runner build + pool enqueue")
with io.open(r"state-bm-c.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state flipped 259->260")

# ---- 5) heartbeat (epoch int law)
with io.open(r"fleet\machines\bm-c.json", encoding="utf-8") as f:
    hb = json.load(f)
epoch = int(time.time())
hb["last_seen"] = now
hb["current_task"] = "SLOT-9 frozen (steps 1-5); r261 runner build next"
hb["round_no"] = 260
hb["verdict"] = ("alive: r260 closed (SLOT-9 freeze steps 1-5 ALL GREEN), "
                 "r261 runner build next")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now
hb["health"] = "ok"
hb["updated_at"] = now
with io.open(r"fleet\machines\bm-c.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with io.open(r"fleet\machines\bm-c.json", encoding="utf-8") as f:
    back = json.load(f)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in back["clock_read"], "clock_read not ISO-T"
print("heartbeat written, epoch", epoch, "int self-verified")
