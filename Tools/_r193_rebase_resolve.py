"""R193 rebase conflict resolution, stage2/stage3 full-blob route (R186 law:
conflict-marker stitching is unreliable for whole-file rewrites; the index
carries both full sides). Recipes: autofill/compute_audit history ts-union +
latest take-newer (r161/r186); dashboard whole-file newer generated_at
(r185); S6 mirrors whole-file newest real run (r192); token per-key union.
autofill_state was already resolved single-block and is skipped here."""
import io
import json
import subprocess


def stage(path: str, n: int) -> dict:
    raw = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True,
                         check=True).stdout
    return json.loads(raw.decode("utf-8-sig"))


def _ts(x) -> str:
    if isinstance(x, dict):
        for k in ("ts", "generated_at", "as_of", "last_run", "updated_at"):
            if k in x:
                return str(x[k])
        return json.dumps(x, sort_keys=True)
    return str(x)


def union_hist(a: list, b: list) -> list:
    out = {json.dumps(x, sort_keys=True): x for x in a}
    for x in b:
        out.setdefault(json.dumps(x, sort_keys=True), x)
    return sorted(out.values(), key=_ts)


def main() -> int:
    # compute_audit: history union + latest take-newer side
    p = "results/compute_audit.json"
    jo, jt = stage(p, 2), stage(p, 3)
    merged = dict(jt if _ts(jt) >= _ts(jo) else jo)
    merged["history"] = union_hist(jo.get("history", []), jt.get("history", []))
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    print("compute_audit: history", len(merged["history"]), "latest ts", merged.get("ts"))

    # dashboard_status.json: whole newer generated_at
    p = "results/dashboard_status.json"
    jo, jt = stage(p, 2), stage(p, 3)
    win = jo if str(jo.get("generated_at", "")) >= str(jt.get("generated_at", "")) else jt
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(win, fh, ensure_ascii=False, indent=1)
    print("dashboard_status.json ->", win.get("generated_at"))

    # dashboard_status.js: whole newer generated_at (raw text)
    p = "results/dashboard_status.js"
    o2 = subprocess.run(["git", "show", f":2:{p}"], capture_output=True, check=True).stdout.decode("utf-8")
    t3 = subprocess.run(["git", "show", f":3:{p}"], capture_output=True, check=True).stdout.decode("utf-8")
    import re
    g = lambda s: (re.search(r"generated_at\D+(\d{4}-\d{2}-\d{2}T[\d:.]+)", s) or [None, ""])[1]
    win = o2 if g(o2) >= g(t3) else t3
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(win)
    print("dashboard_status.js ->", g(win))

    # S6 mirrors: whole newest real-run side
    for p in ("results/update_status.json", "results/futures_update_status.json",
              "results/heat_update_status.json", "results/lhb_update_status.json",
              "results/regime_state.json", "results/fundamental_b_layer_filter.json"):
        jo, jt = stage(p, 2), stage(p, 3)
        win = jo if _ts(jo) >= _ts(jt) else jt
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(win, fh, ensure_ascii=False, indent=1)
        print(p, "->", _ts(win))

    # token_usage: per-key union preferring newer
    p = "results/token_usage.json"
    jo, jt = stage(p, 2), stage(p, 3)
    merged = dict(jo)
    for k, v in jt.items():
        if k not in merged or _ts(v) >= _ts(merged[k]):
            merged[k] = v
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    print("token_usage: keys", len(merged))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
