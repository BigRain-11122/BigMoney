# -*- coding: utf-8 -*-
"""R266 bm-a -- T-83 s4 quarterly entropy-audit wiring confirmation.

Slice claimed per R263 yield-note open face (bm-b s1/s2 owner untouched, GM
s3 reserved). Deliverables:
  1. Tools/iteration_prompt.txt quarterly leg (already inserted via editor)
  2. Ticket progress_r266 slice note (five-face byte-mirrored per R254/255/257)
  3. post_review criteria row T-83-S4-QUARTERLY-WIRING (pre-frozen spec face)
Fail-closed: every face probe asserted before any write.
"""
import json
import subprocess
import sys

TICKET = "fleet/tasks/T-2026-09-26-83-P1.json"
CRIT = "results/post_review_criteria.json"


def probe(path):
    raw = open(path, "rb").read()
    return {
        "bom": raw[:3] == b"\xef\xbb\xbf",
        "crlf": raw.count(b"\r\n"),
        "lf_only": raw.count(b"\n") - raw.count(b"\r\n"),
        "trailing_nl": raw.endswith(b"\n"),
        "ascii_esc": b"\\u" in raw,
    }


def write_mirror(path, obj, faces, indent):
    # mirror BOM / CRLF / trailing-newline / ensure_ascii faces exactly
    txt = json.dumps(obj, ensure_ascii=False, indent=indent) + ("\n" if faces["trailing_nl"] else "")
    with open(path, "w", encoding="utf-8" if not faces["bom"] else "utf-8-sig",
              newline=None) as fh:  # newline=None: \n -> CRLF on win32
        fh.write(txt)


def main():
    tf = probe(TICKET)
    assert not tf["bom"], "ticket BOM face drift"
    assert tf["lf_only"] == 0, "ticket has LF-only lines"
    t = json.loads(open(TICKET, encoding="utf-8-sig").read())
    # indent face: count leading spaces of second line (R255 law)
    raw_lines = open(TICKET, "rb").read().decode("utf-8-sig").split("\r\n")
    body = [l for l in raw_lines[1:] if l.strip() and not l.strip().startswith("}")]
    indents = {len(l) - len(l.lstrip(" ")) for l in body}
    assert len(indents) == 1, f"indent face mixed: {indents}"
    indent = indents.pop()
    assert "progress_r266" not in t, "progress_r266 already present"

    t["progress_r266"] = (
        "bm-a R266: s4 DELIVERED (slice per R263 yield-note open face; zero overlap "
        "with bm-b s1/s2 + GM-reserved s3) -- quarterly entropy-audit standing wiring "
        "confirmed & landed: Tools/iteration_prompt.txt 每季首轮加跑治理法熵审视 leg "
        "inserted (cadence=quarter-first-round nine-layer refresh + conflict/dead-face "
        "detection; GM-signed optimization per O-1355 discipline; group canon pointer="
        "cph4/retention.md §10 每季行 L3+CEO 法熵审视 + §8.5 流程瘦身日; instance ledger="
        "T-83 this batch is the 2026-Q4 slot early-trigger instance, fired 09-26 ahead "
        "of the 10-01 boundary, slot discharged, no governance double-run at 10-01; "
        "next regular instance=2027-01-01 first round Q1-2027); post_review row "
        "T-83-S4-QUARTERLY-WIRING registered same round (4 machine checks, spec s4 "
        "frozen face); ticket stays claimed by bm-b (s1/s2 owner) pending GM s3"
    )
    write_mirror(TICKET, t, tf, indent)

    cf = probe(CRIT)
    assert not cf["bom"], "criteria BOM face drift"
    c = json.loads(open(CRIT, encoding="utf-8-sig").read())
    clev = c["items"]
    assert not any(r.get("id") == "T-83-S4-QUARTERLY-WIRING" for r in clev), "row exists"
    clev.append({
        "id": "T-83-S4-QUARTERLY-WIRING",
        "claim": (
            "T-83 s4 quarterly entropy-audit wiring confirmed (O-20260926-1355 常设化): "
            "BigMoney cadence = 每季首轮治理法熵审视 (nine-layer inventory refresh + "
            "conflict/duplication/dead-face detection; GM-signed optimization per "
            "O-1355 discipline: measure-first / thin-law pointers / archive-not-delete "
            "/ CEO reserved faces untouched) wired into Tools/iteration_prompt.txt "
            "standing prompt; group canon pointer = cph4/retention.md §10 每季行 "
            "(L3+CEO 法熵审视) + §8.5 流程瘦身日; instance ledger: T-83 batch = "
            "2026-Q4 slot early-trigger instance (09-26 ahead of 10-01 boundary, slot "
            "discharged, no double-run at 10-01), next regular = 2027-01-01 first round"
        ),
        "claim_source": (
            "T-2026-09-26-83-P1.json spec slice s4 (frozen at ticket creation "
            "13:55 per O-1355 派工) + cph4/retention.md §10 L108 quarterly row + "
            "Tools/iteration_prompt.txt s4 leg (this round, R266 bm-a)"
        ),
        "status": "closed",
        "checks": [
            {"kind": "file_contains",
             "args": ["Tools/iteration_prompt.txt", "每季首轮加跑治理法熵审视"]},
            {"kind": "file_contains",
             "args": ["Tools/iteration_prompt.txt", "cph4/retention.md §10"]},
            {"kind": "file_contains",
             "args": ["Tools/iteration_prompt.txt", "2027-01-01"]},
            {"kind": "file_contains",
             "args": ["fleet/tasks/T-2026-09-26-83-P1.json", "progress_r266"]},
        ],
    })
    write_mirror(CRIT, c, cf, 1)

    # post-write verification: parse-back + face re-probe + git diff --stat
    t2 = json.loads(open(TICKET, encoding="utf-8-sig").read())
    assert t2["progress_r266"].startswith("bm-a R266")
    c2 = json.loads(open(CRIT, encoding="utf-8-sig").read())
    assert any(r["id"] == "T-83-S4-QUARTERLY-WIRING" for r in c2["items"])
    for p, old in ((TICKET, tf), (CRIT, cf)):
        f2 = probe(p)
        assert f2["bom"] == old["bom"] and f2["trailing_nl"] == old["trailing_nl"], p
        assert f2["lf_only"] == 0, f"{p} LF-only leak"
    st = subprocess.run(["git", "diff", "--stat", "--", TICKET, CRIT],
                         capture_output=True, text=True, encoding="utf-8").stdout
    print(st)
    print("WIRING OK: ticket progress_r266 + criteria row registered, faces mirrored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
