import json, time, datetime
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
# state file
s = json.load(open("state-bm-a.json", encoding="utf-8"))
s["round_no"] = 420
s["did"] = "r420-cont closeout+integration: harvested dead r420 session S6 products (51 faces verified in 08:14-08:20 window, chain-complete through token_meter) -> commit 5e02c28f; merge origin/main bm-b r415 W6-JUDGE closure per pit-93 two-step (18 UU: 11 morning-resolver reuse all-take-ours fresher, 1 prospect take-new, 6 ALL_FACES merge_lane_views resolve union) -> merge 7bd9be1fe; escape branch machine/bm-a-r420 + atomic FF main push LANDED; post-merge dualrun sampled drift honestly (shared top updated_at 06:00:54 ISO vs merged 07:33, streak reset 0, observation-phase) -> same-window compute_audit leg sync_face settle healed pool face (wrote_shared+wrote_lane); audit FLAG:supply_floor ready=0<3 standing; orders 122/122 zero-diff; decisions.md 03:20 no-new; smoke 26/26"
s["verify"] = "harvest+merge+escape+FF push all landed (076c1ba46..7bd9be1fe main); UU=0 post-resolve; smoke 26/26; dualrun drift recorded + pool settle confirmed {wrote_shared:true,wrote_lane:true}; watermark red=false lane healthy next_pick=claimed"
s["next"] = "supply side per TRIAL_LABOR_LAW: pool EMPTY (110/110 full-clear per bm-b r415) + supply_floor breach 16h standing -> next round draft next trial wave candidate batch (frozen grammar, dedup gate T-84s3) or standby-pool supply intake B2-B4; W6-JUDGE chain family all-dead verdict 48h CEO clock (deadline 2026-10-01 08:14, bm-b owns); 10-01 month-first triple + REGIME_GUARD v3 activate"
s["last_round_at"] = now
s["current_task"] = "r420-cont closeout+integration round"
s["updated"] = now
s["last_round_ts"] = now
json.dump(s, open("state-bm-a.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
# heartbeat
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
h["last_seen"] = now
h["current_task"] = "r420-cont: harvest dead-session products + pit-93 merge (18 UU canon-resolved) + FF main push landed + post-merge pool settle"
epoch = int(time.time())
assert isinstance(epoch, int)
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
h["round_no"] = 420
h["verdict"] = "r420-cont recovered: dead r420 session S6 products harvested + bm-b r415 integrated via pit-93 two-step merge (escape branch + atomic FF push, zero rebase replays); post-merge pool face settled same-window; supply_floor standing (pool empty) -> trial-labor next-wave drafting = next round head; smoke 26/26"
json.dump(h, open("fleet/machines/bm-a.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
back = json.loads(open("fleet/machines/bm-a.json", encoding="utf-8").read())
assert isinstance(back["heartbeat_epoch_utc"], int)
print("state+heartbeat written, epoch int-verified:", epoch)
