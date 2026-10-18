# -*- coding: utf-8 -*-
# _r1087bmc_closeout.py - r1087 closeout: state 1087->1088 + heartbeat (epoch int)
# + ledger path-split heal (r1086 row union logs->root verbatim per r750/r985 family)
# + canonical round-row append to ROOT round_reports-bm-c.md. Fresh read-modify-write.
import io, json, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(now.timestamp())
STATE = REPO + r"\state-bm-c.json"
HEART = REPO + r"\fleet\machines\bm-c.json"
ROOT_LEDGER = REPO + r"\round_reports-bm-c.md"
LOGS_LEDGER = REPO + r"\logs\iteration-loop\round_reports-bm-c.md"

did = ("r1087: O-20261018-0948 bm-c receipt duties FULL same-window (v2 adoption verified: own spawning line "
       "'10:35:02 spawning headless round (hard-cap 240min, silence-kill 25min, prompt_chars=31210...)'; TIMEOUT census "
       "432 total most-recent 09:50:02; MiniGame-family audit 7 runners + watchdog: SAME DISEASE x2 fixed in place "
       "(EngineTick.ps1 20-min wall + ModeTick.ps1 HardKillSeconds wall -> liveness-gated budget: per-lane silence "
       "gates on stdout+stderr byte growth + 240-min hard cap + whole-tree kill; task args/locks untouched; "
       "TIMEOUT_KILLED/EXIT_254 substrings preserved; PS Parser 0 errors; pure ASCII) = MiniGame commit df88bb98a; "
       "zero-adaptation x3 TickWatchdog/ComfyDraftWorker_C/siliconwatch-generate; receipts MSG-20261018-1047-bmc-rootfix "
       "+ order-file receipt section) + ORD delta consumed 8f6162d9->aaba08bb (two 09:5x rows; mem-gate --report "
       "87,546B/95) + W267 PREREG FREEZE LANDED origin df55e3fab9 (ALL GATES PASS 3rd-try, 2 needle heals, banned ADMIT "
       "rc0, 23,008B sha256_16 0918b8990154a23b; bands A 602_701..604_700 16th A-hop / B 604_701..604_900 17th "
       "above-own-A) + smoke 49/49 + S6 10/10 rc0 (dualrun streak 44 / fundprem weekend no-op / clock ORANGE_COOL / "
       "dreport faces=5 / token 0) + push non-FF stash-bridge rebase clean (receipt bff1822597 + freeze df55e3fab9)")

next_pointer = ("r1088: (1) W267 SPLICE CHAIN = FIRST ACTION per frozen prereg df55e3fab9: needle preflight (MEASURED "
                "counts on the W267 prereg face per r1077 law) + editor derive canon-clone of the W266 editor "
                "(_w266bmc_derive_editor.py family, age() machine-needle law) -> freeze_edits -> five-face splice -> "
                "engine mtime-watch self-burn 12/12 -> sixgate PRE-FINALIZE (30th consecutive target) -> finalize "
                "one-pass -> fivekeys 6/6 -> sec.7/8 backfill -> W268 seat publish (W268p projection A naive "
                "604_701..606_700 / B 604_901..605_100 on the pre-W267 universe; live re-derive governs r587 never "
                "transcribe); (2) Monday 10-20 15:30 bars window: full papers chain fires (weekend 10-18/19 no bars, "
                "cutoff 10-16, papers debt=0); (3) 24h died-pre-closeout incident-review watch standing per "
                "O-20261018-0948 sec.3.4 (v2 live since the 10:35 firing; recurrence = gate-failure review law); "
                "(4) next 5x HANDOVER row due at r1090; (5) GPU lane = gen-only (CEO weekend-use standing, loop "
                "CPU-only); short-video lane DISABLED standing per O-20261017-1741")

latest_artifact = ("research/PERPETUAL_N1_W267_PREREG.md (23,008B/64 lines, sha256_16 0918b8990154a23b, origin "
                   "df55e3fab9, frozen 2026-10-18 10:5x) + fleet/inbox/MSG-20261018-1047-bmc-rootfix.md + MiniGame "
                   "repo commit df88bb98a (EngineTick+ModeTick v2 liveness fix)")

prod_lanes = ("CPU=engine W267 supply chain armed (prereg frozen df55e3fab9; splice chain = r1088 FIRST ACTION) ; "
              "GPU=gen-only lane (CEO weekend-use standing: GPU 6% idle window, loop CPU-only); short-video lane "
              "DISABLED standing per O-20261017-1741")

verify = ("smoke 49/49 + satengine ALIVE rc0 (burns/queue idle; W267 prereg frozen) + attrition 4 CLEAN + dualrun "
          "ZERO-DRIFT streak 44 + W267 freeze origin-landed df55e3fab9 + receipt bff1822597 + d19 advance read-back "
          "aaba08bb + canonical orders_ack BOTH faces 227 (O-20261018-0948 acked; --help probe-pollution healed "
          "same-window) + orphan face=0 zero-kill + idle --worked rc0 + epoch int readback + ledger path-split heal "
          "(r1086 row union logs->root verbatim) + behind-origin=0 (closeout push rides this window)")

closeout_note = ("r1087: (1) S0-1 anchor bm-c + probe py_faces=3 orphans=0 zero-kill + S0 discard-5-regenerables + "
                 "pull (bm-a r1052 W267-seat race YIELD chain: bm-c MSG-1025 10:25 on origin beats bm-a local "
                 "10:28:55, W267 = bm-c 86th own wave) + group fetch bda53c2..90cc777; (2) S0.5 probe rc3: ORD delta "
                 "TRUE consumed 8f6162d9->aaba08bb via d19 update --advance (rows = O-20261018-0948 root-cure "
                 "[bm-c ACTIONABLE executed same-window per CEO-ticket law] + CEO order-2 memory/continuity [bm-c "
                 "legs: gate --report 87,546B/95 entries + zero local cleanup owed; snapshot-before-clean law "
                 "standing]); dec delta FALSE hold 0ad85a30; unacked=[O-20261018-0948-bm-a] -> acked via canonical "
                 "orders_ack_append BOTH faces (r1052-bma two-face law; --help probe-pollution healed same-window "
                 "zero residue); (3) S1 smoke 49/49 (r1086 deferred debt cleared); (4) P0 CEO-TICKET O-20261018-0948 "
                 "receipt duties FULL execution incl. MiniGame cross-repo fix (commit df88bb98a, push/sync stays in "
                 "the EngineTick lane self-heal domain, repo intentionally behind origin per the 10-18 00:3x "
                 "alignment row); (5) P0 PRODUCT W267 PREREG FREEZE: frozen face triple byte-verified + needle probe "
                 "+ block-classification ctx-dumps (18 raw W267 = 2 non-block leg-covered + 16 block-interior; 07:0x "
                 "2 non-block + 2 block-interior; bands/shas classified) + derive ALL GATES PASS 3rd-try with 2 "
                 "disclosed heals + banned ADMIT; push non-FF -> stash-bridge (state d19 advance preserved through "
                 "bridge; watermark_red UU resolved origin-face regenerable live-wins) -> rebase clean -> LANDED; "
                 "(6) S6 10 legs rc0 weekend-honest; (7) S7: attrition 4 CLEAN + idle --worked rc0 + ledger "
                 "path-split heal (r1086 row logs->root verbatim union, r985 family 5th instance disclosed) + this "
                 "closeout writes the CANONICAL root path per r750 law; counter 1087->1088")

# --- ledger path-split heal: union the r1086 row from logs -> root (verbatim) ---
logs_txt = io.open(LOGS_LEDGER, encoding="utf-8", newline="").read()
root_txt = io.open(ROOT_LEDGER, encoding="utf-8", newline="").read()
marker = "2026-10-18T10:28:15+08:00 | r1086 | "
healed = False
for line in logs_txt.split("\n"):
    if line.startswith(marker):
        if line not in root_txt:
            if not root_txt.endswith("\n"):
                root_txt += "\n"
            root_txt += line + "\n"
            healed = True
        break
assert any(l.startswith(marker) for l in logs_txt.split("\n")), "r1086 row not found in logs ledger"

row = (ts + " | r1087 | bm-c | watermark verdict=green (red=false / satengine ALIVE rc0 W267 prereg frozen + "
       "receipt duties done / dualrun streak 44) | r1087 (clean continuation window, counter at open 1087, advanced "
       "1087->1088 so next=r1088): (1) S0-1 anchor bm-c + probe py_faces=3 orphans=0 zero-kill; S0 discard-5-"
       "regenerables + pull (bm-a r1052 W267-seat race YIELD) + group fetch; (2) S0.5 probe rc3 -> ORD delta TRUE "
       "consumed 8f6162d9->aaba08bb (rows = O-20261018-0948 root-cure [ACTIONABLE executed same-window] + CEO "
       "order-2 [bm-c legs --report 87,546B/95]); dec hold; unacked [O-20261018-0948] -> canonical orders_ack_append "
       "BOTH faces 227 (two-face law; --help pollution healed); (3) smoke 49/49 (r1086 debt cleared); (4) P0 "
       "CEO-TICKET O-20261018-0948 receipt duties FULL: v2 adoption verified (own spawning line hard-cap 240min / "
       "silence-kill 25min), TIMEOUT census 432/most-recent 09:50:02, MiniGame audit: SAME DISEASE x2 fixed in place "
       "(EngineTick 20-min wall + ModeTick HardKillSeconds wall -> liveness-gated, task args/locks untouched, "
       "consumer substrings intact, PS Parser 0, pure ASCII) = MiniGame commit df88bb98a; zero-adaptation x3; "
       "receipts MSG-1047 + order receipt section; (5) P0 PRODUCT W267 PREREG FREEZE origin df55e3fab9: frozen face "
       "triple byte-verified (22,970B sha256_16 a273485226cbeefa == blob 417bc0b8 @ 595433d63c pre-backfill; HEAD "
       "twin a9b453235f disclosed NOT used), ALL GATES PASS 3rd-try (2 disclosed needle heals: se_mu chain trailing "
       "label P1-captured->W267 + W264 0.000323->0.000322 true-history), banned ADMIT rc0, out 23,008B sha256_16 "
       "0918b8990154a23b; bands A 602_701..604_700 SIXTEENTH A-hop / B 604_701..604_900 SEVENTEENTH above-own-A; "
       "push non-FF -> stash-bridge -> rebase -> LANDED receipt bff1822597 + freeze df55e3fab9 behind=0; (6) S6 10 "
       "legs rc0 (dualrun streak 44 [461] / update_daily weekend no-op cutoff 10-16 / clock CALL-2026-10-16 "
       "ORANGE_COOL / fundprem weekend no-op bm-c lane / dreport faces=5 / token 0); (7) S7: attrition 4 CLEAN + "
       "idle --worked + ledger path-split heal (r1086 row union logs->root verbatim, r985 family) | verify: smoke "
       "49/49 + freeze df55e3fab9 + receipt bff1822597 + d19 read-back aaba08bb + ack both faces 227 + attrition "
       "CLEAN + behind-origin=0 | orphan face=0 | next r1088: W267 SPLICE CHAIN FIRST ACTION (editor canon-clone + "
       "needle preflight MEASURED + five-face splice -> burn 12/12 -> sixgate 30th -> finalize -> fivekeys -> "
       "sec.7/8 -> W268 seat) + Monday 10-20 15:30 papers chain + 24h died-pre-closeout watch standing")
if not root_txt.endswith("\n"):
    root_txt += "\n"
root_txt += row + "\n"
io.open(ROOT_LEDGER, "w", encoding="utf-8", newline="").write(root_txt)
print("ledger: r1086-row healed=%s ; r1087 row appended to ROOT canonical (%d bytes)" % (healed, len(row.encode("utf-8"))))

# --- state ---
d = json.load(io.open(STATE, encoding="utf-8"))
d["round_no"] = 1088
d["round_no_label"] = "r1087 closeout -> counter 1088"
d["last_round"] = "r1087"
d["last_round_at"] = ts
d["last_round_ts"] = ts
d["last_seen"] = ts
d["last_round_label"] = "r1087"
d["last_round_closed"] = ts
d["clock_read"] = ts
d["ts"] = ts
d["updated"] = ts
d["updated_at"] = ts
d["now_active"] = ts
d["activity_now"] = ts
d["current_task"] = "r1087 closeout: O-20261018-0948 receipt + W267 prereg freeze; next = W267 splice chain r1088 FIRST ACTION"
d["current_task_at"] = ts
d["did"] = did
d["last_round_summary"] = did
d["last_round_summary_at"] = ts
d["last_action"] = "r1087 closeout (O-20261018-0948 bm-c receipt + W267 PREREG FREEZE df55e3fab9 + S6 10/10 + ledger path-split heal; counter 1087->1088)"
d["last_action_at"] = ts
d["verdict"] = "green: r1087 = clean continuation product window (counter 1087 at open, executed r1087, advanced 1087->1088); product = O-20261018-0948 bm-c receipt duties FULL (v2 adoption + 432 TIMEOUT census + MiniGame cross-repo liveness fix df88bb98a) + W267 PREREG FREEZE origin df55e3fab9 (ALL GATES PASS, banned ADMIT, 16th A-hop / 17th above-own-A staircase continues); engine daemon alive; CEO weekend-use standing (loop CPU-only); short-video lane DISABLED standing per O-20261017-1741"
d["next"] = next_pointer
d["next_pointer"] = next_pointer
d["next_milestone"] = "W267 splice chain -> burn -> sixgate 30th -> finalize (r1088-r1089, within 48h); Monday 10-20 15:30 bars papers chain; 24h dead-window watch (O-20261018-0948)"
d["latest_artifact"] = latest_artifact
d["last_artifact"] = latest_artifact
d["recent_artifact"] = latest_artifact
d["head_sha"] = "r1087 closeout (O-20261018-0948 receipt bff1822597 + W267 PREREG FREEZE df55e3fab9; counter 1087->1088)"
d["prod_lanes"] = prod_lanes
d["full_load_selfproof"] = {"占用一行": prod_lanes}
d["verify"] = verify
d["orphan_face"] = 0
d["orphan_faces"] = 0
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["r1087_closeout_note"] = closeout_note
d["orders_ack_ts"] = ts
d["orders_ack_receipt"] = ("r1087: O-20261018-0948-bm-a acked via canonical orders_ack_append BOTH faces (count 227 "
                           "state+heartbeat; --help probe-pollution healed same-window zero residue); ORD delta "
                           "consumed 8f6162d9->aaba08bb (rows: root-cure [ACTIONABLE executed same-window] + CEO "
                           "order-2 [--report leg done 87,546B/95]); dec hold 0ad85a30; unacked=0")
d["last_orders_sha_note"] = "r1087: ORD 8f6162d9->aaba08bb consumed via d19 update --advance (pinned content-sha1 method r977), read-back full-string equality"
d["last_decisions_read_note"] = "r1087: DEC delta FALSE hold (raw-blob sha256 0ad85a30 pinned-probe, zero rows owed)"
io.open(STATE, "w", encoding="utf-8", newline="").write(json.dumps(d, ensure_ascii=False, indent=1))

# --- heartbeat (mirror core faces; epoch MUST be int) ---
h = json.load(io.open(HEART, encoding="utf-8"))
h["clock_read"] = ts
h["ts"] = ts
h["updated"] = ts
h["updated_at"] = ts
h["last_seen"] = ts
h["last_seen_at"] = ts
h["now_active"] = ts
h["activity_now"] = ts
h["current_task"] = d["current_task"]
h["current_task_at"] = ts
h["current_task_ts"] = epoch
h["did"] = did
h["last_round_summary"] = did
h["last_round_summary_at"] = ts
h["last_round"] = "r1087"
h["last_round_at"] = ts
h["last_round_ts"] = ts
h["last_round_closed"] = ts
h["round_no"] = 1088
h["round_no_label"] = d["round_no_label"]
h["last_action"] = d["last_action"]
h["last_action_at"] = ts
h["verdict"] = d["verdict"]
h["next"] = next_pointer
h["next_pointer"] = next_pointer
h["next_milestone"] = d["next_milestone"]
h["latest_artifact"] = latest_artifact
h["last_artifact"] = latest_artifact
h["recent_artifact"] = latest_artifact
h["head_sha"] = d["head_sha"]
h["prod_lanes"] = prod_lanes
h["full_load_selfproof"] = {"占用一行": prod_lanes}
h["verify"] = verify
h["heartbeat_epoch_utc"] = epoch
h["heartbeat_epoch_utc_type"] = "int (assert)"
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orders_ack_ts"] = ts
h["r1087_closeout_note"] = closeout_note
h["health"] = "ok"
h["sync"] = {"origin_tip": "r1087 closeout commit rides this window (push + fetch-verify same window)", "ts": ts}
io.open(HEART, "w", encoding="utf-8", newline="").write(json.dumps(h, ensure_ascii=False, indent=1))

# --- self-verify: epoch int + ack closure + json validity ---
d2 = json.load(io.open(STATE, encoding="utf-8"))
h2 = json.load(io.open(HEART, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch not int"
assert d2["round_no"] == 1088 and h2["round_no"] == 1088
assert "O-20261018-0948-bm-a.md" in d2["orders_ack"] and "O-20261018-0948-bm-a.md" in h2["orders_ack"]
assert "--help" not in d2["orders_ack"] and "--help" not in h2["orders_ack"]
assert d2["last_orders_sha"] == "aaba08bb506addbff0c5f731315ff04941dc2fde"
print("state: round_no=1088 epoch=%d (int) ack=%d orders_sha=%s" % (h2["heartbeat_epoch_utc"], len(h2["orders_ack"]), d2["last_orders_sha"]))
print("closeout OK @ " + ts)
