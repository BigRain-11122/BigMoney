# r329 bm-a: S7 closeout writer -- state r329 + heartbeat + round report line (one atomic writer)
import json, io, time, datetime

now = datetime.datetime.now()
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
epoch = int(time.time())
clock_read = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

DID = ("R329: S0 INHERITED-REBASE COMPLETION = r328 dead-session mid-rebase rescued and LANDED "
       "(16-UU canon-resolved per skill: CODELY memory-union+shiliu-pi archival bidirectional-entry-verified 8405B zero-loss zero-phantom; "
       "autofill composite-key union 45 zero-divergent incl bm-b 14:20:02 W2A launch preserved; "
       "compute_audit ts-key union 210|201->211 overlap-200-identical survival-proofed; regime asof-union state-take-new; "
       "daily-report json+md twins coupled-side :3: newer 14:39:44; dashboard js same-second tie->origin r140; "
       "12 snapshot/status faces take-new-by-deep-ts; resolver=results/_r328bma_resolve3.py code-review-fixed 3 latent bugs) "
       "-> rebase continue ONE-PASS (no r329 false-refusal) -> push LANDED f3afd952..a36cf53c r328 message-faithful; "
       "S0.5 orders 96/96 round-start wrap-both-scans zero-unacked + decisions origin-direct aacae41 zero-new-rows (D-06..10 all receipted r327/r328); "
       "smoke 25/25; S6 32/32 rc=0 (_r329bma_s6_chain.ps1 r326-lineage header-delta, 32-leg resident form per r329 pitlaw); "
       "W2-A takeover decision point DISCHARGED NOT by takeover: bm-b autofill launched burn 14:20:02 pid7796 per MSG-20260927-1428 spec-reading-ack "
       "(code-join universe >=5000 fail-closed accepted, probe-first overtaken, 3-6h est) -- bm-a zero-action, pool ready-face = pre-harvest normal r312; "
       "sina_mf A1 repull probe 5017/5228=96.0% zero-fail live-advancing ETA ~15:03 next-round three-piece")

VERDICT = ("green: red=false lane healthy @14:54; py_low_with_work_cands LEGAL-occupied double-face: "
           "sina_mf A1 repull in flight 96% (network-paced zero CPU conflict) + W2-A census burn in flight bm-b pid7796 since 14:20:02; "
           "audit v2.3 CLEAN flags=[]; board 0 open; orders 96/96 double-scan zero-unacked")

NEXT = ("R330+: (1) sina_mf repull terminal three-piece ~15:0x (update_sina_mf exit-code law + sina_mf_accept sec-4 gates "
        "coverage>=5000/self-collapse-zero/idempotency + N=250 depth census) then moneyflow-IC gate unblock + MSG ready-panel notice; "
        "(2) W2-A burn harvest watch bm-b lane (3-6h est, checkpoint face, pool done-flip by bm-b per r312); "
        "(3) R330 5x HANDOVER check due; (4) SKILL.md twin-coupling + in-place-union manual-verify recipe sync candidate (r83 law, low priority); "
        "(5) Mon 09-28: T-91 s3 auto-fire 09:15 + Monday new-bar chain 32-leg resident form (REGIME_GUARD enforce request-face pre-10-01 date-gate shadow); "
        "(6) 10-01 month trio (science_audit + monthly_briefing + self_review)")

# ---- state file
sp = "state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 329
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
for k in ("ts", "last_round_ts", "updated_at", "last_seen"):
    st[k] = ts_iso
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")
json.loads(io.open(sp, encoding="utf-8").read())
print("state r329 written")

# ---- heartbeat
hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = ts_iso
hb["current_task"] = "R329 done: inherited r328 rebase landed (16-UU canon-resolved); R330: sina_mf terminal three-piece + W2-A harvest watch + HANDOVER 5x"
hb["task"] = "R329 done: inherited rebase re-land + W2-A takeover decision discharged (bm-b burn in flight); R330: repull three-piece + HANDOVER 5x"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock_read
hb["round_no"] = 329
hb["verdict"] = VERDICT
hb["cpu_pct"] = 15.0
hb["cpu_util_pct"] = 15.0
hb["free_ram_gb"] = 53.0
hb["idle_ram_gb"] = 53.0
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
v = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in v["clock_read"], "clock_read must be T-separated ISO 8601 (R262 law)"
print("heartbeat written: epoch=%d int OK clock=%s" % (v["heartbeat_epoch_utc"], v["clock_read"]))

# ---- round report
rp = "logs/iteration-loop/round_reports-bm-a.md"
line = ("%s | R329 bm-a (dept:engineering+fleet+governance) | WM first-line verdict: %s | did: %s | next: %s | evidence: results/_r328bma_resolve3.py + _r329bma_repull_probe.json + _r329bma_s6_chain.ps1 (32/32 rc=0) | inbox: MSG-20260927-1428 (bm-b W2A spec-reading-ack, to bm-a) processed->processed dir; MSG-1407 (bm-c->bm-b autofill cc-strip) not-ours left in place\n" % (clock_read, VERDICT, DID, NEXT))
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report line appended")
