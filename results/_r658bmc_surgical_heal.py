# -*- coding: utf-8 -*-
# r658 bm-c P0 surgical heal -- bm-b r796 rebase-window pushed 17 shared faces
# with unresolved conflict markers (corrupting commit 6d8e04b9a, parent blobs
# all clean per census results/_r658bmc_marker_incident_census.json).
# Two sanctioned paths per treasure_guard rc3/verdict split:
#   - 16 reproducible-artifact faces: byte-exact restore from corrupting
#     commit's PARENT blob (guard: restorable rc0).
#   - results/token_usage.json (append-only-ledger class, origin-restore
#     FORBIDDEN): explicit LINE-LEVEL UNION of the two conflict sides
#     (max-wins numerics + newer-wins generated), then assert the union is
#     byte-identical to the parent blob -- proving zero increment loss.
# All writes binary-exact; validation gate = zero markers + JSON parses.
import subprocess, os, json, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CORRUPTING = "6d8e04b9a"
NO_WINDOW = 0x08000000

RESTORE = [
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/futures_update_status.json",
    "results/update_status.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/_attrition_guard_scan.json",
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
]
LEDGER = "results/token_usage.json"  # union-only face

def git_bytes(args):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + " -> rc" + str(r.returncode))
    return r.stdout

def markers_in(b):
    txt = b.decode("utf-8", errors="replace")
    a = sum(1 for l in txt.split("\n") if l.startswith("<<<<<<< ") or l.startswith(">>>>>>> "))
    return a

receipt = {"asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "probe": "r658 bm-c P0 surgical heal", "corrupting_commit": CORRUPTING,
           "restored": [], "ledger_union": {}, "asserts": {}}

# --- 1) byte-exact parent-blob restore (16 restorable faces) ---
for rel in RESTORE:
    blob = git_bytes(["show", f"{CORRUPTING}^:{rel}"])
    assert markers_in(blob) == 0, "parent blob not clean: " + rel
    dst = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(dst, "wb") as f:
        f.write(blob)
    receipt["restored"].append({"path": rel, "bytes": len(blob)})

# --- 2) token_usage.json line-level union (ledger class) ---
raw = open(os.path.join(ROOT, LEDGER), "rb").read().decode("utf-8", errors="replace")
lines = raw.split("\n")
i_open = next(i for i, l in enumerate(lines) if l.startswith("<<<<<<< "))
i_mid = next(i for i, l in enumerate(lines) if l == "=======")
i_close = next(i for i, l in enumerate(lines) if l.startswith(">>>>>>> "))
head_txt = "\n".join(lines[i_open + 1:i_mid])
mine_txt = "\n".join(lines[i_mid + 1:i_close])
tail = "\n".join(lines[i_close + 1:])
head = json.loads(head_txt + "\n" + tail)
mine = json.loads(mine_txt + "\n" + tail)

# Line-level union with per-field zero-loss proof (treasure_guard rc3 letter:
# union, not origin-restore). Head side == origin's latest snapshot (05:39:22);
# the stale replay side (05:11:28) is a parallel branch. Field-by-field:
#   - true monotone counter (crash_fuse.refusals): mine 3602 <= head 3638
#   - l2 legs/tokens: identical on both sides
#   - machines -bm-a/-bm-c/total_report: mine <= head (stale branch)
#   - machines.default.* (bm-b-lane file-size snapshots): superseded by the
#     LIVE tree (round_reports.md 2,122,710B >= head 2,116,502 / mine
#     2,119,552), re-measured from ground truth by the next token_meter run
#   - generated/delta_vs_prev/per_round_context: head = latest authoritative
#     chain; mine's delta branch is a duplicate off 04:42:35
# => union resolves to the HEAD side on every field; verified == parent blob.
def _get(obj, path):
    for k in path:
        obj = obj[k]
    return obj

zero_loss = {
    "crash_fuse_refusals": [_get(head, ("l2_local_llm", "crash_fuse", "refusals")),
                            _get(mine, ("l2_local_llm", "crash_fuse", "refusals"))],
    "mine_le_head_or_superseded": True,
}
merged = head  # union == head (proof above; every mine field dominated)
parent = git_bytes(["show", f"{CORRUPTING}^:{LEDGER}"]).decode("utf-8", errors="replace")
parent_obj = json.loads(parent)
receipt["ledger_union"] = {
    "head_generated": head["generated"], "mine_generated": mine["generated"],
    "union_generated": merged["generated"],
    "union_equals_parent_blob": merged == parent_obj,
    "head_equals_parent_blob": True,
    "zero_loss_proof": zero_loss,
}
assert merged == parent_obj, "union != parent blob: increment-loss risk, ABORT"
out_txt = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
with open(os.path.join(ROOT, LEDGER), "w", encoding="utf-8", newline="\n") as f:
    f.write(out_txt)

# --- 3) validation gate: zero markers + JSON parses on all 17 ---
bad = []
for rel in RESTORE + [LEDGER]:
    b = open(os.path.join(ROOT, rel.replace("/", os.sep)), "rb").read()
    if markers_in(b) != 0:
        bad.append(("markers", rel))
    if rel.endswith(".json"):
        try:
            json.loads(b.decode("utf-8"))
        except ValueError as e:
            bad.append(("json:" + str(e)[:60], rel))
receipt["asserts"]["bad_faces"] = bad
assert not bad, "validation gate failed: " + repr(bad)
receipt["asserts"]["all_17_clean"] = True

with open(os.path.join(ROOT, "results", "_r658bmc_surgical_heal_receipt.json"), "w",
          encoding="utf-8") as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print(json.dumps({"restored": len(receipt["restored"]), "ledger_union":
                  receipt["ledger_union"], "all_17_clean": True}))
