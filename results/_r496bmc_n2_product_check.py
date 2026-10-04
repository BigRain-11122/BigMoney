"""r496 bm-c N2-W15 generate product structural check (first-land canonical
face per r486 / MSG-2025 sec.4 mechanism). Read-only probe: parse, shape,
counts, provenance hash. Zero console CJK (r446 probe-to-file law)."""
import hashlib
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = os.path.join(REPO, "results", "n2_w15", "n2_w15_candidates.json")
OUT = os.path.join(REPO, "results", "_r496bmc_n2_product_check.txt")


def shape(v, depth=0):
    if isinstance(v, dict):
        return {k: shape(vv, depth + 1) for k, vv in list(v.items())[:12]} if depth < 2 else "dict(%d keys)" % len(v)
    if isinstance(v, list):
        return ["list len=%d" % len(v), shape(v[0], depth + 1)] if v else ["list len=0"]
    if isinstance(v, str) and len(v) > 80:
        return "str(%d chars) %s..." % (len(v), v[:60])
    return v


def main():
    lines = []
    raw = open(PATH, "rb").read()
    lines.append("file: %s" % PATH)
    lines.append("size_bytes: %d" % len(raw))
    lines.append("sha256: %s" % hashlib.sha256(raw).hexdigest())
    try:
        doc = json.loads(raw.decode("utf-8"))
        lines.append("parse: OK")
    except Exception as e:
        lines.append("parse: FAIL %r" % e)
        open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
        print("PRODUCT_CHECK PARSE_FAIL")
        return
    if isinstance(doc, dict):
        lines.append("top_keys: %s" % sorted(doc.keys()))
        for k, v in doc.items():
            if isinstance(v, list):
                lines.append("  %s: list len=%d" % (k, len(v)))
                if v and isinstance(v[0], dict):
                    lines.append("    row_keys: %s" % sorted(v[0].keys()))
                elif v:
                    lines.append("    row0: %r" % (v[0],))
            elif isinstance(v, dict):
                lines.append("  %s: dict keys=%s" % (k, sorted(v.keys())[:20]))
            else:
                lines.append("  %s: %r" % (k, v))
        # C2 lawful-key face: top-level evidence_cutoff presence (honest report)
        lines.append("evidence_cutoff_top_level: %s" % ("evidence_cutoff" in doc))
        # seek counts meta
        for cand_key in ("rows", "candidates", "survivors", "cells"):
            if cand_key in doc and isinstance(doc[cand_key], list):
                rows = doc[cand_key]
                lines.append("rows[%s]: n=%d" % (cand_key, len(rows)))
                if rows and isinstance(rows[0], dict):
                    rk = sorted(rows[0].keys())
                    lines.append("rows[%s].row0 full: %s" % (cand_key, json.dumps(rows[0], ensure_ascii=True)[:600]))
    else:
        lines.append("top_type: %s" % type(doc).__name__)
    open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("PRODUCT_CHECK_DONE_WROTE", OUT)


if __name__ == "__main__":
    main()
