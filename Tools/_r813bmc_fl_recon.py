# -*- coding: utf-8 -*-
"""r813 bm-c fleet-link upgrade recon (O-20261009-1750 dispatch leg):
1) scheduled task FluxGroup-FleetLink current action/trigger;
2) local group-tree Tools/fleet-link.ps1 version vs origin/main version;
3) local dirty Tools/fleet-nodes.json vs local HEAD vs origin/main;
4) running listener processes (self-match-safe: python.exe host, pattern
   'fleet-link' never appears in THIS process cmdline)."""
import subprocess
import json
import io
import os

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
out = io.open(os.path.join(R, "results", "_r813bmc_fl_recon.txt"), "w",
              encoding="utf-8")
w = out.write


def gb(args, t=60):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, r.stdout.decode("utf-8", "replace"), \
        r.stderr.decode("utf-8", "replace")


# --- origin vs local disk listener version ---
rc, origin_link, _ = gb(["show", "origin/main:Tools/fleet-link.ps1"])
local_path = os.path.join(G, "Tools", "fleet-link.ps1")
local_link = io.open(local_path, encoding="utf-8", errors="replace").read() \
    if os.path.exists(local_path) else ""


def ver_of(txt):
    for ln in txt.splitlines():
        if "version" in ln.lower() and ("=" in ln or ":" in ln):
            s = ln.strip()
            if len(s) < 120:
                return s
    return "none"


w("origin fleet-link.ps1 bytes=%d  version-line: %s\n"
  % (len(origin_link.encode("utf-8")), ver_of(origin_link)))
w("local  fleet-link.ps1 bytes=%d  version-line: %s\n"
  % (len(local_link.encode("utf-8")), ver_of(local_link)))
w("origin has poke-worker ref=%s repo_heads=%s selfupgrade=%s\n" % (
    "fleet-poke-worker" in origin_link, "repo_heads" in origin_link,
    "state.json" in origin_link and "kill" in origin_link.lower()))
w("origin register ref MultipleInstances in ORIGIN register file checked separately\n")
rc, origin_reg, _ = gb(["show", "origin/main:Tools/register-fleet-link.ps1"])
w("origin register has Parallel=%s\n"
  % ("MultipleInstances Parallel" in origin_reg))
for f in ("Tools/fleet-poke-worker.ps1", "Tools/InvisibleRunner.vbs"):
    rc, o, _ = gb(["show", "origin/main:" + f])
    w("origin %s rc=%d bytes=%d | local exists=%s same=%s\n" % (
        f, rc, len(o.encode("utf-8")),
        os.path.exists(os.path.join(G, f.replace("/", "\\"))),
        (io.open(os.path.join(G, f.replace("/", "\\")),
                 encoding="utf-8", errors="replace").read()
         == o) if os.path.exists(os.path.join(G, f.replace("/", "\\")))
        and rc == 0 else "n/a"))

# --- fleet-nodes.json three-way ---
rc, origin_nodes, _ = gb(["show", "origin/main:Tools/fleet-nodes.json"])
rc2, head_nodes, _ = gb(["show", "HEAD:Tools/fleet-nodes.json"])
local_nodes = io.open(os.path.join(G, "Tools", "fleet-nodes.json"),
                      encoding="utf-8", errors="replace").read()
w("nodes: local==origin? %s | local==HEAD? %s | origin bytes=%d\n"
  % (local_nodes == origin_nodes, local_nodes == head_nodes,
     len(origin_nodes.encode("utf-8"))))
try:
    nj = json.loads(origin_nodes)
    w("origin nodes: port=%s ids=%s\n" % (
        nj.get("port"),
        [n.get("id") for n in nj.get("nodes", [])]))
    for n in nj.get("nodes", []):
        if n.get("host") and os.environ.get("COMPUTERNAME", ""):
            w("  node %s host=%s (COMPUTERNAME=%s match=%s)\n" % (
                n.get("id"), n.get("host"), os.environ.get("COMPUTERNAME"),
                str(n.get("host", "")).upper()
                == os.environ.get("COMPUTERNAME", "").upper()))
except Exception as ex:
    w("origin nodes parse err: %s\n" % ex)
try:
    lj = json.loads(local_nodes)
    w("local nodes: port=%s ids=%s\n" % (
        lj.get("port"), [n.get("id") for n in lj.get("nodes", [])]))
except Exception as ex:
    w("local nodes parse err: %s\n" % ex)

# --- current scheduled task face (via schtasks, zero-window wrapper) ---
try:
    p = subprocess.run(
        ["schtasks", "/query", "/tn", "FluxGroup-FleetLink", "/xml"],
        capture_output=True, creationflags=CNW, timeout=30)
    xml = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8",
                                                                "replace")
    w("TASK query rc=%d len=%d\n" % (p.returncode, len(xml)))
    for ln in xml.splitlines():
        if any(k in ln for k in ("<Command>", "<Arguments>", "<Id>")):
            w("  TASK " + ln.strip()[:400] + "\n")
except Exception as ex:
    w("task query err: %s\n" % ex)

# --- running listener processes (self-match safe) ---
try:
    import psutil
    n = 0
    for pr in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cl = " ".join(pr.info["cmdline"] or [])
            if "fleet-link" in cl and pr.info["name"] and \
                    pr.info["name"].lower().startswith("powershell"):
                w("PROC pid=%d name=%s cmd=%s\n" % (
                    pr.pid, pr.info["name"], cl[:200]))
                n += 1
        except Exception:
            pass
    w("listener-like powershell procs=%d\n" % n)
except Exception as ex:
    w("psutil err: %s\n" % ex)
out.close()
print("fl recon written")
