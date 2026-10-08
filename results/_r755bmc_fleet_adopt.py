# -*- coding: utf-8 -*-
"""r755 bm-c FleetLink adoption executor (O-20261008-1205-bm-c + P-09 receipt
+ C-20261008-01 quick-fix face). Phases:
  local-roster : fetch -> build fixed bm-c roster entry from CURRENT origin
                 entry (preserve HQ keys) -> validate -> write LOCAL
                 Tools/fleet-nodes.json (order-mandated in-place fix; the
                 listener reads the local copy at startup).
  cas          : fetch -> rebuild both payloads on current base (roster fix +
                 P-09 receipt sub-line with listener self-proof) -> CAS
                 direct-commit to group origin/main (temp-index + commit-tree
                 + push sha:main, r739 law family: 40-hex hard validation,
                 push keyword scan, ls-remote tip verify, one race retry).
Zero working-tree surgery beyond the roster file the order names."""
import datetime
import json
import os
import re
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000  # CREATE_NO_WINDOW (O-1300 law)

WAKE_TASKS = [
    "Bigmoney-IterationLoop",
    "Bigmoney-SaturationEngine",
    "Bigmoney-ResidentDispatcher",
    "Bigmoney-Autofill",
    "Bigmoney-PoolWorker",
    "MiniGameEngineTick",
    "MiniGameComfyDraftTick",
    "MiniGameAuditTick",
    "MiniGameGateTick",
    "MiniGameRadarTick",
    "MiniGameRadarDeepTick",
    "MiniGameSiliconWatchTick",
]
NOTE = ("adopted 10-08 bm-c r755 (O-20261008-1205-bm-c): host/root/wake_tasks "
        "confirmed locally (host=FLUXGROUP per machine.json; root=K:/Fluxgroup/"
        "FluxGroup; wake_tasks 12 live task names verified via task enum); "
        "FluxGroup-FleetLink task registered + listener on :8790 health OK; "
        "awaiting HQ poke verify to close adoption.")


def git(args, env=None):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


def fetch():
    rc, _, err = git(["fetch", "origin"])
    return rc, err


def show_blob(path):
    rc, out, err = git(["show", "origin/main:" + path])
    if rc != 0:
        raise SystemExit("ABORT show %s: %s" % (path, err[:200]))
    return out


def build_roster_text():
    """Origin roster text with the bm-c entry block surgically replaced.
    Preserves every other node byte-for-byte; bm-c entry inherits origin keys
    (id/tailnet_ip/enabled/repos/status_files) with host/root/wake_tasks/note
    fixed per order."""
    text = show_blob("Tools/fleet-nodes.json")
    anchor = text.find('"id": "bm-c"')
    assert anchor > 0, "bm-c entry anchor missing"
    start = text.rfind("{", 0, anchor)
    depth = 0
    end = -1
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    assert end > start, "bm-c block brace walk failed"
    block = text[start:end + 1]
    entry = json.loads(block)
    entry["host"] = "FLUXGROUP"
    entry["root"] = "K:/Fluxgroup/FluxGroup"
    entry["wake_tasks"] = WAKE_TASKS
    entry["note"] = NOTE
    if "enabled" not in entry:
        entry["enabled"] = True
    new_block = json.dumps(entry, indent=2, ensure_ascii=False)
    lines = new_block.splitlines()
    indented = "\n".join(("    " + ln) if ln.strip() else ln for ln in lines)
    new_text = text[:start] + indented + text[end + 1:]
    # validation: parse whole file, bm-c facts
    parsed = json.loads(new_text)
    bmc = [n for n in parsed["nodes"] if n["id"] == "bm-c"][0]
    assert bmc["host"] == "FLUXGROUP" and bmc["root"] == "K:/Fluxgroup/FluxGroup"
    assert bmc["wake_tasks"] == WAKE_TASKS and len(WAKE_TASKS) == 12
    assert bmc.get("enabled") is True and bmc.get("tailnet_ip") == "100.123.74.104"
    return new_text, bmc


def build_ledger_text(now_hm):
    """Origin ledger text with the bm-c receipt sub-line inserted directly
    under the P-2026-10-08-09 row (append-only, one line)."""
    text = show_blob("cph4/evolution-ledger.md")
    eol = "\r\n" if "\r\n" in text[:2000] else "\n"
    lines = text.split(eol)
    idx = -1
    for i, ln in enumerate(lines):
        if ln.startswith("- **P-2026-10-08-09 |"):
            idx = i
            break
    assert idx >= 0, "P-09 row not found"
    assert "P-2026-10-08-09" in lines[idx]
    receipt = ("  - 回执（bm-c r755·2026-10-08 " + now_hm + "·收令=轮首 pull 11:40·SLA ≤1h 内）："
               "①O-20261008-1205-bm-c 全三步收口——tailscale 步按 12:1x 修正版跳过（10-06 CEO 已点）；"
               "fleet-nodes.json bm-c 条目就地修正（host=FLUXGROUP·root=K:/Fluxgroup/FluxGroup·"
               "wake_tasks=12 实核真值：Bigmoney-IterationLoop/SaturationEngine/ResidentDispatcher/"
               "Autofill/PoolWorker+MiniGame 七 tick）；FluxGroup-FleetLink 任务已注册+监听 :8790 "
               "health=ok（node=bm-c·tailnet 100.123.74.104+loopback 双绑）——待 HQ poke 验证即采纳收口；"
               "②总动员令 bm-c 全力面如实申报=BigMoney 线 10min 迭代循环在役（本窗 r755·SAT 引擎活实核）"
               "+MiniGame 线 EngineTick Running+六 tick 任务在册+qwen3.6-coder:35b 常驻 100% GPU 供职"
               "（ollama ps Forever 实核）+ComfyUI 服务面常驻（draft-queue 产线承载）；"
               "自领计划=fleet 板全 claimed 无 open 票·next_pick=claimed（moneyflow IC 参考批·advisory）·"
               "GREEN-IDLE 未达档（RAM 为常驻产线占用·idle_rounds=0）如实申报；"
               "③治理令 C-20261008-01 bm-c 快改=心跳双字段 last_pulled_at/head_sha 本窗补写+"
               "轮首 pull 步核查回执自下轮起入 S0 常规执法。[via bm-c r755]")
    lines.insert(idx + 1, receipt)
    return eol.join(lines), receipt


def cas_push(roster_text, ledger_text, msg_text):
    tmp_roster = os.path.join(REPO, "results", "_r755bmc_cas_roster.json")
    tmp_ledger = os.path.join(REPO, "results", "_r755bmc_cas_ledger.md")
    tmp_msg = os.path.join(REPO, "results", "_r755bmc_cas_msg.txt")
    idx = os.path.join(REPO, "results", "_r755bmc_cas.index")
    for path, content in ((tmp_roster, roster_text), (tmp_ledger, ledger_text),
                          (tmp_msg, msg_text)):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    rc, base, err = git(["rev-parse", "origin/main"])
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", base.strip()):
        return None, "bad base rc=%d %s" % (rc, err[:200])
    blobs = {}
    for target, src in (("Tools/fleet-nodes.json", tmp_roster),
                        ("cph4/evolution-ledger.md", tmp_ledger)):
        p = subprocess.run(["git", "-C", GROUP, "hash-object", "-w", src],
                           capture_output=True, creationflags=CF)
        blob = p.stdout.decode("utf-8", "replace").strip()
        if not re.fullmatch(r"[0-9a-f]{40}", blob):
            return None, "bad blob for %s: %s %s" % (target, blob[:60],
                                                      p.stderr.decode()[:150])
        blobs[target] = blob
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    if os.path.exists(idx):
        os.remove(idx)
    rc, _, err = git(["read-tree", base.strip()], env=env)
    if rc != 0:
        return None, "read-tree: %s" % err[:200]
    for target, blob in blobs.items():
        rc, _, err = git(["update-index", "--add", "--cacheinfo", "100644",
                          blob, target], env=env)
        if rc != 0:
            return None, "update-index %s: %s" % (target, err[:200])
    rc, tree, err = git(["write-tree"], env=env)
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", tree.strip()):
        return None, "bad tree rc=%d %s" % (rc, err[:200])
    rc, newc, err = git(["commit-tree", tree.strip(), "-p", base.strip(),
                         "-F", tmp_msg])
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", newc.strip()):
        return None, "bad commit rc=%d %s" % (rc, err[:200])
    rc, out, err = git(["push", "origin", newc.strip() + ":main"])
    combined = (out + " " + err).lower()
    if rc != 0 or any(k in combined for k in ("fatal", "rejected", "failed",
                                              "error")):
        return None, "push fail rc=%d out=%s err=%s" % (rc, out[:200], err[:200])
    rc, tip, _ = git(["ls-remote", "origin", "main"])
    tip_sha = tip.strip().split("\t")[0] if tip.strip() else ""
    if tip_sha != newc.strip():
        return None, "tip verify fail: %s != %s" % (tip_sha[:12], newc[:12])
    for f in (idx,):
        if os.path.exists(f):
            os.remove(f)
    return {"base": base.strip()[:12], "commit": newc.strip(),
            "tree": tree.strip()[:12], "tip_verified": tip_sha[:12],
            "blobs": {k: v[:12] for k, v in blobs.items()}}, None


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    now = datetime.datetime.now().astimezone()
    if phase == "local-roster":
        rc, err = fetch()
        if rc != 0:
            print("FETCH-WARN rc=%d %s (proceed with existing refs)" % (rc, err[:150]))
        new_text, bmc = build_roster_text()
        local_path = os.path.join(GROUP, "Tools", "fleet-nodes.json")
        with open(local_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_text)
        back = json.load(open(local_path, encoding="utf-8"))
        bmc2 = [n for n in back["nodes"] if n["id"] == "bm-c"][0]
        assert bmc2["host"] == "FLUXGROUP" and len(bmc2["wake_tasks"]) == 12
        print("LOCAL ROSTER FIXED: host=%s root=%s wake=%d tailnet=%s enabled=%s"
              % (bmc2["host"], bmc2["root"], len(bmc2["wake_tasks"]),
                 bmc2["tailnet_ip"], bmc2["enabled"]))
        return 0
    if phase == "cas":
        msg_text = ("FleetLink bm-c 采纳三步+P-09 回执（O-20261008-1205-bm-c·总动员令回执·"
                    "治理令 C-01 快改面）：roster bm-c 条目就地修正（host=FLUXGROUP·root="
                    "K:/Fluxgroup/FluxGroup·wake_tasks=12 实核真值）+P-2026-10-08-09 回执行"
                    "（listener :8790 health ok 自证+全力面+自领计划）[via bm-c r755]\n")
        for attempt in (1, 2):
            rc, err = fetch()
            if rc != 0:
                print("FETCH-WARN rc=%d %s" % (rc, err[:150]))
            roster_text, _ = build_roster_text()
            ledger_text, receipt = build_ledger_text(now.strftime("%H:%M"))
            result, why = cas_push(roster_text, ledger_text, msg_text)
            if result:
                receipt_out = {"phase": "cas", "attempt": attempt,
                               "receipt_line": receipt, "cas": result,
                               "ts": now.isoformat(timespec="seconds")}
                with open(os.path.join(REPO, "results",
                                       "_r755bmc_fleet_adopt_receipt.json"),
                          "w", encoding="utf-8") as fh:
                    json.dump(receipt_out, fh, indent=1, ensure_ascii=False)
                print("CAS OK attempt=%d base=%s commit=%s tip=%s"
                      % (attempt, result["base"], result["commit"][:12],
                         result["tip_verified"]))
                print("RECEIPT %dB" % len(receipt.encode("utf-8")))
                return 0
            print("CAS attempt %d failed: %s" % (attempt, why))
            if attempt == 1:
                print("racing with a concurrent push -> refetch + rebuild once")
        return 2
    print("usage: fleet_adopt.py local-roster|cas")
    return 3


if __name__ == "__main__":
    sys.exit(main())
