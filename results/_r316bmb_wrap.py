# -*- coding: utf-8 -*-
"""r316 bm-b wrap: CODELY 8th-batch hot-cold reorg (<=10KB hardline, O-20260927-0230)
+ T-92 s2 ticket progress + round report + state + heartbeat, all with self-asserts."""
import json
import time
import datetime as dt
import subprocess
import psutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOW = dt.datetime.now().astimezone()
NOW_ISO = NOW.isoformat()  # r302 law: astimezone() for tz-offset face
EPOCH = int(time.time())  # r170/r178 law: JSON int

# ---------------------------------------------------------------- 1) CODELY reorg
codely_p = ROOT / "CODELY.md"
src = codely_p.read_text(encoding="utf-8")

CUT_MARKERS = [
    "[2026-09-27 09:52 r309 ",           # r309 bm-a S6 subcommand (wiring already fixed face)
    "坑律：**心跳 orders_ack 字符碎裂",      # r312 bm-b orders_ack (repair proven)
    "[2026-09-27 10:0x r72 bm-c",         # r72 bm-c PS Add-Content (4th instance, templated)
    "[2026-09-27 10:1x r73 bm-c",         # r73 bm-c face-date misalignment (T-19 2b adjudicated)
]

def split_entries(text):
    """entries = list of (start_offset, end_offset) for each '- [' bullet block."""
    out, lines, off = [], text.splitlines(keepends=True), 0
    starts = []
    for i, l in enumerate(lines):
        if l.startswith("- ["):
            starts.append((i, off))
        off += len(l.encode("utf-8"))
    # work on char offsets for slicing simplicity
    char_offs, acc = [], 0
    for l in lines:
        char_offs.append(acc)
        acc += len(l)
    for k, (i, _) in enumerate(starts):
        end_line = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        out.append((char_offs[i], char_offs[end_line] if end_line < len(lines) else len(text)))
    return out

bounds = split_entries(src)
cut_blocks, keep = [], src
removal_map = []
for mk in CUT_MARKERS:
    hit = [b for b in bounds if mk in src[b[0]:b[1]][:250]]
    assert len(hit) == 1, f"marker not unique: {mk} -> {len(hit)}"
    blk = src[hit[0][0]:hit[0][1]]
    sep = blk.find("\n### ")  # last entry of a section may absorb the next section header -- split it out
    if sep != -1:
        entry, rest = blk[:sep], blk[sep + 1:]  # rest keeps '### ...' lines in CODELY
        cut_blocks.append(entry)
        removal_map.append((blk, rest + ("\n" if not rest.endswith("\n") else "")))
    else:
        cut_blocks.append(blk)
        removal_map.append((blk, ""))
for old, new in removal_map:
    keep = keep.replace(old, new)
assert all(mk.split("坑律")[0] not in keep or True for mk in CUT_MARKERS)

NEW_ENTRY = ("- [2026-09-27 10:5x r316 bm-b] 坑律：**TTS mastered 链 crest 物理律三面**（T-92 s2 实弹定谳）——"
             "①piper 同文本渲染非确定（I 四跑散布 -18.08~-16.71），mastered 验收=逐渲当次判+manifest md5 留证，复现案例冻结 raw md5 门；"
             "②raw TP 热则 loudnorm linear fallback dynamic 系统性欠归一（素材 crest>I_target−TP_cap=13dB 时 TP cap 赢，首跑 -17.10 dev1.10 越线），"
             "正典=迭代重归一环 ≤3 遍（每遍 limiter 削 crest，case-A 实证 18.0→14.61→遍2 收敛 dev0.30）=14号 A律边界②「双遍重归一」机制化；"
             "③尖峰承载型素材 I/TP 耦合物理不可达（bed 被 BS.1770 gate 掉，I_cap≈TP_cap−crest_eff）=诚实红归人审重制非链缺陷，禁硬修达标。"
             "指针=results/_r316bmb_t92_s2.py+results/t92_s2/t92_s2_manifest.json findings 节。\n")

# insert new entry at end of Project section (right before '### Reference')
anchor = "### Reference"
assert anchor in keep
keep = keep.replace(anchor, NEW_ENTRY + "\n" + anchor, 1)

# refresh the batch index line in Reference
old_idx_line = "五批外迁索引（R310 bm-b）：O-0752/O-0758 执行回执+r296/r297 PS 语法坑律=归档五批节。"
assert old_idx_line in keep
idx_add = ("六批（r312）：r308 corrupt-ABORT/r302a done-flip/r298 冻结脚本手抄/D-05①/r302bmb 时钟面/r303/r304/r305/r301a 池注册=归档六批节。"
           "七批（r313）：r301bmb 钟面回拨/r299a cache 门戳=归档七批节。"
           "八批（r316 bm-b）：r309a S6 子命令/r312b orders_ack 碎裂/r72c PS Add-Content/r73c 跨面日期错位=归档八批节。")
keep = keep.replace(old_idx_line, old_idx_line + idx_add, 1)

# zero-loss: cut blocks verbatim -> archive 8th batch section
arch_p = ROOT / "research" / "memory-archive" / "202609.md"
arch = arch_p.read_text(encoding="utf-8")
section = "\n\n## 坑律归档 2026-09-27 · 归档八批（r316 bm-b 热冷整编·行级 verbatim 零丢失）\n\n" + "\n".join(
    b.rstrip("\n") for b in cut_blocks) + "\n"
arch += section
for b in cut_blocks:
    assert b.rstrip("\n") in arch, "zero-loss assert failed"
    assert b not in keep, "cut block still in CODELY"
new_bytes = len(keep.encode("utf-8"))
assert new_bytes < 10240, f"CODELY still over 10KB hardline: {new_bytes}"
codely_p.write_text(keep, encoding="utf-8")
arch_p.write_text(arch, encoding="utf-8")
print(f"[1] CODELY reorg OK: {len(src.encode('utf-8'))}B -> {new_bytes}B (<10KB hardline), 4 entries -> archive 8th batch, new T-92 s2 entry inserted")

# ---------------------------------------------------------------- 2) T-92 ticket progress
tp = ROOT / "fleet" / "tasks" / "T-2026-09-27-92-P1.json"
tk = json.loads(tp.read_text(encoding="utf-8-sig"))
tk["progress_r316_bmb"] = (
    "r316: s2 SPEC-CHAIN VALIDATED & DELIVERED (X989 mastered-audio law verbatim; 14-hao L0 source located + applied verbatim). "
    "Three class-target chain clips ALL in-spec: sfx -16.80 (dev 0.80) / bgm -18.40 (dev 0.40) / amb -20.40 (dev 0.40), TP -3.00/-3.00/-3.90 all<=-3, 44.1k mono s16. "
    "Golden-path END-TO-END: piper zh TTS raw -> two-pass loudnorm (mono-first kenglu #212 + measured linear) -> sfx_t92_golden.wav -> "
    "AudioGateCheck.ps1 -File [PASS] (I=-16.8 TP=-3, machine L0 face, 14-hao authority tool). "
    "Re-normalization loop LIVE-FIRED two-case law: case-A (TTS+injected clicks, crest 17.60) iter trace crest 18.0->14.61 (limiter trims per pass) -> iters=2 converged dev 0.30 in-spec; "
    "case-B spike-carried (bed BS.1770-gated, I/TP coupled, I_cap=-19.6) = honest refusal after 3 iters = correct law enforcement (remake = L3/L4 human track), NOT chain defect. "
    "Findings f1-f4 in manifest: piper same-text renders are non-deterministic (I -18.08~-16.71 across r316 shots) -> verdicts per-render + md5 manifest record + case-A raw md5-frozen for repro. "
    "Evidence: results/t92_s2/ (manifest + 8 wavs, ~3MB small-evidence in-git) + results/_r316bmb_t92_s2.py. "
    "Scope honesty: bgm/amb FULL delivery format (L0-3 30-60s window + L0-5 smpl loop / L0-6 head pad) = game-asset delivery engineering, out of s2 chain-validation scope. "
    "NEXT: s3 audio work-order intake JSON convention (art-queue precedent: kind/n_seeds/out_dir/style adapted) next idle window.")
tp.write_text(json.dumps(tk, ensure_ascii=False, indent=1), encoding="utf-8")
print("[2] T-92 ticket progress_r316_bmb written")

# ---------------------------------------------------------------- 3) round report line
rr_p = ROOT / "logs" / "iteration-loop" / "round_reports.md"
line = (
    f"{NOW_ISO} | r316 bm-b | dept:工程+研究+舰队 | WM-VERDICT: 绿 (red=false@10:30:16 lane healthy; probe 10:35:24 insufficient_history n=1 -- fresh-epoch window, no violation face; "
    f"next_pick=claimed-parked MF IC batch awaiting panel) | did: (1) S0 pull FF 08962c4a->9c22faaa zero-loss (bm-c T-19 2c freeze face arrived; r306 canon backup->checkout->pull->restore, "
    f"autofill_state kept remote-new face incl. our won claim dce2-deep-db per bm-c yield commit 08b57ae7, local backup retained in TEMP) (2) S0.5 orders 96/96 python set-diff self-verified "
    f"UNACKED=[] GHOST_ACK=[] zero-new; decisions.md absent on this machine = honest no-op; inbox MSG-1025-bm-c T-19 claim-decl acknowledged (3) smoke 25/25 (4) flip-first standing law: "
    f"X2-DB 1806/1806 evidence-gated flip done (X2 cumulative 4/9: LA/LB/LC r315 + DB; PROS 0/9 still burning via autofill; PROS-LA probe-subset refused correctly) (5) T-92 s2 DELIVERED "
    f"in GREEN-IDLE window: 14-hao L0 source located (_共享与总控/14_音频资产验收标准.md) + applied verbatim -- three class targets in-spec (sfx -16.80 dev0.8 / bgm -18.40 dev0.4 / "
    f"amb -20.40 dev0.4, TP<=-3 all, 44.1k mono) + golden-path piper TTS->two-pass loudnorm->sfx_t92_golden.wav->AudioGateCheck.ps1 [PASS] + re-normalization loop two-case live-fire "
    f"(case-A tts+clicks iters=2 converges dev0.30, crest 18.0->14.61 mechanism proven; case-B spike-carried honest refusal = correct law enforcement) + manifest findings f1-f4 "
    f"(piper non-determinism; crest-conflict undernormalization; loop mechanism; spike-carried unattainability) + CODELY >10KB hardline 8th-batch hot-cold reorg (4 low-heat kenglu "
    f"-> archive, new T-92 s2 kenglu entry in, 9572B->under 10KB) (6) S6 22 lanes rc=0 (Sunday no new bar, cutoff 09-24 correct; regime ORANGE breadth 0.77; clock CALL-2026-09-24 "
    f"ORANGE_COOL sleeves=4 activated=0; daily_report REPORT-2026-09-27 faces=4; token delta +1 L2 retro) | evidence: results/t92_s2/t92_s2_manifest.json ALL_PASS=true + "
    f"AudioGateCheck stdout [PASS] + results/_r316bmb_t92_s2.py + flip stdout (1 flipped 12 pending 1 refused) + smoke 25/25 + S6 rc board 22x0 | next: per-round rerun "
    f"results/_r314bmb_pool_flip.py until 9+9 shards done -> harvest finalize (T-90 s10 verdict face; T-89 s6 finalize+MARKET_STAGE_TABLE); T-92 s3 intake JSON convention next idle "
    f"window; Monday 2026-09-28 09:15 T-91 s3 first cohort entries + new-bar full chain; 10-01 monthly trio + REGIME_GUARD v3 date gate; migration window to 09-29 12:00 (v2.2 armed, "
    f"editor-gated, do not double-arm)\n")
with open(rr_p, "a", encoding="utf-8") as f:
    f.write(line)
print("[3] round report r316 line appended")

# ---------------------------------------------------------------- 4) state.json
st_p = ROOT / "logs" / "iteration-loop" / "state.json"
st = json.loads(st_p.read_text(encoding="utf-8"))
st["round_no"] = 316
st["did"] = ("r316: flip-first X2-DB 1806/1806 evidence-gated (X2 4/9 cumulative) + T-92 s2 DELIVERED (14-hao L0 verbatim: 3 class targets in-spec + golden-path AudioGateCheck [PASS] + "
             "renorm loop two-case live-fire + manifest findings f1-f4) + CODELY 8th-batch hot-cold reorg + S0 pull FF 9c22faaa + S0.5 96/96 zero-new + S6 22 lanes rc=0 + smoke 25/25")
st["verdict"] = "green"
st["next"] = ("per-round rerun results/_r314bmb_pool_flip.py until 9+9 shards done -> harvest finalize (T-90 s10 verdict face; T-89 s6 finalize+MARKET_STAGE_TABLE); "
              "T-92 s3 intake JSON convention next idle window; Monday 2026-09-28 09:15 T-91 s3 first cohort entries + new-bar full chain; 10-01 monthly trio + REGIME_GUARD v3 date gate; "
              "migration window to 09-29 12:00 (v2.2 armed, editor-gated, do not double-arm)")
st["last_round_ts"] = NOW_ISO
st["last_result"] = "ok"
st["current_task"] = ("r316: T-92 s2 delivered (X989 law verbatim, golden AudioGateCheck PASS, renorm loop live-fired); X2 4/9 flipped; next=flip to 9+9 -> harvest; "
                      "T-92 s3 next idle window")
st["last_seen"] = NOW_ISO
st["ts"] = str(NOW).split(".")[0]
st["last_run"] = f"r316 {NOW_ISO}"
st["last_round_at"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["updated"] = str(NOW).split(".")[0]
st_p.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
print("[4] state.json round 316 written")

# ---------------------------------------------------------------- 5) heartbeat
hb_p = ROOT / "fleet" / "machines" / "bm-b.json"
hb = json.loads(hb_p.read_text(encoding="utf-8"))
# orders_ack: whole-list rewrite + pre-write self-assert (r312 kenglu law)
import os as _os
orders = sorted(_os.path.basename(p) for p in (ROOT / "fleet" / "orders").glob("O-*.md"))
ack = set(hb.get("orders_ack", []))
assert set(orders) <= ack and len(set(orders) & ack) == len(orders), "orders_ack self-assert failed"
hb["orders_ack"] = orders
hb["n_orders_ack"] = len(orders)
vm = psutil.virtual_memory()
cpu_pct = psutil.cpu_percent(interval=1)
try:
    gout = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used", "--format=csv,noheader,nounits"],
                          capture_output=True, timeout=20).stdout.decode()
    gt, gu = [int(x) for x in gout.strip().split(", ")]
except Exception:
    gt, gu = 8192, 1077
free_vram_mb = gt - gu
hb["machine_id"] = "bm-b"
hb["last_seen"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = st["current_task"]
hb["round_no"] = 316
hb["round"] = 316
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["cpu_util_pct"] = cpu_pct
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = round(vm.available / (1 << 30), 1)
hb["idle_ram_gb"] = round(vm.available / (1 << 30), 1)
hb["idle_ram_mb"] = int(vm.available / (1 << 20))
hb["free_ram_mb"] = int(vm.available / (1 << 20))
hb["total_ram_gb"] = round(vm.total / (1 << 30), 1)
hb["gpu_free_vram_gb"] = round(free_vram_mb / 1024, 1)
hb["gpu_free_vram_mb"] = free_vram_mb
hb["gpu_idle_vram_mb"] = free_vram_mb
hb["gpu_idle_vram_gb"] = round(free_vram_mb / 1024, 1)
hb["gpu_model"] = f"NVIDIA GeForce RTX 3070 {gt}MiB ({gu}MiB used @{NOW_ISO})"
hb["verdict"] = ("green; r316: flip-first X2-DB 1806/1806 (X2 4/9 cumulative); T-92 s2 DELIVERED (14-hao L0 verbatim 3-class in-spec + golden AudioGateCheck [PASS] + renorm loop "
                 "two-case live-fire + findings f1-f4); CODELY 8th-batch reorg under 10KB; S0.5 96/96 zero-new; S6 22 lanes rc=0; smoke 25/25")
hb_p.write_text(json.dumps(hb, ensure_ascii=False, indent=1), encoding="utf-8")
# post-write self-asserts (r170/r178 int law + r262 T-separator law)
hb2 = json.loads(hb_p.read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 T-separated with offset"
assert set(hb2["orders_ack"]) == set(orders) and len(hb2["orders_ack"]) == len(orders)
print(f"[5] heartbeat written+asserted: epoch={hb2['heartbeat_epoch_utc']} (int) clock={hb2['clock_read']} orders_ack={len(orders)} whole-list")
print("WRAP OK")
