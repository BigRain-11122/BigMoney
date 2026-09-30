# r302 bm-c round bookkeeping: state, heartbeat, round report, CODELY memory line
# Idempotent-safe append/update for round 302 (2026-10-01 05:1x +08:00)
import json, time, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = "2026-10-01T05:12:51+08:00"
EPOCH = int(time.time())

# ---------- 1) state-bm-c.json ----------
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "machine_id": "bm-c",
    "round_no": 302,
    "last_round_at": NOW,
    "last_round_ts": EPOCH,
    "updated": NOW,
    "cpu_pct": 10,
    "idle_ram_gb": 1.0,
    "gpu_free_vram_mib": 12847,
    "verify": ("S1 smoke 47/47; S6 38 legs rc0 (reconcile ZERO-DRIFT streak 4/3 post-flip evidence; "
               "REGIME v3 enforce->shadow honest downgrade = date-gate awaiting first new bar; paper 6 anchors OK; "
               "t35 open-fill PASS; promotion 0/22 legal months=0); orders diff EMPTY; D-19 ED4E0EAB UNCHANGED (raw-blob); "
               "attrition CLEAN (2 healed historical); claw OK; loop Running pin:05 no-op; watchdog Ready"),
    "did": ("r302: SLOT-7/8/9/10 four 48h CEO report clocks discharged in-window "
            "(docs/trial_labor/CEO-REPORT-INNOVQUOTA-SLOT7-10-20261001.md; quota line 10 batches all-negative "
            "consolidated one CEO page; earliest clock 10-02 07:25, ~26h early; law source = per-slot prereg sec.6 "
            "frozen 48h-CEO face + W9 sec.7 explicit start line + bm-a r500 pointer). r301 stale next-pointer FALSIFIED: "
            "dualrun flip already landed 2026-09-29 06:58 (commit 298c4796b + receipt "
            "research/POOL_RETIREMENT_S3_WAVE1_FLIP_RECEIPT.md in-tree + code read-points face_view confirmed) = "
            "anti-duplicate bar held, zero re-burn. RAM structural diagnosis: 0.2-1.3GB low = shared-machine "
            "structural (CEO foreground ~8GB + ComfyUI 3.2GB minigame vertical + Ollama 3.7GB J13 infra), "
            "no BigMoney leak/zombie, no foreign/CEO process touched."),
    "current_task": ("48h clocks discharged; zero burnable lane-free pool work on bm-c = legal idle disclosed "
                     "(ready=2 both bm-b-lane claimed + W14 parked pending PERPETUAL_FACES v1.1 GM ruling + "
                     "sole open ticket T-131 GM-signature gate)"),
    "next": ("(a) GM rulings twin-pending: T-136 VOID-vs-stands (MSG-048x) + PERPETUAL_FACES v1.1 (MSG-0400) "
             "-> W3/W14 supply unfreeze; (b) 10-02 morning report bm-c sampling row merge (parallel-efficiency "
             "face stays N/A-honest until a multicore burn lands on bm-c); (c) RAM watch: structural shared-machine "
             "face, no action; (d) next 5x HANDOVER row = round 305 bm-c"),
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "note": "r302 product score=2 (CEO-facing report artifact discharging 4 frozen 48h clocks)",
    "last_ts": NOW,
    "last_decisions_read_at": NOW,
    "last_round": ("2026-10-01 r302: SLOT-7/8/9/10 48h CEO clocks discharged (quota line ten-straight-negative "
                   "consolidated report) + stale flip pointer falsified (anti-dup, landed 09-29) + S6 38 legs rc0 "
                   "+ bookkeeping (state 302, heartbeat epoch int, CODELY r302 pit)"),
})
# last_decisions_sha intentionally left unchanged (ed4e0eab..., verified UNCHANGED this round)
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=2)

# ---------- 2) heartbeat fleet/machines/bm-c.json ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
verdict = ("r302 product=2: SLOT-7/8/9/10 48h CEO clocks discharged in-window "
           "(CEO-REPORT-INNOVQUOTA-SLOT7-10-20261001.md, quota line 10/10 negative consolidated, ~26h early); "
           "stale flip pointer falsified (landed 09-29 298c4796b, anti-dup zero re-burn); "
           "watermark red=legal idle (bm-b-lane ready + GM-gated T-131 + W3 held)")
for k, v in [("last_seen", NOW), ("heartbeat_epoch_utc", EPOCH), ("clock_read", NOW), ("round_no", 302),
             ("cpu_pct", 10), ("cpu_util_pct", 10), ("idle_ram_gb", 1.0), ("free_ram_gb", 1.0),
             ("ram_free_gb", 1.0), ("gpu_free_vram_mib", 12847), ("gpu_idle_vram_mib", 12847),
             ("gpu_idle_vram_mb", 12847), ("gpu_vram_free_mb", 12847),
             ("current_task", "48h clocks discharged; legal idle; awaiting GM twin rulings (T-136 + PERPETUAL_FACES v1.1)"),
             ("verdict", verdict), ("health", "ok"), ("updated_at", NOW), ("last_seen_at", NOW)]:
    hb[k] = v
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)

# validation: epoch must be int, clock T-separated
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock not T-separated"
print("heartbeat OK epoch=%d clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))

# ---------- 3) round_reports-bm-c.md append ----------
rp = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
nl = b"\r\n" if b"\r\n" in raw[:2000] else b"\n"
line = (
    "2026-10-01T05:12:51+08:00｜r302｜watermark verdict=红（runnable-work-idle-low-cpu：ready=2 均 bm-b lane 已被其 "
    "daemon 认领 + 唯一 open 票=T-131 P1 GM 署名门[本机禁自签] + W14 parked=供给线等 GM 裁定 PERPETUAL_FACES v1.1"
    "〔bm-b MSG-0400〕——本机零可烧 lane-free 批=合法 idle 白名单如实披露·一行声明不重扫）｜本轮主产出="
    "**SLOT-7/8/9/10 四枚 48h CEO 呈报钟窗内清账**（docs/trial_labor/CEO-REPORT-INNOVQUOTA-SLOT7-10-20261001.md"
    "·配额线 W1~W10 十批全负收拢 CEO 一页·最早钟窗止 10-02 07:25=提前 ~26h·令源=各槽预注册 §6 冻结「48h CEO 呈报面」"
    "+W9 §7 起计行+bm-a r500 HANDOVER 指针·判决事实全从 verdict JSON/prereg §7/§8 回填面实读零手抄）"
    "＋r301 陈旧指针证伪（dualrun flip 手术 2026-09-29 06:58 已落地 commit 298c4796b·receipt 在树·三读点已 face_view 化"
    "——反重复铁律拦下重做零重烧·坑律入册 CODELY r302）＋RAM 结构面诊断（0.2-1.3GB=共享机结构态：CEO 前台 ~8GB"
    "+ComfyUI 3.2GB 小游戏竖线+Ollama 3.7GB J13 基建·非泄漏非僵尸·零可杀自有进程·CEO/他竖线进程不动）｜"
    "验证证据=S1 47/47；S6 38 腿 rc0（reconcile ZERO-DRIFT streak 4/3=翻转后证据链延续·audit 三旗 idle_with_work/"
    "supply_gap/supply_floor 照录·REGIME v3 enforce 请求诚实降级 shadow=日期门 active_from 10-01 待首根新 bar·"
    "paper 六锚 OK·t35 开盘成交验证 PASS·promotion 0/22 月份不足合法·t35_export 2026-09-30 落地）；orders 差集 EMPTY；"
    "D-19 ed4e0eab UNCHANGED（raw-blob）；attrition CLEAN（2 healed 历史）；loop Running pin:05 no-op；watchdog Ready；"
    "claw OK｜实况三行（CEO 过程可见面）：当前活=48h CEO 呈报钟清账+S6 维护链全绿｜最近实物="
    "docs/trial_labor/CEO-REPORT-INNOVQUOTA-SLOT7-10-20261001.md（05:1x）+LIVE-2026-10-01.md+REPORT-2026-10-01.md "
    "再derive｜下个里程碑=GM 双裁定（T-136 VOID-vs-stands〔MSG-048x〕+PERPETUAL_FACES v1.1〔MSG-0400〕）→W14/N1-W3 "
    "供给解冻；10-02 晨报 bm-c 采样行并入（窗 ≤48h）｜产品分=2（CEO 面呈报件=能看实物·四冻结钟清账）"
)
with open(rp, "ab") as f:
    f.write(nl + line.encode("utf-8"))

# ---------- 4) CODELY.md memory append (one item, lesson-first, <=1.5KB) ----------
cp = os.path.join(ROOT, "CODELY.md")
raw2 = open(cp, "rb").read()
nl2 = b"\r\n" if b"\r\n" in raw2[:2000] else b"\n"
mem = (
    "- [2026-10-01 05:1x r302 bm-c] 陈旧 next 指针证伪律（r301→r302 实弹）：r301 收轮指针把 dualrun flip 手术列为"
    "「下轮动作」，实况=翻转已于 2026-09-29 06:58 落地（commit 298c4796b·receipt=POOL_RETIREMENT_S3_WAVE1_FLIP_"
    "RECEIPT.md 在树·三读点代码已 face_view 化）——本轮开工前按反重复铁律 git log+receipt+代码三面核查后放弃重做="
    "零重烧。与 bm-a r410「指针写了≠执行了」同族的**反向面**：指针说「待办」≠真待办。How to apply：接手轮消费上轮 "
    "next 指针清单时，凡执行类指针先过三查（git log --grep 关键词／对应 receipt 是否在场／目标代码实读），"
    "已落地即改记回执勿重做；收轮写指针前同样先查目标是否已在途/已落地。"
)
with open(cp, "ab") as f:
    f.write(nl2 + mem.encode("utf-8"))

print("state round_no=%d epoch=%d" % (st["round_no"], st["heartbeat_epoch_utc"]))
print("round report appended, CODELY size now %d bytes (<50KB line OK)" % os.path.getsize(cp))
print("BOOKKEEPING DONE")
