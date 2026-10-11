# -*- coding: utf-8 -*-
"""r879 bm-b supplement: E16 shard-0 COMPLETED mid-closeout (ckpt 28,651B rows
landed 12:50:49 = wiring-fix real-fire proof LANDED THIS ROUND, ahead of the
~13:10 estimate written into the main r879 line); shard-1 auto-claimed 12:52:26.
Append-only addendum to round report (r839 precedent), state/heartbeat refresh."""
import json, time, io

TS = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- round report addendum (append-only, r839 precedent) ----------
ADD = ("{ts} | r879 bm-b SUPPLEMENT | E16 shard-0 COMPLETED mid-closeout: "
       "ckpt/shard_0of12.jsonl 28,651B rows landed 12:50:49 = **with-缩进接线修复实弹过火证明已落**"
       "（主行 13:10 估计被实测提前 20min 超越·首 flush 零崩+全分片走完）+shard_0of12.json 产物 44.5KB"
       "（elapsed 1109.6s/18.5min·n_formulas/n_ok 如实·cutoff 2026-10-09·universe 3514）+"
       "autofill 12:52:26 已自动续领 shard-1（ckpt/shard_1of12.jsonl 开面·烧批链自转实证）·"
       "E16 进度 1/12 done+1 in-flight·剩 10 分片 autofill 顺领节奏 ~18.5min/片≈3h→12/12 可望今日 16:xx"
       "（milestone ≤2026-10-13 大幅提前·finalize=观察轮 12/12 后）\n").format(ts=TS)
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(ADD)

# ---------- state.json refresh ----------
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
for k in ("last_seen", "ts", "updated", "updated_at", "last_action_at"):
    s[k] = TS
s["now_active"] = ("r879 supplement: E16 shard-0 COMPLETE (ckpt 28,651B + product shard_0of12.json "
                   "44.5KB landed 12:50:49, wiring-fix real-fire proof LANDED); shard-1 auto-claimed "
                   "12:52:26 in flight; 1/12 done + 1 burning, autofill chain self-turning")
s["did"] = (s["did"] + " | SUPPLEMENT: shard-0 completion landed mid-closeout (ckpt rows + product "
            "12:50:49, elapsed 18.5min, proof landed ahead of 13:10 estimate); shard-1 claimed "
            "12:52:26 by autofill (chain self-turning verified)")
s["last_action"] = s["did"]
s["latest_artifact"] = ("r879: results/alphagen_rg/shard_0of12.json (E16 1/12 shard product, "
                        "n_ok census face) + results/alphagen_rg/ckpt/shard_0of12.jsonl 28,651B "
                        "(with-indent wiring fix PROVEN in real fire)")
s["current_task"] = ("r880: E16 shard-1..11 completion watch (autofill ~18.5min/shard cadence, "
                     "12/12 expected today ~16:xx) -> finalize when 12/12 (observing round, "
                     "refuse-if-exists) -> CENSUS-2026-10-09.json verdict face -> T-184 transfer "
                     "receiver restore SAME round origin/transfer/t184-510880 lands (deadline "
                     "2026-10-12 15:30) -> W210 freeze anchor watch (W209 bm-c) -> 48h CEO report "
                     "due 2026-10-13 11:2x")
s["task"] = s["current_task"]
s["next"] = s["current_task"]
s["next_milestone"] = ("E16 12/12 + finalize TODAY ~16:xx (1/12 done 12:50 + autofill cadence; "
                       "bound <=2026-10-13); T-184 510880 restore before 2026-10-12 15:30")
s["verdict"] = ("GREEN: r879 COMPLETE+ (first-action pitlaw+minisplit; E16 shard-0 DONE 12:50:49 "
                "ckpt 28.6KB+product 44.5KB = wiring real-fire proof LANDED THIS ROUND; shard-1 "
                "burning since 12:52, chain self-turning); smoke 49/49; S6 39rc0+alloc rc2 T-184 "
                "dep honest; WM red = burn ramp window GM-waiver legal")
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat refresh ----------
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h["ts"] = TS
h["last_seen"] = TS
h["heartbeat_epoch_utc"] = EPOCH
h["now_active"] = s["now_active"]
h["did"] = s["did"]
h["last_action"] = s["did"]
h["last_action_at"] = TS
h["latest_artifact"] = s["latest_artifact"]
h["current_task"] = s["current_task"]
h["task"] = s["current_task"]
h["next"] = s["next"]
h["next_milestone"] = s["next_milestone"]
h["verdict"] = s["verdict"]
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print(json.dumps({"supplement": True, "ts": TS, "epoch": chk["heartbeat_epoch_utc"],
                  "shard0": "done 12:50:49", "shard1": "in flight 12:52:26"}))
