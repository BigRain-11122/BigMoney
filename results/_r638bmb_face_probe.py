import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor import build_status as bs

faces = {"repo": bs._repo_state, "options": bs._options_state,
         "fund_premium": bs._premium_state, "ah_panel": bs._ah_state}
ok = True
for name, fn in faces.items():
    try:
        d = fn()
        print(f"[{name}] {json.dumps(d, ensure_ascii=False, default=str)[:300]}")
        if not isinstance(d, dict) or "present" not in d or "status" not in d or "text" not in d:
            ok = False
            print(f"  !! contract violation (present/status/text missing)")
        if d.get("present") and d.get("status") == "none":
            ok = False
            print("  !! present but status=none")
    except Exception as e:
        ok = False
        print(f"[{name}] EXCEPTION: {e!r}")
print("PROBE", "PASS" if ok else "FAIL")
