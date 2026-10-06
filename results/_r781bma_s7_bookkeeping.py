# -*- coding: utf-8 -*-
"""r781 bm-a S7 bookkeeping: state round_no, heartbeat (CEO three-line
visibility face), round-report line, CODELY.md pit-law append (append-only
via python single-file fresh-read-modify-write per the multi-writer
replace-ban law; needle < 1.5KB per the memory gate)."""
import io
import json
import time

# 1) state-bm-a.json round_no -> 781
sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 781
io.open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(s, ensure_ascii=False, indent=1) + "\n")
assert json.load(open(sp, encoding="utf-8"))["round_no"] == 781

# 2) heartbeat fleet/machines/bm-a.json (CEO process-visibility three lines)
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
now = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
h["last_seen"] = "2026-10-06 16:1x"
h["round"] = 781
h["round_no"] = 781
h["last_round"] = "r781"
h["now_active"] = ("W159 shard burn in flight via saturation engine "
                   "(auto-ignited post-freeze, PERPETUAL-N1-W159 12-shard set)")
h["last_action"] = ("r781: W159 freeze landed+pushed (bm-a 75th owned/149th wave, "
                    "A 364_604..366_603 / B 366_604..366_803, gate r779 ADMIT verbatim) "
                    "+ engine auto-ignited W159 burn")
h["latest_artifact"] = ("freeze commit 6ee1207bb + scripts/perpetual_faces.py W159 row "
                        "+ scripts/perpetual_faces_n1.py W159 entry "
                        "@2026-10-06T15:4x (pushed 138eefb2a, delivery 0/0)")
h["next_milestone"] = ("W159 finalize (one-pass, ledger 753,012+2,200 projected) + "
                       "W160 pre-seat next window (<=48h) + 10-07 D-06 collection "
                       "window closeout + T-173 report due 10-08 noon")
h["task"] = ("r781 W159 freeze+ignition done; next = W159 burn-off monitor -> finalize; "
             "10-07 D-06 closeout window")
h["current_task"] = h["task"]
h["current"] = "W159 frozen+ignited; burn in flight"
h["cpu_cores"] = 32
h["idle_ram_gb"] = 45.0
h["gpu_free_vram_gb"] = 8.0
h["verdict"] = ("green: W159 freeze landed (never-dry lane, <=48h window met), "
                "engine alive burning W159, smoke 48/48, S6 38/38 rc0")
h["heartbeat_epoch_utc"] = int(time.time())
assert isinstance(h["heartbeat_epoch_utc"], int)
h["clock_read"] = now
h["ts"] = now
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(h, ensure_ascii=False, indent=1) + "\n")
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]
assert "T" in h2["ts"]

# 3) round report line (watermark verdict first + delivery line)
rr_path = "round_reports-bm-a.md"
line = ("| 2026-10-06 16:1x | r781 | watermark GREEN (py idle, board lane legal: engine "
        "burning W159; watermark_red red=false) | W159 FREEZE landed (bm-a 75th owned, "
        "149th wave): pf.py N1_BANDS[159] A 364_604..366_603 / B 366_604..366_803 "
        "(r779 band-gate ADMIT verbatim, staircase 18th instance E36, hops=1/1) + "
        "n1.py WAVE_CONFIGS[159] entry/materializer(chain 138..158 n=21)/PASS-claim; "
        "r773 pit-law editor compliance (pre-TOK 4-face probe inventory byte-identical "
        "to r779 dumps, whole-string composite tokens incl round+sha, bare 158/157 "
        "backstop LAST, full-file start>end scans CLEAN both files, W160p re-derived "
        "from r779 gate leg3); honesty fixups (seat delivery = merge-absorb 7b60d09da "
        "NOT direct-ff; self-ack = landed bm-c r625; W158 freeze r775/6957f509e; W158 "
        "finalize r778/753,012/K=345,520 prereg-anchored); r775-bloodline L310 latent "
        "cross-fragment false-negative needle settled (fragment-safe needles in edits+"
        "verify scripts); ENGINE AUTO-IGNITED W159 burn (PERPETUAL-N1-W159/n1w159-3of12 "
        "pid live, queue_depth 8); push rejected behind-5 -> churn-absorb leg1 (own "
        "daemon faces) + merge absorb (bm-c r626 batch; marks UU = content-identical "
        "2=2 union zero-loss) -> re-push clean | freeze verify rc0 + pf selftest 9/9 + "
        "smoke 48/48 + S6 38/38 rc0 155.9s + attrition 4 ledgers CLEAN + S7 quartet "
        "green (loop pin=8 no-op, watchdog reloaded, claws content-match) | 本地未达 "
        "origin commit 数=0 (post-push fetch ls-tree self-verified); next: W159 "
        "burn-off -> finalize one-pass, W160 pre-seat next window, 10-07 D-06 "
        "closeout |\n")
with io.open(rr_path, "a", encoding="utf-8", newline="") as f:
    f.write(line)

# 4) CODELY.md pit-law append (multi-writer file: python append-only, NOT replace)
cp = "CODELY.md"
pit = ("\n- [2026-10-06 15:4x r781 bm-a] **冻结编辑器跨片段连续 needle 假阴坑（r775 血统 L310 "
       "潜缺陷·r781 实弹当场治愈零 origin 伤害）**：n1.py WAVE_CONFIGS 投影散文按 python 字符串续行分片"
       "（'...will refuse the naive \"' 尾片 + 换行缩进 + '\"W160 A window; W160 freezer ...' 头片）——"
       "按逻辑串写的连续 needle（'refuse the naive W160 A window; W160 freezer'）横跨片段边界 count==0 假阴"
       "（r775 冻结机 L310 断言 needle 同病：实测 r775 落地件中该连续串 count=0=该断言从未真过；r775 会话"
       "事后以 selftest+smoke 收口但脚本内断言未修，血统照抄即爆）。正法=断言一律取片内形"
       "（'\"W160 A window; W160 freezer MUST re-derive on the \"' 含引号全片 count==1）+ 前片尾"
       "（'will refuse the naive \"'）独立断言；编后置断言套件跑挂不回滚文件=先跑 verify-only 套件"
       "（_r781bma_w159_freeze_verify.py 范式=edit 写盘后断言分离）。How to apply：W160+ 冻结机照"
       " r781 双件（edits+verify）血统；一切跨 python 字符串续行的散文断言先 probe dump 物理行再取片内形。\n")
src = io.open(cp, encoding="utf-8", newline="").read()
assert "冻结编辑器跨片段连续 needle 假阴坑" not in src, "pit already present (double-append guard)"
io.open(cp, "a", encoding="utf-8", newline="").write(pit)
print("S7 bookkeeping landed: state=781, heartbeat epoch int + ts T-form, "
      "RR line (watermark GREEN + delivery 0), CODELY.md pit append (L310 kin, "
      "append-only python, double-append guard PASS)")
