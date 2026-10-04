"""r696 bm-b closeout: state.json + heartbeat + round report append (r645/r679/r694 laws).

- state.json: programmatic json write + json.loads self-verify + epoch int check
- heartbeat fleet/machines/bm-b.json: same discipline, orders_ack preserved verbatim
- round report logs/iteration-loop/round_reports.md: append-only, marker idem gate
"""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().isoformat(timespec="seconds") + "+08:00"
EPOCH = int(time.time())

# ---------- state.json ----------
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 696
st["note"] = ("r696: S0 daemon-lane absorb 11 faces (2f973e34b delivered) + orders probe tree-ish fix "
              "(154/154 zero unacked, pit->CODELY) + D-19 dual MATCH + smoke 48/48 + S6 37/38 rc0 "
              "(update_lhb rc=2 EM SSL transient honest-report, self-heal next round) + attrition CLEAN")
st["last_round_at"] = NOW
for k in ("ts", "updated", "last_seen", "clock_read"):
    st[k] = NOW
st["round_no_label"] = "round 696 (bm-b)"
st["next"] = ("(a) trio NULLS V close ~10-06T17 / Q 10-07T11 / D 10-08T0x -> RAM window -> N2-W15 screen shards "
              "SHARD-2 (claimed) + SHARD-3..11 daemon self-claim -> same-window burner-side done-flip; "
              "(b) W3 judge bm-c landing watch (~22:1x); (c) N2 screen finalize = all-12-done then first-arrival; "
              "(d) update_lhb rc=2 retry re-verify next round; (e) 10-09 post-holiday data-chain check")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 696 and chk["last_round_at"] == NOW
print("STATE OK round 696 @", NOW)

# ---------- heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 696
hb["round_no_label"] = "round 696 (bm-b)"
hb["current_task"] = ("r696 closed: S0 absorb delivered, orders probe tree-ish fix, S6 37/38 (lhb rc=2 EM SSL "
                      "self-heal), CODELY pit append; next = trio V close 10-06T17 -> RAM window -> N2 screen "
                      "self-claim + CONTEST-RC auto-burn -> CEO face <= 10-08")
hb["verdict"] = ("healthy burning (trio NULLS three-family + N2-W15 screen shards RAM-gated + CONTEST-RC queued; "
                 "update_lhb EM source SSL transient rc=2 self-heal pending)")
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
hb["free_ram_gb"] = 3.3
hb["idle_ram_gb"] = 3.3
hb["ram_free_gb"] = 3.3
hb["ram_avail_gb"] = 3.3
hb["total_ram_gb"] = 25.7
hb["ram_gb"] = 25.7
hb["gpu_idle_vram_gb"] = 3.29
hb["gpu_free_vram_gb"] = 3.29
hb["gpu_idle_vram_mb"] = 3294
hb["gpu_free_vram_mb"] = 3294
hb["gpu_vram_free"] = 3294
hb["gpu_free_vram_mib"] = 3294
hb["gpu_free_mb"] = 3294
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert chk2["heartbeat_epoch_utc"] == EPOCH and chk2["round_no"] == 696
assert chk2["orders_ack_count"] == 154 and len(chk2["orders_ack"]) == 154
print("HB OK epoch=", EPOCH, "orders_ack=154 preserved")

# ---------- round report ----------
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
MARK = " | r696 (bm-b) "
line = (
    NOW + " | r696 (bm-b) PRODUCT (dept:数据维护+舰队协同): "
    "[watermark verdict: GREEN (red=false lane=healthy; satengine alive rc0 queue=18 held by RAM-floor "
    "3.3GB<4.0GB 机队纪律自持; audit CLEAN py 85.3% trio burning-healthy; dualrun ZERO-DRIFT streak 5 "
    "@390 entries cutoff 21:18:07; post_review ✓45/✗0/🟡5 零活红 r693 读数复用本窗无新复审动作; S0.5 令差集 "
    "154/154 零未回执零 extra; D-19 decisions/orders 双键 MATCH 水位零动作)] | "
    "当前活: FUND trio NULLS 三族续烧 (owner=bm-b keepalive 鲜活, ETA V 10-06T17 / Q 10-07T11 / D 10-08T0x) + "
    "N2-W15 SCREEN 12 分片 (SHARD-0 bm-c / SHARD-1 bm-a 双机烧中, SHARD-2 本机已认领候 RAM 窗, SHARD-3..11 无主 "
    "RAM 窗开后 daemon 自取) + W3 judge finalize bm-c 帯落地观察 (~22:1x r487 工时标定·零重探针属主侧) + "
    "CONTEST-RC RAM-gated 排队 (due 10-08) | "
    "最近实物: results/_r696bmb_orders_check.py (令差集探针 tree-ish 形修正可复用件) + S6 37/38 rc0 "
    "(REPORT/LIVE-2026-10-04 再生·ORANGE cap50 COOL) @ " + NOW + " | "
    "下个里程碑: trio V 收口 10-06T17 → RAM 窗开 → N2 screen 分片收割 + CONTEST-RC anchor+mirror 自燃 → "
    "assembly 219-measured CEO 面 ≤10-08 治理日; 开市 10-09 数据链复首 (窗沿48h=10-06T17) | "
    "做了什么: S0-1 machine.json 单源锚定 bm-b + S0 daemon-lane absorb 11 面 (origin 交集零实证→commit 2f973e34b "
    "push 送达) + S0.5 令差集探针本窗新写 (首跑 ls-tree 目录 pathspec 形态坑 ORDERS=0 当场自纠→tree-ish 正形 "
    "154/154 零差集; 坑律入 CODELY) + D-19 双键 MATCH (r686 血统探针 method_for sha256/sha1 口径自证复跑) + "
    "决策审核步零新涉本司行 (水位不变零动作) + S1 smoke 48/48 + S2 板扫 169 票 0 open + job_list 空 + "
    "S3 satengine rc0 活 + 修红时序无红可修 + trio watch 三证 OK + S6 37/38 rc0 (唯一红腿 update_lhb rc=2 "
    "EM 源 SSL 瞬态失败 10/11 页如实上报·30min 节流+conn-fuse 自愈下轮重试) + S7 quartet 绝续 (loop pin=2 "
    "no-op 首燃 21:42 / watchdog 幂等重装 / 双钳 LF 归一签) + attrition 4 台账 CLEAN + CODELY 水位观察 "
    "(102.8→103.5KB·GM 阈值重锚 r690 登记面在册) | "
    "验证证据: smoke 48/48; D-19 probe JSON 双 MATCH methods=sha256/sha1; orders probe 154 零差集 "
    "(_r696bmb_orders_check.json); S6 log 38 腿逐跑 (_r696bmb_s6_log.txt·NON-ZERO LEGS: update_lhb rc=2 "
    "如实照录); satengine status rc0; trio watch rc0 OK; attrition scan CLEAN (evidence "
    "_attrition_guard_scan.json); HB/STATE roundtrip+json.loads 自证+epoch int 自证 (本脚本 stdout) | "
    "产品分: 1 (S6 再生面+探针修正实物; 真实在飞产出=trio nulls 三行 daemon 自提 commit 持续落盘) | "
    "坑例新增: 1 (CODELY r696 ls-tree 目录路径形态坑) | "
    "下轮指针: (a) trio 看护续跑 (V 10-06T17 收口窗); (b) N2-W15 screen 分片收割观察; (c) W3 judge bm-c 落地观察; "
    "(d) CONTEST-RC RAM 窗自燃观察; (e) update_lhb 下轮重试红复验; (f) 10-09 开市数据链核验 | "
    "本地未达 origin commit 数: 收口 push 后 push_verify 实证回填\n"
)
with open(rp, "rb") as f:
    blob = f.read()
assert blob.count(MARK.encode("utf-8")) == 0, "idem gate: r696 line already present"
eol = b"\r\n" if blob.count(b"\r\n") * 2 > blob.count(b"\n") else b"\n"
if not blob.endswith(eol):
    blob += eol
blob += line.encode("utf-8") + eol if not line.endswith("\n") else line.encode("utf-8")
with open(rp, "wb") as f:
    f.write(blob)
with open(rp, "rb") as f:
    check = f.read()
assert check.count(MARK.encode("utf-8")) == 1, "post-marker must be exactly 1"
print("REPORT OK r696 line appended")
print("CLOSEOUT ALL OK")
