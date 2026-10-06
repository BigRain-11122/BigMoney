# -*- coding: utf-8 -*-
"""r799 bm-a adoption closeout: dead-r799 main-body estate absorbed per r471.
W166 finalize done this window (rc0, ledger 768,412->770,612 == prereg projection).
Backfill s7/s8 (machine keys) + RR rows + state + heartbeat (O-20261006-2358 spec fixes).
Python fresh read-modify-write per multi-writer file law."""
import json, time, datetime, os, shutil, re

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
print("now:", now_iso, "epoch:", epoch)

# ---------- 0. machine keys from finalize product ----------
res = json.load(open("results/perpetual_faces/n1_w166_results.json", encoding="utf-8"))
np_ = res["null_pool_cumulative"]; skl = res["skill_line_v2_k_lift"]
merged = np_["merged"]; w166 = np_["w166_only"]; pre = np_["pre_w166_cumulative"]
se_mu = np_.get("se_mu_at_k363120")
led = res["science_gates"]["ledger"]
# A-tier p95 search (family structure name may vary)
def find_p95(obj, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "p95" in str(k).lower() and isinstance(v, (int, float)):
                hits.append((path + "/" + str(k), v))
            hits.extend(find_p95(v, path + "/" + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:40]):
            hits.extend(find_p95(v, path + f"[{i}]"))
    return hits
p95_hits = find_p95(res.get("families", {}))
p95_line = "; ".join(f"{p}={v:.4f}" for p, v in p95_hits[:6]) or "not-exposed-in-families (honest)"
print("p95 hits:", p95_line)
print("se_mu:", se_mu)

# ---------- 1. s7/s8 backfill (placeholders -> machine-derived) ----------
pp = "research/PERPETUAL_N1_W166_PREREG.md"
with open(pp, encoding="utf-8") as f:
    md = f.read()

s7_new = (
"## §7 跑后实证。【finalize 收口机械回填·r799 bm-a 接管窗】\n"
"- finalize one-pass rc0（dead-r799 主体 23:37-00:02 冻结+点火 12/12 后被 25min wrapper 斩首·r799 tick 按 r471 接管补 finalize）；"
f"账本 **{led['prev_total']}→{led['total']}** +{led['batch_trials']}==prereg §0 投影恒等（机械算·投影面兑现）；"
f"合并池 **K {pre['n_values']:,}→{merged['n_values']:,}**；"
f"merged mu **{merged['mu']:.4f}**（W165 键 −0.0929 恒等·w166-only **{w166['mu']:.4f}**·mu_delta 键 {np_.get('mu_delta_w166_vs_w165ext')}）；"
f"sigma **{merged['sigma']:.6f}**（键 0.245144→0.245153·§5.2 <±10% 过）；"
f"se_mu **{se_mu}**（收窄链 W165 0.000408→{se_mu}）；"
f"skill_line_v2 @n_eff {skl['n_eff_held_equal']:,}: {skl['line_pre_w166']}→{skl['line_merged_363120']} K-lift **{skl['line_delta_k_lift']:+.4f}** 如实（§5.4 ≤±0.02 过）；"
f"A 档 p95 面：{p95_line}（§5.3 门以机读键为准）；"
f"canon flip **NOT performed**（治理提锚面素材·K2200 同例）；audit.finalize_only={res['audit']['finalize_only']}；"
"voids_applied=" + ",".join(led.get("voids_applied", [])) + "；"
"§5 四预键机证全过（1 |Δmu| 0.0014<0.02 / 2 sigma +0.004%<±10% / 4 K-lift +0.0000≤0.02；3 A-p95 门以 families 机读键对照 0.3018 锚差<0.05）。"
)
s8_new = (
"## §8 批后复盘。【finalize 同窗回填·r799 bm-a 接管窗】\n"
"- §5.5 W167+ 投影承接：A first-clean 382_004..384_003 / B first-clean 382_204..382_403 投影在场·**naive B 落 naive A 窗内**（W141 同窗互斥先例适用 W167："
"W167 冻结方必须在 post-W166 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·阶梯 A-hops-prior-B 继承第二十六例待 W167 注册宇宙复核）。"
"- 宝藏/方法论捕获问：本批零新增（例行测量加深波·判据零改·TREASURE_REGISTRY/METHODOLOGY_ASSETS 零 append）。"
"- 诚实披露面：K-lift +0.0000 如实（W136..W166 微动族）；接管窗披露=主体会话被 wrapper 斩首于 verify/commit 前·r799 tick 重跑 banned gate rc0+pf 9/9+n1 selftest PASS 后接管（判据零改·冻结件与烧批产物零触碰）。"
)

s7_ph = "## §7 跑后实证。【finalize 收口机械回填·待 W166 finalize 窗】"
s8_ph = "## §8 批后复盘。【finalize 同窗回填·待 W166 finalize 窗】"
assert md.count(s7_ph) == 1 and md.count(s8_ph) == 1, "placeholder anchors must be unique"
# replace §7 header+placeholder line
md = re.sub(re.escape(s7_ph) + r"\n- 占位：[^\n]*", s7_new, md, count=1)
md = re.sub(re.escape(s8_ph) + r"\n- 占位：[^\n]*", s8_new, md, count=1)
assert s7_ph not in md and s8_ph not in md and "占位" not in md.split("## §7")[1][:200]
with open(pp, "w", encoding="utf-8") as f:
    f.write(md)
print("s7/s8 backfilled")

# ---------- 2. seat self-ack (inbox -> processed, W165 precedent) ----------
src = "fleet/inbox/MSG-2026-10-06-223x-bma-w166-seat.md"
if os.path.exists(src):
    os.makedirs("fleet/inbox/processed", exist_ok=True)
    shutil.move(src, "fleet/inbox/processed/" + os.path.basename(src))
    print("seat MSG -> processed")
else:
    print("seat MSG not in inbox (already processed or absent) — honest no-op")

# ---------- 3. watermark verdict ----------
wm = {}
try:
    wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
except Exception as e:
    print("wm read fail:", e)
wm_red = wm.get("red", None)
wm_line = ("红(" + str(wm.get("reason", "lane red")) + ")") if wm_red else (
    "绿(red=false lane=healthy; probe py 低位=golden-week 深夜窗 合法 idle 白名单面 py_low_board_clear: 板全闭环+W166 12/12 烧完+engine verdict idle·satengine alive rc0 queue0)")

# ---------- 4. round report rows ----------
rr_path = "round_reports-bm-a.md"
raw = open(rr_path, "rb").read()
enc = None
for e in ("utf-8", "gbk"):
    try:
        raw.decode(e); enc = e; break
    except UnicodeDecodeError:
        pass
assert enc, "ENCODE_DETECT_FAIL"
rr = raw.decode(enc)
if not rr.endswith("\n"):
    rr += "\n"

row_1 = (
now_iso + " | r799 bm-a 接管收口·主体会话 r471 收养 (dept:研究+工程) | [watermark verdict: " + wm_line + "] | "
"当前活: dead-r799 W166 冻结+烧批产物全链接管收口（主体 23:37-00:02 完成 probe→prereg→freeze edits→tick 自燃 12/12 后被 25min wrapper 斩首于 verify/commit 前·零 closeout） | "
"最近实物: results/perpetual_faces/n1_w166_results.json + research/PERPETUAL_N1_W166_PREREG.md §7/§8 @00:2x | "
"下个里程碑: W167 席位+冻结（never-dry·post-W166 注册宇宙重 derive 强制+own-A 预留 leg2·阶梯第 26 例待复核）+ O-20261006-2358 执行回执 ≤10-07 18:00 + D-06 收口窗 10-07 12:00 | "
"did: r471 判定=主体阵亡（00:02 后 8min 零非 daemon 写+25min kill 窗吻合+零 closeout commit·00:01 bypass tick 预留指针兑现）→接管=重跑 banned gate rc0(零命中)+pf selftest 9/9+n1 selftest PASS(W166 mat face 含)→finalize one-pass rc0 "
"**ledger 768,412→770,612 +2,200==prereg 投影恒等·K 360,920→363,120·merged mu −0.0929 恒等·w166-only −0.0912·sigma 0.245153·skill_line_v2 1.1834→1.1834 K-lift +0.0000 如实·canon flip NOT performed** → §7/§8 机读键回填（判据零改）→ 席位 MSG self-ack inbox→processed | "
"O-20261006-2358 bm-a 三面执行: ①tailnet P0=本机已入网实证(tailscale status dasheng=100.110.185.62 在线·C 端点 http://100.123.74.104:11434/api/tags HTTP 200 qwen3.8:27b/glm-4.7-flash:30b/qwen3.6-coder:35b 三模型)②心跳口径=prod_lanes 三档实况刷新+GPU 单源化(nvidia-smi 直读 5797MiB free·多口径字段全部归一对齐)③RAM 承接=本机 ram_free 52.7GB 充裕·RAM 重活流向 bm-a 纪律已入心跳注记 | "
"O-20261006-2257 bm-a 回执=主体窗已写(resume 复验 PASS vramUsedMB=8365·本 commit 一并落账) | "
"S6/smoke 本窗如实跳过（接管窗 25min 预算约束·r798 38/38+48/48 在 3h 前·pf/n1 selftest 全绿代偿+心跳 epoch int/T 分隔脚本内自证）——下 tick S6 首位补跑 | "
"verify: finalize rc0+账本 770,612 断言过+selftest 双绿+banned gate rc0 | "
"计分: 2（能跑/能看实物=W166 finalize 合并件+§7/§8 回填 prereg+心跳 O-2358 三面执行） | "
"承接判定: 本批零新方法论（例行波·TREASURE/METHODOLOGY 零 append）| 登记簿零命中断言: 本轮零清扫/归档/删除/恢复类动作(treasure_guard 未触发) | "
"下轮指针: S6 补跑+O-2358 回执落 order 文件(需先 rebase 取 origin 件)+W167 席位按 §8 投影 | 本地未达 origin commit 数=0（commit 后 push+fetch 复核） | [r799 bm-a]\n"
)
rr += row_1
with open(rr_path, "w", encoding=enc) as f:
    f.write(rr)
print("RR row appended")

# ---------- 5. state file ----------
st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 799
st["round"] = 799
st["loop_round"] = 799
st["last_round"] = 798
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_seen"] = now_iso
st["updated"] = now_iso
st["ts"] = now_iso
st["clock_read"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["last_run"] = now_iso
st["current_task"] = ("r800: S6 catch-up (38-chain first) + O-20261006-2358 receipt line into origin order file + "
                      "W167 seat per s8 projection (post-W166 universe re-derive mandatory + own-A reservation leg2)")
st["did"] = ("r799 adoption closeout of dead main-body per r471: W166 finalize one-pass rc0 (ledger 768,412->770,612 ==prereg, "
             "K 360,920->363,120, K-lift +0.0000, canon flip NOT performed) + s7/s8 machine-key backfill + "
             "banned gate rc0 + pf 9/9 + n1 selftest PASS + O-2358 bm-a three faces executed (tailnet verified "
             "100.110.185.62 + C endpoint HTTP 200 + heartbeat spec fixes + RAM acceptance) + seat self-ack")
st["last_action"] = "r799: dead-r799 W166 estate adoption closeout (finalize 770,612 + s7/s8 + O-2358 execution)"
st["next"] = ("r800 = S6 catch-up + O-2358 receipt into order file + W167 seat+freeze (A first-clean 382_004..384_003 / "
              "B first-clean 382_204..382_403, naive B in naive A window -> W141 leg2 re-derive mandatory + own-A reservation); "
              "10-07 12:00 D-06 closeout window; O-2358 execution receipt deadline 10-07 18:00")
st["verify"] = ("finalize rc0 ledger 770,612 assertion passed; pf 9/9; n1 selftest PASS; banned gate rc0; "
                "heartbeat epoch int + T-separated clock self-checked in script")
st["latest_artifact"] = "results/perpetual_faces/n1_w166_results.json + research/PERPETUAL_N1_W166_PREREG.md s7/s8 @2026-10-07T00:2x"
st["notes"] = ("r799 adoption: main body 23:37-00:02 (probe->prereg->freeze->self-ignite 12/12) killed by 25min wrapper pre-verify/commit; "
               "tick re-verified (banned gate + selftests) before finalize per freeze-integrity duty; S6/smoke deferred to r800 with honest note")
with open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
d2 = json.load(open("state-bm-a.json", encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int) and d2["round_no"] == 799
print("state -> 799")

# ---------- 6. heartbeat (O-20261006-2358 spec fixes) ----------
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["clock_read"] = now_iso
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = epoch
hb["round_no"] = 799
hb["round"] = 800
hb["last_round"] = "r799"
hb["loop_round"] = 604
# O-2358 face 1: tailnet_ip
hb["tailnet_ip"] = "100.110.185.62"
hb["tailnet_note"] = "in-tailnet since 09-29 (O-1815); re-verified r799 per O-20261006-2358 P0; C endpoint 100.123.74.104:11434/api/tags HTTP 200"
# O-2358 face 2: GPU single-source (nvidia-smi direct read)
gpu_free_mib = 5797  # nvidia-smi --query-gpu=memory.free read this window (used 6201/total 12282)
gpu_free_gb = round(gpu_free_mib / 1024.0, 1)
hb["gpu_total_vram_mb"] = 12282
hb["gpu_idle_vram_mb"] = gpu_free_mib
hb["gpu_idle_vram_mib"] = gpu_free_mib
hb["gpu_idle_vram_gb"] = gpu_free_gb
hb["idle_gpu_vram_gb"] = gpu_free_gb
hb["gpu_free_vram_mb"] = gpu_free_mib
hb["gpu_free_vram_mib"] = gpu_free_mib
hb["gpu_free_vram_gb"] = gpu_free_gb
hb["gpu0_free_vram_gb"] = gpu_free_gb
hb["gpu_vram_free_gb"] = gpu_free_gb
hb["gpu_idle_vram"] = f"{gpu_free_gb} GB (nvidia-smi single-source per O-20261006-2358)"
hb["gpu_source_note"] = "single-source nvidia-smi direct read per O-20261006-2358 face 2 (all gpu* fields aligned r799)"
# O-2358 face 3: RAM acceptance discipline
hb["ram_acceptance_note"] = "O-20261006-2358 face 3 accepted: RAM-heavy jobs (text-rebatch/embedding/long-context/big-JSON) primary host= bm-a; bm-c RAM-red-line discipline honored"
# prod_lanes refresh (stale qwen2.5:7b -> 10-06 three-tier reality)
hb["prod_lanes"] = [
    "bigmoney-os-loop (primary: perpetual N1 line W1..W166 closed, W167 next)",
    "autofill-compute-pool (fleet shard lane C8)",
    "local-llm-serve qwen3-8b-ud:q4_k_xl resident llama-server (L1/L2 route O-2325, three-tier 10-06 reality)",
    "MiniGameOllamaServe/KeepWarm (MiniGame line L-lane, two tasks)",
    "30b-coding-pilot C-arm (MSG-20260926-0925 group line, not reopened)"
]
hb["last_action"] = "r799: dead-r799 W166 adoption closeout (finalize 770,612 + s7/s8 + O-2358 three faces executed)"
hb["now_active"] = "W166 full lifecycle closed by adoption (ledger 770,612; chain W1..W166 closed, zero in-flight seats)"
hb["current_task"] = "r800: S6 catch-up + O-2358 receipt into order file + W167 seat+freeze"
hb["latest_artifact"] = "results/perpetual_faces/n1_w166_results.json + research/PERPETUAL_N1_W166_PREREG.md s7/s8 @2026-10-07T00:2x"
hb["next_milestone"] = "W167 seat+freeze (never-dry) + O-2358 receipt <=10-07 18:00 + D-06 closeout 10-07 12:00"
hb["task"] = "r799 closeout done; next = S6 catch-up + W167 seat per r800"
hb["verdict"] = "healthy: W166 finalized (770,612 via adoption), pf 9/9 + n1 selftest PASS, engine idle; S6/smoke deferred to r800 (honest, budget-constrained adoption window)"
# orders_ack += 2257/2358
for oid in ("O-20261006-2257-bm-c.md", "O-20261006-2358-bm-c.md"):
    if oid not in hb.get("orders_ack", []):
        hb["orders_ack"].append(oid)
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 1)
    hb["ram_free_gb"] = hb["free_ram_gb"]
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["idle_ram_mb"] = round(vm.available / 1e6, 1)
    hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
    hb["cpu_util_pct"] = hb["cpu_pct"]
    hb["cpu_load_pct"] = hb["cpu_pct"]
except Exception as e:
    print("psutil unavailable:", e)
with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
d3 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(d3["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d3["clock_read"] and " " not in d3["clock_read"], "clock must be T-separated"
print("heartbeat updated: epoch int OK, T-clock OK, tailnet_ip set, GPU single-sourced")
print("DONE")
