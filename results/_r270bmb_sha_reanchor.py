"""r270 bm-b -- post_review criteria sha re-anchor to EOL-normalized (git-blob canonical) face.

Context: 3 T-81 rows derived NO on bm-b because their json_field sha anchors were
registered from bm-a's working-tree face (autocrlf=true -> CRLF disk face), while
results/strategy_scorecard.json is regenerated every S6 round by whichever machine
runs it (hashlib over raw disk bytes -> machine-dependent value). Same-file identity
modulo EOL is preserved (R253 law family: content-equal modulo \\r passes; raw vs
LF-normalized double gate). Producers were fixed this round to hash the LF-normalized
face, so the anchors must be re-encoded to the same frozen files' canonical face.

R256 law: fact-verify first, then durably re-encode the SAME frozen fact + _reconciled
annotation. No check is deleted or weakened -- each json_field keeps pinning the exact
sha256_16 of the exact prereg file; only the face convention changes (CRLF-disk ->
git-blob LF), and both faces are byte-proven equal modulo EOL below.
"""
import hashlib
import json
import subprocess

REG = "results/post_review_criteria.json"
FILES = {
    "T-81-PROFILE-CARDS": ("research/PROFILE_CARDS_P1.md",
                           "profile_cards.prereg_sha256_16"),
    "T-81-SAMPLE-SCIENCE": ("research/SAMPLE_SCIENCE_P1.md",
                            "profile_cards.sample_science_prereg_sha256_16"),
    "T-81-LANDING-HOOKS": ("research/LANDING_HOOKS_P1.md",
                           "landing_hooks.prereg_sha256_16"),
    "T-81-L3-ACTIVATION-EVIDENCE": ("research/L3_ACTIVATION_EVIDENCE.md",
                                     "l3_evidence.prereg_sha256_16"),
}
RECONCILE_NOTE = (
    " | 2026-09-26 19:3x r270 bm-b: T-81 sha anchors re-encoded from CRLF working-tree "
    "face to EOL-normalized git-blob face (producers strategy_scorecard.py x3 + market_clock_call.py "
    "now hash LF-normalized bytes; oscillating YES/NO by regenerating machine was the defect -- r269 "
    "YES x4 derived against bm-a-face scorecard pre-19:26:46 regen, NO x3 post-regen on bm-b LF face; "
    "fact-proof: sha256(CRLF face of each prereg) == old anchor value byte-exact, same file modulo \\r; "
    "R253/R256 family: same frozen fact, canonical face, zero check deleted/weakened)"
)


def faces(path):
    raw = open(path, "rb").read()
    lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    crlf = hashlib.sha256(raw.replace(b"\n", b"\r\n")
                          if b"\r\n" not in raw else raw).hexdigest()[:16]
    return lf, crlf


def main():
    blob = subprocess.run(["git", "cat-file", "blob", "HEAD:" + REG.replace("\\", "/")],
                         capture_output=True, check=True).stdout
    bom = blob.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in blob
    trailing_nl = blob.endswith(b"\n")
    txt = blob.decode("utf-8-sig")
    reg = json.loads(txt)
    body = txt.rstrip("\n")

    # probe indent depth from second line's leading spaces
    lines = body.split("\n")
    indent = len(lines[1]) - len(lines[1].lstrip(" "))

    changed = []
    for row in reg["items"]:
        rid = row["id"]
        if rid not in FILES:
            continue
        path, _ = FILES[rid]
        lf, crlf_sha = faces(path)
        for c in row["checks"]:
            if c["kind"] == "json_field" and "sha256_16" in str(c["args"]):
                old = c["args"][2]
                if old == crlf_sha and old != lf:
                    c["args"][2] = lf
                    changed.append((rid, old, lf, "CRLF->LF re-anchored"))
                elif old == lf:
                    changed.append((rid, old, lf, "already LF face, verified stable"))
                else:
                    raise SystemExit(f"FAIL-CLOSED {rid}: anchor {old} matches neither "
                                     f"LF({lf}) nor CRLF({crlf_sha}) face of {path}")
    if len(changed) != 4:
        raise SystemExit(f"FAIL-CLOSED: expected 4 rows touched, got {len(changed)}")

    reg["_reconciled"] = reg.get("_reconciled", "") + RECONCILE_NOTE
    out = json.dumps(reg, ensure_ascii=False, indent=1)
    if crlf:
        out = out.replace("\n", "\r\n")
    if trailing_nl:
        out += "\n" if not crlf else "\r\n"
    if bom:
        out = "\xef\xbb\xbf" + out
    with open(REG, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    for r in changed:
        print(r)


if __name__ == "__main__":
    main()
