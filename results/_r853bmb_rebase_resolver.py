# -*- coding: utf-8 -*-
"""r853 bm-b rebase-conflict resolver (31-UU window, pick db05c8b26 replay onto origin/main 5f2766618).

Law lineage:
- r782: rebase stage semantics REVERSED (stage2=onto side, stage3=replayed pick=our r852 content).
        ts evidence decides side, never stage labels.
- r917: per-face 3-state read (WT marker-free + daemon postwrite => WT live-wins; marker => S2/S3 newest-ts;
        jsonl => line-union).
- r794/r648: per-UU sha via ls-files -u + cat-file (only reliable stage read channel; :N: can yield empty rc0).
- r516: no-ts fallback MUST deep-audit both blobs (never blind-mine); receipt written for audit.
- r808: marker guard before add (caller); tip must be marker-free after continue.
- r642: registry/ledger-class faces => row-equality probe -> local(pick) side or union; never blind overwrite.

Policy per face class:
- jsonl              : line-union (S2 base then S3-only lines appended).
- md                 : embedded-ISO newest; neither parse => stage3 (replay side, r917 theirs-bytes analog).
- ledger/registry    : payload-equal => newer ts; superset => superset side; else key-union; fail-closed if impossible.
- regenerable S6     : newest-ts wins (deep recursive ts scan; no-ts-both-sides => fail-closed per r516 deep-audit law).
"""
import json, re, subprocess, sys, os, datetime, io

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = os.path.join(REPO, "results", "_r853bmb_rebase_resolver.json")
ISO_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
ISO_MIN_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
TS_KEY_RE = re.compile(r"(ts|time|date|asof|updated|generated|last|epoch|when)", re.I)

LEDGER_FACES = {
    "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
    "results/token_usage.json", "results/_attrition_guard_scan.json",
}
JSONL_FACES = {"results/x2_watch_log.jsonl", "results/saturation_engine/history_bm-b.jsonl"}

def git(*args, binary=False):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (args[0], r.returncode, r.stderr[:400].decode("utf-8", "replace")))
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")

def uu_entries():
    out = git("ls-files", "-u")
    ent = {}
    for line in out.splitlines():
        meta, path = line.split("\t")
        mode, sha, stage = meta.split()
        ent.setdefault(path, {})[int(stage)] = sha
    return {k: v for k, v in ent.items() if 2 in v and 3 in v}

def blob(sha):
    return git("cat-file", "blob", sha, binary=True)

def parse_iso(s):
    s = s.replace(" ", "T")
    try:
        return datetime.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        pass
    try:
        return datetime.datetime.strptime(s[:16], "%Y-%m-%dT%H:%M")
    except Exception:
        return None

def deep_ts(obj, best=None):
    if best is None: best = {"v": None}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                t = None
                if TS_KEY_RE.search(str(k)):
                    m = ISO_RE.search(v) or ISO_MIN_RE.search(v)
                    t = parse_iso(m.group(0)) if m else None
                if t is None:
                    m = ISO_RE.search(v)
                    t = parse_iso(m.group(0)) if m else None
                if t and (best["v"] is None or t > best["v"]): best["v"] = t
            deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj: deep_ts(v, best)
    elif isinstance(obj, str):
        m = ISO_RE.search(obj)
        if m:
            t = parse_iso(m.group(0))
            if t and (best["v"] is None or t > best["v"]): best["v"] = t
    return best["v"]

def strip_volatile_ts(obj):
    if isinstance(obj, dict):
        return {k: strip_volatile_ts(v) for k, v in sorted(obj.items())
                if not (TS_KEY_RE.search(str(k)) and isinstance(v, str) and ISO_RE.search(v))}
    if isinstance(obj, list):
        return [strip_volatile_ts(v) for v in obj]
    return obj

def key_rows(obj):
    rows = {}
    def walk(o, path):
        if isinstance(o, dict):
            if o and all(not isinstance(v, (dict, list)) for v in o.values()):
                rows[path] = o
            else:
                for k, v in o.items(): walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, path + "/%d" % i)
    walk(obj, "")
    return rows

def resolve():
    ents = uu_entries()
    receipt = {"round": "r853", "pick": "db05c8b26", "onto": "5f2766618",
               "uu_count": len(ents), "faces": {}, "unresolved": []}
    for path in sorted(ents):
        s2, s3 = blob(ents[path][2]), blob(ents[path][3])
        wt_path = os.path.join(REPO, path.replace("/", os.sep))
        if path in JSONL_FACES:
            l2 = [l for l in s2.decode("utf-8", "replace").splitlines() if l.strip()]
            l3 = [l for l in s3.decode("utf-8", "replace").splitlines() if l.strip()]
            seen = set(l2); merged = list(l2)
            for l in l3:
                if l not in seen: merged.append(l); seen.add(l)
            out = ("\n".join(merged) + "\n").encode("utf-8")
            dec = {"policy": "jsonl-line-union", "s2_lines": len(l2), "s3_lines": len(l3), "out_lines": len(merged)}
        elif path.endswith(".json"):
            try:
                j2 = json.loads(s2.decode("utf-8", "replace"))
                j3 = json.loads(s3.decode("utf-8", "replace"))
            except Exception as e:
                out, dec = s3, {"policy": "stage3-replay", "reason": "json-parse-fail:%s" % e}
            else:
                t2, t3 = deep_ts(j2), deep_ts(j3)
                p2, p3 = strip_volatile_ts(j2), strip_volatile_ts(j3)
                if p2 == p3:
                    side = "s3" if (t3 or datetime.datetime.min) >= (t2 or datetime.datetime.min) else "s2"
                    out = s3 if side == "s3" else s2
                    dec = {"policy": "payload-equal-newer-ts", "t2": str(t2), "t3": str(t3), "side": side}
                elif path in LEDGER_FACES:
                    r2, r3 = key_rows(j2), key_rows(j3)
                    k2, k3 = set(r2), set(r3)
                    if k3 >= k2:
                        out, dec = s3, {"policy": "ledger-superset-pick", "rows2": len(r2), "rows3": len(r3)}
                    elif k2 >= k3:
                        out, dec = s2, {"policy": "ledger-superset-onto", "rows2": len(r2), "rows3": len(r3)}
                    else:
                        merged = json.loads(s2.decode("utf-8", "replace"))
                        added = 0
                        for k in sorted(k3 - k2):
                            merged.setdefault("_r853_union_from_pick", {})[k] = r3[k]; added += 1
                        out = (json.dumps(merged, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
                        dec = {"policy": "ledger-key-union", "only2": len(k2 - k3), "only3": added}
                else:
                    if t2 is None and t3 is None:
                        receipt["unresolved"].append(path)
                        receipt["faces"][path] = {"policy": "FAIL-CLOSED-no-ts-both-sides"}
                        continue
                    side = "s3" if (t3 or datetime.datetime.min) >= (t2 or datetime.datetime.min) else "s2"
                    out = s3 if side == "s3" else s2
                    dec = {"policy": "regen-newest-ts", "t2": str(t2), "t3": str(t3), "side": side}
        elif path.endswith(".md") or path.endswith(".js"):
            m2 = ISO_RE.findall(s2.decode("utf-8", "replace"))
            m3 = ISO_RE.findall(s3.decode("utf-8", "replace"))
            t2 = max((parse_iso(x) for x in m2), default=None)
            t3 = max((parse_iso(x) for x in m3), default=None)
            if t2 is None and t3 is None:
                out, dec = s3, {"policy": "text-theirs-bytes", "reason": "no-iso-either"}
            else:
                side = "s3" if (t3 or datetime.datetime.min) >= (t2 or datetime.datetime.min) else "s2"
                out = s3 if side == "s3" else s2
                dec = {"policy": "text-newest-iso", "t2": str(t2), "t3": str(t3), "side": side}
        else:
            receipt["unresolved"].append(path)
            receipt["faces"][path] = {"policy": "FAIL-CLOSED-unknown-class"}
            continue
        # r648 治愈律: stage blob 自带冲突标记(对端窗污染入库) => 取对侧干净 blob; 双侧污染 => fail-closed
        if b"<<<<<<<" in out or b">>>>>>>" in out:
            alt = s2 if out is s3 else s3
            if b"<<<<<<<" not in alt and b">>>>>>>" not in alt:
                out = alt
                dec["policy"] += "+r648-clean-side-relay"
                dec["relay_from"] = "s3" if alt is s2 else "s2"
            else:
                receipt["unresolved"].append(path)
                receipt["faces"][path] = {"policy": "FAIL-CLOSED-marker-both-sides"}
                continue
        with open(wt_path, "wb") as f:
            f.write(out)
        reread = open(wt_path, "rb").read()
        assert reread == out, "write-back mismatch %s" % path
        dec["bytes"] = len(out)
        receipt["faces"][path] = dec
    receipt["ok"] = len(receipt["unresolved"]) == 0
    with io.open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("RESOLVED %d/%d ok=%s unresolved=%s" % (len(receipt["faces"]), receipt["uu_count"],
                                                   receipt["ok"], receipt["unresolved"]))
    return 0 if receipt["ok"] else 1

if __name__ == "__main__":
    sys.exit(resolve())
