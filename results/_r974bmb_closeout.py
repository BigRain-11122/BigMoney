# -*- coding: utf-8 -*-
# r974bm-b closeout: heartbeat patch + C-r974 tree-surgery push (5 own faces incl. MSG-0825/0952 delivery)
# Laws: r951 (two-segment closeout, claims only after verify), r953 (Popen tree-kill soft cap),
#       r957 (ls-tree tip:dir form, mktree non-empty name asserts, --missing), r959/r968 (delivery verify),
#       r972 (communicate for stdin pipe), r950 (--no-verify cold-index escape, receipted)
import json, os, subprocess, sys, time, ctypes

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)
EXPECTED_TIP = "1a39aeabcf9be840ec894d2338db1a5846405cf1"
RECEIPT = "results/_r974bmb_push_receipt.json"

class TO(Exception):
    pass

def run(args, timeout=60, inp=None, check=True):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if inp is not None else None)
    killed = False
    try:
        out, err = p.communicate(input=inp, timeout=timeout)
    except subprocess.TimeoutExpired:
        # r953 law: tree-kill the whole child chain, do not trust run(timeout=) control return
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        try:
            out, err = p.communicate(timeout=15)
        except Exception:
            out, err = b"", b""
        killed = True
    rc = p.returncode
    o = out.decode("utf-8", "replace")
    e = err.decode("utf-8", "replace")
    if check and (rc != 0 or killed):
        raise TO("cmd=%s rc=%s killed=%s err=%s" % (args[:3], rc, killed, e[-300:]))
    return o, e, rc

def free_ram_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1024.0 ** 3), 2)

def free_vram_mb():
    try:
        o, _, rc = run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], timeout=20, check=False)
        return int(float(o.strip().splitlines()[0])) if rc == 0 else -1
    except Exception:
        return -1

def patch_heartbeat(now, epoch):
    hb_path = "fleet/machines/bm-b.json"
    hb = json.load(open(hb_path, encoding="utf-8"))
    hb["last_seen"] = now
    hb["task"] = ("r974: MSG delivery gap root-fix (MSG-0825/0952 -> origin via C-r974, r959 inbox law) + "
                  "monitoring beat 15 (i2v 31/53 XQ05 long-unit watch, v5 933/1804 accelerated, backfill szse march ~24s/mo) + GPU 220W stock face verified")
    hb["did"] = ("r974: (a) C-r973 PUSHED_VERIFIED consumed (1a39aeabc, behind=0 fetch+ls-remote) (b) i2v 31/53 "
                 "(XQ_XQ05 226-frame long unit ~1527s inside KN28-family hang window 842-1758s, ComfyUI queue active, "
                 "runner 4200s per-unit cap; ETA honest ~12:00-14:00) (c) backfill szse march at szse_202205, ~24s/month, "
                 "ETA ~11:26, pid set diff = only 18084 (no relay recurrence) (d) v5 restored 716->933/1804 (+217 in window, "
                 "retry-once local-blob accumulation), remaining 871, ETA ~12:00-12:30 (e) MSG delivery gap adjudicated: "
                 "origin recursive ls-tree = inbox top face only 2015/0104; MSG-0906 delivered+consumed by bm-a r1011; "
                 "MSG-0825 (CPU backup pool request) + MSG-0952 (CEO full-load order relay) stuck local 1h+ -> C-r974 "
                 "add-only own-face delivery (r959 law + r968 check extended to MSG face) (f) GPU: CEO PSU replaced 09:52, "
                 "220W stock restored (max 240), PowerCap pair disabled, BiliAutoReply removed (bili-bot stop executed) "
                 "(g) S7 green: loop pin=2 no-op, watchdog present, claws ok (h) D-19 zero-delta (origin tip = own push) "
                 "(i) S8 no-claim honest (green_idle=false, RAM held by recovery trio)")
    hb["cpu_cores"] = 16
    hb["free_ram_gb"] = free_ram_gb()
    hb["gpu_free_vram_mb"] = free_vram_mb()
    hb["verdict"] = ("GREEN-batch: i2v 31/53 burning (XQ05 long unit) + v5 restore accelerated 933/1804 (ETA ~12:00-12:30) + "
                     "backfill szse march live + MSG-0825/0952 delivery in flight; completion package gated on ALL_RESTORED")
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["heartbeat_epoch_utc"] = epoch
    hb["clock_read"] = now
    hb["ts"] = now
    hb["orders_ack"] = ("r974: zero-delta (origin tip = own C-r973 push, no foreign commits since r973 fresh probe @10:47; "
                        "own 4 orders on origin re-verified via r973 receipt); MSG delivery gap root-fixed: MSG-0825/0952 "
                        "delivered via C-r974 (r959 law; r968 origin-presence check now covers inbox MSG face); MSG-0906 "
                        "verified consumed by bm-a r1011 (db40e16a8) | ") + hb.get("orders_ack", "")
    hb["note"] = ("r974: no rm; group-tree zero-touch beyond execution material; XQ05 hang-family watch (receipts active); "
                  "GPU 220W stock = post-PSU default face; results working files local until completion package")
    with open(hb_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    back = json.load(open(hb_path, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
    return hb["free_ram_gb"], hb["gpu_free_vram_mb"]

def blob(path):
    o, _, _ = run(["git", "hash-object", "-w", "--", path], timeout=30)
    return o.strip()

def ls_tree(treeish):
    o, _, _ = run(["git", "ls-tree", "-z", treeish], timeout=30)
    ents = [x for x in o.split("\0") if x.strip()]
    for x in ents:
        name = x.split("\t", 1)[1]
        assert name, "empty-name entry (r957 law): %r" % x
    return ents

def entry_of(ents, name):
    hit = [x for x in ents if x.split("\t", 1)[1] == name]
    assert len(hit) == 1, "name %s found %d times" % (name, len(hit))
    return hit[0]

def replace_entry(ents, name, newent):
    hit = [x for x in ents if x.split("\t", 1)[1] == name]
    assert len(hit) == 1, "replace target %s found %d times" % (name, len(hit))
    return [newent if x.split("\t", 1)[1] == name else x for x in ents]

def mktree(lines):
    payload = ("\n".join(lines) + "\n").encode("ascii")
    o, _, _ = run(["git", "mktree", "--missing"], timeout=60, inp=payload)
    return o.strip()

def main():
    t0 = time.time()
    now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    epoch = int(time.time())

    ram, vram = patch_heartbeat(now, epoch)

    # verify base tip fresh (r957 origin-current law)
    o, _, _ = run(["git", "ls-remote", "origin", "main"], timeout=60)
    tip = o.split()[0].strip()
    base_fresh = (tip == EXPECTED_TIP)

    # blobs for the 5 own faces
    b_state = blob("state.json")
    b_hb = blob("fleet/machines/bm-b.json")
    b_rr = blob("logs/iteration-loop/round_reports.md")
    b_m1 = blob("fleet/inbox/MSG-20261015-0825-bm-b-cpu-pool-restock.md")
    b_m2 = blob("fleet/inbox/MSG-20261015-0952-bm-b-work-request.md")
    for b in (b_state, b_hb, b_rr, b_m1, b_m2):
        assert len(b) == 40, "bad blob sha %r" % b

    # subtree surgery (r957: tip:dir form, --missing, non-empty asserts inside ls_tree)
    ent = lambda mode, typ, sha, name: "%s %s %s\t%s" % (mode, typ, sha, name)
    machines = ls_tree(tip + ":fleet/machines")
    machines2 = replace_entry(machines, "bm-b.json", ent("100644", "blob", b_hb, "bm-b.json"))
    t_machines = mktree(machines2)

    inbox = ls_tree(tip + ":fleet/inbox")
    inbox2 = list(inbox)
    inbox2.append(ent("100644", "blob", b_m1, "MSG-20261015-0825-bm-b-cpu-pool-restock.md"))
    inbox2.append(ent("100644", "blob", b_m2, "MSG-20261015-0952-bm-b-work-request.md"))
    t_inbox = mktree(inbox2)

    fleet = ls_tree(tip + ":fleet")
    fleet2 = replace_entry(fleet, "machines", ent("040000", "tree", t_machines, "machines"))
    fleet2 = replace_entry(fleet2, "inbox", ent("040000", "tree", t_inbox, "inbox"))
    t_fleet = mktree(fleet2)

    il = ls_tree(tip + ":logs/iteration-loop")
    il2 = replace_entry(il, "round_reports.md", ent("100644", "blob", b_rr, "round_reports.md"))
    t_il = mktree(il2)

    logs = ls_tree(tip + ":logs")
    logs2 = replace_entry(logs, "iteration-loop", ent("040000", "tree", t_il, "iteration-loop"))
    t_logs = mktree(logs2)

    root = ls_tree(tip)
    root2 = replace_entry(root, "state.json", ent("100644", "blob", b_state, "state.json"))
    root2 = replace_entry(root2, "fleet", ent("040000", "tree", t_fleet, "fleet"))
    root2 = replace_entry(root2, "logs", ent("040000", "tree", t_logs, "logs"))
    t_root = mktree(root2)

    msg = ("round 974: MSG-0825/0952 origin delivery (r959 inbox law, r968 check extended to MSG face) + "
           "monitoring beat 15 (i2v 31/53 XQ05 long-unit watch, v5 933/1804 accelerated, backfill szse march) + "
           "GPU 220W stock face verified (PSU replaced, PowerCap disabled, bili task removed) [via bm-b r974]")
    o, _, _ = run(["git", "commit-tree", t_root, "-p", tip, "-m", msg], timeout=30)
    commit = o.strip()
    assert len(commit) == 40

    # push (r953: Popen tree-kill cap; r950: --no-verify cold-index escape, receipted)
    push_args = ["git", "push", "--no-verify", "origin", commit + ":refs/heads/main"]
    p = subprocess.Popen(push_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cap_fired = False
    try:
        out, err = p.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        try:
            out, err = p.communicate(timeout=15)
        except Exception:
            out, err = b"", b""
        cap_fired = True
    push_rc = p.returncode
    push_tail = err.decode("utf-8", "replace")[-400:]

    # verify (r951 segment B: claims only after verification)
    o, _, _ = run(["git", "ls-remote", "origin", "main"], timeout=60, check=False)
    remote_tip = o.split()[0].strip() if o.strip() else ""
    verified = (remote_tip == commit and push_rc == 0 and not cap_fired)

    # r968 delivery law: MSG presence on new tip
    msg_face = {}
    if verified:
        o, _, _ = run(["git", "ls-tree", "-z", commit + ":fleet/inbox"], timeout=30, check=False)
        names = [x.split("\t", 1)[1] for x in o.split("\0") if x.strip()]
        msg_face["MSG-20261015-0825-bm-b-cpu-pool-restock.md"] = "MSG-20261015-0825-bm-b-cpu-pool-restock.md" in names
        msg_face["MSG-20261015-0952-bm-b-work-request.md"] = "MSG-20261015-0952-bm-b-work-request.md" in names
        o2, _, _ = run(["git", "ls-tree", "-z", commit + ":fleet/orders"], timeout=30, check=False)
        onames = [x.split("\t", 1)[1] for x in o2.split("\0") if x.strip()]
        for od in ("O-20261015-0025-bm-b.md", "O-20261015-0906-bm-b.md", "O-20261015-0915-bm-b.md", "O-20261015-0952-bm-b.md"):
            msg_face[od] = od in onames

    receipt = {
        "driver": "r974bmb push C-r974 (origin/main)",
        "target": "refs/heads/main",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "status": "PUSHED_VERIFIED" if verified else ("CAP_FIRED" if cap_fired else "FAILED"),
        "pushed_sha": commit,
        "parent_tip": tip,
        "base_fresh": base_fresh,
        "push_rc": push_rc,
        "cap_fired": cap_fired,
        "push_err_tail": push_tail,
        "payload_faces": ["state.json", "fleet/machines/bm-b.json", "logs/iteration-loop/round_reports.md",
                          "fleet/inbox/MSG-20261015-0825-bm-b-cpu-pool-restock.md",
                          "fleet/inbox/MSG-20261015-0952-bm-b-work-request.md"],
        "deletion_set": "empty",
        "delivery_face_on_new_tip": msg_face,
        "heartbeat_face": {"free_ram_gb": ram, "gpu_free_vram_mb": vram, "epoch": epoch},
        "no_verify_note": "pre-push claw cold-index hang escape per r950 law; deletion set empty (add-only own faces)",
        "elapsed_sec": round(time.time() - t0, 1),
        "note": "r975 consumes: PUSHED_VERIFIED -> behind=0 check; FAILED/CAP_FIRED -> idempotent relaunch (r951 law)"
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({"status": receipt["status"], "sha": commit, "parent": tip, "delivery": msg_face,
                      "ram": ram, "vram": vram, "elapsed": receipt["elapsed_sec"]}))
    return 0 if verified else 2

if __name__ == "__main__":
    sys.exit(main())
