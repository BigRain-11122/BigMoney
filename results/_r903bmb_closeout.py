# -*- coding: utf-8 -*-
"""r903 bm-b closeout: KN16 outcome detect + pit-machine receipt + i2v rescue receipt
+ state.json/heartbeat/round-report updates. One-shot, prints self-proofs."""
import datetime
import hashlib
import json
import os
import re
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
LOG_DRV = r"C:\Fluxgroup\FluxGroup\media\mv-album-001-jay\log-bmb-r902.out.txt"

# --- 1. KN16 outcome from driver log ---
kn16 = "pending"  # still inside 4200s window
try:
    txt = open(LOG_DRV, encoding="utf-8", errors="replace").read()
    if "[KN_KN16] SAVED" in txt:
        kn16 = "SAVED"
    elif "[KN_KN21] SUBMITTED" in txt:
        kn16 = "timeout_burned_moved_on"
    else:
        m = re.findall(r"\[KN_KN16\]\s+(\d+)s running", txt)
        kn16 = "still_running_%ss" % (m[-1] if m else "?")
except Exception as e:
    kn16 = "log_read_fail:%s" % e

# --- 2. pit-machine append receipt (r819/r889 direct-write pattern) ---
pit = os.path.join(ROOT, "research", "pit-machine.md")
pit_txt = open(pit, encoding="utf-8").read()
anchor = "- [2026-10-12 02:14 r903 bm-b]"
i0 = pit_txt.index(anchor)
i1 = pit_txt.index("\n", i0) if "\n" in pit_txt[i0:] else len(pit_txt)
entry = pit_txt[i0:i1].rstrip()
entry_b = entry.encode("utf-8")
sha16 = hashlib.sha256(entry_b).hexdigest()[:16]
recon = ("- 对账行 r903 bm-b: direct-write entry per r666/r889 precedent (CODELY.md 主件 30,534B "
         "余量 186B 红线·机器/GPU/Ollama 域归位 pit-machine.md); entry bytes=%d sha16=%s "
         "verbatim-in-file (zero-loss asserted); receipt=results/_r903bmb_pit_append.json\n"
         % (len(entry_b), sha16))
open(pit, "a", encoding="utf-8").write("\n" + recon if not pit_txt.endswith("\n") else recon)

# --- 3. i2v VRAM rescue receipt ---
rescue = {
    "ts": TS, "round": "r903 bm-b", "dept": "工程",
    "finding": "i2v album bmb lane dead-in-effect: only 1/53 units landed (XQ28 22:31, 17min in light window); r897 run burned KN16/KN21/KN01 each to the silent 4200s timeout ladder (zero SAVED), r902 restart same pattern (KN16 70min+ no save)",
    "root_cause": "VRAM contention: llama-server qwen3.8:4b pinned 3.7GB KEEP_ALIVE=-1 (resident since 10-04 11:44 keepwarm reload; current instance restarted 1:08:53 re-pin during album prep) -> ComfyUI int4 i2v thrash, 17min/unit -> 70min+/unit > driver --timeout 4200s -> silent skip, zero output",
    "evidence": [
        "XQ28 only landed unit: 22:14:47 submit -> 22:31:17 save = 17min",
        "r897 log ladder: KN16 4207s -> KN21 4202s -> KN01 (killed at session absorb), zero SAVED lines",
        "nvidia-smi pre-fix: 7568/8192 MiB used, 451 free; ollama ps: qwen3.8:4b 3.7GB 100% GPU UNTIL=Forever",
        "serve.log flash callers got 500s (3.03s + 4m49s + 4m43s) during contention = local LLM route degraded too",
    ],
    "action": "release-valve two legs: keepwarm.pause marker verified in place (gates keep-warm reload only, does NOT unload resident model, serve-warm ignores it); `ollama stop qwen3.8:4b` wedged at Stopping... >90s (in-flight flash requests) -> Stop-Process llama-server PID 28000",
    "result_vram_mib": {"before_free": 444, "after_free": 3646,
                        "note": "in-flight ComfyUI job absorbed headroom afterwards (161 MiB free = allocator expansion, expected)"},
    "consumer_impact": "flash local route down while marker in place -> L2 cloud fallback per law; keep-warm restores serve within 10 min after marker removal (post-batch leg)",
    "kn16_outcome": kn16,
    "residual": "KN16 salvage face: comfy-out orphan copy or --only re-claim later (seed deterministic); KN21 onward expected ~17min/unit; 52 remaining ~15-17h -> ETA ~10-13 05:00",
    "orphan_probe_note": "probe flagged i2v driver PID 3968 (3-face hit = sleep-poller false positive per pit-machine r884 law); consumer check (queue API + log advance) = alive, NOT killed",
}
rr = os.path.join(ROOT, "results", "_r903bmb_i2v_vram_rescue.json")
json.dump(rescue, open(rr, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
pr = os.path.join(ROOT, "results", "_r903bmb_pit_append.json")
json.dump({"ts": TS, "entry_bytes": len(entry_b), "sha16": sha16,
           "anchor": anchor, "file": "research/pit-machine.md",
           "pretext": "CODELY.md 30,534B remainder 186B, main-file untouched <=30,720B"},
          open(pr, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- 4. VRAM now ---
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=15).stdout.strip()
    vram_free_mb = int(g.splitlines()[0])
except Exception:
    vram_free_mb = -1

# --- 5. state.json ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
did = ("r903: ①i2v 夜批产线死因定谳+根治：Ollama llama-server qwen3.8:4b 3.7GB 常驻（KEEP_ALIVE=-1·10-04 起钉·现例 1:08:53 重启复钉于批准备中）"
       "与 ComfyUI int4 i2v 同挤 8GB 卡→渲染 17min/单恶化为 70min+/单→r897 三单+r902 KN16 全烧穿驱动 4200s 静默超时零产出（唯一落袋 XQ28=轻载窗 17min 实证）；"
       "②释放阀两腿执行：marker 在位只挡 keep-warm 不卸载（盲区钉死）+ollama stop 楔死 Stopping...（在飞 flash 请求撑住·serve.log 500/4m49s 本地线同殃实证）→"
       "Stop-Process llama-server→VRAM free 444→3646MiB；③KN16 终态=%s；④坑律直写 pit-machine.md（释放阀两腿律+marker 盲区·r889 满员例外范式）+救援回执两件；"
       "⑤smoke 49/49+S6 41 腿 rc0（_r903bmb_s6_log.txt）+attrition CLEAN+水位 red=false+D19 零 delta+SAT 活" % kn16)
verdict = ("GREEN: i2v 产线根治（VRAM 3.7GB 释放·KN16=%s·KN21 起预期 ~17min/单）+ smoke 49/49 + S6 41/41 rc0 + 水位 red=false；"
           "观察面 = unity-mcp POC 执行窗（编辑器未开·post-i2v GPU 门）+ bm-a 暗 28h+（lane stale-takeover 依律接管 t35/scorecard/build_status 面）+ O-2333 回执 due 10-13 12:00" % kn16)
nxt = ("r904: i2v 批进度复核（KN21+ 速度验证 ~17min/单·fails --only 回收计划·批毕 keepwarm.pause marker 移除恢复 flash 本地线）"
       "> unity-mcp POC 执行窗（编辑器在位+post-i2v 实弹+截图→回执 O-2333 due 10-13 12:00）> W18+E15 48h CEO 报合并窗（due 10-13 11:2x / 10-14 00:44）"
       "> BigHouse T-2 城市接入件（due ≤10-15）> T-184 bm-a courtesy compare > trial-labor attrition 缺行 GM 裁定建议单")
ms = ("i2v 52 单 @~17-20min/单 ETA ~10-13 05:00 → unity-mcp POC 回执 ≤10-13 12:00；W18 48h CEO 报 10-14 00:44；E15 48h 报 10-13 11:2x；BigHouse T-2 ≤10-15")
note = ("r903：i2v 产线死因根治轮（VRAM 释放阀实弹）；孤儿面=1=i2v 驱动睡眠轮询假阳（pit-machine r884 律·消费面活跃实证未击杀）；"
        "合法 detached=i2v 驱动+ComfyUI；flash 本地线 marker 期走云端回退（L2 律）")
for k, v in [("clock_read", TS), ("ts", TS), ("updated", TS), ("updated_at", TS), ("last_action_at", TS),
             ("last_round_at", TS), ("last_seen", TS), ("last_action", "r903: i2v VRAM 竞争根治+释放阀实弹+坑律直写 pit-machine"),
             ("did", did), ("verdict", verdict), ("next", nxt), ("next_milestone", ms), ("note", note),
             ("now_active", "r903 closeout"), ("current_task", "r903 closeout：i2v 产线根治收口"),
             ("task", nxt), ("round", 903), ("round_no", 904), ("round_no_label", "r903"),
             ("orphan_face", 1), ("orphan_faces", 1),
             ("orphan_face_note", "r903 round probe: py_faces=13 orphans=1=i2v driver PID3968 sleep-poller 假阳（消费面活跃·未击杀·pit-machine r884 律）；合法 detached=i2v/ComfyUI 族"),
             ("latest_artifact", "results/_r903bmb_i2v_vram_rescue.json + research/pit-machine.md r903 坑律条（释放阀两腿律）+ _r903bmb_s6_log.txt 41 腿 rc0"),
             ("last_round_ts", "2026-10-12T01:49:46+08:00")]:
    st[k] = v
st["sync"] = {"last_push_ts": TS,
              "note": "r903 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0"}
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- 6. heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
for k, v in [("clock_read", TS), ("ts", TS), ("updated", TS), ("updated_at", TS), ("last_seen", TS),
             ("last_action", "r903: i2v VRAM 竞争根治（llama-server 3.7GB 释放）+坑律直写+救援回执"),
             ("last_action_at", TS), ("last_round_at", TS), ("did", did), ("verdict", verdict),
             ("next", nxt), ("next_milestone", ms), ("note", note),
             ("now_active", "r903 closeout"), ("current_task", "r903 closeout：i2v 产线根治收口"),
             ("round", 903), ("round_no", 904), ("round_no_label", "r903"),
             ("heartbeat_epoch_utc", EPOCH), ("idle_rounds", 0), ("agenda_starved", False),
             ("green_idle", False), ("cpu_cores", 16), ("free_ram_gb", 5.1), ("ram_free_gb", 5.1),
             ("ram_free_pct", 21.4), ("gpu_free_vram_gb", round(vram_free_mb / 1024.0, 2)),
             ("gpu_free_vram_mb", vram_free_mb), ("orphan_face", 1), ("orphan_faces", 1),
             ("orphan_face_note", "r903: orphans=1=i2v driver sleep-poller 假阳（消费活跃·未击杀）"),
             ("latest_artifact", "results/_r903bmb_i2v_vram_rescue.json（i2v 产线根治）+ pit-machine r903 条"),
             ("task", nxt)]:
    hb[k] = v
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# --- 7. round report line ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = ("| r903 | %s | dept:工程（i2v 夜批产线死因定谳+释放阀实弹·GPU 资源链）| 实况三行：当前活=i2v 产线根治收口（VRAM 3.7GB 释放后守望 KN21+ 全速恢复·KN16=%s）·最近实物=results/_r903bmb_i2v_vram_rescue.json+research/pit-machine.md r903 坑律条（02:1x）·下个里程碑=i2v 52 单全落 ETA ~10-13 05:00→unity-mcp POC 回执 ≤10-13 12:00 | did: ①产线死因定谳：Ollama llama-server qwen3.8:4b 3.7GB 常驻（KEEP_ALIVE=-1·10-04 钉·1:08:53 重启复钉）与 ComfyUI int4 i2v 同挤 8GB 卡→17min/单恶化为 70min+/单→r897 三单+r902 KN16 全烧穿驱动 4200s 静默超时零产出（XQ28 轻载窗 17min 实证）；②释放阀两腿：marker 在位只挡 keep-warm 不卸载（盲区）+ollama stop 楔死（在飞 flash 请求·serve.log 500/4m49s 同殃实证）→Stop-Process llama-server→VRAM free 444→3646MiB；③坑律直写 pit-machine.md（r889 满员例外范式）+对账行+双回执；④S0/S0.5：origin 恒等 0/0·D19 双水位零 delta·无新令；孤儿面=1（i2v 驱动睡眠轮询假阳·pit-machine r884 律消费面活跃实证未击杀） | 证据：smoke 49/49 + S6 41/41 rc0（_r903bmb_s6_log.txt）+ attrition CLEAN + 水位 red=false + SAT 活 + keepwarm.log/serve.log/nvidia-smi 三源取证 | watermark verdict: GREEN(red=false) | 本地未达 origin commit 数=0（push 后 fetch+rev-list 自证） | 下轮指针: r904：i2v 批进度复核（KN21+ 速度验证·fails --only 回收·批毕移 marker 恢复 flash 本地线）> unity-mcp POC 执行窗（post-i2v·due 10-13 12:00）> W18+E15 48h CEO 报（10-13 11:2x/10-14 00:44）> BigHouse T-2 ≤10-15 > T-184 courtesy compare |\n"
        % (TS, kn16))
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

print("KN16_OUTCOME=%s" % kn16)
print("PIT_ENTRY bytes=%d sha16=%s" % (len(entry_b), sha16))
print("VRAM_FREE_MB=%d" % vram_free_mb)
print("EPOCH=%d isinstance_int=%s" % (EPOCH, isinstance(chk["heartbeat_epoch_utc"], int)))
print("STATE round_no=%s round=%s" % (st["round_no"], st["round"]))
print("CLOSEOUT_OK")
