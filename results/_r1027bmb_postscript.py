# r1027 bm-b postscript: S7-tail consumption + push-verified flip + tail row
import json, time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

TAIL_ROW = (f"{ts} | r1027 bm-b postscript | S7 尾双扫执法面：3 新 ORD 行同窗消费（16:0x MV 年代工业逻辑教学令〔CRAFT 正典件+QC §5 v1.2 三查落闸〕/16:23 MV 导演全量学习令〔调研波已派 R-20261019-mv-directors-full-01+适合律落件〕/16:2x 艺术MV定谳+短视频风格禁入令〔CRAFT §七+QC §22 v1.4 三查〕——全 BigStream/MV 域 bm-a 交互窗执行·零 bm-b 派工）+ 水位 77dae663→57e209fd（dec 95879dd9 hold·read-back OK·mirrors synced 3）；r1027 主推送定谳=d5927d43b1..18e4cdbd65 LANDED（首推被 pre-push 爪正确拦截=stale-base 型〔origin 并发推进 bm-a r1080 后旧基座推送判为对他机新面 revert·r1000 同族零盲推〕→吸收重放 8 UU 同日幂等 regen 族全 ours-newer-wins 逐面实测 16:11-16:13>15:13-15:49→再推 LANDED→fetch behind=0 四向验证）；daemon 双面（futures/lhb unsuffixed）stash-pop 冲突按 daemon-live-wins 收面恢复 unstaged 脏稳态不入提交；未达 origin commit 数=0")

# state dual-face: flip r1027 push + tail note
for path, face_note in (("state.json", "r1027: mirror-written per r1020 dual-face law. authoritative face."),
                        ("logs/iteration-loop/state.json", "mirror face; authoritative round_no = repo state.json (r1020 law)")):
    with open(path, encoding="utf-8") as f:
        st = json.load(f)
    st["sync"]["r1027_main_push"] = {
        "status": "PUSHED_VERIFIED (attempt-1 claw-blocked stale-base after concurrent bm-a r1080 advance -- correct block, absorbed + replayed 8 UU ours-newer-wins; attempt-2 LANDED d5927d43b1..18e4cdbd65, fetch behind=0 four-way verified)",
        "pushed_sha": "18e4cdbd65", "consumed_at": "pending r1028", "behind_origin_main": 0,
    }
    st["sync"]["last_push_ts"] = ts
    st["sync"]["behind_origin_main"] = 0
    st["r1027_ord_note"] = (st.get("r1027_ord_note", "") +
        " || S7-TAIL: +3 rows consumed (16:0x MV industry-logic teaching order / 16:23 MV directors full-spectrum learning order / 16:2x art-MV verdict + short-video-style ban order -- all BigStream/MV domain bm-a-executed, zero bm-b dispatch); advance 77dae663->57e209fd read-back OK, dec 95879dd9 hold; heartbeat mirrors synced 3 (r1090 dual-face).")
    st["r1028_first_action_note"] = ("r1028: 1) D-19 fresh probe FIRST ACTION (ord=57e209fd through 16:23; sprint cadence high -- expect more rows) "
        "2) papers conditional retry on bar landing (evening window) 3) ST-012 night 22:0x REBUILD-PLAN-v2 + v2Pro gate 4) W279 prereg watch (bm-c r1121) -> bm-b N1 feed 5) RepoSlim tomorrow 09:03 verify")
    st["clock_read"] = ts; st["ts"] = ts; st["updated"] = ts; st["updated_at"] = ts
    st["last_action_at"] = ts
    st["last_action"] = "r1027: r1026 estate LANDED + D-19 2+3 rows consumed+advanced (77dae663->57e209fd) + S6 43 rc0 + papers honest skip + r1027 push LANDED 18e4cdbd65"
    st["state_face_note"] = face_note
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
        f.write("\n")

# heartbeat tail sync
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "ts": ts, "clock_read": ts, "heartbeat_epoch_utc": epoch, "last_seen": ts, "last_action_at": ts,
    "last_action": st["last_action"],
    "last_orders_sha": "57e209fda2ebffeb02ccebdbdc1e1b2280d7d011bdb11fd91f48267c9a9ce88e",
    "did": "r1027: r1026 estate LANDED (f8f1502e57..8578dcadff) + D-19 5 rows total consumed (2 S0.5 + 3 S7-tail, ord 77dae663->57e209fd) + S6 43 rc0 + papers honest skip + r1027 LANDED 18e4cdbd65 (claw stale-base block absorbed)",
})
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# round report tail row
p = "logs/iteration-loop/round_reports.md"
with open(p, encoding="utf-8") as f:
    txt = f.read()
if not txt.endswith("\n"):
    txt += "\n"
txt += TAIL_ROW + "\n"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(txt)

# verify
d = json.load(open("state.json", encoding="utf-8"))
assert d["round_no"] == 1027
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(h["heartbeat_epoch_utc"], int) and "T" in h["clock_read"]
print("postscript written ts=", ts)
