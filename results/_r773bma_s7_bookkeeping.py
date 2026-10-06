# -*- coding: utf-8 -*-
"""r773 bm-a S7 bookkeeping: state round_no re-sync 767->773 (dead-tail r768..r772
honest backfill per the r768-takeover precedent), heartbeat refresh (epoch int
self-verified, clock T-form), CODELY pit-line append."""
import json
import time
import datetime

# --- state: round_no 767 -> 773 (re-sync with the actual git round series) ----
s = json.load(open("state-bm-a.json", encoding="utf-8"))
assert s["round_no"] == 767, s["round_no"]
s["round_no"] = 773
json.dump(s, open("state-bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk = json.load(open("state-bm-a.json", encoding="utf-8"))
assert chk["round_no"] == 773
print("state round_no -> 773 (BOM-free LF rewrite, re-sync from stale 767 disclosed)")

# --- heartbeat refresh ---------------------------------------------------------
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
now = datetime.datetime.now().astimezone()
h["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+" if now.utcoffset() >= datetime.timedelta(0) else "-") + f"{abs(now.utcoffset()).seconds//3600:02d}:{abs(now.utcoffset()).seconds%3600//60:02d}"
h["heartbeat_epoch_utc"] = int(time.time())
assert isinstance(h["heartbeat_epoch_utc"], int)
h["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
h["current_task"] = ("W157 finalize one-pass landed (ledger 741,411, K=343,320, SS5 4/4) + "
                     "W158 pre-seat/probe/band-gate ADMIT + prereg xform staged + "
                     "W157-entry projection-prose heal; W158 freeze edits = next tick")
h["verdict"] = "healthy (engine idle post-burn, W158 freeze window queued for next tick)"
json.dump(h, open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
h2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]
print("heartbeat: epoch int", h2["heartbeat_epoch_utc"], "clock", h2["clock_read"])

# --- CODELY pit line (one thing, <1.5KB, P0-grade freeze-window trap) ---------
PIT = ("- [2026-10-06 12:2x r773 bm-a] **冻结 vmap 部分token化畸形窗坑（r772 W157 freeze 实弹·r773 "
       "治愈窗发现）**：freeze-edits 值映射对「下波+投影散文」的复合带串（如 \"A first-clean "
       "360_004..362_003 / B first-clean 360_204..360_403\"）按裸前缀部分 tokenize——\"360_004\"→"
       "@BSEED@ 而 \"..362_003\" 残留——产出起点大于终点的畸形窗面（362_204..362_003 / "
       "362_404..360_403 落进 W157 WAVE_CONFIGS cfg 散文；结构字段/带行/seed bases 全机证无损=纯文档面）。"
       "正法=①投影散文复合串必须整串入 TOK（@PRA@/@PRB@ 级 token）禁裸前缀拼凑②冻结后探针必须正则扫全件 "
       "start>end 畸形窗（r772 entry-integrity 探针只盖了带行/seed 面漏了投影散文）③治愈=按冻结窗 gate "
       "回执 leg3 机值整串恢复（r587 非转抄·_r773bma_w157_prose_heal.py 当窗治愈+双 selftest 零伤）。"
       "How to apply：W158+ 冻结编辑器一律先跑 edit_integrity 式实证探针列全字符串清单再定 TOK。")
c = open("CODELY.md", encoding="utf-8").read()
anchor = "### Project\n"
i = c.find(anchor)
assert i > 0
# find the Project section content start (after anchor line)
j = c.find("\n", i) + 1
c2 = c[:j] + PIT + "\n" + c[j:]
open("CODELY.md", "w", encoding="utf-8", newline="\n").write(c2)
assert PIT in open("CODELY.md", encoding="utf-8").read()
print("CODELY pit line appended,", len(PIT), "bytes")
