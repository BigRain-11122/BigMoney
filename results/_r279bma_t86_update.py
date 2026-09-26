# R279 bm-a T-86 ticket progress write (R255/R257 five-face probe law: BOM/EOL/ensure_ascii/indent/trailing-newline)
# Field-level increment only; progress_r279bma = this machine's round-tagged field (r262 identity law)
import json
import sys

PATH = "fleet/tasks/T-2026-09-26-86-P1.json"
raw = open(PATH, "rb").read()
face = {
    "bom": raw.startswith(b"\xef\xbb\xbf"),
    "crlf": b"\r\n" in raw,
    "ends_nl": raw.endswith(b"\n"),
    "ascii": raw.decode("utf-8-sig", "replace").isascii(),
}
d = json.loads(raw.decode("utf-8-sig"))
assert "progress_r277" in d, "anchor field missing"
d["progress_r279bma"] = (
    "bm-a R279: s1 canonical deliverable LANDED = research/FACTOR_CENSUS_REGISTRY.md "
    "(single-source inventory: A engine 28 / B zoo85_stv+terrified+coin_team+zoo93_arc family (frozen r218) / "
    "C GTJA191+WQ101+A158-truegap (T-48 factor_registry.py r162) / D sina-MF four-tier (T-72 collected face) / "
    "E LHB+heat / F bench rs x2; zero-invention law rows anchored to source files; s2 combinatorial census "
    "consumes registry rows only, prereg freeze BEFORE judged runs per R99). R278 dead-round gap closed "
    "(bm-b r279 probe had found file absent); s2 census runner + pool entry = next slice."
)
body = json.dumps(d, ensure_ascii=False, indent=1)
if face["crlf"]:
    body = body.replace("\n", "\r\n")
if face["ends_nl"]:
    body += "\n"
open(PATH, "wb").write((("\ufeff" + body) if face["bom"] else body).encode("utf-8"))
d2 = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
assert "progress_r279bma" in d2
print(f"ticket updated: face={face}")
sys.exit(0)
