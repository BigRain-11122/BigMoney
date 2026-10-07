# -*- coding: utf-8 -*-
"""r821 bm-a S7 closeout: state round 821, D-19 watermark repair (acc32216
bad-provenance -> origin-blob 635c3024 per r786/r813 adjudication law),
heartbeat refresh (epoch int + T-separated clock), round report line."""
import io
import json
import time
import datetime
import subprocess

# ---- state -----------------------------------------------------------------
s = json.load(io.open("state-bm-a.json", encoding="utf-8"))
assert s["round_no"] == 820, s["round_no"]
s["round_no"] = 821
s["round"] = 821
s["loop_round"] = "r821"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
s["ts"] = now_iso
s["updated"] = now_iso
s["last_round"] = 821
s["last_round_at"] = now_iso
s["last_round_ts"] = now_iso
s["last_seen"] = now_iso
s["heartbeat_epoch_utc"] = int(time.time())
s["last_decisions_sha"] = "635c3024a95e4487" + "f" * 0  # repair marker below
# exact sha from origin blob (recompute for truth, never transcribe)
b = subprocess.run(["git", "-C", "C:/Users/sjs20/Desktop/FluxGroup", "show",
                    "origin/main:docs/decisions.md"], capture_output=True).stdout
import hashlib
dec_sha = hashlib.sha256(b).hexdigest()
assert dec_sha.startswith("635c3024"), dec_sha
s["last_decisions_sha"] = dec_sha
s["last_decisions_at"] = now_iso
s["last_decisions_ts"] = now_iso
s["last_decisions_seen"] = "D-20261007-03 (newest; consumed r804/r813; zero new BigMoney dispatch since)"
s["current_task"] = ("W173 freeze chain next window: 5-face freeze edits (pf N1_BANDS[173] + n1 "
                     "WAVE_CONFIGS[173] + W173 materializer + r821 attribution) + verify 8 legs + "
                     "freeze commit + 2-tick ignite + finalize (proj ledger 786,012 / K 378,520)")
s["did"] = ("r821 W173 prereg build landed origin d76ce93d5: PERPETUAL_N1_W173_PREREG.md via "
            "token-vmap from freeze-time W172 blob 59fde9319 (generator execs truncated r819 build "
            "for exact TOK pairs, all r819 asserts re-passed live, zero writes; banned_direction_gate "
            "ADMIT rc0; A 395_404..397_403 staircase 33rd E36 hops=1 / B 397_404..397_603 own-A leg2 "
            "hops=1 per r820 probe receipt; anchor ledger 783,812 / K 376,320; proj 378,520 / 786,012; "
            "seat MSG-1122 sha 9cd8af3af path-derived honesty-noted vs r820 closeout prose 014b4ede5; "
            "ordinal divergence disclosed in-product: W172 sec5.5 anticipated 32nd, r820 receipt "
            "A_semantics machine-read THIRTY-THIRD carried per r587; W174+ projection A 397_404..399_403 "
            "/ B 397_604..397_803 naive-B-inside-naive-A, 34th staircase anticipated) + S6 37/37 rc0 "
            "(golden-week no-op tribe; dualrun ZERO-DRIFT; scorecard/REPORT/LIVE-2026-10-07/build_status "
            "refreshed; attrition CLEAN) + D-19 dec watermark repair acc32216->635c3024 "
            "(r820 bad-provenance regression, r786/r813 adjudication law; zero new content rows: "
            "newest decision D-20261007-03 targets HQ night-shift tool domain, consumed r804/r813; "
            "orders.md e9fa5da4 MATCH zero action; O-20261007-0935 bm-a leg capability inventory "
            "already receipted r817) + smoke 48/48 + push raced behind-9 absorbed by clean rebase 1/1")
s["verify"] = ("banned gate ADMIT rc0 receipt stdout; prereg 20,507B 63 CRLF token-count asserts "
               "PASS residue-zero malformed-window CLEAN; origin delivery d76ce93d5 fetch+rev-list "
               "behind0/ahead0; smoke 48/48; S6 37/37 rc0; watermark repair sha machine-recomputed "
               "from origin blob")
s["next"] = ("(1) r822=W173 freeze chain (5-face edits r815/r819 lineage -> n1+pf selftests -> freeze "
             "commit -> 2-tick ignite -> 12/12 burn watch -> finalize one-pass proj ledger 786,012 "
             "EXACT / K 378,520 EXACT + sec7/sec8 backfill) (2) W174 seat chain post-finalize "
             "(re-derive-MANDATORY on post-W173 universe) (3) 10-08 market-reopen data chain re-arm "
             "(first trading day back: live.paper + t35 + prospect chain legs re-activate) "
             "(4) 下轮 5x=r825 HANDOVER 核查")
s["latest_artifact"] = "research/PERPETUAL_N1_W173_PREREG.md (origin d76ce93d5, 2026-10-07T11:5x)"
s["now_active"] = "W173 freeze chain prep (prereg landed; freeze edits next window per two-session law)"
s["last_action"] = "W173 prereg build + banned gate ADMIT + S6 37/37 + D-19 watermark repair"
json.dump(s, io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
print("state 820->821 written; dec sha repaired to", dec_sha[:16])

# ---- heartbeat -------------------------------------------------------------
h = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
prev_epoch = h.get("heartbeat_epoch_utc")
assert isinstance(prev_epoch, int), prev_epoch
h["last_heartbeat_epoch_utc"] = prev_epoch
epoch = int(time.time())
h["heartbeat_epoch_utc"] = epoch
assert isinstance(h["heartbeat_epoch_utc"], int)
h["clock_read"] = now_iso
assert "T" in h["clock_read"]
h["ts"] = now_iso
h["last_seen"] = now_iso
h["round_no"] = 821
h["round"] = 821
h["loop_round"] = "r821"
h["task"] = "W173 prereg build landed; freeze chain next window (never-dry line held)"
h["current_task"] = s["current_task"]
h["now_active"] = s["now_active"]
h["last_action"] = s["last_action"]
h["latest_artifact"] = s["latest_artifact"]
h["next_milestone"] = ("W173 freeze+ignite+finalize (proj ledger 786,012 / K 378,520, window <=24h "
                       "never-dry) + 10-08 market-reopen data chain re-arm")
h["verdict"] = ("watermark GREEN (red=false lane=healthy); engine ALIVE rc0 idle queue0 (W173 "
                "freeze pending = next supply step, never-dry held); pool 2 live entries both "
                "bm-b-lane burns; golden-week legal idle face")
h["health"] = "ok"
h["last_round"] = "r821"
h["last_run"] = "smoke 48/48; S6 37/37 rc0; banned gate ADMIT"
# freshness readings (probe quick)
try:
    import psutil
    h["cpu_pct"] = psutil.cpu_percent(interval=0.3)
    h["ram_free_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception:
    pass
json.dump(h, io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat written; epoch int", chk["heartbeat_epoch_utc"], "clock", chk["clock_read"])

# ---- round report line -----------------------------------------------------
rr = ("2026-10-07T11:5x+08:00 | r821 bm-a (dept:研究+工程) | watermark verdict: 绿 (red=false "
      "lane=healthy; engine ALIVE rc0 idle queue0 = W173 prereg landed this window, freeze edits "
      "next window per r797/r799 two-session law; golden-week legal idle face: 板全闭环 0 open 票 "
      "+ 池 2 live entries 均 bm-b 车道在烧) | 当前活: W173 预注册构建本窗落地 origin d76ce93d5 "
      "(token-vmap 冻结时 W172 blob 59fde9319→W173 全 50 对 token 断言过; 生成器=exec 截断版 "
      "r819 构建脚本取精确 TOK 对·r819 断言电池全数活跑复验零写) | 最近实物: "
      "research/PERPETUAL_N1_W173_PREREG.md 20,507B @2026-10-07T11:5x (A 395_404..397_403 阶梯第 "
      "三十三例 E36 hops=1 / B 397_404..397_603 own-A leg2 hops=1; anchor 783,812/K=376,320; proj "
      "378,520/786,012; W174+ 投影 397_404..399_403 / 397_604..397_803 naive-B-inside-naive-A 第 "
      "三十四例待复核; 带闸 banned_direction_gate ADMIT rc0) | 下个里程碑: W173 冻结链+点火+"
      "finalize (proj ledger 786,012 EXACT / K 378,520 EXACT·窗 ≤24h never-dry 线) + 10-08 复市"
      "首交易日数据链 re-arm | did: S0 fetch behind0 (脏树=own daemon churn)+S0.5 orders 差集 "
      "167/167 零未回执双扫+D-19 dec 水位修 acc32216(r820 bad-provenance 回归)→635c3024 origin "
      "blob 实算 (r786/r813 定谳律; 零新涉本司行: 最新决策 D-20261007-03 归 HQ 夜班工具域已 "
      "r804/r813 消费; orders e9fa5da4 MATCH; O-0935 bm-a 能力盘点腿已 r817 回执) + 序数分歧诚实"
      "披露: W172 §5.5 投影预告第三十二例 vs r820 回执 A_semantics 机读 THIRTY-THIRD——按回执序"
      "数面记载 (r587 非转抄) + 席位推送 sha 勘正: r820 收口 prose 记 014b4ede5 vs path 实测 "
      "9cd8af3af (pre-seat push 3-item payload 引入席位件; 014b4ede5=churn-absorb checkpoint) "
      "——按 path 派生 sha 记载+prose 失配披露 + S1 smoke 48/48 + S6 37/37 rc0 (golden-week "
      "no-op 族; dualrun ZERO-DRIFT; scorecard/REPORT/LIVE-2026-10-07/build_status 再生; "
      "attrition CLEAN 4 账本) + push 撞窗 behind-9 (bm-b/bm-c 同窗活跃) 干净 rebase 1/1 零冲突 "
      "送达 | verify: banned gate ADMIT rc0; prereg token-count 50/50 asserts PASS+残留 "
      "token 零+畸形窗扫描 CLEAN; origin 送达 d76ce93d5 fetch+rev-list 双向 0; smoke 48/48; "
      "S6 37/37; 心跳 epoch int+clock T 分隔自证 | 计分: 2 (能跑/能看实物=W173 预注册冻结前 "
      "件+生成器工具件) | 登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作 (treasure_guard "
      "未触发) | 下轮指针: r822=W173 冻结链 (5-face edits→双 selftest→freeze commit→2-tick 点火"
      "→finalize)+W174 席位链 post-finalize+10-08 复市数据链 re-arm | 本地未达 origin commit "
      "数=0 (收尾 commit 后 push+fetch 复核) | [r821 bm-a]\n")
with io.open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(rr)
print("round report line appended")
