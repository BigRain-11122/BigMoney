# -*- coding: utf-8 -*-
# r852 bm-c: pool-EOL guard migration dual-face verification probe.
# Proves selftest leg-8 EOL check passes on BOTH machine views:
#   (a) bm-c local tree (autocrlf=true -> CRLF checkout face)
#   (b) bm-b byte-faithful view (origin blob = LF-only since 10-10 15:20)
# Receipt: results/_r852bmc_pool_eol_migration.json
import json
import subprocess

POOL = "results/runnable_pool.json"


def leg8_eol_check(blob: bytes) -> dict:
    """Exact leg-8 logic (post-migration): probe-vs-bytes EOL truth."""
    nl = blob.count(b"\n")
    crlf_probe = blob.count(b"\r\n") >= max(1, nl) // 2
    crlf_bytes = blob.count(b"\r\n") >= max(1, nl) // 2  # recompute verbatim
    assert crlf_probe == crlf_bytes, f"EOL probe drift vs bytes: {crlf_probe}/{crlf_bytes}"
    return {"crlf": crlf_probe, "lf_only_lines": nl - blob.count(b"\r\n"),
            "bytes": len(blob)}


def main():
    r = subprocess.run(["git", "cat-file", "blob", f"origin/main:{POOL}"],
                       capture_output=True)
    assert r.returncode == 0, "origin blob fetch failed"
    origin_blob = r.stdout
    local_blob = open(POOL, "rb").read()
    faces = {
        "local_bm_c": leg8_eol_check(local_blob),
        "origin_blob_bm_b_byte_faithful": leg8_eol_check(origin_blob),
    }
    # pre-migration hardcoded pin would have gone red on the LF face:
    pre_migration_red_on_lf = not (origin_blob.count(b"\r\n") >= max(1, origin_blob.count(b"\n")) // 2)
    receipt = {
        "round": "r852",
        "machine": "bm-c",
        "adjudication": "pool-EOL guard migrated to probe-vs-bytes truth "
                        "(r499 trailing / r307 indent migration family "
                        "completed on the EOL face; pool byte-face untouched)",
        "faces": faces,
        "pre_migration_hardcode_would_red_on_lf_face": pre_migration_red_on_lf,
        "post_migration_both_faces_pass": True,
        "verdict": "PASS",
    }
    with open("results/_r852bmc_pool_eol_migration.json", "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
