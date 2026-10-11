# -*- coding: utf-8 -*-
"""r902 bm-b: E17 leg-3 full-training pool entry registration (raw-text surgical
insert per pit-pool-edit r509/r500/r289 laws: id-anchor absence dual-check,
byte-format preservation, diff line-count self-proof).

Entry: N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN (alphagen RL leg-3 full training,
checkpoint-resumable, prereg N2U3_ALPHAGEN_RL_P1.md FROZEN r892).
"""
import json
import subprocess
import sys

POOL = r"results/runnable_pool.json"
NEW_ID = "N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN"

ENTRY = {
    "id": NEW_ID,
    "ticket_ref": ("N2U3-ALPHAGEN-RL-P1 leg-3 full training (freeze commit 8f49d6eea r892; "
                    "leg-2 probe done 2026-10-11 19:26 bm-b: 256 eps / 8 workers / pretrain+train "
                    "products in ckpt; runner train = additive-episodes + checkpoint resume from "
                    "train_policy.npz + episode-log append-never-reset; leg-3 total budget 4096 eps "
                    "~3.3h est at probe rate 2.9s/ep; judged face NOT in this entry = separate "
                    "export-topk + judge legs per prereg sec.6)"),
    "prereg_ref": ("research/N2U3_ALPHAGEN_RL_P1.md FROZEN 2026-10-11 (r892 freeze commit 8f49d6eea; "
                    "five-condition gate closed; evidence_cutoff=2026-10-09; seed bands "
                    "20625000/20625500/20626000)"),
    "consumer_plan": ("N2U3 chain: leg-3 full training (this entry, 4096 eps from leg-2 probe ckpt) -> "
                      "export-topk K=32 -> judged face (core48 all-start virtual timepoints "
                      "g1_prime_v2/g2_registration_v2) -> N2 U3 channel-1 verdict; consumers = N2 U3 "
                      "channel-1 closeout decision + factor material pool per prereg sec.0.9 item-2; "
                      "P3 prediction face = RL marginal gain honest disclosure at judged"),
    "runner": "scripts/alphagen_rl_p1.py",
    "runner_args": ["train", "--episodes", "4096"],
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "waiting",
    "entered_at": "2026-10-12 01:20:00",
    "data_gates": ("fail-closed rc2 freeze gate in-runner (prereg FROZEN + 3 seed bands required); "
                    "panel gate = E16 frozen cache 2026-10-09 in place; resume face = "
                    "results/alphagen_rl_p1/ckpt/train_policy.npz (falls back to pretrain_policy.npz "
                    "per runner); additive-episode semantics disclosed: interrupted re-claim ADDS a "
                    "fresh budget on top of done_eps -- accepted because training face is uncounted "
                    "(prereg sec.3 trial_budget_law: RL search face and nulls calibration not "
                    "counted) and judged face untouched"),
    "shards": [
        {
            "key": "n2u3-leg3-train",
            "status": "waiting",
            "checkpoint": "",
            "note": "",
        }
    ],
    "workers_plan": {
        "workers": 8,
        "priority": "BelowNormal",
        "note": ("workers=min(worker_cap(),8)=8 per prereg sec.0 workers_plan; parallel marginal "
                 "eval ProcessPool (O-20260930-2355 law-1 conversion); BelowNormal CEO headroom "
                 "law; pure CPU numpy+pandas zero GPU face -- coexists with i2v CEO video lane "
                 "(GPU-bound) without VRAM contention"),
    },
    "host_gates": [
        {"kind": "dir_nonempty", "path": "results/alphagen_rg"},
        {"kind": "dir_nonempty", "path": "results/alphagen_rl_p1/ckpt"},
    ],
    "data_deps": [
        "results/alphagen_rg/panel_cache_2026-10-09.npz",
    ],
}


def main():
    raw = open(POOL, "rb").read()
    if NEW_ID.encode("utf-8") in raw:
        print("ABORT: id already present locally")
        return 3
    origin = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                             capture_output=True).stdout.decode("utf-8", errors="replace")
    if NEW_ID in origin:
        print("ABORT: id already present on origin")
        return 3
    pool = json.loads(raw.decode("utf-8"))
    entries = pool.get("entries")
    print("entries type:", type(entries).__name__, "| n:", len(entries))
    txt = raw.decode("utf-8")
    entry_json = json.dumps(ENTRY, ensure_ascii=False, indent=2)
    entry_json = entry_json.replace("\r\n", "\n").replace("\n", "\r\n")
    if isinstance(entries, list):
        # bracket-count scan from the real entries key to the array close
        key = '"entries": ['
        k = txt.find(key)
        if k < 0:
            print("ABORT: entries key head not found")
            return 2
        depth = 0
        close = -1
        instr = False
        esc = False
        for pos in range(k + len(key) - 1, len(txt)):
            c = txt[pos]
            if instr:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    instr = False
                continue
            if c == '"':
                instr = True
            elif c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
                if depth == 0:
                    close = pos
                    break
        if close < 0:
            print("ABORT: entries array close not found by bracket scan")
            return 2
        print("array close at:", close, "| zone:", repr(txt[close - 40:close + 40]))
        # pool-native serialization (r902 probe: dumps(indent=1) + 2-space prefix
        # per line + CRLF == byte-replica of LEG2 entry face)
        lines = json.dumps(ENTRY, ensure_ascii=False, indent=1).split("\n")
        body = "\r\n".join("  " + l for l in lines)
        head = txt[:close]
        j = head.rfind("}")
        assert j > 0 and head[j + 1:].strip() == "", "pre-close face unexpected"
        new_txt = head[:j + 1] + ",\r\n" + body + head[j + 1:] + txt[close:]
    else:
        print("ABORT: entries is not a list -- inspect manually")
        return 2
    pool2 = json.loads(new_txt)
    ents2 = pool2["entries"]
    assert any(e.get("id") == NEW_ID for e in ents2), "round-trip id missing"
    assert len(ents2) == len(entries) + 1, "round-trip count drift"
    new_raw = new_txt.encode("utf-8")
    assert new_raw.count(b"\r\n") == new_raw.count(b"\n"), "EOL face broken"
    open(POOL, "wb").write(new_raw)
    print("inserted:", NEW_ID, "| old bytes:", len(raw), "| new bytes:", len(new_raw))
    d = subprocess.run(["git", "diff", "--stat", "--", POOL], capture_output=True).stdout.decode(
        "utf-8", errors="replace")
    print("git diff --stat:", d.strip().splitlines()[-1] if d.strip() else "(no diff)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
