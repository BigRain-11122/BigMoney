import json, os, sys, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
ts = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
sync_note = ("r910 closeout: push to main rejected non-FF (2 incoming); 4-UU rebase on shared regen faces "
             "(attrition_guard_scan/compute_audit/regime_state/token_usage) aborted per round time budget; "
             "branch fallback machine/bm-b-r910 delivered a1022166e..38fb32c9b per D-20260925-01(3); "
             "unreached-to-main=2; r911 S0 FIRST MISSION = fetch + 4-face resolver integration (r782/r747 family) + re-push main")
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding='utf-8'))
st["sync"] = {"last_push_ts": ts, "note": sync_note}
json.dump(st, open(sp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding='utf-8'))
hb["sync"] = {"last_push_ts": ts, "note": sync_note}
json.dump(hb, open(hp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
line = (f"| {ts} | r910 bm-b addendum | push-to-main REJ non-FF (2 incoming) + 4-UU rebase "
        f"(attrition_guard_scan/compute_audit/regime_state/token_usage shared regen faces) -> branch fallback "
        f"machine/bm-b-r910 delivered a1022166e..38fb32c9b (D-20260925-01(3)) | unreached-to-main=2 | "
        f"r911 S0 first mission = fetch + 4-face resolver integration (r782/r747 family, pit-git-resolver required reading) + re-push main | "
        f"inbox 2nd read: MSG-20261013-0045-bmc addressee=bm-a zero bm-b action (bm-c RAM receipt + full-work receipt); "
        f"MSG-20261011-0940-bmb = own outbound to bm-a (recipient-side cleanup) -> inbox zero-for-bm-b | "
        f"orders closeout 2nd scan: NEW_UNACKED=1 was archive-202609 dir artifact = real unacked 0 |")
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
raw = open(rp, encoding='utf-8').read()
if not raw.endswith("\n"): raw += "\n"
raw += line + "\n"
open(rp, 'w', encoding='utf-8', newline='\n').write(raw)
print("SYNC FIX OK", ts)
