# -*- coding: utf-8 -*-
"""bm-c U256 local self-driven work-registry gate (C-20261015-01 sec.3.1 landing).

Paradigm: bm-b bmb-work-registry.json (O-20261015-0906-bm-b sec.2.1).
Registry = machine-local JSON stock face (append-only stock; status face is the
only mutable field family: ready/waiting-input -> claimed -> done).
Gate = this in-repo tool. Maintenance = session + loop rounds append-only;
sentinels/fillers only consume, never invent work (meaningfulness law
O-20260928-1820 always applies).

Hard fields per bill sec.3.1: id / lane=cpu-only / target / priority /
consumer_plan / deliverable / timeout / cloud=forbidden / source traceability.
bm-c seat risk-note 1 (bill sec.5 bm-c row): GREEN-IDLE RAM gate often closed
(free ~1.3G observed) -> every item carries ram_mb and the gate enforces
RAM_LIGHT_MAX_MB; claim-time RAM check stays with idle_trigger (unchanged).

Stock admission three-checks (bei-huo zhun-ru san-yan):
  CHECK-1 hard-field completeness (all fields, unique id, valid enums,
          timeout/ram integer bounds)
  CHECK-2 lane compliance (cpu-only, cloud=forbidden, RAM-light cap,
          no GPU-burn / cloud-platform keywords in target/consumer_plan)
  CHECK-3 source traceability + meaning (source evidence path exists in repo;
          consumer_plan names a concrete action; deliverable names a
          checkable artifact)

Subcommands:
  check <file.json>            validate one candidate item file (exit 0/3)
  check-registry               validate every stocked item
  list                         ASCII status summary
  claim <id> --by <mid>        atomic claim (lock + ledger append)
  done <id> --done-file <p>    close with deliverable-exists check
  selftest                     offline self-check (no registry writes)

Exit codes: 0 ok, 1 usage, 2 mechanism fault, 3 admission/claim reject.
"""
import io
import json
import os
import re
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAM_LIGHT_MAX_MB = 1500
PRIORITIES = ("P0", "P1", "P2", "P3")
STATUSES = ("ready", "waiting-input", "claimed", "done")
REQUIRED = ("id", "lane", "target", "priority", "consumer_plan", "deliverable",
            "timeout_min", "cloud", "source", "ram_mb", "status", "stocked_at", "stocked_by")
GPU_KW = re.compile(r"\b(cuda|gpu|vram|comfyui|llama|ollama|lora|diffusion|flux|krea|i2v)\b", re.I)
CLOUD_KW = re.compile(r"\b(tjgenerators|seedance|minimax|cloud[- ]credit)\b", re.I)


def _registry_path():
    override = os.environ.get("BMC_WORK_REGISTRY")
    if override:
        return override
    try:
        with io.open(os.path.join(REPO, "fleet", "machine.json"), "r", encoding="utf-8") as fh:
            root = json.load(fh)["root_path"]
    except Exception:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(REPO))))
    return os.path.join(root, ".codely-cli", "sentinel", "bmc-work-registry.json")


def _ledger_path(registry):
    return registry[:-len(".json")] + "-ledger.jsonl"


def _load_registry(path):
    if not os.path.exists(path):
        raise SystemExit("exit 2: registry not found: %s" % path)
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _repo_rel_exists(source):
    if re.match(r"^https?://", source):
        return True  # external pointer: cannot disk-verify, allowed but noted
    cand = source if os.path.isabs(source) else os.path.join(REPO, source)
    return os.path.exists(cand)


def validate_item(item, known_ids=None):
    fails = []
    for field in REQUIRED:
        if field not in item or item[field] in (None, ""):
            fails.append("CHECK-1 missing/empty hard field: %s" % field)
    if fails:
        return fails
    if not re.match(r"^bmc-w\d{3,}$", str(item["id"])):
        fails.append("CHECK-1 id must match bmc-wNNN: %s" % item["id"])
    if known_ids is not None and item["id"] in known_ids:
        fails.append("CHECK-1 duplicate id: %s" % item["id"])
    if item["lane"] != "cpu-only":
        fails.append("CHECK-2 lane must be cpu-only (C-20261012-03 bm-c GPU lane protected): %s" % item["lane"])
    if item["cloud"] != "forbidden":
        fails.append("CHECK-2 cloud must be forbidden: %s" % item["cloud"])
    if item["priority"] not in PRIORITIES:
        fails.append("CHECK-1 priority enum: %s" % item["priority"])
    if item["status"] not in STATUSES:
        fails.append("CHECK-1 status enum: %s" % item["status"])
    try:
        ram = int(item["ram_mb"])
        if not (1 <= ram <= RAM_LIGHT_MAX_MB):
            fails.append("CHECK-2 ram_mb %s outside RAM-light band 1..%d (bm-c seat note 1)" % (ram, RAM_LIGHT_MAX_MB))
    except (TypeError, ValueError):
        fails.append("CHECK-1 ram_mb not integer: %r" % item["ram_mb"])
    try:
        tmo = int(item["timeout_min"])
        if not (1 <= tmo <= 1440):
            fails.append("CHECK-1 timeout_min outside 1..1440: %s" % tmo)
    except (TypeError, ValueError):
        fails.append("CHECK-1 timeout_min not integer: %r" % item["timeout_min"])
    text = "%s %s" % (item.get("target", ""), item.get("consumer_plan", ""))
    if GPU_KW.search(text):
        fails.append("CHECK-2 GPU-burn keyword in target/consumer_plan (bm-c GPU = generation-visual lane, not poolable)")
    if CLOUD_KW.search(text):
        fails.append("CHECK-2 cloud-platform keyword in target/consumer_plan (pool items are zero-cloud)")
    if not _repo_rel_exists(str(item["source"])):
        fails.append("CHECK-3 source evidence path not found in repo: %s" % item["source"])
    if len(str(item["consumer_plan"])) < 20:
        fails.append("CHECK-3 consumer_plan too thin (<20 chars) to be a concrete action")
    if not re.search(r"[\w\-]+\.(json|jsonl|md|csv|parquet|txt|log|py|png|jpg|html)", str(item["deliverable"])):
        fails.append("CHECK-3 deliverable must name a checkable artifact path (extension pattern)")
    if item["status"] == "waiting-input" and not item.get("waiting_input"):
        fails.append("CHECK-1 waiting-input item must carry waiting_input reason")
    return fails


def cmd_check(args):
    if not args:
        print("usage: check <file.json>")
        return 1
    with io.open(args[0], "r", encoding="utf-8") as fh:
        item = json.load(fh)
    fails = validate_item(item)
    if fails:
        for f in fails:
            print("REJECT %s" % f)
        return 3
    print("ADMIT %s" % item["id"])
    return 0


def cmd_check_registry(args):
    reg_path = _registry_path()
    reg = _load_registry(reg_path)
    items = reg.get("items", [])
    known, rc = set(), 0
    print("registry=%s items=%d" % (reg_path, len(items)))
    for item in items:
        fails = validate_item(item, known)
        known.add(item.get("id"))
        if fails:
            rc = 3
            print("REJECT %s" % item.get("id"))
            for f in fails:
                print("  %s" % f)
        else:
            print("PASS %s status=%s pri=%s ram_mb=%s" % (item["id"], item["status"], item["priority"], item["ram_mb"]))
    print("check-registry exit=%d" % rc)
    return rc


def cmd_list(args):
    reg = _load_registry(_registry_path())
    counts = {}
    for item in reg.get("items", []):
        counts[item.get("status", "?")] = counts.get(item.get("status", "?"), 0) + 1
    print("registry items=%d statuses=%s" % (len(reg.get("items", [])), json.dumps(counts, sort_keys=True)))
    for item in reg.get("items", []):
        print("  %s %s %s" % (item["id"], item["status"], item["priority"]))
    return 0


def _ledger_append(reg_path, event):
    lp = _ledger_path(reg_path)
    with io.open(lp, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")


def cmd_claim(args):
    if len(args) < 3 or args[1] != "--by":
        print("usage: claim <id> --by <machine-or-session>")
        return 1
    reg_path = _registry_path()
    lock = reg_path + ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except OSError:
        print("REJECT claim single-flight lock busy: %s" % lock)
        return 3
    try:
        reg = _load_registry(reg_path)
        for item in reg.get("items", []):
            if item["id"] == args[0]:
                if item["status"] != "ready":
                    print("REJECT %s not claimable (status=%s)" % (item["id"], item["status"]))
                    return 3
                item["status"] = "claimed"
                item["claimed_by"] = args[2]
                item["claimed_at"] = int(time.time())
                tmp = reg_path + ".tmp"
                with io.open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(reg, fh, ensure_ascii=False, indent=1)
                    fh.write("\n")
                os.replace(tmp, reg_path)
                _ledger_append(reg_path, {"event": "claim", "id": args[0], "by": args[2],
                                          "ts": int(time.time())})
                print("CLAIMED %s by %s" % (args[0], args[2]))
                return 0
        print("REJECT id not found: %s" % args[0])
        return 3
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def cmd_done(args):
    idx = 0
    if "--done-file" not in args:
        print("usage: done <id> --done-file <path>")
        return 1
    item_id = args[0]
    done_file = args[args.index("--done-file") + 1]
    reg_path = _registry_path()
    if not os.path.exists(done_file) or os.path.getsize(done_file) == 0:
        print("REJECT done_file missing or empty (appendix-3 deliverable check): %s" % done_file)
        return 3
    reg = _load_registry(reg_path)
    for item in reg.get("items", []):
        if item["id"] == item_id:
            if item["status"] != "claimed":
                print("REJECT %s not in claimed state (status=%s)" % (item_id, item["status"]))
                return 3
            item["status"] = "done"
            item["done_file"] = done_file
            item["done_at"] = int(time.time())
            tmp = reg_path + ".tmp"
            with io.open(tmp, "w", encoding="utf-8") as fh:
                json.dump(reg, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            os.replace(tmp, reg_path)
            _ledger_append(reg_path, {"event": "done", "id": item_id, "done_file": done_file,
                                      "ts": int(time.time())})
            print("DONE %s" % item_id)
            return 0
    print("REJECT id not found: %s" % item_id)
    return 3


def cmd_selftest(args):
    good = {
        "id": "bmc-w001", "lane": "cpu-only", "target": "supply funnel audit beat",
        "priority": "P2", "consumer_plan": "rerun funnel audit probe locally and diff route verdicts",
        "deliverable": "results/_selftest_funnel.json", "timeout_min": 30, "cloud": "forbidden",
        "source": "results/watermark_red.json", "ram_mb": 300, "status": "ready",
        "stocked_at": 1792032000, "stocked_by": "selftest",
    }
    assert validate_item(good) == [], "good item must pass"
    def bad(**kw):
        d = dict(good)
        for k, v in kw.items():
            if v is None:
                d.pop(k, None)
            else:
                d[k] = v
        return validate_item(d)
    assert any("missing/empty hard field: deliverable" in f for f in bad(deliverable=None)), "C1 miss"
    assert any("duplicate id" in f for f in validate_item(good, {"bmc-w001"})), "C1 dup"
    assert any("ram_mb" in f for f in bad(ram_mb=9999)), "C2 ram"
    assert any("GPU-burn keyword" in f for f in bad(target="comfyui 8188 burn")), "C2 gpu kw"
    assert any("cloud-platform keyword" in f for f in bad(consumer_plan="call seedance api for video")), "C2 cloud kw"
    assert any("source evidence path not found" in f for f in bad(source="results/__nope__.json")), "C3 source"
    assert any("deliverable must name" in f for f in bad(deliverable="a feeling of progress")), "C3 deliverable"
    assert any("waiting-input item must carry" in f for f in bad(status="waiting-input")), "C1 waiting"
    print("selftest 9/9 PASS")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__.splitlines()[0])
        print("subcommands: check check-registry list claim done selftest")
        return 1
    cmd, args = sys.argv[1], sys.argv[2:]
    table = {"check": cmd_check, "check-registry": cmd_check_registry, "list": cmd_list,
             "claim": cmd_claim, "done": cmd_done, "selftest": cmd_selftest}
    if cmd not in table:
        print("unknown subcommand: %s" % cmd)
        return 1
    return table[cmd](args)


if __name__ == "__main__":
    sys.exit(main())
