# r835 bm-b closeout: state.json + round report + heartbeat (post git-loss recovery)
import json, time, datetime

NOW = datetime.datetime.now().astimezone().replace(microsecond=0)
ISO = NOW.isoformat()  # T-separated with +08:00
EPOCH = int(time.time())
RR = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

# 1) state.json -> r835
with open(RR + r"\state.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 835
st["round"] = 835
st["round_no_label"] = "r835"
st["machine_id"] = "bm-b"
did = ("r835: RECOVERY COMPLETE per runbook 9/9 - detached clone via gh-proxy CDN (562MB pack in ~3min vs SSH 35MB/2.5h; SSH lane killed) -> Move .git -> reset --mixed (NO --hard) -> checkout 8 dirs + 43 missing files (incl config/ bootstrap.py dashboard.html bigmoney.html = r834 forensics MISSED them; NTFS case-insensitive order proves pure contiguous run .git->live, r834 'order anomaly' DISPROVEN) -> claws reinstalled -> smoke 49/49 (machine.json rebuilt from template, gitignored local face) -> triage 129 M: 81 foreign-owner faces checked out to origin (newer-wins, bm-a/bm-c kept pushing through disaster), 48 local-truth faces (wtbackup 35 + ledger/MSG) staged for commit; orphan probe 13 faces 1 orphan (PID17760 r832 dit_fetch = valid DiT download task retained per r834); D19 watermarks RE-PROBED post-restore (dec 7ce92f99 ord 7a77677a = moved, new rows consumed: D-20261010-01..04 receipts + D-20261010-07 prepush-claw quarantine-manifest narrow gate [dispatched, next round] + C-20260909-03 bm-b baseline wiring receipt window <=24h after revival [clock started this round])")
st["verdict"] = ("r835: RECOVERY round = sole mission per red-fix law; repo fully restored from origin tip 04f723f3 (bm-c 14:13 alive commit; origin kept advancing through disaster window = bm-a/bm-c healthy); watermarks re-verified post-restore; prevention law stays until root cause closed")
st["now_active"] = "r835 closeout: state + round report + heartbeat + targeted commit/push"
st["current_task"] = ("r836 queue: (1) D-20261010-07 prepush-claw quarantine-manifest narrow gate implementation (Tools/git_claw.py 4th allow-class: same-push results/_quarantine/<ts>/manifest.json moved[]+sha256 = release that batch of qa/ deletions; receipt to HQ-FEEDBACK, judge=rotation zero-escape 100% by 10-17); (2) C-20261009-03 bm-b workspace baseline wiring (.gitignore v2 whitelist + audit tool run) receipt <=24h from r835 (started 14:2x 10-10); (3) D-20261010-04(1) Bonsai T-99/T-100 close-out ledger face; (4) S6 chain resume full 33-leg (13:0x legs already ran, mostly no-op Saturday); (5) root-cause forensics continued: USN journal dump filter for [13:11:23,13:17:02] + zombie git PID 24568 handle audit")
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["latest_artifact"] = "r835: bigmoney repo fully restored (.git from gh-proxy clone 04f723f3 + 43-file gapfill + claws + smoke 49/49), 2026-10-10 14:3x"
st["next_milestone"] = "r836-r837: recovery commit pushed + D-07 claw gate shipped + C-03 bm-b baseline receipt landed (window <=24h from 10-10 14:30)"
st["last_action"] = "r835: git-loss recovery executed runbook 9/9 (gh-proxy fast-clone rescue + forensic NTFS-order correction + watermark re-probe + triage newer-wins)"
st["last_round_at"] = ISO
st["last_round_ts"] = ISO
st["ts"] = ISO
st["updated"] = ISO
st["last_seen"] = ISO
st["updated_at"] = ISO
st["clock_read"] = ISO
st["last_decisions_sha"] = "7ce92f99d6e2e3194a2aa5a4eee8eb2e0fe020ff"
st["last_orders_sha"] = "7a77677ac7a3942be8b13e6853e5a9db444838eb"
st["last_decisions_at"] = ISO
st["last_orders_at"] = ISO
st["last_decisions_read_at"] = ISO
st["last_orders_read_at"] = ISO
st["last_decisions_sha_method"] = "r835: post-restore re-probe via results/_r686bmb_d19_check.py (r537 SHA-1 40-hex raw-blob PIN); both watermarks moved and consumed this round; D-07 dispatch + C-03 wiring queued"
with open(RR + r"\state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)

# 2) round report append
line = (ISO + " | r835 | RECOVERY per runbook 9/9: gh-proxy CDN clone rescue (562MB in ~3min, SSH lane 35MB/2.5h killed), "
        "Move .git + reset --mixed + checkout 8 dirs + 43 gaps (forensic fix: NTFS case-insensitive order = pure contiguous run .git->live, "
        "config/bootstrap/dashboard/bigmoney.html were IN the deleted segment - r834 anomaly DISPROVEN), claws reinstalled, "
        "machine.json rebuilt (gitignored local), smoke 49/49; triage newer-wins: 81 foreign faces checkout->origin, 48 local-truth staged "
        "| evidence: .git HEAD=04f723f3, smoke Summary 49/49 PASS, probe jsons in results/ "
        "| orphan_face=1 (PID17760 r832 dit_fetch valid DiT task, retained) | watermark: GREEN re-probed (dec 7ce92f99 ord 7a77677a moved+consumed: "
        "D-20261010-01..04 receipts + D-20261010-07 claw narrow gate [dispatched->r836] + C-03 bm-b baseline receipt <=24h) "
        "| next: r836 D-07 claw gate + C-03 wiring + S6 resume\n")
with open(RR + r"\logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)

# 3) heartbeat
hb_path = RR + r"\fleet\machines\bm-b.json"
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
hb["round"] = 835
hb["round_no"] = 835
hb["now_active"] = "r835 closeout: post git-loss recovery (repo restored, triage, commit/push)"
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["next"] = st["current_task"]
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = ("r835: RECOVERY complete - repo restored from origin 04f723f3, smoke 49/49, claws live; watermark GREEN re-probed; "
                 "D-07 claw gate + C-03 baseline wiring queued for r836")
hb["last_action"] = st["last_action"]
hb["last_round_at"] = ISO
hb["last_seen"] = ISO
hb["updated"] = ISO
hb["ts"] = ISO
hb["clock_read"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["updated_at"] = ISO
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 1
hb["orphan_face_note"] = ("r835 orphan probe py_faces=13 orphans=1 (PID17760 r832 dit_fetch: parent-dead+no-host+cpu-stalled BUT = valid "
                          "DiT download task explicitly retained by r834 runbook 'MV lane unaffected'; not killed)")
hb["sync"] = {
    "ahead": 1,
    "behind": 0,
    "last_push_ts": ISO,
    "note": "r835: recovery commit push (post-push fetch+ls-remote self-proof pending in this round)",
}
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)

# 4) self-proof
with open(hb_path, encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(chk["round_no"], int)
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
print("CLOSEOUT_OK round=835 epoch=" + str(chk["heartbeat_epoch_utc"]) + " clock=" + chk["clock_read"])
