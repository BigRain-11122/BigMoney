# Trio NULLS health probe: verify QUALITY burner pid alive (r659 CSV/CIM law) + pool adoption check
import subprocess, json

def cim_pid(pid):
    # r659 law: no tasklist /FI single-pid filter (false-dead). Use CIM direct query.
    # r661 fix: %d placeholder must actually be formatted (first run shipped literal 'ProcessId=%d'
    # as WQL -> empty result -> false-dead read; repro disproved CIM, it was this format-string bug)
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process -Filter 'ProcessId=%d' | Select-Object ProcessId,Name | Format-List" % pid],
        capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    return ("ProcessId" in out), out.strip()[:200]

def main():
    # 1) pid 57116 alive check (bm-c MSG-0915 request)
    alive, detail = cim_pid(57116)
    print("pid 57116 alive:", alive, "|", detail.replace("\n", " ") if alive else "")
    # 2) current pool claim rows for trio (shared face read-only)
    try:
        pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
        entries = pool.get("entries", pool if isinstance(pool, list) else [])
        for e in entries:
            key = str(e.get("entry", e.get("key", "")))
            if "nulls" in key and any(f in key for f in ("fund-value", "fund-quality", "fund-divlowvol")):
                print("POOL:", key, "| owner=", e.get("owner"), "| owner_since=", e.get("owner_since"))
    except Exception as ex:
        print("pool read ERR:", ex)
    # 3) autofill keepalive state (bm-b lane)
    try:
        af = json.load(open("results/autofill_state.bm-b.json", encoding="utf-8"))
        print("autofill last_tick:", af.get("last_tick", af.get("ts", "?")))
        msgs = af.get("last_tick_message", af.get("message", ""))
        print("autofill msg:", str(msgs)[:300])
    except Exception as ex:
        print("autofill read ERR:", ex)
    # 4) nulls growth check (quality k now vs 510 @ 09:00 per MSG)
    for fam in ("fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"):
        p = "results/%s/nulls.jsonl" % fam
        with open(p, "rb") as f:
            lines = [l for l in f.read().split(b"\n") if l.strip()]
        print(fam, "k=", len(lines))

if __name__ == "__main__":
    main()
