# -*- coding: utf-8 -*-
"""r890 bm-b closeout: pit direct-write + receipt + HANDOVER 5x line +
round-report ledger line + state.json + heartbeat update.
Byte-domain appends only (r838/r839 EOL law): pit-encoding.md/HANDOVER.md
are LF files, round_reports.md is CRLF-dominant; JSON faces rewritten via
json module with utf-8. Self-verifying: prints byte accounting + re-read
asserts. ASCII-only code; CJK lives in the string constants below."""
import json, os, subprocess, time, hashlib
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------------- 1. pit direct-write (main CODELY.md full: 30,534B,
# headroom 186B -> r666/r889 direct-write exception, receipt below) ----
PIT = P("research", "pit-encoding.md")
pit_entry = (
"- [2026-10-11 18:0x r890 bm-b] **冻结 sha 锚=冻结机工作树字节面，跨机 raw-byte 哈希门假 mismatch 崩溃环坑（W18 entry-gate 实弹·P0）**："
"bm-c r879 冻结窗在自身 CRLF 检出树上给 w16_candidates.json 钉 sha256_16=22179881b7537193，runner _entry_load 按 raw bytes 哈希；"
"bm-b LF 检出（git blob 33f7ea3fcf 双侧恒等·本机 autocrlf=false）算得 9974725830e76f31 → W18 screen 8 分片全 ENTRY-GATE FAIL ~20s 崩 → autofill 崩溃环烧穿 fuse 拒绝 6/8。"
"内容恒等证明=LF→CRLF 单换算字节恰=22179881b7537193。正法=哈希门取规范化面（raw.replace(b'\\r\\n',b'\\n').replace(b'\\n',b'\\r\\n') 幂等归一后哈希；锚字节不动；内容漂移仍 fail-closed）+commit 后 fuse 按 code sha 变化自动清（S16c）。"
"禁项=改冻结锚值/改检出配置翻全树面/手工代烧池批。How to apply：跨机消费的 sha 锚/哈希门一律规范化面哈希，或直接钉 git blob sha（天生跨机恒等）；"
"冻结窗钉文件锚必附「字节面（CRLF/LF）+冻结机 autocrlf」两字段；遇「同内容异 sha」先跑 EOL 面互换探针定谳（r838/r839/r857 EOL 族姊妹面）再动手。")
with open(PIT, "rb") as fh: pit_before = fh.read()
if pit_entry.encode("utf-8") in pit_before:
    pit_after = pit_before; print("pit: already present, skip")
else:
    add_b = (pit_entry.encode("utf-8") + b"\n") if pit_before.endswith(b"\n") else (b"\n" + pit_entry.encode("utf-8") + b"\n")
    pit_after = pit_before + add_b
    with open(PIT, "wb") as fh: fh.write(pit_after)
    assert pit_entry.encode("utf-8") in pit_after, "pit verbatim assert"
pit_entry_bytes = len(pit_entry.encode("utf-8"))
print("pit: %d -> %d" % (len(pit_before), len(pit_after)))

# ---------------- 2. receipt -------------------------------------------
receipt = {
  "receipt": "r890 bm-b CODELY direct-write (r666/r889 precedent; main 30,534B headroom 186B < entry -> full-member exception)",
  "pit": "W18 frozen-sha-anchor cross-machine byte-face false-mismatch crash-loop (P0)",
  "target": "research/pit-encoding.md",
  "entry_bytes": pit_entry_bytes,
  "target_bytes_before": len(pit_before),
  "target_bytes_after": len(pit_after),
  "target_eol": "LF",
  "verbatim_in_target": True,
  "main_bytes_untouched": os.path.getsize(P("CODELY.md")),
  "main_cap_bytes": 30720,
  "main_within_cap": os.path.getsize(P("CODELY.md")) <= 30720,
  "commit_ref": "be5faa031 (fix) / c1446c894 (origin tip at fix push)",
  "round": "r890 bm-b", "ts": TS,
}
with open(P("results", "_r890bmb_codely_directwrite.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("receipt: main %dB <= cap %dB=%s" % (receipt["main_bytes_untouched"], 30720, receipt["main_within_cap"]))

# ---------------- 3. HANDOVER 5x line (r885 slot missed -> disclose) --
HO = P("research", "HANDOVER.md")
ho_line = (
"- 冻结入口·产出清单核对（冻结不删）：**round 890 bm-b（5x 核对位）**｜2026-10-11 18:0x 核对｜账本范围=本机 r881-r890 十轮"
"（r885 5x 位未核=OVERDUE-DISCLOSED·该窗=mini-split 仪式轮只办拆件未落 5x 行·本行并账补核）｜账本权威=round 880 bm-b 行（round_reports.md 本机分库）｜"
"新实物=**r890 W18 entry-gate 字节面 P0 修复+烧录复燃**（scripts/trial_labor_w18.py CRLF 规范化面哈希·锚 22179881b7537193 字节不动·commit be5faa031·"
"W18-SCREEN shard-2 done 17:56:03+shards-1/3..7 点火烧录+MSG-1735-bmc relay 落地）+"
"**r886-r889 E16 alphagen RG census 全链**（12 分片+finalize·census_holds=true·obs family max |ICIR| 0.455>null p95 0.077·n_ok 200/200·CENSUS-2026-10-09.json）+"
"**r889 N2 U3 channel-1 开窗+DRAFT prereg**（research/N2U3_ALPHAGEN_RL_P1.md·judged K=32·E17 登记 open）+r887-r888 死会话遗产收编+RW-4 修复+T-184 冲突标治愈｜"
"在飞=W18 burn→finalize 协商（8/8 checkpoint 属地=我机 1..7+bm-c 0·Tailscale 通道 O-20261010-0058）+T-184 510880 transfer deadline 10-12 15:30（bm-a 停机 ~20h 阻塞）+"
"48h CEO 报 due 10-13 11:2x（E16 verdict+W18+机队态）+IntradayMarks 首火 10-12 09:25 watch")
with open(HO, "rb") as fh: ho_before = fh.read()
if ho_line.encode("utf-8") in ho_before:
    print("handover: already present, skip")
else:
    add_h = (ho_line.encode("utf-8") + b"\n") if ho_before.endswith(b"\n") else (b"\n" + ho_line.encode("utf-8") + b"\n")
    with open(HO, "wb") as fh: fh.write(ho_before + add_h)
    assert ho_line.encode("utf-8") in (ho_before + add_h)
    print("handover: %d -> %d" % (len(ho_before), len(ho_before) + len(add_h)))

# ---------------- 4. round report ledger line (CRLF-dominant file) -----
RP = P("logs", "iteration-loop", "round_reports.md")
rr_line = (
TS + " | r890 bm-b | dept:工程：W18 entry-gate 字节面 P0 修复+全链复燃（根因=bm-c r879 冻结锚钉其 CRLF 检出面·我机 LF 检出 raw 哈希假 mismatch 9974725830e76f31!=22179881b7537193→8 分片 ~20s 崩溃环·fuse 拒 6/8；"
"修复=CRLF 规范化面哈希·锚字节不动·fail-closed 保留·selftest 24/24+live gate PASS n=173·commit be5faa031 推达 origin tip c1446c894 rev-list 0）；"
"W18 复燃=shard-2 done 17:56:03（checkpoint 112KB）+shards-3..7 烧录中+shard-1 ext-claim 20min stale 接管点火 17:56:24+shard-0 bm-c park（MSG-1735-bmc relay 落地+回执 MSG-1810-bmb）；"
"+dept:研究：E17 保持 open（leg-1 RL runner 下轮主工）；S0 stash-pop 守护进程活面冲突自愈（PS 吞 stash@{0} 语法→drop→SHA 82da9fff 恢复 13 件零丢失）；"
"D19 dec 81f27c6d+ord 69090314 零 delta；smoke 49/49；S6 33 腿 0 红（周日 no-op 重：dualrun streak 49·ORANGE_COOL call@2026-10-09·bm-a 心跳 stale 1202min→STALE_MIN 法接管 derive 三面·shard-1 ignition_sla 旗随接管自愈）；"
"孤儿面=0（11 py 活）；本地未达 origin commit 数=0（收口 push 后自证）"
" | 证据：scripts/trial_labor_w18.py gate 修复+results/trial_labor_w18/checkpoint/screen_shard_2of8.jsonl+logs/autofill.log C8 LAUNCH 线+results/_r890bmb_codely_directwrite.json "
"| 下轮：r891 E17 leg-1 RL runner 建+W18 burn watch→finalize 协商+T-184 deadline 10-12 15:30+48h CEO 报 10-13 11:2x")
with open(RP, "rb") as fh: rp_before = fh.read()
if rr_line.encode("utf-8")[:80] in rp_before:
    print("round_report: already present, skip")
else:
    nl = b"\r\n" if rp_before.count(b"\r\n") * 2 >= rp_before.count(b"\n") else b"\n"
    sep = b"" if (not rp_before or rp_before.endswith(b"\n")) else nl
    with open(RP, "wb") as fh: fh.write(rp_before + sep + rr_line.encode("utf-8") + nl)
    print("round_report: appended (eol=%s)" % ("CRLF" if nl == b"\r\n" else "LF"))

# ---------------- 5. state.json closeout -------------------------------
did = ("r890: W18 entry-gate byte-face P0 修复+烧录复燃（根因=bm-c r879 冻结锚 22179881b7537193 钉在其 CRLF 检出面·bm-b LF 检出（blob 33f7ea3fcf 恒等）raw 哈希算得 9974725830e76f31→8 分片 ENTRY-GATE FAIL ~20s 崩→fuse 崩溃环拒 6/8；"
"修复=CRLF 规范化面哈希·锚字节不动·漂移仍 fail-closed·selftest 24/24+live gate PASS n=173·commit be5faa031·origin tip c1446c894·rev-list 0）"
"+复燃=shard-2 done 17:56:03+shards-3..7 烧录中+shard-1 ext-claim stale 接管点火 17:56:24+shard-0 bm-c park（MSG-1735-bmc relay+回执 MSG-1810-bmb）；"
"S0 stash-pop 守护进程活面冲突自愈（PS 吞 stash@{0}→drop→SHA 恢复 13 件零丢失）；D19 dec 81f27c6d+ord 69090314 零 delta；smoke 49/49；"
"S6 33 腿 0 红（周日 no-op 重：dualrun streak 49·ORANGE_COOL@2026-10-09·bm-a 心跳 stale 1202min→STALE_MIN 法接管 derive 三面）；孤儿面=0（11 py 活）；"
"idle not GREEN（烧录中无领单义务）；wm py_low_with_work_cands=崩溃环窗均值·复燃后自愈中")
nxt = ("r891: E17 leg-1 RL env runner build（scripts/alphagen_rl_p1.py·表达式树采样+协同池边际 IC+PPO 最小复现集+selftest hermetic·底座=research/N2U3_ALPHAGEN_RL_P1.md DRAFT）-> freeze-gate 五条件窗（seed_admit_gate+banned gate+shared-lib refs） "
"> W18 burn watch（8/8 后 finalize 协商：我机持 1..7 checkpoint+bm-c 0·Tailscale 通道 O-20261010-0058） > 48h CEO 报 due 2026-10-13 11:2x（E16 verdict+W18+机队态） "
"> T-184 510880 transfer deadline 10-12 15:30（bm-a 停机 ~20h 阻塞·回归即探） > IntradayMarks 首火 Monday 10-12 09:25 watch")
ST = P("state.json")
st = json.load(open(ST, encoding="utf-8"))
st.update({
  "round": 890, "round_no": 891, "round_no_label": "r890",
  "ts": TS, "clock_read": TS, "updated": TS, "updated_at": TS,
  "last_round_at": TS, "last_round_ts": TS, "last_seen": TS,
  "last_action": did, "last_action_at": TS, "did": did,
  "now_active": "r890 closeout: W18 entry-gate byte-face P0 repair + burn relight",
  "note": "r890: W18 crash-loop root-caused (cross-machine frozen-anchor byte-face) + fixed + relit; E17 leg-1 = next-round primary",
  "task": nxt, "next": nxt, "current_task": nxt,
  "next_milestone": "E17 leg-1 RL runner <=48h; W18 finalize 协商窗; T-184 deadline 10-12 15:30; 48h CEO 报 10-13 11:2x",
  "latest_artifact": "r890: scripts/trial_labor_w18.py gate fix (commit be5faa031) + W18 screen shard-2 done (checkpoint 112KB) + pit-encoding.md r890 条",
  "verdict": "GREEN: r890 COMPLETE (W18 entry-gate 字节面 P0 修复+8/8 分片处置/点火+S6 0 红; E17 leg-1 未动=下轮主工)",
  "orphan_face": 0, "orphan_faces": 0,
  "orphan_face_note": "r890 round probe: py_faces=11 alive, orphans=0",
  "last_decisions_read_at": st.get("last_decisions_read_at"),
  "last_orders_read_at": st.get("last_orders_read_at"),
  "sync": {"last_push_ts": TS, "note": "r890 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0"},
})
with open(ST, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
json.load(open(ST, encoding="utf-8")); print("state.json OK round=890 -> round_no=891")

# ---------------- 6. heartbeat -----------------------------------------
ram_gb = ram_pct = vram_gb = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_gb = round(vm.available / 1024**3, 1); ram_pct = round(100 - vm.percent, 1)
except Exception:
    pass
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, timeout=20).stdout.decode("ascii", "replace").strip().splitlines()
    vram_gb = round(int(out[0]) / 1024, 1)
except Exception:
    pass
HB = P("fleet", "machines", "bm-b.json")
hb = json.load(open(HB, encoding="utf-8"))
epoch = int(time.time())
hb.update({
  "ts": TS, "clock_read": TS, "last_seen": TS, "last_round_at": TS,
  "heartbeat_epoch_utc": epoch,
  "round": 890, "round_no": 891,
  "current_task": nxt, "task": nxt, "next": nxt,
  "did": did, "last_action": did, "last_action_at": TS,
  "now_active": "r890 closeout: W18 entry-gate byte-face P0 repair + burn relight",
  "latest_artifact": "r890: scripts/trial_labor_w18.py gate fix (be5faa031) + W18 shard-2 done",
  "next_milestone": "E17 leg-1 RL runner <=48h; W18 finalize 协商; T-184 deadline 10-12 15:30; 48h CEO 报 10-13 11:2x",
  "note": "r890: W18 crash-loop fixed (byte-face) + relit; E17 leg-1 next",
  "verdict": "green",
  "idle_rounds": 0, "agenda_starved": False,
  "orphan_face": 0, "orphan_faces": 0,
  "orphan_face_note": "r890 round probe: py_faces=11 alive, orphans=0",
})
if ram_gb is not None: hb["ram_free_gb"] = ram_gb; hb["free_ram_gb"] = ram_gb
if ram_pct is not None: hb["ram_free_pct"] = ram_pct
if vram_gb is not None:
    hb["gpu_free_vram_gb"] = vram_gb; hb["vram_free_gb"] = vram_gb; hb["gpu_free_vram_mb"] = int(vram_gb * 1024)
hb["sync"] = {"last_push_ts": TS, "note": "r890 closeout push lands with this commit"}
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read T-separator (R262 law)"
print("heartbeat OK epoch=%s(int) clock=%s ram=%sGB vram=%sGB idle_rounds=%s starved=%s"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], hb2.get("ram_free_gb"), hb2.get("gpu_free_vram_gb"), hb2["idle_rounds"], hb2["agenda_starved"]))
print("CLOSEOUT DONE @", TS)
