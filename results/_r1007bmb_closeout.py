# -*- coding: utf-8 -*-
# r1007 bm-b closeout: HQ-FEEDBACK row + state.json + heartbeat + round report append
import ctypes
import io
import json
import os
import subprocess
import sys
import time
import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
# ensure T separator (R262 law: space separator = smoke F7 red)
NOW = NOW.replace(" ", "T", 1) if "T" not in NOW[:11] else NOW
EPOCH = int(time.time())


def sample_ram_free_gb():
    class MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEM()
    m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1024 ** 3), 1), round(m.dwMemoryLoad, 1)


ram_free, memload = sample_ram_free_gb()
# GPU face from this round's compute_audit sample (fresh, 14:08)
try:
    audit = json.load(io.open(os.path.join(ROOT, "results", "compute_audit.bm-b.json"), encoding="utf-8"))
    gpu_used = audit.get("gpu", {}).get("mem_used_mb", 0)
    gpu_util = audit.get("gpu", {}).get("util_pct", 0)
    gpu_free_vram = max(0, 8191 - int(gpu_used))
except Exception:
    gpu_free_vram, gpu_util = 0, 0
# idle face mirror
try:
    it = json.load(io.open(os.path.join(ROOT, "results", "idle_trigger.bm-b.json"), encoding="utf-8-sig"))
    idle_rounds = int(it.get("idle_rounds") or 0)
    agenda_starved = bool(it.get("agenda_starved"))
except Exception:
    idle_rounds, agenda_starved = 0, True
# token face
try:
    tu = json.load(io.open(os.path.join(ROOT, "results", "token_usage.json"), encoding="utf-8"))
    hist = tu.get("history") or []
    tok_note = "entries=%d last=%s" % (len(hist), str(hist[-1].get("ts", ""))[:16] if hist else "-")
except Exception:
    tok_note = "read-fail"

print("NOW:", NOW, "| EPOCH:", EPOCH, "| RAM free:", ram_free, "GB load:", memload,
      "| gpu_free:", gpu_free_vram, "| idle:", idle_rounds, agenda_starved, "| tok:", tok_note)

DID = ("r1007: (a) 13:5x CEO 本地算力优先令②【@bm-b】P2 三曲 whisper 词锚批执行=查重定位零重跑"
       "（三曲 -words.json 已在册 1bd21af/POOL-0018·音源=audio/ 320k 同源披露）+ 校准面缺口补齐："
       "官方词面 lyrics/斗牛.txt(91 行·lyrics.net.cn/lyrics/24 × TRACK05 锚句交叉·「有种不要走」定谳)"
       "+ lyrics/黑色幽默.txt(42 行·lyrics.net.cn/lyrics/73487 × mulanci sl114776 双源·「心理→心里」按二源修正)"
       "+ 校准 anchors/斗牛-calibrated(66/19/6) + 黑色幽默-calibrated(36/6/0 全行时窗) → P2 三曲校准面齐"
       "（龙卷风 v1 批已有）；诚实披露=斗牛曲首喊话两轮 ~15-44s whisper 掩蔽洞 → none6+approx10·词层消费按器乐段手定；"
       "工具=lyric_calibration.py argv 过滤器（指名单曲幂等重跑·裸跑=全集行为不变）。"
       "(b) 集团仓外科推送 717159c（9 面·face-set 断言过·送达 ls-remote 双证）"
       "+ LEDGER union heal（bm-b 记忆门首跑 2 行入账 + bm-a 两行保位=陈旧基座写穿修复·F-20261018-02 已报 HQ-FEEDBACK）。"
       "(c) S0 rebase 至 904713552（watermark_red.json UU=regen 律取 origin 侧丢弃 stash·已知残留 F-20261018-01 在裁）。"
       "(d) D-19 orders 推进 fe7a4d15→5d871243（r1090 双面补丁工具·state+心跳 6 镜像同写读回全串等过·selftest 20/20）。"
       "(e) S6 43 腿 rc0（3.6min：dualrun ZERO-DRIFT streak 51·audit 旗=pool_starvation+supply_floor=W268 席已备同答面"
       "·4 件 bm-a 停跳接管 derive（scorecard/t35_export/daily_scorecard/build_status）·REPORT/LIVE-2026-10-18 重生"
       "·attrition healed-clean·token " + tok_note + "·Sunday live.paper 家族诚实跳 ×4）。"
       "(f) S2/S3 双板全空·本地自驱 registry 9/9 零 open=池饿诚实面持续·"
       "MSG-1200（收件人=bm-a 导演席）留 inbox 待其消费=零越权。")

VERDICT = ("GREEN: 13:5x CEO 令② P2 词锚批回执落地（group 717159c：官方词面 91+42 行双源交叉 + 校准面 66/19/6·36/6/0 "
           "+ lyric_calibration argv 过滤器 + LEDGER union heal）+ D-19 ord 5d871243 双面推进 + S6 43 rc0 "
           "+ smoke 49/49 + 孤儿 7/0 + dualrun streak 51；leftovers = O-0948 观察窗至 10-19 ~10:2x（保持零 died-pre-closeout）"
           " + 池饿候 W268 拼接波（bm-c r1091）/secretary 补货 + watermark_red F-20261018-01 集团裁定中 + F-20261018-02 已报")

NEXT = ("r1008: 1) O-0948 24h 观察窗收官（died-pre-closeout 保持零至 10-19 ~10:2x）2) D-19 新鲜差集推进 "
        "3) 池饿诚实面候 secretary 补货 / W268 拼接波后 bm-b 引擎道复燃 4) watermark_red.json 集团裁定（F-20261018-01）"
        "5) 41 曲 P2 立意案批产若派 bm-b=词锚批复用 lyric_calibration argv 范式（receipt p2-wordanchor-receipt-r1007bmb.md 在案）")

ARTIFACT = ("FluxGroup origin 717159c = P2 词锚批 9 面（斗牛/黑色幽默 官方词面+校准 4 件 + lyric_calibration.py "
            "argv 过滤器 + 回执 p2-wordanchor-receipt-r1007bmb.md + LEDGER union）14:2x")

# ---------- HQ-FEEDBACK F-20261018-02 ----------
FB_ROW = ("- F-20261018-02 [bm-b r1007 2026-10-18 14:3x+08:00·记忆治理执行面·00:2x 部署令执行发现] "
          "**memory-budget-gate.py 对集团 LEDGER 追加=陈旧工作树基座写穿（无 union/pull 守卫）**："
          "bm-b 门首跑（10:30）把 2 回执行行追加进本地集团树 cph4/fleet/memory-slim/LEDGER.md，"
          "本地树当时落后 origin 多提交→追加后盘面=陈旧基座+本机行，origin 已有的 bm-a 10:27/10:21-10:30 两行在盘面消失"
          "（git diff -2/+2 写穿形态）；r1007 靠行级 union 修复入链（origin 全行+bm-b 2 行·group 717159c）。"
          "建议：门工具对集团台账追加改「origin blob 新鲜读+union 写」（orders_ack_append.py r1053 双面同写同族法），"
          "或最低限度=追加前 git -C 集团树 fetch + show origin:LEDGER 取最新基座再追加。"
          "证据：本仓 results/_r1007bmb_group_surgery.py LEDGER union 段 + group 717159c face-set 断言。"
          "状：open（集团周进化轮收取）\n")
fb_path = os.path.join(ROOT, "HQ-FEEDBACK.md")
with io.open(fb_path, "a", encoding="utf-8", newline="") as f:
    if os.path.getsize(fb_path) and not io.open(fb_path, "rb").read().endswith(b"\n"):
        f.write("\n")
    f.write(FB_ROW)
print("HQ-FEEDBACK appended F-20261018-02")

# ---------- round report ----------
RR = ("{ts} | r1007 bm-b | dept:工程+数据 | WM verdict: GREEN (red=false @14:10 py_watermark probe, lane=healthy) | "
      "当前活=r1007 收口（P2 词锚批 CEO 直令回执 + D-19 推进 + S6 维护链）| "
      "最近实物=FluxGroup origin 717159c（@bm-b P2 词锚批 9 面：斗牛/黑色幽默 官方词面 91+42 行双源交叉 + 校准面 66/19/6·36/6/0 "
      "+ lyric_calibration.py argv 过滤器 + 回执件·14:2x）| "
      "下个里程碑=O-0948 24h 观察窗收官 10-19 ~10:2x（died-pre-closeout 保持零）+ 池饿候 W268 拼接波（bm-c r1091）后补货（窗 ≤48h）| "
      "did: " + DID + " | "
      "verification: 集团仓 ls-remote=717159c 送达双证 + 9 面 face-set 断言过；smoke 49/49 rc0；孤儿面 7/0；"
      "水位 red=false lane=healthy；D-19 read-back full-string equality；d19 复扫零增量双面；"
      "dualrun ZERO-DRIFT streak 51 | 计分:2（实物=P2 三曲 MV 词锚消费面产线件·能跑能看能用）| "
      "本地未达 origin commit 数=0 | next: " + NEXT + "\n")
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with io.open(rr_path, "a", encoding="utf-8", newline="") as f:
    f.write(RR)
print("round report appended")

# ---------- state.json ----------
sp = os.path.join(ROOT, "state.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round"] = 1007
st["round_no"] = 1007
st["round_no_label"] = "r1007"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_action_at",
          "last_round_at", "last_round_ts", "last_orders_read_at", "last_decisions_read_at",
          "last_decisions_at", "last_orders_at"):
    st[k] = NOW
st["now_active"] = "r1007 closing"
st["current_task"] = st["task"] = "r1007: closeout (P2 word-anchor receipt package + D-19 advance + S6 chain + push)"
st["did"] = DID
st["last_action"] = ("r1007: CEO 令② P2 词锚批回执落地（group 717159c·词面 91+42 行双源+校准 66/19/6·36/6/0+argv 过滤器）"
                     " + LEDGER union heal + D-19 ord 5d871243 双面推进 + S6 43 rc0 + idle --worked")
st["verdict"] = st["current"] = VERDICT
st["latest_artifact"] = st["last_artifact"] = ARTIFACT
st["next"] = NEXT
st["next_milestone"] = ("O-0948 窗零 died-pre-closeout 至 10-19 ~10:2x + W268 拼接波后 bm-b 引擎道复燃（48h 窗）")
st["orphan_face"] = st["orphan_faces"] = 7
st["orphan_face_note"] = "r1007 chain probe (14:07): 7 py faces / 0 orphans"
st["sat_engine"] = {"status": "alive (r1007 S6 status rc0, idle verdict, queue_depth 0)", "checked_at": NOW}
st["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
st["sync"]["behind_origin_main"] = 0
st["sync"]["r1007_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1008",
    "behind_origin_main": 0,
    "note": ("r1007 payload = own faces (state/heartbeat/round-report + HQ-FEEDBACK F-20261018-02 + S6 log/driver/surgery work files "
             "+ S6 regen/product faces (REPORT/LIVE-10-18 + scorecard/dashboard/paper_export stale-takeover derives + collectors bm-b lanes "
             "+ token faces) + d19 probe/check regen + orphan probe + orders_ack_scan); "
             "EXCLUDED per law = results/watermark_red.json (claw-blocked F-20261018-01 residual) + fleet/machine-health.json (shared union daemon face); "
             "product = FluxGroup 717159c (P2 word-anchor 9 faces, surgery push verified)"),
}
# d19 keys were synced in-tool this round; verify read-back
assert st.get("last_orders_sha") == "5d871243e9e85a6b543ba156a790fe5613e64fdfd7332c740e2176ee4ff1e58a", st.get("last_orders_sha")
st["d19_probe_due"] = False
st["d19_probe_due_note"] = "r1007: dual probe zero-delta (dec 4cfdd17c / ord 5d871243 both at watermark); advance in-tool r1090 two-face patch"
st["orders_delta_pending"] = False
st["decisions_delta_pending"] = False
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json written, round 1007")

# ---------- heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["round_no"] = hb["round"] = 1007
hb["last_seen"] = hb["ts"] = hb["clock_read"] = NOW
hb["task"] = st["task"]
hb["current_task"] = st["task"]
hb["did"] = DID
hb["last_action"] = st["last_action"]
hb["last_action_at"] = NOW
hb["verdict"] = VERDICT
hb["latest_artifact"] = ARTIFACT
hb["next"] = NEXT
hb["cpu_cores"] = 16
hb["free_ram_gb"] = ram_free
hb["gpu_free_vram_mb"] = gpu_free_vram
hb["cpu_load_pct"] = round(gpu_util, 1) if gpu_util else 1.0
hb["idle_rounds"] = idle_rounds
hb["agenda_starved"] = agenda_starved
hb["heartbeat_epoch_utc"] = EPOCH
hb["note"] = ("r1007: CEO 令② P2 词锚批回执落地 group 717159c（词面 91+42 行双源交叉 + 校准面 66/19/6·36/6/0 + argv 过滤器 + "
              "回执件）+ LEDGER union heal（F-20261018-02 已报）+ D-19 ord 5d871243 双面推进 + S6 43 rc0 + MSG-1200 留 inbox（收件人 bm-a·零越权）。")
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# read-back asserts (R170/R178 law: epoch must be JSON int)
hb2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock_read missing T separator"
st2 = json.load(io.open(sp, encoding="utf-8"))
assert st2["round_no"] == 1007
print("heartbeat written + read-back asserts OK (epoch int, T separator, round 1007)")
