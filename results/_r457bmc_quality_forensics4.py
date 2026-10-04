"""r457 bm-c QUALITY forensics4: crash_fuse sigs (quality-nulls keep-block family) + local
autofill claim posture + refusal counters. Evidence for MSG-to-bm-b advisory."""
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def load_local(rel):
    with open(rel.replace("/", "\\"), encoding="utf-8-sig") as fh:
        return json.load(fh)


def main():
    rc, blob, err = git_raw(["show", "origin/main:results/crash_fuse.json"])
    if rc == 0:
        d = json.loads(blob.decode("utf-8-sig"))
        print("== crash_fuse.json (origin) sigs matching quality/fund_nulls ==")
        for k, v in d.items():
            kl = k.lower()
            if "quality" in kl or "nulls" in kl:
                if isinstance(v, dict):
                    print("SIG %s" % k[:120])
                    for kk in ("keep_blocked", "refusals", "note", "code_sha256",
                               "cleared_ts", "last_refusal_ts"):
                        if kk in v:
                            print("   %s = %s" % (kk, str(v[kk])[:180]))
                else:
                    print("KEY %s = %s" % (k[:120], str(v)[:160]))
        print("total sig keys:", len(d))
    else:
        print("crash_fuse read fail:", err[:160])
    print("== local bm-c autofill state ==")
    try:
        st = load_local("results/autofill_state.bm-c.json")
        print("keys:", list(st.keys()))
        launches = st.get("launches", {})
        print("launch count:", len(launches) if hasattr(launches, "__len__") else "?")
        txt = json.dumps(st)
        for kw in ("FUND", "quality", "NULLS"):
            print("  contains '%s': %s" % (kw, kw in txt))
        print("last_tick:", st.get("last_tick"))
    except Exception as e:
        print("local autofill read fail:", e)
    # origin bm-b autofill: launches detail for quality
    rc, blob, _ = git_raw(["show", "origin/main:results/autofill_state.bm-b.json"])
    if rc == 0:
        d = json.loads(blob.decode("utf-8-sig"))
        launches = d.get("launches", {})
        print("== origin bm-b autofill launches ==")
        if isinstance(launches, dict):
            for k, v in list(launches.items())[:20]:
                print("  %s -> %s" % (str(k)[:80], str(v)[:160]))
        elif isinstance(launches, list):
            for v in launches[:20]:
                print("  ", str(v)[:220])


if __name__ == "__main__":
    main()
