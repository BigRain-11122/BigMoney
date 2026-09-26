# -*- coding: utf-8 -*-
"""R277 bm-a: claim T-85/86/87 per O-20260926-2320 (CEO immediate law: claim-and-start same round).
Byte-face safe ticket edits per R255/R257 laws: probe BOM/EOL/ensure_ascii/indent/trailing-newline,
round-trip json preserving all faces, field-level diff only (verify via --stat after).
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-09-26 23:1x"
CLAIM_NOTE = ("claimed bm-a R277 same-round start per O-20260926-2320 CEO immediate law: "
              "audit v2.3 fix + s1 faces opening this round; batch faces enter runnable pool with "
              "workers_plan as slices land (24h saturation directive); pool shard law = any fleet "
              "machine may burn shards, ticket lock locks science face only")

def probe(p: Path):
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    txt = raw.decode("utf-8-sig" if bom else "utf-8")
    non_ascii = any(ord(c) > 127 for c in txt)
    indent = 1
    for ln in txt.splitlines():
        if ln.startswith(" "):
            indent = len(ln) - len(ln.lstrip(" "))
            break
    trailing_nl = raw.endswith(b"\n")
    return raw, bom, eol, non_ascii, indent, trailing_nl

def main():
    tids = ["T-2026-09-26-85-P1", "T-2026-09-26-86-P1", "T-2026-09-26-87-P1"]
    for tid in tids:
        p = ROOT / "fleet" / "tasks" / f"{tid}.json"
        raw, bom, eol, non_ascii, indent, tnl = probe(p)
        d = json.loads(raw.decode("utf-8-sig" if bom else "utf-8"))
        assert d.get("status") == "open", f"{tid} status={d.get('status')} ABORT (anti-collision)"
        d["status"] = "claimed"
        d["claimed_by"] = "bm-a"
        d["claimed_at"] = NOW
        d["claim_note"] = CLAIM_NOTE
        out = json.dumps(d, ensure_ascii=not non_ascii, indent=indent)
        if tnl:
            out += "\n"
        data = out.encode("utf-8")
        if bom:
            data = b"\xef\xbb\xbf" + data
        if eol == b"\r\n":
            data = data.replace(b"\n", b"\r\n")
        p.write_bytes(data)
        print(f"{tid}: claimed (bom={bom} eol={eol!r} ascii={not non_ascii} indent={indent} tnl={tnl})")
    r = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True, cwd=ROOT)
    print("--- git diff --stat (must be field-level) ---")
    print(r.stdout)

if __name__ == "__main__":
    main()
