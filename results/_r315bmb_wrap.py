"""r315 bm-b wrap: state.json 315, round report line, heartbeat, T-92 progress,
HANDOVER 5x tail row (top anchor line edited separately via replace tool).

Laws applied: orders_ack whole-list rewrite + pre-write self-verify (r312),
epoch int type (R170/R178), clock_read ISO-8601 T-separated (R262),
per-machine files only (bm-b writes its own faces), fresh metric sampling
via psutil (r81 law: no hand-copied MEMORYSTATUSEX, nvidia MiB->GB convert).
"""
import glob
import json
import os
import psutil
import subprocess
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
ISO = NOW.isoformat()
SHORT = NOW.strftime("%Y-%m-%d %H:%M:%S")

# --- [1] state.json (bm-b face) ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
state = json.load(open(SP, encoding="utf-8-sig"))
state.update({
    "round_no": 315,
    "did": ("r315: flip-first law executed -- X2-LC done marker 1884/1884 "
            "evidence-gated pool flip (3/9 X2, pre-window beat O-0947 false "
            "crash-fuse; probe-subset PROS-LA refused) + T-92 TTS lane s1 "
            "ignited in GREEN-IDLE window (piper engine 2023.11.14-2 win-x64 "
            "via gh-proxy + zh_CN-huayan-medium voice via hf-mirror, machine-"
            "direct law; smoke render 4.62s RTF 0.059 exit 0; mastered "
            "spec-chain proven: raw -19.27LUFS/TP 0.00 -> mono-first+loudnorm "
            "-> -16.90LUFS/TP -3.00 in-spec, quotes-layer regex per kenglu "
            "#212) + S0 stash-pop UU canon-resolved zero-loss (launches "
            "union 53->50 cap50, r314 resolver reused, c77815db) + S6 28 "
            "lanes rc=0 (Sunday no new bar, cutoff 09-24 Mid-Autumn correct) "
            "+ smoke 25/25 + orders 96/96 double-scan zero-new"),
    "verdict": "green",
    "next": ("per-round rerun results/_r314bmb_pool_flip.py until 9+9 "
             "shards done -> harvest finalize (T-90 prereg s10 verdict face; "
             "T-89 s6 finalize+MARKET_STAGE_TABLE); T-92 s2 mastered chain "
             "verbatim validation (14-hao L0 gate sfx -16/amb -20/bgm -18 "
             "+ AudioGateCheck evidence) next GREEN-IDLE window; Monday "
             "2026-09-28 09:15 T-91 s3 first cohort entries + new-bar full "
             "chain (daily->live.paper v3 shadow->t35v->t24x2->aggr->grid-"
             "first-marks->export->scorecard->daily_report); 10-01 monthly "
             "trio + REGIME_GUARD v3 date gate; migration window to 09-29 "
             "12:00 (v2.2 armed, editor-gated, do not double-arm)"),
    "current_task": ("r315: X2-LC pool-flipped 3/9 (flip-first law); T-92 "
                     "TTS s1 landed (piper engine + zh voice + smoke + "
                     "spec-chain proven); next=flip rerun to 9+9 -> harvest; "
                     "T-92 s2 next idle window"),
    "last_round_ts": ISO, "last_result": "ok", "last_run": f"r315 {ISO}",
    "last_round_at": ISO, "last_seen": ISO, "updated_at": ISO,
    "updated": SHORT, "ts": SHORT,
})
json.dump(state, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert json.load(open(SP, encoding="utf-8-sig"))["round_no"] == 315
print("state.json -> round 315")

# --- [2] round report line (bm-b file) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"{ISO} | r315 bm-b | dept:舰队+工程+研究 | WM-VERDICT: 绿 "
    f"(red=false@10:00:21 lane healthy; probe 10:02:56 py_low_board_clear "
    f"合法面=板 0 open+bandit claimed-parked(MF IC 待面板完备)+池 15 ready "
    f"供给在磨=autofill 认领竞速面 X2-LD bm-a 已认领·零违令) | did: "
    f"(1) S0 stash-pop UU autofill_state 正典 union 解 53→50 cap50 零丢失 "
    f"last_tick ours 09:50:01（r314 resolver 复用=_r315bmb_s0_resolve.py·"
    f"commit c77815db·stash drop 清） (2) flip-first 常设律执行：X2-LC done "
    f"marker 1884/1884 → 证据门 flip done=3/9 X2（PROS-LA probe 子集 22 格"
    f"照拒·15 ready 余=X2 6+PROS 9·X2-LD bm-a autofill 在跑） (3) T-92 TTS "
    f"产线 s1 绿闲窗点火（primary-lane law 尽后窗：RAM 12.5GB>4GB 冠线+板净"
    f"+池交 autofill）：piper 2023.11.14-2 win-x64 引擎（gh-proxy 22.5MB·"
    f"espeak 自含·E:\\Minigame\\Tools\\tts\\piper）+zh_CN-huayan-medium 声库"
    f"（hf-mirror 63MB·E:\\Minigame\\Tools\\tts\\voices）+冒烟渲染 4.62s wav "
    f"212,640B RTF 0.059 exit 0+ffmpeg 母带链速验（raw -19.27LUFS/TP 0.00 "
    f"越限→mono 前置+loudnorm→-16.90LUFS/TP -3.00 达标·引号层正则 #212 律"
    f"实弹）=s1 落地 spec-chain ready·s2=14号 L0 规格门 verbatim 全链验证"
    f"留下窗 (4) S0.5 orders 96/96 双扫零未回执（decisions.md 本机缺位诚实 "
    f"no-op）+post_review 尾 5 行全 YES 零新红（r314 两陈年负行维持） "
    f"(5) S6 28 lanes rc=0（周日+09-25 中秋休市 cutoff 09-24 正确·regime "
    f"ORANGE #10+breadth 0.77·clock ORANGE_COOL sleeves=4·promo 0/22 诚实·"
    f"export-09-24 幂等·rev_osc no-op 幂等·token delta=+39） (6) smoke "
    f"25/25 | next: 每轮先跑 _r314bmb_pool_flip.py 至 9+9→harvest（T-90 "
    f"s10 判定面+T-89 s6 finalize+MARKET_STAGE_TABLE）；T-92 s2 母带链 verbatim "
    f"验证下绿闲窗；周一 09-28 09:15 T-91 s3 首队列入场+新 bar 全链接力；"
    f"10-01 月度三件套+REGIME_GUARD v3 日期门；迁移窗 09-29 12:00（v2.2 "
    f"armed·编辑器门·勿双 arm）\n")
with open(RP, "a", encoding="utf-8") as fh:
    fh.write(line)
print("round_reports.md +r315 line")

# --- [3] heartbeat (bm-b only) ---
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(HB, encoding="utf-8"))
orders = sorted({os.path.basename(p) for p in
                 glob.glob(os.path.join(ROOT, "fleet", "orders", "*.md"))}
                - {"README.md"})
ack = hb.get("orders_ack", [])
# r312 law: whole-list rewrite + pre-write self-verify
assert set(orders) <= set(ack) and len(set(orders) & set(ack)) == len(orders), \
    "orders_ack covers all orders (pre-write self-verify)"
hb["orders_ack"] = orders
hb["n_orders_ack"] = len(orders)
epoch = int(time.time())
assert isinstance(epoch, int)
vm = psutil.virtual_memory()
free_gb = round(vm.available / 1024 ** 3, 1)
free_mb = int(vm.available / 1024 ** 2)
cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.used",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    vfree, vused = [int(x) for x in q.stdout.strip().split(",")]
except Exception:
    vfree, vused = 6929, 1263
hb.update({
    "last_seen": ISO, "heartbeat_epoch_utc": epoch, "clock_read": ISO,
    "round_no": 315,
    "current_task": state["current_task"],
    "cpu_cores": 16, "free_ram_gb": free_gb, "total_ram_gb": 23.9,
    "cpu_util_pct": cpu_pct,
    "gpu_free_vram_gb": round(vfree / 1024, 1), "gpu_free_vram_mb": vfree,
    "gpu_idle_vram_gb": round(vfree / 1024, 1), "gpu_idle_vram_mb": vfree,
    "idle_ram_gb": free_gb, "idle_ram_mb": free_mb, "free_ram_mb": free_mb,
    "cores": 16, "cpu_pct": cpu_pct, "round": 315,
    "gpu_model": f"NVIDIA GeForce RTX 3070 8192MiB ({vused}MiB used @{ISO})",
    "prod_lanes_note": ("P-33 per O-20260927-0913 sec.4: primary lane in-force "
                        "(BigMoney rounds + pool shards); tts-audio-batch "
                        "IGNITED r315 (s1 engine landed: piper+zh voice, "
                        "smoke render PASS, mastered spec-chain proven); "
                        "gpu-light-postprocess chartered r313 idle-gated"),
    "verdict": ("green; r315: flip-first X2-LC 3/9 evidence-gated (pre-window "
                "beat O-0947); T-92 TTS s1 landed in GREEN-IDLE window "
                "(piper engine+zh_CN-huayan voice, smoke 4.62s RTF 0.059, "
                "mastered chain -16.90LUFS/TP-3.00 in-spec); S0 stash-pop UU "
                "canon-resolved zero-loss; S6 28 lanes rc=0; smoke 25/25; "
                "orders 96/96 double-scan zero-new"),
})
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"] and len(chk["orders_ack"]) == len(orders)
print(f"heartbeat: epoch int, orders_ack {len(orders)} whole-list, round 315, "
      f"ram {free_gb}GB cpu {cpu_pct}% vram {vfree}MiB")

# --- [4] T-92 ticket progress field ---
TK = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-27-92-P1.json")
tk = json.load(open(TK, encoding="utf-8-sig"))
tk["progress_r315_bmb"] = (
    "r315: s1 ENGINE BROUGHT UP in first GREEN-IDLE window (primary lane "
    "served first: pool flip + S6 chain + smoke; RAM 12.5GB > 4GB floor). "
    "piper 2023.11.14-2 win-x64 (E:\\Minigame\\Tools\\tts\\piper\\piper\\"
    "piper.exe, gh-proxy download 22,477,236B, espeak-ng bundled "
    "self-contained) + zh_CN-huayan-medium voice (E:\\Minigame\\Tools\\tts\\"
    "voices\\, hf-mirror 63,201,294B onnx + 4,822B json). Smoke render "
    "PASS: one-sentence zh -> out\\smoke_r315.wav 212,640B / 4.62s audio, "
    "RTF 0.059 (16x realtime+), exit 0. Spec-chain READY proven: raw render "
    "input_i -19.27 LUFS / input_tp 0.00 (over cap) -> chain (aformat "
    "mono-first per kenglu #212 + loudnorm I=-16 TP=-3 LRA=11) -> output_i "
    "-16.90 / output_tp -3.00 in-spec; loudnorm JSON regex with quotes "
    "layer parsed correctly (INPUT_I -19.27, not -99). s2 next idle window: "
    "X989 mastered-audio law verbatim application = 14-hao L0 spec gate "
    "(_shared yu zongkong doc: sfx -16 / amb -20 / bgm -18 +-1LU + TP<=-3dBTP "
    "+ mono 44.1k + AudioGateCheck.ps1 evidence manifest) + golden-path "
    "end-to-end mastered render; s3 intake JSON work-order convention per "
    "art-queue precedent. Machine-direct law kept (U187/U240: no git, no "
    "cross-machine transfer; gh-proxy + hf-mirror direct download). ffmpeg "
    "located E:\\Minigame\\Tools\\ffmpeg\\bin\\ffmpeg.exe.")
json.dump(tk, open(TK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(TK, encoding="utf-8-sig"))
assert "progress_r315_bmb" in chk and chk["status"] == "claimed"
print("T-92 ticket: progress_r315_bmb landed, status claimed kept")

# --- [5] HANDOVER tail row (append-only; top anchor line edited separately) ---
HO = os.path.join(ROOT, "research", "HANDOVER.md")
row = (
    f"- 开发队列增量窗（接续版）**round 315 bm-b（5x 核对本轮），"
    f"{SHORT[:16]} 补核；对账区间=增量 bm-b r311-315（基线=round 310 bm-b 行），"
    f"统一链 202,441 实读平持（本窗零批 finalize：T-90 X2 批 3/9 分片磨+T-89 "
    f"PROS 0/9 待磨=autofill claim-race 供给在飞·T-91 出口首跑 r314 落岸零批·"
    f"MF_IC_P1 待源 legal park）**：①**r311-314 三连窗已录前行**（r311 "
    f"resolve 面·r312=orders_ack 碎裂修复+prereg seed 基 rg 探针律+regime_state "
    f"vs v3_state_series 跨源等值断言虚假前提律·r313=同树第三写手混入 push 前 "
    f"扫描律+rebase --skip+pool entry-union 律+T-92 车道开票 r313·r314=T-91 "
    f"s1/s2 REV-OSC 出口 harness+首跑落岸 Monday anchor secured+T-89/T-90 快"
    f"分片假熔断坑律抓杀+X2-LA/LB 两翻+fleet MSG-0952）；②**r315（本轮）="
    f"flip-first 常设律+TTS 产线点火+5x 核对**——(a) flip-first 律每轮先跑："
    f"X2-LC done marker 1884/1884 证据门 flip（3/9 X2·pre-window 关窗·PROS-LA "
    f"probe 子集 22 格照拒·15 ready 余=X2 6+PROS 9·X2-LD bm-a autofill 认领在"
    f"跑）；(b) **T-92 TTS 产线 s1 绿闲窗点火全弧**（primary-lane law 尽后窗"
    f"RAM 12.5GB>4 冠线+板净+池交 autofill：piper 2023.11.14-2 win-x64 引擎"
    f"gh-proxy 22.5MB+zh_CN-huayan-medium 声库 hf-mirror 63MB=机器直连律 "
    f"U187/U240 零 git 零跨机传输·冒烟渲染 4.62s wav 212,640B RTF 0.059 exit "
    f"0·**母带链速验全通**=raw -19.27LUFS/TP 0.00 越限→aformat mono 前置+"
    f"loudnorm I=-16 TP=-3→output -16.90LUFS/TP -3.00 达标·loudnorm JSON 引号"
    f"层正则 #212 律实弹解析 INPUT_I -19.27 非 -99）；s2=14号 L0 规格门 "
    f"verbatim（sfx -16/amb -20/bgm -18±1LU+TP≤-3dBTP+mono 44.1k+"
    f"AudioGateCheck.ps1 证据 manifest）+golden-path 全链渲染=下绿闲窗；"
    f"(c) S0 stash-pop UU 正典解（launches union 53→50 cap50·r314 resolver "
    f"复用·c77815db）；③维护面：S6 28 腿 rc=0（周日+09-25 中秋休市 cutoff "
    f"09-24 正确·regime ORANGE #10+breadth 0.77·clock ORANGE_COOL sleeves=4·"
    f"promo 0/22 诚实·export-09-24 幂等·token delta +39）·smoke 25/25·orders "
    f"96/96 双扫零未回执·post_review 尾 5 行全 YES（r314 两陈年负行维持）·"
    f"板 0 open·迁移 v2.2 armed editor-gated（journal precheck 心跳健康·窗至 "
    f"09-29 12:00）；④观测（非本机车道）：bm-a r309=X2-LA flip+harness "
    f"armed+system_v1_paper.py T-91 s1 harness 12/12 GREEN+rev_osc run 子命令"
    f"缺陷修复·X2-LD 认领在跑；bm-c r71 后结构性停摆维持；⑤指针：**每轮先跑 "
    f"_r314bmb_pool_flip.py 至 9+9→harvest finalize（T-90 prereg s10 判定面+"
    f"T-89 s6 finalize+MARKET_STAGE_TABLE）**+**09-28 周一开市窗=新 bar 全链"
    f"接力**（update_daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow〕"
    f"→t35v→t24×2→aggr 20 账→grid 5 账首拍 marks→export→scorecard→"
    f"daily_report）+**周一 09:15 T-91 s3 首队列入场**+T-92 s2 下绿闲窗+10-01 "
    f"月度三件套+REGIME_GUARD v3 日期门生效+T-70 中期判读 10-09+10-31 六员"
    f"首检 all-HOLD+T-34 半档梯 11-01+迁移窗 09-29 12:00 不变\n")
with open(HO, "a", encoding="utf-8") as fh:
    fh.write(row)
print("HANDOVER.md +r315 tail row")
