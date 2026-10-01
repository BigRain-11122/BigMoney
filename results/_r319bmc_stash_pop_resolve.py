import subprocess, re
# r299 law: stash-pop conflicts on re-derivable state faces -> newer-wins (stash
# side = live daemon/engine writes during the rebase window). Verify by ts.
FILES = ["results/_attrition_guard_scan.json",
         "results/saturation_engine_state.bm-c.json",
         "results/token_usage.json"]
for p in FILES:
    def st(n):
        r = subprocess.run(["git", "show", ":%d:%s" % (n, p)], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    head, stash = st(2), st(3)
    if stash is None:
        print("SKIP %s (no :3: stage)" % p)
        continue
    def ts(raw):
        m = re.search(rb'"(?:ts|last_cycle_ts|updated[_a-z]*|heartbeat_epoch)"\s*:\s*("?[^",}]+["}]?)', raw)
        return m.group(1).decode("utf-8", "ignore") if m else None
    th, tss = ts(head or b""), ts(stash)
    win = stash if head is None else (stash if (tss or "") >= (th or "") else head)
    with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\\" + p.replace("/", "\\"), "wb") as fh:
        fh.write(win)
    print("%s head_ts=%s stash_ts=%s -> %s" % (p, th, tss,
          "STASH(newer)" if win is stash else "HEAD"))
