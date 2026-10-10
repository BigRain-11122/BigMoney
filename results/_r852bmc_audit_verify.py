# -*- coding: utf-8 -*-
# r852 bm-c: compute_audit blob-to-blob content verification (r641 rumor law)
import subprocess
import json

old = subprocess.run(["git", "show", "HEAD~1:results/compute_audit.json"],
                     capture_output=True).stdout
new = subprocess.run(["git", "show", "HEAD:results/compute_audit.json"],
                     capture_output=True).stdout
print("old blob: bytes=%d crlf=%d lf=%d | new blob: bytes=%d crlf=%d lf=%d" % (
    len(old), old.count(b"\r\n"), old.count(b"\n") - old.count(b"\r\n"),
    len(new), new.count(b"\r\n"), new.count(b"\n") - new.count(b"\r\n")))
do = json.loads(old.decode("utf-8"))
dn = json.loads(new.decode("utf-8"))
oh = do["history"]
nh = dn["history"]
print("history old_n=%d new_n=%d prefix_preserved=%s" % (
    len(oh), len(nh), oh == nh[:len(oh)]))
if len(nh) == len(oh) and len(oh) > 2:
    print("shift1 (old[1:]==new[:-1]):", oh[1:] == nh[:-1])
    print("new tail ts:", nh[-1].get("ts"), "| old tail ts:", oh[-1].get("ts"))
    print("new head ts:", nh[0].get("ts"), "| old head ts:", oh[0].get("ts"))
    print("latest old ts:", do["latest"].get("ts"), "| latest new ts:", dn["latest"].get("ts"))
    # content-set diff on history (order-insensitive) to see what really changed
    so = {json.dumps(x, sort_keys=True) for x in oh}
    sn = {json.dumps(x, sort_keys=True) for x in nh}
    print("only_in_old=%d only_in_new=%d" % (len(so - sn), len(sn - so)))
    for x in sorted(sn - so)[:3]:
        e = json.loads(x)
        print("  NEW-ENTRY:", str(e)[:180])
    for x in sorted(so - sn)[:3]:
        e = json.loads(x)
        print("  EVICTED-ENTRY:", str(e)[:180])
