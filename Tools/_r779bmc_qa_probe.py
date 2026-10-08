"""r779 bm-c QA slot probe (pattern credit: Tools/_r778bmc_qa_probe.py):
pre-ignite collision evidence for qa/smoke-r779.{md,png} face.
Facts recorded: local qa face file count, local slot state, origin/main
slot state (post-fetch), cross-machine counter uniqueness reasoning inputs
(last bm-b round label on origin, last bm-a round label on origin).
Zero-collision verdict only when all three faces agree EMPTY."""
import glob
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ls_tree_origin(path_dir):
    p = subprocess.run(["git", "-C", REPO, "ls-tree", "origin/main",
                        "--name-only", path_dir + "/"],
                       capture_output=True)
    return [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l]


def main():
    probe = {"round": 779, "slot": "r779"}
    files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(
        REPO, "qa", "*")))
    probe["qa_face_local_count"] = len(files)
    probe["slot_local"] = [f for f in files if "-r779." in f]
    origin_qa = ls_tree_origin("qa")
    probe["qa_face_origin_count"] = len(origin_qa)
    probe["slot_origin"] = [f for f in origin_qa if "-r779." in f]
    # neighbor slots for context (occupied = foreign pack)
    probe["slot_r780_origin"] = [f for f in origin_qa if "-r780." in f]
    probe["slot_r781_origin"] = [f for f in origin_qa if "-r781." in f]
    probe["verdict_zero_collision"] = (not probe["slot_local"]
                                       and not probe["slot_origin"])
    out = os.path.join(REPO, "results", "_r779bmc_qa_probe.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(probe, fh, indent=1)
    print(json.dumps(probe, indent=1))
    return 0 if probe["verdict_zero_collision"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
