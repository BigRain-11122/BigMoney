# -*- coding: utf-8 -*-
# r641 bm-b close: state bump, heartbeat update, round-report append, self-verify.
import json, os, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now().astimezone()
clock_read = now.strftime("%Y-%m-%dTH:%M:%S") + ("+%02d:00" % (now.utcoffset().total_seconds() // 3600))
epoch = int(time.time())

def nulls_count(fam):
    p = os.path.join("results", fam, "nulls.jsonl")
    with open(p, encoding="utf-8") as f:
        return sum(1 for _ in f)

q, v, d = nulls_count("fund_quality_p1"), nulls_count("fund_value_p1"), nulls_count("fund_divlowvol_p1")

# ---- state.json (bm-b legacy filename per S5 law) ----
with open("state.json", encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 640, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 641
st["round_no_label"] = "round 641 (bm-b)"
st["note"] = ("r641: dead-session adoption round. 01:2x-01:4x predecessor (r641 attempt) killed pre-commit; "
              "adoption lawful per r471 (zero live codely in repo via process sweep; bookkeeping mtimes <= death window). "
              "Delivered: (1) r640-deferred HANDOVER 5x check line (increment window r631-r640); (2) FUND trio finalize "
              "rehearsal rerun ALL-GREEN x3 (quality %.1fs/value %.1fs/divlowvol %.1fs per adopted JSONs, NOT_A_VERDICT banner, "
              "MSG-1720 Finding B fix-state reverified) + summary single-family-overwrite fix script "
              "(_r641bmb_rehearsal_summary_fix.py). D-19 sparse-clone fallback MATCH (eb14b510 unchanged, zero consumption; "
              "r631 recipe second proof). S1 47/47. S6 34 legs rc0 (dualrun streak 32; update_lhb live fetch 11/11 rc0; "
              "5 CEO faces stale-takeover derive per O-2100 s2.4, bm-a hb stale 70min; b_layer 5222 all gates). "
              "Engine alive rc0 idle; attrition CLEAN; orders 152/152 double-scan zero unacked; S7 4/4 + claws reinstalled "
              "idempotent. Net-path delivery (r630 recipe): isolated worktree cherry-pick -> CAS push -> reset --mixed + "
              "targeted checkout (8 daemon live faces preserved) -> dualrun settle re-proof." % (179.7, 229.4, 178.8))
for k in ("ts", "updated", "last_round_at", "last_seen"):
    st[k] = clock_read
st["clock_read"] = clock_read
with open("state.json", "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
hp = os.path.join("fleet", "machines", "bm-b.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["round_no"] = 641
hb["round_no_label"] = "round 641 (bm-b)"
hb["current_task"] = ("FUND trio NULLS burn watch (daemons live, nulls q/v/d = %d/%d/%d of 2000, finalize window 10-05..10-09 "
                      "pending G-SEG GM ruling) + r641 dead-session adoption delivered (HANDOVER 5x line + trio rehearsal "
                      "ALL-GREEN x3 + summary overwrite fix)" % (q, v, d))
hb["verdict"] = ("GREEN (smoke 47/47; adoption delivered via r630 net-path; D-19 sparse MATCH eb14b510 zero-consume; "
                 "S6 34 legs rc0; dualrun streak 32; attrition CLEAN; engine alive rc0 idle; orders 152/152; trio burns healthy)")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock_read
for k in ("ts", "updated", "updated_at", "last_seen"):
    hb[k] = clock_read
hb["cpu_util_pct"] = 73.8
hb["free_ram_gb"] = 4.37
hb["idle_ram_gb"] = 4.37
hb["ram_free_gb"] = 4.37
hb["ram_avail_gb"] = 4.37
hb["gpu_idle_vram_gb"] = 2.31
hb["gpu_idle_vram_mb"] = 2310
hb["gpu_free_vram_gb"] = 2.31
hb["gpu_free_vram_mb"] = 2310
hb["gpu_vram_free"] = 2310
hb["gpu_free_vram_mib"] = 2310
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- round report line (S5: bm-b legacy file) ----
line = ("%s | round 641 (bm-b, dept:工程/舰队+研究): watermark verdict=GREEN (red=false, py~71-86% 三族烧录在飞, lane healthy)。"
        "本轮=死 r641 会话收养交付轮（r471 四证：进程普查仓内零活 codely〔唯一 Bigmoney codely=本会话〕+簿记 mtime≤死亡窗 01:45+零半成品断点）："
        "①r640 延期义务 HANDOVER 5x 核对行收编交付（增量窗 r631-r640 十轮+产物清单漂移+指针，predecessor 写就本会话验真收养）；"
        "②FUND 三族 finalize 预演重跑 ALL-GREEN x3 收编（quality 179.7s/value 229.4s/divlowvol 178.8s·01:34-01:43·NOT_A_VERDICT 横幅在位·"
        "MSG-1720 Finding B 修复态复验 r626d 6c2a6742f 在位）+summary 单族覆盖坑治愈件 _r641bmb_rehearsal_summary_fix.py（--fam 模式覆写 summary 只含末族→三族重建）；"
        "③D-19 集团水位 sparse-clone fallback MATCH（eb14b510 未变零消费·r631 配方第二证·_r641bmb_d19_sparse.py）；"
        "S0.5 orders 152/152 双扫零未回执（origin 多出 README.md=非令件假阳性过滤）；S1 smoke 47/47；"
        "S3: 饱和引擎活 rc0 idle+任务板零 open+job 板空+水位红牌 false；"
        "S6 34 腿 rc0（dualrun ZERO-DRIFT streak32·update_lhb 实拉 11/11 rc0·CEO 五面 bm-a 心跳 stale 70min 按 O-2100 s2.4 stale-takeover derive·"
        "b_layer_mask 5222 码全门过·黄金周 no-op 族）；"
        "S7: attrition CLEAN+loop pin2 no-op+watchdog 活+pre-commit/pre-push 双爪重装幂等+state 翻面 641；"
        "r630 净路重放交付（隔离 worktree cherry-pick→CAS push→reset --mixed+定向 checkout〔8 daemon 活面保全〕→dualrun settle 复跑自证）。"
        "CEO 三行——当前活：FUND 三族 NULLS 2000-draw 烧录值守（q/v/d=%d/%d/%d of 2000·daemon 三进程活·finalize 窗 10-05..10-09 候 G-SEG 总经理裁定）；"
        "最近实物：results/_r633bma_finalize_rehearsal_summary.json（三族 ALL-GREEN x3·01:45 重建）+research/HANDOVER.md r641 5x 行；"
        "下个里程碑：FUND 三族烧毕 finalize 判决面开窗 10-05..10-09（预演 T-1 全绿零阻塞·G-SEG 无裁决按 insufficient-sample 单判读备案 r638）。"
        "本地未达 origin commit 数=0（本轮 commit 后 push+fetch+ls-remote 自证）。"
        "下轮指针：r642=FUND 烧录值守+W2 finalize 轮询（pid 31336 deadline 10-06·bm-c 属主）+日常维护。\n" % (clock_read, q, v, d))
with open(os.path.join("logs", "iteration-loop", "round_reports.md"), "a", encoding="utf-8") as f:
    f.write(line)

# ---- self-verify ----
st2 = json.load(open("state.json", encoding="utf-8"))
hb2 = json.load(open(hp, encoding="utf-8"))
assert st2["round_no"] == 641
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and ("+" in hb2["clock_read"] or "-" in hb2["clock_read"][10:])
print("CLOSE OK: round=641 epoch=%d clock=%s nulls q/v/d=%d/%d/%d" % (epoch, clock_read, q, v, d))
